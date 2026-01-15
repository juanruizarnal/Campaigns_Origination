"""Origination Pipeline for Alter-5 Origination Engine.

This module coordinates the flow of agents 1→2→3 for new company origination:
1. BuscadorEmpresas: Find new companies matching criteria
2. EnriquecedorDatos: Enrich company data from web sources
3. EvaluadorFEI: Evaluate FEI eligibility

Usage:
    from core.origination_pipeline import OriginationPipeline
    
    pipeline = OriginationPipeline()
    result = pipeline.originate(
        sector="renovables",
        country="ES",
        limit=25,
    )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
import uuid

import structlog

from agents.buscador import (
    BuscadorEmpresas,
    SearchResult,
    SearchCriteria,
    get_buscador,
)
from agents.enriquecedor import EnriquecedorDatos, EnrichmentResult, get_enriquecedor
from agents.evaluador_fei import EvaluadorFEI, EvaluationResult, get_evaluador_fei
from core.models import FEIStatus

logger = structlog.get_logger()


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class CompanyOriginationResult:
    """Result for a single company through the pipeline."""
    company_id: str
    company_name: str
    search_success: bool = True
    enrichment_result: Optional[EnrichmentResult] = None
    fei_result: Optional[EvaluationResult] = None
    success: bool = False
    errors: list[str] = field(default_factory=list)
    
    def summary(self) -> str:
        """Get summary line for this company."""
        status = "✅" if self.success else "❌"
        
        fei_status = "N/A"
        if self.fei_result:
            fei_status = self.fei_result.status.value
        
        enriched = "✓" if self.enrichment_result and self.enrichment_result.success else "✗"
        
        return f"{status} {self.company_name[:30]}: FEI={fei_status}, Enriched={enriched}"


@dataclass
class OriginationResult:
    """Result of full origination pipeline."""
    criteria: SearchCriteria
    search_result: Optional[SearchResult] = None
    company_results: list[CompanyOriginationResult] = field(default_factory=list)
    companies_found: int = 0
    companies_enriched: int = 0
    companies_fei_evaluated: int = 0
    companies_fei_eligible: int = 0
    success: bool = False
    errors: list[str] = field(default_factory=list)
    total_processing_time_seconds: float = 0.0
    
    def __str__(self) -> str:
        if not self.success:
            return f"❌ Origination failed: {', '.join(self.errors)}"
        
        return (
            f"✅ Origination Pipeline Complete\n"
            f"   Criteria: {self.criteria.to_query()[:40]}...\n"
            f"   Companies Found: {self.companies_found}\n"
            f"   Companies Enriched: {self.companies_enriched}\n"
            f"   FEI Evaluated: {self.companies_fei_evaluated}\n"
            f"   FEI Eligible: {self.companies_fei_eligible}\n"
            f"   Processing Time: {self.total_processing_time_seconds:.1f}s"
        )
    
    def get_eligible_companies(self) -> list[CompanyOriginationResult]:
        """Get companies that are FEI eligible."""
        return [
            r for r in self.company_results
            if r.fei_result and r.fei_result.status == FEIStatus.ELIGIBLE
        ]


# ==============================================================================
# ORIGINATION PIPELINE
# ==============================================================================

class OriginationPipeline:
    """Pipeline for discovering and qualifying new companies.
    
    Coordinates the sequence:
    1. BuscadorEmpresas: Search for new companies
    2. EnriquecedorDatos: Enrich company data
    3. EvaluadorFEI: Evaluate FEI eligibility
    
    Example:
        pipeline = OriginationPipeline()
        
        result = pipeline.originate(
            sector="renovables",
            country="ES",
            region="Andalucía",
            limit=25,
            enrich=True,
            evaluate_fei=True,
        )
        
        for company in result.get_eligible_companies():
            print(f"FEI Eligible: {company.company_name}")
    """
    
    def __init__(
        self,
        buscador: Optional[BuscadorEmpresas] = None,
        enriquecedor: Optional[EnriquecedorDatos] = None,
        evaluador: Optional[EvaluadorFEI] = None,
    ):
        """Initialize the origination pipeline.
        
        Args:
            buscador: Optional custom BuscadorEmpresas
            enriquecedor: Optional custom EnriquecedorDatos
            evaluador: Optional custom EvaluadorFEI
        """
        self._buscador = buscador or get_buscador()
        self._enriquecedor = enriquecedor or get_enriquecedor()
        self._evaluador = evaluador or get_evaluador_fei()
        
        logger.info("origination_pipeline_initialized")
    
    def originate(
        self,
        sector: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        min_employees: Optional[int] = None,
        max_employees: Optional[int] = None,
        limit: int = 25,
        enrich: bool = True,
        evaluate_fei: bool = True,
        verify_urls: bool = True,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        dry_run: bool = False,
    ) -> OriginationResult:
        """Run the full origination pipeline.
        
        Args:
            sector: Target sector
            country: Target country code
            region: Target region
            keywords: Additional search keywords
            min_employees: Minimum employee count
            max_employees: Maximum employee count
            limit: Maximum companies to find
            enrich: If True, run enrichment on found companies
            evaluate_fei: If True, run FEI evaluation
            verify_urls: If True, verify company URLs
            on_progress: Optional callback for progress updates
            dry_run: If True, don't create/update records
            
        Returns:
            OriginationResult with all pipeline results
        """
        start_time = datetime.now()
        task_id = str(uuid.uuid4())[:8]
        
        criteria = SearchCriteria(
            sector=sector,
            country=country,
            region=region,
            keywords=keywords or [],
            min_employees=min_employees,
            max_employees=max_employees,
            limit=limit,
        )
        
        logger.info(
            "origination_pipeline_started",
            task_id=task_id,
            query=criteria.to_query(),
            enrich=enrich,
            evaluate_fei=evaluate_fei,
        )
        
        result = OriginationResult(criteria=criteria)
        
        try:
            # Step 1: Search for companies
            if on_progress:
                on_progress(0, 3, "Searching for companies...")
            
            search_result = self._buscador.search(
                sector=sector,
                country=country,
                region=region,
                keywords=keywords,
                min_employees=min_employees,
                max_employees=max_employees,
                limit=limit,
                verify_urls=verify_urls,
                deduplicate=True,
                create_records=not dry_run,
                dry_run=dry_run,
            )
            result.search_result = search_result
            result.companies_found = len(search_result.companies_created) if not dry_run else len(search_result.get_new_candidates())
            
            if not search_result.success:
                result.errors.extend(search_result.errors)
                logger.error(
                    "search_phase_failed",
                    task_id=task_id,
                    errors=search_result.errors,
                )
                return result
            
            logger.info(
                "search_phase_completed",
                task_id=task_id,
                companies_found=result.companies_found,
            )
            
            # Get company IDs for further processing
            if dry_run:
                # In dry run, use candidate names as IDs
                company_entries = [
                    (f"dry_run_{i}", c.name)
                    for i, c in enumerate(search_result.get_new_candidates())
                ]
            else:
                # Use actual created IDs
                company_entries = [
                    (cid, search_result.candidates_found[i].name if i < len(search_result.candidates_found) else "Unknown")
                    for i, cid in enumerate(search_result.companies_created)
                ]
            
            # Initialize company results
            for company_id, company_name in company_entries:
                result.company_results.append(
                    CompanyOriginationResult(
                        company_id=company_id,
                        company_name=company_name,
                    )
                )
            
            # Step 2: Enrich companies (if enabled)
            if enrich and company_entries and not dry_run:
                if on_progress:
                    on_progress(1, 3, "Enriching company data...")
                
                for i, company_result in enumerate(result.company_results):
                    try:
                        enrichment = self._enriquecedor.enrich(
                            company_id=company_result.company_id,
                            dry_run=dry_run,
                        )
                        company_result.enrichment_result = enrichment
                        if enrichment.success:
                            result.companies_enriched += 1
                    except Exception as e:
                        company_result.errors.append(f"Enrichment error: {e}")
                        logger.error(
                            "enrichment_failed",
                            task_id=task_id,
                            company_id=company_result.company_id,
                            error=str(e),
                        )
                
                logger.info(
                    "enrichment_phase_completed",
                    task_id=task_id,
                    enriched=result.companies_enriched,
                )
            
            # Step 3: Evaluate FEI (if enabled)
            if evaluate_fei and company_entries and not dry_run:
                if on_progress:
                    on_progress(2, 3, "Evaluating FEI eligibility...")
                
                for company_result in result.company_results:
                    try:
                        fei_eval = self._evaluador.evaluate(
                            company_id=company_result.company_id,
                            dry_run=dry_run,
                        )
                        company_result.fei_result = fei_eval
                        result.companies_fei_evaluated += 1
                        
                        if fei_eval.status == FEIStatus.ELIGIBLE:
                            result.companies_fei_eligible += 1
                            
                    except Exception as e:
                        company_result.errors.append(f"FEI evaluation error: {e}")
                        logger.error(
                            "fei_evaluation_failed",
                            task_id=task_id,
                            company_id=company_result.company_id,
                            error=str(e),
                        )
                
                logger.info(
                    "fei_evaluation_phase_completed",
                    task_id=task_id,
                    evaluated=result.companies_fei_evaluated,
                    eligible=result.companies_fei_eligible,
                )
            
            # Mark companies as successful if they passed all enabled phases
            for company_result in result.company_results:
                all_passed = True
                
                if enrich and not dry_run:
                    all_passed = all_passed and (
                        company_result.enrichment_result is not None
                        and company_result.enrichment_result.success
                    )
                
                if evaluate_fei and not dry_run:
                    all_passed = all_passed and (
                        company_result.fei_result is not None
                    )
                
                company_result.success = all_passed
            
            if on_progress:
                on_progress(3, 3, "Pipeline complete!")
            
            result.success = True
            
        except Exception as e:
            logger.error(
                "origination_pipeline_error",
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            result.errors.append(str(e))
        
        result.total_processing_time_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            "origination_pipeline_completed",
            task_id=task_id,
            success=result.success,
            companies_found=result.companies_found,
            companies_enriched=result.companies_enriched,
            companies_fei_eligible=result.companies_fei_eligible,
            processing_time=result.total_processing_time_seconds,
        )
        
        return result


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

_pipeline: Optional[OriginationPipeline] = None


def get_origination_pipeline() -> OriginationPipeline:
    """Get shared OriginationPipeline instance.
    
    Returns:
        Singleton OriginationPipeline instance
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = OriginationPipeline()
    return _pipeline

