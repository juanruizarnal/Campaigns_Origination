"""Agente Analizador de Contexto for Alter-5 Origination Engine.

This module implements the AnalizadorContexto agent (Agent 4) which analyzes
market triggers and generates structured context for origination campaigns.

The agent can:
- Search for related news using Gemini's search grounding
- Analyze impact on sectors and countries using Claude
- Generate key communication angles for personalization
- Create MarketContext records in Airtable

Usage:
    from agents.analizador import AnalizadorContexto
    
    agent = AnalizadorContexto()
    result = agent.analyze("BCE baja tipos 0.25%")
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Optional
from enum import Enum
import uuid

import structlog

from config.airtable_schema import TABLES
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from core.models import MarketContext
from integrations.gemini import GeminiClient, GeminiError, get_gemini_client
from integrations.claude import ClaudeClient, ClaudeError, get_claude_client

logger = structlog.get_logger()


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Valid sectors for campaigns
VALID_SECTORS = [
    "Industrials",
    "Real Estate", 
    "Utilities",
    "Renewables",
    "Technology",
    "Healthcare",
    "Consumer",
    "Transportation",
    "Manufacturing",
    "Agriculture",
    "Financial Services",
    "Construction",
    "Energy",
    "Telecommunications",
]

# Valid country codes
VALID_COUNTRIES = ["ES", "PT", "FR", "DE", "IT", "NL", "BE", "UK", "IE"]

# Alter-5 products
PRODUCTS = [
    "FEI_Guarantee",
    "Senior_Debt",
    "Mezzanine",
    "Equity_Coinvestment",
]

# Reliable news sources for trigger analysis
TRUSTED_SOURCES = [
    "Reuters",
    "Bloomberg",
    "Financial Times",
    "El Economista",
    "Expansión",
    "Cinco Días",
    "El País Economía",
    "European Commission",
    "ECB",
    "Banco de España",
]


# ==============================================================================
# DATA CLASSES
# ==============================================================================

class Urgency(str, Enum):
    """Urgency level for campaigns."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class NewsItem:
    """A news item related to a trigger."""
    title: str
    source: str
    date: Optional[date] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class ImpactAnalysis:
    """Analysis of trigger impact on sectors and countries."""
    affected_sectors: list[str] = field(default_factory=list)
    affected_countries: list[str] = field(default_factory=list)
    urgency: Urgency = Urgency.MEDIUM
    recommended_product: str = "FEI_Guarantee"
    campaign_potential: int = 3  # 1-5 scale
    impact_summary: str = ""
    opportunities: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete result of trigger analysis."""
    trigger: str
    news_found: list[NewsItem] = field(default_factory=list)
    impact: Optional[ImpactAnalysis] = None
    key_angles: list[str] = field(default_factory=list)
    market_context_id: Optional[str] = None
    success: bool = False
    processing_time_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    
    def should_create_campaign(self) -> bool:
        """Check if analysis recommends creating a campaign."""
        if self.impact is None:
            return False
        return self.impact.campaign_potential >= 4
    
    def get_summary(self) -> str:
        """Get a human-readable summary."""
        if not self.success:
            return f"❌ Analysis failed: {', '.join(self.errors)}"
        
        sectors = ", ".join(self.impact.affected_sectors[:3]) if self.impact else "N/A"
        countries = ", ".join(self.impact.affected_countries) if self.impact else "N/A"
        potential = self.impact.campaign_potential if self.impact else 0
        
        return (
            f"✅ Trigger: {self.trigger[:50]}...\n"
            f"   Sectors: {sectors}\n"
            f"   Countries: {countries}\n"
            f"   Campaign Potential: {'⭐' * potential}\n"
            f"   Angles: {len(self.key_angles)}"
        )


# ==============================================================================
# ANALIZADOR CONTEXTO AGENT
# ==============================================================================

class AnalizadorContexto:
    """Agent for analyzing market triggers and generating campaign context.
    
    Uses a two-phase approach:
    1. Gemini searches for relevant news and market data
    2. Claude analyzes the trigger and generates structured insights
    
    Example:
        agent = AnalizadorContexto()
        result = agent.analyze("BCE baja tipos 0.25%")
        
        if result.should_create_campaign():
            print(f"Recommended to create campaign!")
            print(f"Sectors: {result.impact.affected_sectors}")
            print(f"Key angles: {result.key_angles}")
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        gemini_client: Optional[GeminiClient] = None,
        claude_client: Optional[ClaudeClient] = None,
    ):
        """Initialize the AnalizadorContexto agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            gemini_client: Optional custom Gemini client for news search
            claude_client: Optional custom Claude client for analysis
        """
        self._airtable = airtable_client or get_airtable_client()
        self._gemini = gemini_client or get_gemini_client()
        self._claude = claude_client or get_claude_client()
        self._system_prompt = load_prompt("analizador")
        
        logger.info("analizador_contexto_initialized")
    
    def analyze(
        self,
        trigger: str,
        target_sectors: Optional[list[str]] = None,
        target_countries: Optional[list[str]] = None,
        dry_run: bool = False,
    ) -> AnalysisResult:
        """Analyze a market trigger and generate campaign context.
        
        Args:
            trigger: The market trigger text (e.g., "BCE baja tipos 0.25%")
            target_sectors: Optional list of sectors to focus on
            target_countries: Optional list of countries to focus on
            dry_run: If True, don't save to Airtable
            
        Returns:
            AnalysisResult with news, impact analysis, and key angles
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "trigger_analysis_started",
            task_id=task_id,
            trigger=trigger[:100],
            target_sectors=target_sectors,
            target_countries=target_countries,
            dry_run=dry_run,
        )
        
        result = AnalysisResult(trigger=trigger)
        
        try:
            # Validate trigger
            if not trigger or len(trigger.strip()) < 10:
                result.errors.append("Trigger text is too short (min 10 chars)")
                return result
            
            # 1. Search for related news
            news_items = self._search_news(trigger)
            result.news_found = news_items
            
            logger.info(
                "news_search_completed",
                task_id=task_id,
                news_count=len(news_items),
            )
            
            # 2. Analyze impact on sectors and countries
            impact = self._analyze_impact(
                trigger=trigger,
                news_items=news_items,
                target_sectors=target_sectors,
                target_countries=target_countries,
            )
            result.impact = impact
            
            logger.info(
                "impact_analysis_completed",
                task_id=task_id,
                sectors=impact.affected_sectors,
                countries=impact.affected_countries,
                potential=impact.campaign_potential,
            )
            
            # 3. Generate key communication angles
            key_angles = self._generate_angles(
                trigger=trigger,
                impact=impact,
                news_items=news_items,
            )
            result.key_angles = key_angles
            
            logger.info(
                "angles_generated",
                task_id=task_id,
                angles_count=len(key_angles),
            )
            
            # 4. Save to Airtable
            if not dry_run:
                context_id = self._save_context(result)
                result.market_context_id = context_id
            
            result.success = True
            
        except GeminiError as e:
            logger.error(
                "trigger_analysis_gemini_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Gemini error: {e}")
            
        except ClaudeError as e:
            logger.error(
                "trigger_analysis_claude_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Claude error: {e}")
            
        except AirtableError as e:
            logger.error(
                "trigger_analysis_airtable_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Airtable error: {e}")
            # Still mark as success if analysis worked
            result.success = len(result.key_angles) > 0
            
        except Exception as e:
            logger.error(
                "trigger_analysis_unexpected_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
        
        # Calculate processing time
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "trigger_analysis_completed",
            task_id=task_id,
            success=result.success,
            news_count=len(result.news_found),
            angles_count=len(result.key_angles),
            campaign_recommended=result.should_create_campaign(),
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def _search_news(self, trigger: str) -> list[NewsItem]:
        """Search for news related to the trigger using Gemini.
        
        Args:
            trigger: The market trigger text
            
        Returns:
            List of relevant news items
        """
        logger.debug("searching_news", trigger=trigger[:50])
        
        # Calculate date range (last 2 weeks)
        end_date = date.today()
        start_date = end_date - timedelta(days=14)
        
        query = f"""
Search for recent news and analysis about: "{trigger}"

Focus on:
- Financial news from reputable sources (Reuters, Bloomberg, FT, El Economista, Expansión)
- Official announcements (ECB, European Commission, Banco de España)
- Market analysis and expert opinions
- Impact on European markets, especially Spain and Portugal

Date range: {start_date.isoformat()} to {end_date.isoformat()}

Return ONLY a JSON object with this structure:
{{
    "news_items": [
        {{
            "title": "ECB cuts interest rates by 0.25%",
            "source": "Reuters",
            "date": "2026-01-02",
            "summary": "The European Central Bank reduced rates...",
            "url": "https://...",
            "relevance_score": 0.95
        }}
    ]
}}

Include up to 10 most relevant news items. Sort by relevance.
"""
        
        try:
            response = self._gemini.search_and_generate(
                query=query,
                system_prompt="You are a financial news analyst. Find and summarize the most relevant recent news.",
            )
            
            result = self._gemini.generate_json(
                prompt=f"Extract news items as JSON from this text:\n\n{response['response']}",
            )
            
            news_items = []
            for item_data in result.get("news_items", []):
                if item_data.get("title"):
                    # Parse date if provided
                    item_date = None
                    if item_data.get("date"):
                        try:
                            item_date = date.fromisoformat(item_data["date"])
                        except ValueError:
                            pass
                    
                    news_items.append(NewsItem(
                        title=item_data["title"],
                        source=item_data.get("source", "Unknown"),
                        date=item_date,
                        summary=item_data.get("summary"),
                        url=item_data.get("url"),
                        relevance_score=item_data.get("relevance_score", 0.5),
                    ))
            
            # Sort by relevance and return top 10
            news_items.sort(key=lambda x: x.relevance_score, reverse=True)
            return news_items[:10]
            
        except (GeminiError, KeyError, TypeError) as e:
            logger.warning("news_search_failed", trigger=trigger[:50], error=str(e))
            return []
    
    def _analyze_impact(
        self,
        trigger: str,
        news_items: list[NewsItem],
        target_sectors: Optional[list[str]] = None,
        target_countries: Optional[list[str]] = None,
    ) -> ImpactAnalysis:
        """Analyze the impact of the trigger on sectors and countries.
        
        Args:
            trigger: The market trigger text
            news_items: News items found
            target_sectors: Optional sectors to focus analysis on
            target_countries: Optional countries to focus analysis on
            
        Returns:
            ImpactAnalysis with sectors, countries, urgency, and recommendations
        """
        logger.debug("analyzing_impact", trigger=trigger[:50])
        
        # Compile news summaries for context
        news_context = ""
        if news_items:
            news_summaries = [
                f"- {item.title} ({item.source}): {item.summary or 'No summary'}"
                for item in news_items[:5]
            ]
            news_context = "\n".join(news_summaries)
        
        prompt = f"""
Analyze the following market trigger and its impact:

**TRIGGER**: {trigger}

**RECENT NEWS CONTEXT**:
{news_context if news_context else "No recent news found."}

**AVAILABLE SECTORS** (choose from these):
{', '.join(VALID_SECTORS)}

**AVAILABLE COUNTRIES** (choose from these):
{', '.join(VALID_COUNTRIES)}

**ALTER-5 PRODUCTS**:
- FEI_Guarantee: European Investment Fund guarantees, ideal for companies with environmental certifications
- Senior_Debt: Traditional senior loans
- Mezzanine: Subordinated debt
- Equity_Coinvestment: Co-investment opportunities

**YOUR TASK**:
Analyze which sectors and countries are most affected by this trigger, considering:
1. Direct financial impact (interest rates, credit conditions, etc.)
2. Industry-specific implications
3. Geographic concentration of impact
4. Timing and urgency

{f"Focus especially on these sectors: {', '.join(target_sectors)}" if target_sectors else ""}
{f"Focus especially on these countries: {', '.join(target_countries)}" if target_countries else ""}

Return ONLY a JSON object with this EXACT structure:
{{
    "affected_sectors": ["Industrials", "Real Estate"],
    "affected_countries": ["ES", "PT"],
    "urgency": "high",
    "recommended_product": "FEI_Guarantee",
    "campaign_potential": 4,
    "impact_summary": "Brief summary of the impact...",
    "opportunities": ["Opportunity 1", "Opportunity 2"],
    "risks": ["Risk 1", "Risk 2"]
}}

**Guidelines**:
- affected_sectors: 2-5 sectors most impacted (from the list above)
- affected_countries: 1-3 most affected countries (from the list above)
- urgency: "critical", "high", "medium", or "low"
- recommended_product: Best Alter-5 product for this context
- campaign_potential: 1-5 (5 = excellent opportunity for campaign)
- impact_summary: 2-3 sentences explaining the impact
- opportunities: 2-4 specific business opportunities
- risks: 1-3 potential risks to consider
"""
        
        try:
            result = self._claude.generate_structured(
                prompt=prompt,
                system_prompt=self._system_prompt,
            )
            
            # Validate and filter sectors
            affected_sectors = [
                s for s in result.get("affected_sectors", [])
                if s in VALID_SECTORS
            ]
            if not affected_sectors:
                affected_sectors = ["Industrials"]  # Default
            
            # Validate and filter countries
            affected_countries = [
                c for c in result.get("affected_countries", [])
                if c in VALID_COUNTRIES
            ]
            if not affected_countries:
                affected_countries = ["ES"]  # Default
            
            # Parse urgency
            urgency_str = result.get("urgency", "medium").lower()
            try:
                urgency = Urgency(urgency_str)
            except ValueError:
                urgency = Urgency.MEDIUM
            
            # Validate product
            recommended_product = result.get("recommended_product", "FEI_Guarantee")
            if recommended_product not in PRODUCTS:
                recommended_product = "FEI_Guarantee"
            
            # Validate campaign potential (1-5)
            campaign_potential = result.get("campaign_potential", 3)
            campaign_potential = max(1, min(5, int(campaign_potential)))
            
            return ImpactAnalysis(
                affected_sectors=affected_sectors[:5],
                affected_countries=affected_countries[:3],
                urgency=urgency,
                recommended_product=recommended_product,
                campaign_potential=campaign_potential,
                impact_summary=result.get("impact_summary", ""),
                opportunities=result.get("opportunities", [])[:4],
                risks=result.get("risks", [])[:3],
            )
            
        except (ClaudeError, KeyError, TypeError) as e:
            logger.warning("impact_analysis_failed", trigger=trigger[:50], error=str(e))
            # Return default analysis
            return ImpactAnalysis(
                affected_sectors=target_sectors or ["Industrials"],
                affected_countries=target_countries or ["ES"],
            )
    
    def _generate_angles(
        self,
        trigger: str,
        impact: ImpactAnalysis,
        news_items: list[NewsItem],
    ) -> list[str]:
        """Generate key communication angles for campaign personalization.
        
        Args:
            trigger: The market trigger text
            impact: Impact analysis result
            news_items: News items found
            
        Returns:
            List of 3-5 key communication angles
        """
        logger.debug("generating_angles", trigger=trigger[:50])
        
        # Build context from news
        news_context = ""
        if news_items:
            news_titles = [item.title for item in news_items[:3]]
            news_context = "Recent headlines: " + "; ".join(news_titles)
        
        prompt = f"""
Generate key communication angles for an origination campaign based on this market trigger:

**TRIGGER**: {trigger}

**IMPACT ANALYSIS**:
- Affected Sectors: {', '.join(impact.affected_sectors)}
- Affected Countries: {', '.join(impact.affected_countries)}
- Urgency: {impact.urgency.value}
- Recommended Product: {impact.recommended_product}
- Opportunities: {'; '.join(impact.opportunities)}

**CONTEXT**: {news_context}

**YOUR TASK**:
Generate 3-5 compelling communication angles that:
1. Connect the trigger directly to a business benefit
2. Are specific and actionable (not generic)
3. Create a sense of timeliness/opportunity
4. Consider FEI guarantees as a value-add for eligible companies
5. Are written in Spanish (formal but engaging)

Return ONLY a JSON object with this structure:
{{
    "key_angles": [
        "Oportunidad de refinanciar deuda variable aprovechando la bajada de tipos del BCE",
        "Momento ideal para financiar proyectos de expansión con condiciones favorables",
        "Las empresas con certificación ISO 14001 pueden acceder a garantías FEI con tipos preferentes"
    ]
}}

Each angle should be:
- 10-20 words
- Action-oriented
- Specific to the trigger
- Relevant for B2B origination
"""
        
        try:
            result = self._claude.generate_structured(
                prompt=prompt,
                system_prompt="You are an expert at B2B financial marketing. Generate compelling, specific communication angles in Spanish.",
            )
            
            angles = result.get("key_angles", [])
            
            # Validate angles
            valid_angles = []
            for angle in angles:
                if isinstance(angle, str) and len(angle) >= 20:
                    valid_angles.append(angle.strip())
            
            # Ensure at least 3 angles
            if len(valid_angles) < 3:
                # Add default angles based on trigger
                default_angles = [
                    f"Aprovecha el momento actual para optimizar tu estructura financiera",
                    f"Accede a condiciones preferentes gracias a las garantías del Fondo Europeo de Inversiones",
                    f"Empresas con certificación ambiental pueden beneficiarse de tipos reducidos",
                ]
                valid_angles.extend(default_angles[: 3 - len(valid_angles)])
            
            return valid_angles[:5]
            
        except (ClaudeError, KeyError, TypeError) as e:
            logger.warning("angle_generation_failed", trigger=trigger[:50], error=str(e))
            return [
                "Oportunidad de mejorar condiciones de financiación",
                "Acceso a garantías FEI para empresas elegibles",
                "Momento favorable para nuevos proyectos",
            ]
    
    def _save_context(self, result: AnalysisResult) -> str:
        """Save the analysis result as a MarketContext record in Airtable.
        
        Args:
            result: The analysis result to save
            
        Returns:
            The created record ID
        """
        if not result.impact:
            raise ValueError("Cannot save context without impact analysis")
        
        fields = {
            "Trigger_Description": result.trigger[:500],
            "Affected_Sectors": result.impact.affected_sectors,
            "Affected_Countries": result.impact.affected_countries,
            "Key_Angles": "\n".join(result.key_angles),
            "Urgency": result.impact.urgency.value.capitalize(),
            "Recommended_Product": result.impact.recommended_product,
            "Campaign_Potential": result.impact.campaign_potential,
            "Analysis_Summary": result.impact.impact_summary,
            "Analysis_Date": date.today().isoformat(),
            "Status": "Active",
        }
        
        # Add opportunities and risks if present
        if result.impact.opportunities:
            fields["Opportunities"] = "\n".join(result.impact.opportunities)
        if result.impact.risks:
            fields["Risks"] = "\n".join(result.impact.risks)
        
        # Add news sources if available
        if result.news_found:
            sources = list(set(item.source for item in result.news_found[:5]))
            fields["News_Sources"] = ", ".join(sources)
        
        try:
            record = self._airtable.create_record("market_context", fields)
            record_id = record["id"]
            
            logger.info(
                "market_context_saved",
                record_id=record_id,
                trigger=result.trigger[:50],
            )
            
            return record_id
            
        except AirtableError as e:
            logger.error("market_context_save_failed", error=str(e))
            raise


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[AnalizadorContexto] = None


def get_analizador() -> AnalizadorContexto:
    """Get shared AnalizadorContexto instance.
    
    Returns:
        Singleton AnalizadorContexto instance
    """
    global _agent
    if _agent is None:
        _agent = AnalizadorContexto()
    return _agent

