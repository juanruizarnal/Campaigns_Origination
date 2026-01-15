"""Campaign Orchestrator for Alter-5 Origination Engine.

This module coordinates the flow of agents 4→5→6 for campaign creation:
1. AnalizadorContexto: trigger → Market_Context
2. SelectorTargets: context → List[CampaignTarget] (proposal)
3. [HUMAN APPROVAL]
4. RedactorMensajes: targets → personalized emails

Usage:
    from core.campaign_orchestrator import CampaignOrchestrator
    
    orchestrator = CampaignOrchestrator()
    campaign = orchestrator.create_from_trigger(
        trigger="BCE baja tipos 0.25%",
        sectors=["Industrials", "Renewables"],
        countries=["ES", "PT"],
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
import uuid

import structlog

from config.settings import get_settings
from config.airtable_schema import TABLES
from core.airtable_client import AirtableClient, AirtableError, get_airtable_client
from agents.analizador import AnalizadorContexto, AnalysisResult, get_analizador
from agents.selector import SelectorTargets, SelectionResult, get_selector
from agents.redactor import RedactorMensajes, BatchGenerationResult, get_redactor

logger = structlog.get_logger()
settings = get_settings()


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Campaign status options
CAMPAIGN_STATUS = [
    "Draft",
    "Analyzing",
    "Selecting_Targets",
    "Pending_Approval",
    "Approved",
    "Generating_Messages",
    "Ready",
    "Active",
    "Completed",
    "Cancelled",
]


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class CampaignProposal:
    """Proposal for a new campaign before approval."""
    campaign_id: str
    trigger: str
    analysis: Optional[AnalysisResult] = None
    selection: Optional[SelectionResult] = None
    status: str = "Draft"
    created_at: datetime = field(default_factory=datetime.now)
    
    def summary(self) -> str:
        """Get summary of proposal."""
        lines = [
            f"📋 Campaign Proposal: {self.campaign_id}",
            f"   Trigger: {self.trigger[:50]}...",
            f"   Status: {self.status}",
        ]
        
        if self.analysis and self.analysis.success:
            impact = self.analysis.impact
            if impact:
                lines.append(f"   Sectors: {', '.join(impact.affected_sectors)}")
                lines.append(f"   Countries: {', '.join(impact.affected_countries)}")
                lines.append(f"   Campaign Potential: {impact.campaign_potential}/5")
        
        if self.selection and self.selection.success:
            lines.append(f"   Targets Proposed: {len(self.selection.targets)}")
            if self.selection.targets:
                avg_score = sum(t.fit_score for t in self.selection.targets) / len(self.selection.targets)
                lines.append(f"   Avg Fit Score: {avg_score:.0%}")
        
        return "\n".join(lines)


@dataclass
class CampaignResult:
    """Result of full campaign creation."""
    campaign_id: str
    proposal: Optional[CampaignProposal] = None
    messages: Optional[BatchGenerationResult] = None
    status: str = "Draft"
    success: bool = False
    errors: list[str] = field(default_factory=list)
    total_processing_time_seconds: float = 0.0
    
    def __str__(self) -> str:
        if not self.success:
            return f"❌ Campaign failed: {', '.join(self.errors)}"
        
        lines = [
            f"✅ Campaign {self.campaign_id} created successfully!",
            f"   Status: {self.status}",
        ]
        
        if self.proposal and self.proposal.selection:
            lines.append(f"   Targets: {len(self.proposal.selection.targets)}")
        
        if self.messages:
            lines.append(f"   Messages Generated: {self.messages.success_count}")
        
        lines.append(f"   Processing Time: {self.total_processing_time_seconds:.1f}s")
        
        return "\n".join(lines)


# ==============================================================================
# CAMPAIGN ORCHESTRATOR
# ==============================================================================

class CampaignOrchestrator:
    """Orchestrator for the full campaign creation flow.
    
    Coordinates the sequence:
    1. AnalizadorContexto analyzes the trigger
    2. SelectorTargets selects best BUs
    3. Human approves target list
    4. RedactorMensajes generates personalized emails
    
    Example:
        orchestrator = CampaignOrchestrator()
        
        # Step 1: Create proposal
        proposal = orchestrator.create_proposal(
            trigger="BCE baja tipos 0.25%",
            sectors=["Industrials"],
            countries=["ES"],
        )
        
        # Step 2: Human reviews and approves
        print(proposal.summary())
        
        # Step 3: Complete campaign
        result = orchestrator.complete_campaign(proposal.campaign_id)
    """
    
    def __init__(
        self,
        airtable_client: Optional[AirtableClient] = None,
        analizador: Optional[AnalizadorContexto] = None,
        selector: Optional[SelectorTargets] = None,
        redactor: Optional[RedactorMensajes] = None,
    ):
        """Initialize the orchestrator.
        
        Args:
            airtable_client: Optional custom Airtable client
            analizador: Optional custom AnalizadorContexto
            selector: Optional custom SelectorTargets
            redactor: Optional custom RedactorMensajes
        """
        self._airtable = airtable_client or get_airtable_client()
        self._analizador = analizador or get_analizador()
        self._selector = selector or get_selector()
        self._redactor = redactor or get_redactor()
        
        logger.info("campaign_orchestrator_initialized")
    
    def create_proposal(
        self,
        trigger: str,
        sectors: list[str],
        countries: list[str],
        max_targets: int = 30,
        min_fit_score: float = 0.6,
        dry_run: bool = False,
    ) -> CampaignProposal:
        """Create a campaign proposal for human review.
        
        Steps:
        1. Analyze trigger with AnalizadorContexto
        2. Select targets with SelectorTargets
        3. Save proposal as Draft campaign
        
        Args:
            trigger: Market trigger text
            sectors: List of target sectors
            countries: List of target countries
            max_targets: Maximum targets to select
            min_fit_score: Minimum fit score for selection
            dry_run: If True, don't save to Airtable
            
        Returns:
            CampaignProposal ready for human review
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "campaign_proposal_started",
            task_id=task_id,
            trigger_preview=trigger[:50],
            sectors=sectors,
            countries=countries,
        )
        
        # Create campaign record
        campaign_id = self._create_campaign_record(
            trigger=trigger,
            sectors=sectors,
            countries=countries,
            status="Analyzing",
            dry_run=dry_run,
        )
        
        proposal = CampaignProposal(
            campaign_id=campaign_id,
            trigger=trigger,
            status="Analyzing",
        )
        
        try:
            # Step 1: Analyze trigger
            logger.info("analyzing_trigger", task_id=task_id)
            analysis = self._analizador.analyze(
                trigger=trigger,
                target_sectors=sectors,
                target_countries=countries,
                dry_run=dry_run,
            )
            proposal.analysis = analysis
            
            if not analysis.success:
                proposal.status = "Failed"
                logger.error(
                    "analysis_failed",
                    task_id=task_id,
                    errors=analysis.errors,
                )
                return proposal
            
            # Update campaign status
            self._update_campaign_status(campaign_id, "Selecting_Targets", dry_run)
            proposal.status = "Selecting_Targets"
            
            # Step 2: Select targets
            logger.info("selecting_targets", task_id=task_id)
            
            # Use analysis results if available
            final_sectors = analysis.impact.affected_sectors if analysis.impact else sectors
            final_countries = analysis.impact.affected_countries if analysis.impact else countries
            market_context = analysis.get_summary() if analysis.success else None
            
            selection = self._selector.select(
                campaign_id=campaign_id,
                affected_sectors=final_sectors,
                affected_countries=final_countries,
                market_context_summary=market_context,
                max_targets=max_targets,
                min_fit_score=min_fit_score,
                dry_run=dry_run,
            )
            proposal.selection = selection
            
            if not selection.success or not selection.targets:
                proposal.status = "No_Targets"
                logger.warning(
                    "selection_empty",
                    task_id=task_id,
                    errors=selection.errors,
                )
                return proposal
            
            # Update campaign status
            self._update_campaign_status(campaign_id, "Pending_Approval", dry_run)
            proposal.status = "Pending_Approval"
            
            logger.info(
                "campaign_proposal_ready",
                task_id=task_id,
                campaign_id=campaign_id,
                targets_count=len(selection.targets),
            )
            
        except Exception as e:
            logger.error(
                "campaign_proposal_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            proposal.status = "Failed"
        
        return proposal
    
    def approve_campaign(
        self,
        campaign_id: str,
        dry_run: bool = False,
    ) -> bool:
        """Approve a campaign proposal.
        
        Args:
            campaign_id: The campaign record ID
            dry_run: If True, don't update Airtable
            
        Returns:
            True if approval successful
        """
        logger.info("campaign_approved", campaign_id=campaign_id)
        self._update_campaign_status(campaign_id, "Approved", dry_run)
        return True
    
    def complete_campaign(
        self,
        campaign_id: str,
        campaign_context: Optional[str] = None,
        key_angles: Optional[list[str]] = None,
        tone: str = "professional",
        dry_run: bool = False,
    ) -> CampaignResult:
        """Complete campaign by generating messages.
        
        Should be called after human approval.
        
        Args:
            campaign_id: The campaign record ID
            campaign_context: Optional context for messages
            key_angles: Optional communication angles
            tone: Message tone
            dry_run: If True, don't save messages
            
        Returns:
            CampaignResult with generated messages
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        logger.info(
            "campaign_completion_started",
            task_id=task_id,
            campaign_id=campaign_id,
        )
        
        result = CampaignResult(campaign_id=campaign_id)
        
        try:
            # Update status
            self._update_campaign_status(campaign_id, "Generating_Messages", dry_run)
            result.status = "Generating_Messages"
            
            # Generate messages for all targets
            messages = self._redactor.generate_batch(
                campaign_id=campaign_id,
                campaign_context=campaign_context,
                key_angles=key_angles,
                tone=tone,
                dry_run=dry_run,
            )
            result.messages = messages
            
            if messages.failure_count > 0:
                result.errors.append(f"{messages.failure_count} messages failed to generate")
            
            # Update status
            final_status = "Ready" if messages.success_count > 0 else "Failed"
            self._update_campaign_status(campaign_id, final_status, dry_run)
            result.status = final_status
            result.success = messages.success_count > 0
            
            logger.info(
                "campaign_completion_done",
                task_id=task_id,
                campaign_id=campaign_id,
                messages_generated=messages.success_count,
                messages_failed=messages.failure_count,
            )
            
        except Exception as e:
            logger.error(
                "campaign_completion_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(str(e))
            self._update_campaign_status(campaign_id, "Failed", dry_run)
            result.status = "Failed"
        
        result.total_processing_time_seconds = (datetime.now() - start_time).total_seconds()
        return result
    
    def create_campaign_full(
        self,
        trigger: str,
        sectors: list[str],
        countries: list[str],
        max_targets: int = 30,
        min_fit_score: float = 0.6,
        tone: str = "professional",
        auto_approve: bool = False,
        on_approval_callback: Optional[Callable[[CampaignProposal], bool]] = None,
        dry_run: bool = False,
    ) -> CampaignResult:
        """Create a full campaign from trigger to messages.
        
        This runs the complete flow:
        1. Analyze trigger
        2. Select targets
        3. Get approval (auto or callback)
        4. Generate messages
        
        Args:
            trigger: Market trigger text
            sectors: List of target sectors
            countries: List of target countries
            max_targets: Maximum targets
            min_fit_score: Minimum fit score
            tone: Message tone
            auto_approve: If True, skip approval step
            on_approval_callback: Optional callback for approval
            dry_run: If True, don't save to Airtable
            
        Returns:
            CampaignResult with full campaign
        """
        start_time = datetime.now()
        
        # Step 1-2: Create proposal
        proposal = self.create_proposal(
            trigger=trigger,
            sectors=sectors,
            countries=countries,
            max_targets=max_targets,
            min_fit_score=min_fit_score,
            dry_run=dry_run,
        )
        
        result = CampaignResult(
            campaign_id=proposal.campaign_id,
            proposal=proposal,
        )
        
        if proposal.status not in ["Pending_Approval"]:
            result.errors.append(f"Proposal failed with status: {proposal.status}")
            result.status = "Failed"
            return result
        
        # Step 3: Approval
        approved = False
        if auto_approve:
            approved = True
        elif on_approval_callback:
            approved = on_approval_callback(proposal)
        else:
            # In interactive mode, this would wait for human input
            # For now, auto-approve in non-interactive context
            approved = True
        
        if not approved:
            result.status = "Rejected"
            result.errors.append("Campaign was not approved")
            self._update_campaign_status(proposal.campaign_id, "Cancelled", dry_run)
            return result
        
        self.approve_campaign(proposal.campaign_id, dry_run)
        
        # Step 4: Generate messages
        key_angles = proposal.analysis.key_angles if proposal.analysis else None
        context = proposal.trigger
        
        completion = self.complete_campaign(
            campaign_id=proposal.campaign_id,
            campaign_context=context,
            key_angles=key_angles,
            tone=tone,
            dry_run=dry_run,
        )
        
        result.messages = completion.messages
        result.status = completion.status
        result.success = completion.success
        result.errors.extend(completion.errors)
        result.total_processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def _create_campaign_record(
        self,
        trigger: str,
        sectors: list[str],
        countries: list[str],
        status: str = "Draft",
        dry_run: bool = False,
    ) -> str:
        """Create campaign record in Airtable.
        
        Args:
            trigger: Trigger description
            sectors: Target sectors
            countries: Target countries
            status: Initial status
            dry_run: If True, return fake ID
            
        Returns:
            Campaign record ID
        """
        if dry_run:
            return f"rec_dry_run_{uuid.uuid4().hex[:8]}"
        
        fields = {
            "Trigger_Description": trigger,
            "Target_Sectors": sectors,
            "Target_Countries": countries,
            "Status": status,
            "Created_Date": datetime.now().isoformat(),
        }
        
        try:
            record = self._airtable.create_record("origination_campaigns", fields)
            return record["id"]
        except AirtableError as e:
            logger.error("campaign_create_failed", error=str(e))
            return f"rec_error_{uuid.uuid4().hex[:8]}"
    
    def _update_campaign_status(
        self,
        campaign_id: str,
        status: str,
        dry_run: bool = False,
    ) -> None:
        """Update campaign status in Airtable.
        
        Args:
            campaign_id: Campaign record ID
            status: New status
            dry_run: If True, skip update
        """
        if dry_run or campaign_id.startswith("rec_dry_run"):
            return
        
        try:
            self._airtable.update_record(
                "origination_campaigns",
                campaign_id,
                {"Status": status},
            )
        except AirtableError as e:
            logger.error(
                "campaign_status_update_failed",
                campaign_id=campaign_id,
                status=status,
                error=str(e),
            )


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_orchestrator: Optional[CampaignOrchestrator] = None


def get_orchestrator() -> CampaignOrchestrator:
    """Get shared CampaignOrchestrator instance.
    
    Returns:
        Singleton CampaignOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CampaignOrchestrator()
    return _orchestrator

