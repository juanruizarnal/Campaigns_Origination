"""Agente Trigger Detector for Alter-5 Origination Engine.

This module implements the TriggerDetector agent (Agent 7) which monitors
external sources 24/7 for market triggers that could initiate campaigns.

Sources monitored:
- RSS feeds (Financial Times, Reuters, etc.)
- Google Alerts (via email parsing)
- Company newsletters

The agent classifies triggers by relevance and recommends actions.

Usage:
    from agents.trigger_detector import TriggerDetector
    
    agent = TriggerDetector()
    triggers = await agent.scan_all_sources()
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import feedparser
import structlog

from config.settings import get_settings
from core.models import (
    DetectedTrigger,
    TriggerSource,
    TriggerRelevance,
)
from integrations.gemini import GeminiClient, get_gemini_client

logger = structlog.get_logger(__name__)


class TriggerDetector:
    """Agent for detecting market triggers from external sources.
    
    Monitors RSS feeds, news sources, and alerts to identify events
    that could be relevant for origination campaigns.
    
    Features:
    - Multi-source monitoring (RSS, alerts)
    - Relevance scoring based on keywords
    - AI-powered classification with Gemini
    - Configurable relevance thresholds
    """
    
    # RSS feeds to monitor
    RSS_FEEDS = [
        ("Financial Times - Companies", "https://www.ft.com/rss/companies"),
        ("Financial Times - Markets", "https://www.ft.com/rss/markets"),
        ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
        ("Reuters Europe", "https://feeds.reuters.com/reuters/UKBankingFinancial"),
        ("El Economista", "https://www.eleconomista.es/rss/rss-mercados.php"),
        ("Expansión", "https://e00-expansion.uecdn.es/rss/mercados.xml"),
    ]
    
    # High relevance keywords (financial/origination related)
    HIGH_RELEVANCE_KEYWORDS = [
        # Interest rates / monetary policy
        "BCE", "ECB", "tipos de interés", "interest rates", "rate cut", "rate hike",
        "bajada de tipos", "subida de tipos", "monetary policy", "política monetaria",
        
        # M&A / Corporate
        "adquisición", "acquisition", "fusión", "merger", "M&A",
        "OPA", "takeover", "LBO", "leverage buyout",
        
        # Financing
        "refinanciación", "refinancing", "financiación", "funding",
        "ampliación de capital", "capital increase", "emisión de bonos", "bond issue",
        "préstamo sindicado", "syndicated loan", "deuda corporativa", "corporate debt",
        
        # Green/Sustainability (FEI relevant)
        "FEI", "EIF", "garantía europea", "EU guarantee",
        "transición energética", "energy transition", "renovables", "renewables",
        "ESG", "sostenibilidad", "sustainability", "green finance",
        
        # Sectors
        "real estate", "inmobiliario", "defensa", "defense",
        "infraestructuras", "infrastructure", "energía", "energy",
    ]
    
    MEDIUM_RELEVANCE_KEYWORDS = [
        "inversión", "investment", "private equity", "venture capital",
        "startup", "scale-up", "pyme", "SME",
        "expansión", "expansion", "crecimiento", "growth",
        "mercados financieros", "financial markets",
        "europa", "europe", "españa", "spain", "portugal",
        "uk", "francia", "france", "alemania", "germany",
    ]
    
    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        relevance_threshold: Optional[float] = None,
    ):
        """Initialize the TriggerDetector agent.
        
        Args:
            gemini_client: Optional custom Gemini client
            relevance_threshold: Minimum relevance to consider (default from settings)
        """
        self._gemini = gemini_client or get_gemini_client()
        
        settings = get_settings()
        self._relevance_threshold = relevance_threshold or settings.TRIGGER_RELEVANCE_THRESHOLD
        self._scan_interval = settings.TRIGGER_SCAN_INTERVAL
        
        logger.info(
            "trigger_detector_initialized",
            relevance_threshold=self._relevance_threshold,
            scan_interval=self._scan_interval,
        )
    
    async def scan_all_sources(
        self,
        hours_back: int = 24,
    ) -> list[DetectedTrigger]:
        """Scan all configured sources for triggers.
        
        Args:
            hours_back: How many hours back to look
            
        Returns:
            List of detected triggers above relevance threshold
        """
        logger.info("trigger_scan_started", hours_back=hours_back)
        
        all_triggers = []
        
        # Scan RSS feeds
        rss_triggers = await self._scan_rss_feeds(hours_back)
        all_triggers.extend(rss_triggers)
        
        # Remove duplicates (by URL)
        seen_urls = set()
        unique_triggers = []
        for trigger in all_triggers:
            if trigger.source_url not in seen_urls:
                seen_urls.add(trigger.source_url)
                unique_triggers.append(trigger)
        
        # Sort by relevance
        unique_triggers.sort(key=lambda t: t.relevance_score, reverse=True)
        
        # Filter by threshold
        filtered = [t for t in unique_triggers if t.relevance_score >= self._relevance_threshold]
        
        logger.info(
            "trigger_scan_completed",
            total_found=len(all_triggers),
            unique=len(unique_triggers),
            above_threshold=len(filtered),
        )
        
        return filtered
    
    async def _scan_rss_feeds(
        self,
        hours_back: int = 24,
    ) -> list[DetectedTrigger]:
        """Scan RSS feeds for triggers.
        
        Args:
            hours_back: How many hours back to look
            
        Returns:
            List of detected triggers
        """
        triggers = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for feed_name, feed_url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:30]:  # Last 30 entries per feed
                    # Parse publication date
                    published = self._parse_entry_date(entry)
                    if published and published < cutoff_time:
                        continue
                    
                    # Get content
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    link = entry.get("link", "")
                    
                    if not title:
                        continue
                    
                    # Calculate relevance
                    text = f"{title} {summary}"
                    relevance = self._calculate_relevance(text)
                    
                    if relevance >= self._relevance_threshold * 0.5:  # Pre-filter
                        trigger = DetectedTrigger(
                            source=TriggerSource.RSS_FEED,
                            source_name=feed_name,
                            source_url=link,
                            title=title[:200],
                            summary=summary[:500] if summary else None,
                            published_at=published or datetime.now(),
                            relevance_score=relevance,
                            relevance_level=self._get_relevance_level(relevance),
                            keywords_matched=self._get_matched_keywords(text),
                            recommended_action=self._determine_action(relevance),
                        )
                        triggers.append(trigger)
                
                logger.debug(
                    "rss_feed_scanned",
                    feed=feed_name,
                    entries_checked=len(feed.entries[:30]),
                    triggers_found=len([t for t in triggers if t.source_name == feed_name]),
                )
                
            except Exception as e:
                logger.warning(
                    "rss_feed_scan_failed",
                    feed=feed_name,
                    error=str(e),
                )
        
        return triggers
    
    def _parse_entry_date(self, entry: dict) -> Optional[datetime]:
        """Parse publication date from RSS entry."""
        # Try different date fields
        date_fields = ["published_parsed", "updated_parsed", "created_parsed"]
        
        for field in date_fields:
            time_struct = entry.get(field)
            if time_struct:
                try:
                    return datetime(*time_struct[:6])
                except Exception:
                    pass
        
        # Try string parsing
        date_str = entry.get("published") or entry.get("updated")
        if date_str:
            try:
                from dateutil import parser
                return parser.parse(date_str)
            except Exception:
                pass
        
        return None
    
    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance score for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Relevance score (0-1)
        """
        text_lower = text.lower()
        score = 0.0
        
        # High relevance keywords
        for keyword in self.HIGH_RELEVANCE_KEYWORDS:
            if keyword.lower() in text_lower:
                score += 0.15
        
        # Medium relevance keywords
        for keyword in self.MEDIUM_RELEVANCE_KEYWORDS:
            if keyword.lower() in text_lower:
                score += 0.05
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _get_relevance_level(self, score: float) -> TriggerRelevance:
        """Get relevance level from score."""
        if score >= 0.8:
            return TriggerRelevance.HIGH
        elif score >= 0.5:
            return TriggerRelevance.MEDIUM
        return TriggerRelevance.LOW
    
    def _get_matched_keywords(self, text: str) -> list[str]:
        """Get list of matched keywords."""
        text_lower = text.lower()
        matched = []
        
        for keyword in self.HIGH_RELEVANCE_KEYWORDS + self.MEDIUM_RELEVANCE_KEYWORDS:
            if keyword.lower() in text_lower:
                matched.append(keyword)
        
        return matched[:10]  # Limit
    
    def _determine_action(self, relevance: float) -> str:
        """Determine recommended action based on relevance."""
        if relevance >= 0.8:
            return "create_campaign"
        elif relevance >= 0.6:
            return "notify_and_suggest"
        elif relevance >= 0.4:
            return "notify"
        return "log_only"
    
    async def analyze_trigger_with_ai(
        self,
        trigger: DetectedTrigger,
    ) -> dict:
        """Use AI to analyze a trigger in depth.
        
        Args:
            trigger: Detected trigger to analyze
            
        Returns:
            Analysis with affected sectors, countries, and products
        """
        prompt = f"""
Analiza este trigger de mercado para determinar oportunidades de originación:

**Título**: {trigger.title}
**Fuente**: {trigger.source_name}
**Resumen**: {trigger.summary or 'No disponible'}

Determina:
1. ¿Qué sectores empresariales se ven afectados?
2. ¿Qué países/regiones están más afectados?
3. ¿Qué productos financieros de Alter-5 son más relevantes?
   - FEI Guarantee (garantía europea para empresas verdes)
   - Senior Debt (deuda senior)
   - Mezzanine (financiación mezzanine)
   - Project Finance (financiación de proyectos)
4. ¿Qué tipo de campaña recomiendas?
   - Masiva (>100 targets)
   - Micro-targeting (15-30 targets específicos)
   - Individual (1-5 targets muy específicos)
5. ¿Cuál es el mensaje clave para la comunicación?

Devuelve un JSON con esta estructura:
{{
    "affected_sectors": ["Renewables", "Real Estate"],
    "affected_countries": ["España", "Portugal"],
    "recommended_products": ["Senior Debt", "FEI Guarantee"],
    "campaign_type": "micro_targeting",
    "key_message": "Con la bajada de tipos del BCE...",
    "urgency": "high|medium|low",
    "confidence": 85
}}
"""
        
        try:
            result = self._gemini.generate_json(prompt)
            
            # Update trigger with analysis
            trigger.affected_sectors = result.get("affected_sectors", [])
            trigger.affected_countries = result.get("affected_countries", [])
            trigger.recommended_products = result.get("recommended_products", [])
            
            return result
            
        except Exception as e:
            logger.error("trigger_ai_analysis_failed", error=str(e))
            return {}
    
    async def run_continuous(
        self,
        on_trigger: Optional[callable] = None,
        max_iterations: Optional[int] = None,
    ):
        """Run continuous trigger detection.
        
        Args:
            on_trigger: Callback for each detected trigger
            max_iterations: Maximum iterations (None = infinite)
        """
        logger.info(
            "continuous_trigger_detection_started",
            interval_minutes=self._scan_interval,
            max_iterations=max_iterations,
        )
        
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            try:
                # Scan for triggers
                triggers = await self.scan_all_sources(hours_back=self._scan_interval // 60 + 1)
                
                logger.info(
                    "trigger_scan_iteration",
                    iteration=iteration,
                    triggers_found=len(triggers),
                )
                
                # Process each trigger
                for trigger in triggers:
                    if on_trigger:
                        await on_trigger(trigger)
                
                # Wait for next scan
                await asyncio.sleep(self._scan_interval * 60)
                
            except Exception as e:
                logger.error("trigger_detection_error", error=str(e))
                await asyncio.sleep(60)  # Wait 1 minute on error
            
            iteration += 1


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[TriggerDetector] = None


def get_trigger_detector() -> TriggerDetector:
    """Get shared TriggerDetector instance."""
    global _agent
    if _agent is None:
        _agent = TriggerDetector()
    return _agent


async def scan_for_triggers(hours_back: int = 24) -> list[DetectedTrigger]:
    """Convenience function to scan for triggers."""
    agent = get_trigger_detector()
    return await agent.scan_all_sources(hours_back=hours_back)
