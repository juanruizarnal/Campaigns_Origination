"""Agente Redactor de Mensajes for Alter-5 Origination Engine.

This module implements the RedactorMensajes agent (Agent 6) which generates
personalized email messages for origination campaigns.

The agent can:
- Load target information from Airtable
- Generate personalized subject lines
- Create message body with company-specific angles
- Ensure max 150 words per email
- Apply tone and style guidelines
- Save messages to Airtable

Usage:
    from agents.redactor import RedactorMensajes
    
    agent = RedactorMensajes()
    result = agent.generate(
        target_id="recTarget001",
        campaign_context="BCE baja tipos 0.25%",
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import uuid
import re

import structlog

from config.settings import get_settings
from config.airtable_schema import TABLES
from config.prompts import load_prompt
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from integrations.claude import ClaudeClient, ClaudeError, get_claude_client

logger = structlog.get_logger()
settings = get_settings()


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Maximum words per email body
MAX_EMAIL_WORDS = 150

# Maximum characters for subject line
MAX_SUBJECT_CHARS = 80

# Email tone options
TONE_OPTIONS = ["formal", "professional", "friendly", "urgent"]

# Default tone
DEFAULT_TONE = "professional"

# Sender name
DEFAULT_SENDER_NAME = "Alter5"

# FEI products
FEI_PRODUCTS = [
    "FEI_Guarantee",
    "InnovFin_Guarantee",
    "EGF_Guarantee",
    "EFSI_Guarantee",
]


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class TargetContext:
    """Context information about a campaign target."""
    target_id: str
    campaign_id: str
    business_unit_id: str
    business_unit_name: str
    company_id: str
    company_name: str
    sector: Optional[str] = None
    country: Optional[str] = None
    fei_status: str = "Unknown"
    fei_criteria_met: list[str] = field(default_factory=list)
    fei_certificates: list[str] = field(default_factory=list)
    contact_name: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_role: Optional[str] = None
    contact_email: Optional[str] = None
    contact_linkedin_url: Optional[str] = None
    contact_recent_posts: list[str] = field(default_factory=list)
    company_linkedin_url: Optional[str] = None
    company_recent_posts: list[str] = field(default_factory=list)
    company_description: Optional[str] = None
    selection_justification: Optional[str] = None
    fit_score: float = 0.0
    campaign_trigger: Optional[str] = None
    key_angles: list[str] = field(default_factory=list)
    product_recommendation: Optional[str] = None
    
    def has_personalization_data(self) -> bool:
        """Check if target has enough data for personalization."""
        return (
            self.contact_first_name is not None
            and self.company_name is not None
            and (self.sector is not None or self.fei_status != "Unknown")
        )
    
    def has_linkedin_context(self) -> bool:
        """Check if LinkedIn data is available for ultra-personalization."""
        return bool(self.contact_recent_posts) or bool(self.company_recent_posts)
    
    def get_personalization_level(self) -> str:
        """Get the level of personalization possible."""
        if self.has_linkedin_context():
            return "ultra"  # Can reference recent posts
        elif self.has_personalization_data():
            return "high"  # Has contact name, company, sector
        elif self.company_name:
            return "medium"  # Has company at least
        else:
            return "basic"  # Generic


@dataclass
class GeneratedMessage:
    """A generated email message."""
    target_id: str
    subject: str
    body: str
    word_count: int
    personalization_score: float
    tone: str = DEFAULT_TONE
    sender_name: str = DEFAULT_SENDER_NAME
    cta: Optional[str] = None
    
    def is_within_limits(self) -> bool:
        """Check if message meets length requirements."""
        return (
            self.word_count <= MAX_EMAIL_WORDS
            and len(self.subject) <= MAX_SUBJECT_CHARS
        )


@dataclass
class GenerationResult:
    """Result of message generation process."""
    target_id: str
    message: Optional[GeneratedMessage] = None
    success: bool = False
    processing_time_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        if not self.success:
            return f"❌ Generation failed for {self.target_id}: {', '.join(self.errors)}"
        
        msg = self.message
        return (
            f"✅ Message generated for {self.target_id}\n"
            f"   Subject: {msg.subject[:50]}...\n"
            f"   Words: {msg.word_count}/{MAX_EMAIL_WORDS}\n"
            f"   Personalization: {msg.personalization_score:.0%}"
        )


@dataclass
class BatchGenerationResult:
    """Result of batch message generation."""
    campaign_id: str
    results: list[GenerationResult] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    total_processing_time_seconds: float = 0.0
    
    def __str__(self) -> str:
        return (
            f"Batch generation for campaign {self.campaign_id}:\n"
            f"  ✅ Success: {self.success_count}\n"
            f"  ❌ Failed: {self.failure_count}\n"
            f"  ⏱️ Time: {self.total_processing_time_seconds:.1f}s"
        )


# ==============================================================================
# REDACTOR MENSAJES AGENT
# ==============================================================================

class RedactorMensajes:
    """Agent for generating personalized campaign messages.
    
    Uses Claude for creative message generation with:
    - Company-specific personalization
    - Campaign trigger integration
    - FEI product recommendations
    - Tone adaptation
    - Length constraints (max 150 words)
    
    Example:
        agent = RedactorMensajes()
        result = agent.generate(
            target_id="recTarget001",
            campaign_context="BCE baja tipos de interés 0.25%",
        )
        
        print(result.message.subject)
        print(result.message.body)
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        claude_client: Optional[ClaudeClient] = None,
    ):
        """Initialize the RedactorMensajes agent.
        
        Args:
            airtable_client: Optional custom Airtable client
            claude_client: Optional custom Claude client
        """
        self._airtable = airtable_client or get_airtable_client()
        self._claude = claude_client or get_claude_client()
        self._system_prompt = load_prompt("redactor")
        
        logger.info("redactor_mensajes_initialized")
    
    def generate(
        self,
        target_id: str,
        campaign_context: Optional[str] = None,
        key_angles: Optional[list[str]] = None,
        tone: str = DEFAULT_TONE,
        dry_run: bool = False,
    ) -> GenerationResult:
        """Generate a personalized message for a campaign target.
        
        Args:
            target_id: The CampaignTarget record ID
            campaign_context: Optional campaign trigger/context
            key_angles: Optional list of communication angles
            tone: Message tone (formal, professional, friendly, urgent)
            dry_run: If True, don't save to Airtable
            
        Returns:
            GenerationResult with generated message
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "message_generation_started",
            task_id=task_id,
            target_id=target_id,
            tone=tone,
        )
        
        result = GenerationResult(target_id=target_id)
        
        try:
            # 1. Load target context
            context = self._load_target_context(target_id)
            
            if campaign_context:
                context.campaign_trigger = campaign_context
            if key_angles:
                context.key_angles = key_angles
            
            logger.debug(
                "target_context_loaded",
                task_id=task_id,
                company=context.company_name,
                contact=context.contact_name,
            )
            
            # 2. Check personalization data
            if not context.has_personalization_data():
                result.warnings.append("Limited personalization data available")
            
            # 3. Generate subject line
            subject = self._generate_subject(context, tone)
            
            # 4. Generate body
            body = self._generate_body(context, tone)
            
            # 5. Calculate personalization score
            personalization_score = self._calculate_personalization_score(context, body)
            
            # 6. Count words
            word_count = self._count_words(body)
            
            # 7. Validate and truncate if needed
            if word_count > MAX_EMAIL_WORDS:
                body = self._truncate_body(body)
                word_count = self._count_words(body)
                result.warnings.append(f"Body truncated to {MAX_EMAIL_WORDS} words")
            
            if len(subject) > MAX_SUBJECT_CHARS:
                subject = subject[:MAX_SUBJECT_CHARS - 3] + "..."
                result.warnings.append(f"Subject truncated to {MAX_SUBJECT_CHARS} chars")
            
            # 8. Create message
            message = GeneratedMessage(
                target_id=target_id,
                subject=subject,
                body=body,
                word_count=word_count,
                personalization_score=personalization_score,
                tone=tone,
                cta=self._extract_cta(body),
            )
            
            # 9. Save if not dry run
            if not dry_run:
                self._save_message(target_id, message)
            
            result.message = message
            result.success = True
            
        except AirtableError as e:
            logger.error(
                "message_generation_airtable_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Airtable error: {e}")
            
        except ClaudeError as e:
            logger.error(
                "message_generation_claude_error",
                task_id=task_id,
                error=str(e),
            )
            result.errors.append(f"Claude error: {e}")
            
        except Exception as e:
            logger.error(
                "message_generation_unexpected_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(f"Unexpected error: {e}")
        
        result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "message_generation_completed",
            task_id=task_id,
            success=result.success,
            word_count=result.message.word_count if result.message else 0,
            processing_time=result.processing_time_seconds,
        )
        
        return result
    
    def generate_batch(
        self,
        campaign_id: str,
        campaign_context: Optional[str] = None,
        key_angles: Optional[list[str]] = None,
        tone: str = DEFAULT_TONE,
        dry_run: bool = False,
    ) -> BatchGenerationResult:
        """Generate messages for all targets in a campaign.
        
        Args:
            campaign_id: The Campaign record ID
            campaign_context: Optional campaign trigger/context
            key_angles: Optional list of communication angles
            tone: Message tone for all messages
            dry_run: If True, don't save to Airtable
            
        Returns:
            BatchGenerationResult with all individual results
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "batch_generation_started",
            task_id=task_id,
            campaign_id=campaign_id,
        )
        
        batch_result = BatchGenerationResult(campaign_id=campaign_id)
        
        try:
            # Get all targets for campaign
            targets = self._airtable.query_records(
                table_name="campaign_targets",
                formula=f"FIND('{campaign_id}', ARRAYJOIN({{Campaign}}))",
            )
            
            logger.info(
                "batch_targets_loaded",
                task_id=task_id,
                count=len(targets),
            )
            
            for target in targets:
                target_id = target["id"]
                
                result = self.generate(
                    target_id=target_id,
                    campaign_context=campaign_context,
                    key_angles=key_angles,
                    tone=tone,
                    dry_run=dry_run,
                )
                
                batch_result.results.append(result)
                
                if result.success:
                    batch_result.success_count += 1
                else:
                    batch_result.failure_count += 1
                    
        except AirtableError as e:
            logger.error(
                "batch_generation_failed",
                task_id=task_id,
                error=str(e),
            )
        
        batch_result.total_processing_time_seconds = (
            datetime.now() - start_time
        ).total_seconds()
        
        logger.info(
            "batch_generation_completed",
            task_id=task_id,
            success=batch_result.success_count,
            failed=batch_result.failure_count,
            processing_time=batch_result.total_processing_time_seconds,
        )
        
        return batch_result
    
    def _load_target_context(self, target_id: str) -> TargetContext:
        """Load all context needed for message generation.
        
        Args:
            target_id: The CampaignTarget record ID
            
        Returns:
            TargetContext with all relevant information
        """
        # Get target record
        target_record = self._airtable.get_record("campaign_targets", target_id)
        target_fields = target_record.get("fields", {})
        
        # Get campaign
        campaign_ids = target_fields.get("Campaign", [])
        campaign_id = campaign_ids[0] if campaign_ids else None
        campaign_trigger = None
        key_angles = []
        product_recommendation = None
        
        if campaign_id:
            try:
                campaign_record = self._airtable.get_record("origination_campaigns", campaign_id)
                campaign_fields = campaign_record.get("fields", {})
                campaign_trigger = campaign_fields.get("Trigger_Description")
                key_angles = campaign_fields.get("Key_Angles", [])
                product_recommendation = campaign_fields.get("Recommended_Product")
            except AirtableError:
                pass
        
        # Get business unit
        bu_ids = target_fields.get("Business_Unit", [])
        bu_id = bu_ids[0] if bu_ids else None
        bu_name = None
        company_id = None
        sector = None
        country = None
        
        if bu_id:
            try:
                bu_record = self._airtable.get_record("business_units", bu_id)
                bu_fields = bu_record.get("fields", {})
                bu_name = bu_fields.get("Business Unit Name")
                sector = bu_fields.get("Sector")
                country = bu_fields.get("Country")
                company_ids = bu_fields.get("Company", [])
                company_id = company_ids[0] if company_ids else None
            except AirtableError:
                pass
        
        # Get company
        company_name = None
        fei_status = "Unknown"
        fei_criteria_met = []
        
        if company_id:
            try:
                company_record = self._airtable.get_record("companies", company_id)
                company_fields = company_record.get("fields", {})
                company_name = company_fields.get("Company Name")
                fei_status = company_fields.get("FEI_Status", "Unknown")
                fei_criteria_met = company_fields.get("FEI_Criteria_Met", [])
                sector = sector or company_fields.get("Sector")
                country = country or company_fields.get("Country")
            except AirtableError:
                pass
        
        # Get contact
        contact_ids = target_fields.get("Contact", [])
        contact_name = None
        contact_first_name = None
        contact_role = None
        contact_email = None
        contact_linkedin_url = None
        contact_recent_posts = []
        
        if contact_ids:
            try:
                contact_record = self._airtable.get_record("contacts", contact_ids[0])
                contact_fields = contact_record.get("fields", {})
                first_name = contact_fields.get("First Name", "")
                last_name = contact_fields.get("Last Name", "")
                contact_name = f"{first_name} {last_name}".strip()
                contact_first_name = first_name
                contact_role = contact_fields.get("Role")
                contact_email = contact_fields.get("Email")
                contact_linkedin_url = contact_fields.get("LinkedIn_URL") or contact_fields.get("linkedin_url")
                
                # Try to get recent LinkedIn posts
                linkedin_data_str = contact_fields.get("LinkedIn_Data")
                if linkedin_data_str:
                    try:
                        import json
                        linkedin_data = json.loads(linkedin_data_str) if isinstance(linkedin_data_str, str) else linkedin_data_str
                        contact_recent_posts = linkedin_data.get("recent_posts", [])[:3]
                    except (json.JSONDecodeError, TypeError):
                        pass
            except AirtableError:
                pass
        
        # Get company LinkedIn data
        company_linkedin_url = None
        company_recent_posts = []
        company_description = None
        fei_certificates = []
        
        if company_id:
            try:
                # Reuse company_fields if already fetched
                company_linkedin_url = company_fields.get("LinkedIn_URL") if company_fields else None
                company_description = company_fields.get("Description") if company_fields else None
                fei_certificates = company_fields.get("Certificates", []) if company_fields else []
                
                linkedin_data_str = company_fields.get("LinkedIn_Data") if company_fields else None
                if linkedin_data_str:
                    try:
                        import json
                        linkedin_data = json.loads(linkedin_data_str) if isinstance(linkedin_data_str, str) else linkedin_data_str
                        company_recent_posts = linkedin_data.get("recent_posts", [])[:3]
                    except (json.JSONDecodeError, TypeError):
                        pass
            except:
                pass
        
        return TargetContext(
            target_id=target_id,
            campaign_id=campaign_id or "",
            business_unit_id=bu_id or "",
            business_unit_name=bu_name or "Unknown",
            company_id=company_id or "",
            company_name=company_name or "Unknown",
            sector=sector,
            country=country,
            fei_status=fei_status,
            fei_criteria_met=fei_criteria_met,
            fei_certificates=fei_certificates,
            contact_name=contact_name,
            contact_first_name=contact_first_name,
            contact_role=contact_role,
            contact_email=contact_email,
            contact_linkedin_url=contact_linkedin_url,
            contact_recent_posts=contact_recent_posts,
            company_linkedin_url=company_linkedin_url,
            company_recent_posts=company_recent_posts,
            company_description=company_description,
            selection_justification=target_fields.get("Selection_Justification"),
            fit_score=target_fields.get("Fit_Score", 0.0),
            campaign_trigger=campaign_trigger,
            key_angles=key_angles,
            product_recommendation=product_recommendation,
        )
    
    def _generate_subject(self, context: TargetContext, tone: str) -> str:
        """Generate email subject line.
        
        Args:
            context: Target context information
            tone: Desired message tone
            
        Returns:
            Generated subject line (max 80 chars)
        """
        prompt = f"""
Generate a compelling email subject line for a B2B sales outreach.

TARGET:
- Company: {context.company_name}
- Contact: {context.contact_first_name or 'N/A'}
- Sector: {context.sector or 'N/A'}
- FEI Status: {context.fei_status}

CAMPAIGN CONTEXT:
{context.campaign_trigger or 'General outreach'}

REQUIREMENTS:
- Max 80 characters
- Tone: {tone}
- Include company name or personalization if space allows
- Create urgency or curiosity without being spammy
- In Spanish

Return ONLY a JSON object:
{{"subject": "Your subject line here"}}
"""
        
        try:
            result = self._claude.generate_structured(
                prompt=prompt,
                system_prompt=self._system_prompt,
            )
            subject = result.get("subject", "")
            
            # Fallback if empty
            if not subject:
                subject = self._default_subject(context)
            
            return subject[:MAX_SUBJECT_CHARS]
            
        except ClaudeError:
            return self._default_subject(context)
    
    def _default_subject(self, context: TargetContext) -> str:
        """Generate default subject line without Claude.
        
        Args:
            context: Target context information
            
        Returns:
            Default subject line
        """
        if context.fei_status == "Eligible":
            return f"{context.company_name}: Acceso preferente a garantías FEI"
        elif context.campaign_trigger:
            return f"{context.company_name}: Oportunidad de financiación"
        else:
            return f"Colaboración con {context.company_name}"
    
    def _generate_body(self, context: TargetContext, tone: str) -> str:
        """Generate email body text.
        
        Args:
            context: Target context information
            tone: Desired message tone
            
        Returns:
            Generated email body (target max 150 words)
        """
        # Build LinkedIn context if available (ultra-personalization)
        linkedin_context = ""
        if context.has_linkedin_context():
            if context.contact_recent_posts:
                linkedin_context += f"""
LINKEDIN CONTEXT (use to personalize):
- Recent posts by {context.contact_first_name}: {'; '.join(context.contact_recent_posts[:2])}
"""
            if context.company_recent_posts:
                linkedin_context += f"""
- Recent company posts: {'; '.join(context.company_recent_posts[:2])}
"""
            linkedin_context += """
IMPORTANT: Reference a specific post or activity naturally in your message to show research.
"""
        
        # Build certificates context
        certs_context = ""
        if context.fei_certificates:
            certs_context = f"\n- Green Certificates: {', '.join(context.fei_certificates)}"
        
        prompt = f"""
Generate a personalized B2B sales email body for an origination campaign.

TARGET INFORMATION:
- Company: {context.company_name}
- Business Unit: {context.business_unit_name}
- Contact Name: {context.contact_name or 'Estimado/a'}
- Contact Role: {context.contact_role or 'N/A'}
- Sector: {context.sector or 'N/A'}
- Country: {context.country or 'N/A'}
- FEI Status: {context.fei_status}
- FEI Criteria Met: {', '.join(context.fei_criteria_met) if context.fei_criteria_met else 'None'}{certs_context}
- Company Description: {context.company_description[:200] if context.company_description else 'N/A'}
{linkedin_context}
CAMPAIGN CONTEXT:
Trigger: {context.campaign_trigger or 'General outreach'}
Key Angles: {', '.join(context.key_angles) if context.key_angles else 'None specified'}
Recommended Product: {context.product_recommendation or 'FEI Guarantee'}
Selection Reason: {context.selection_justification or 'Good fit for campaign'}

REQUIREMENTS:
- Max {MAX_EMAIL_WORDS} words STRICTLY
- Tone: {tone}
- Language: Spanish
- Structure:
  1. Personalized opening mentioning contact by first name
  2. {"Reference to recent LinkedIn activity if available, or " if context.has_linkedin_context() else ""}Connection to campaign trigger/market context
  3. Value proposition specific to their situation (highlight FEI eligibility if applicable)
  4. Clear CTA (call/meeting request)
  5. Professional closing

DO NOT include:
- Subject line (only body)
- Signature
- Generic greetings like "Espero que este mensaje le encuentre bien"
- Excessive formality

Return ONLY a JSON object:
{{"body": "Your email body here", "cta": "Specific call to action"}}
"""
        
        try:
            result = self._claude.generate_structured(
                prompt=prompt,
                system_prompt=self._system_prompt,
            )
            body = result.get("body", "")
            
            # Fallback if empty
            if not body:
                body = self._default_body(context)
            
            return body
            
        except ClaudeError:
            return self._default_body(context)
    
    def _default_body(self, context: TargetContext) -> str:
        """Generate default email body without Claude.
        
        Args:
            context: Target context information
            
        Returns:
            Default email body
        """
        first_name = context.contact_first_name or "Estimado/a"
        company = context.company_name
        
        if context.fei_status == "Eligible":
            return f"""Hola {first_name},

Me pongo en contacto porque {company} cumple los criterios para acceder a garantías del Fondo Europeo de Inversiones (FEI), lo que permite obtener financiación en condiciones preferentes.

Dada la posición de {company} en el mercado, creemos que podría beneficiarse significativamente de estas líneas de financiación alternativa.

¿Podríamos agendar una llamada de 15 minutos esta semana para explorar esta oportunidad?

Un saludo,
Alter5"""
        else:
            return f"""Hola {first_name},

Me pongo en contacto para presentarte las soluciones de financiación alternativa que ofrecemos desde Alter5.

Trabajamos con empresas del sector {context.sector or 'industrial'} como {company} para facilitar el acceso a financiación con garantías europeas.

¿Te interesaría una breve conversación para valorar si podemos aportar valor a {company}?

Un saludo,
Alter5"""
    
    def _calculate_personalization_score(self, context: TargetContext, body: str) -> float:
        """Calculate how personalized the message is.
        
        Score based on:
        - Contact name used: +0.15
        - Company name used: +0.15
        - Sector mentioned: +0.15
        - FEI/criteria mentioned: +0.15
        - Campaign trigger integrated: +0.15
        - Role mentioned: +0.10
        - LinkedIn reference: +0.15 (ultra-personalization)
        - Certificates mentioned: +0.09
        
        Args:
            context: Target context
            body: Generated message body
            
        Returns:
            Personalization score (0-1)
        """
        score = 0.0
        body_lower = body.lower()
        
        # Contact name used
        if context.contact_first_name and context.contact_first_name.lower() in body_lower:
            score += 0.15
        
        # Company name used
        if context.company_name and context.company_name.lower() in body_lower:
            score += 0.15
        
        # Sector mentioned
        if context.sector and context.sector.lower() in body_lower:
            score += 0.15
        
        # FEI mentioned
        if "fei" in body_lower or "fondo europeo" in body_lower or "garantía europea" in body_lower:
            score += 0.15
        
        # Campaign trigger integrated
        if context.campaign_trigger:
            # Check if any word from trigger appears in body
            trigger_words = context.campaign_trigger.lower().split()
            if any(word in body_lower for word in trigger_words if len(word) > 4):
                score += 0.15
        
        # Role mentioned
        if context.contact_role and context.contact_role.lower() in body_lower:
            score += 0.10
        
        # LinkedIn reference (ultra-personalization bonus)
        linkedin_referenced = False
        if context.contact_recent_posts:
            for post in context.contact_recent_posts:
                if any(word.lower() in body_lower for word in post.split()[:5] if len(word) > 4):
                    linkedin_referenced = True
                    break
        if context.company_recent_posts and not linkedin_referenced:
            for post in context.company_recent_posts:
                if any(word.lower() in body_lower for word in post.split()[:5] if len(word) > 4):
                    linkedin_referenced = True
                    break
        if linkedin_referenced or "linkedin" in body_lower or "publicación" in body_lower:
            score += 0.15
        
        # Certificates mentioned
        if context.fei_certificates:
            for cert in context.fei_certificates:
                if cert.lower() in body_lower:
                    score += 0.09
                    break
        
        return min(1.0, score)
    
    def _count_words(self, text: str) -> int:
        """Count words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Word count
        """
        # Remove extra whitespace and count
        words = text.split()
        return len(words)
    
    def _truncate_body(self, body: str) -> str:
        """Truncate body to max words while maintaining coherence.
        
        Args:
            body: Body text to truncate
            
        Returns:
            Truncated body
        """
        words = body.split()
        
        if len(words) <= MAX_EMAIL_WORDS:
            return body
        
        # Try to find a good break point
        truncated = words[:MAX_EMAIL_WORDS]
        text = " ".join(truncated)
        
        # Try to end at a sentence
        sentences = re.split(r'[.!?]', text)
        if len(sentences) > 1:
            # Keep all complete sentences
            complete = text[:text.rfind('.') + 1] if '.' in text else text
            if self._count_words(complete) >= MAX_EMAIL_WORDS * 0.7:
                return complete
        
        # Add closing if cut mid-sentence
        if not text.endswith(('.', '!', '?')):
            text = text.rstrip(',;:') + "..."
        
        return text
    
    def _extract_cta(self, body: str) -> Optional[str]:
        """Extract call-to-action from message body.
        
        Args:
            body: Message body
            
        Returns:
            Extracted CTA or None
        """
        # Look for common CTA patterns
        cta_patterns = [
            r'¿(?:Podríamos|Podemos|Te interesaría|Tienes)[^?]+\?',
            r'¿[^?]*(?:llamada|reunión|conversación|charlar)[^?]*\?',
            r'(?:Quedo|Quedamos)[^.!?]+[.!?]',
        ]
        
        for pattern in cta_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _save_message(self, target_id: str, message: GeneratedMessage) -> None:
        """Save generated message to Airtable.
        
        Updates the CampaignTarget record with the message.
        
        Args:
            target_id: The CampaignTarget record ID
            message: The generated message
        """
        fields = {
            "Email_Subject": message.subject,
            "Email_Body": message.body,
            "Email_Word_Count": message.word_count,
            "Personalization_Score": message.personalization_score,
            "Email_Tone": message.tone,
            "Message_Status": "Generated",
        }
        
        if message.cta:
            fields["Email_CTA"] = message.cta
        
        try:
            self._airtable.update_record("campaign_targets", target_id, fields)
            
            logger.debug(
                "message_saved",
                target_id=target_id,
                subject_preview=message.subject[:30],
            )
            
        except AirtableError as e:
            logger.error(
                "message_save_failed",
                target_id=target_id,
                error=str(e),
            )
            raise


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_agent: Optional[RedactorMensajes] = None


def get_redactor() -> RedactorMensajes:
    """Get shared RedactorMensajes instance.
    
    Returns:
        Singleton RedactorMensajes instance
    """
    global _agent
    if _agent is None:
        _agent = RedactorMensajes()
    return _agent

