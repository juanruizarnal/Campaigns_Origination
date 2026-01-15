"""AI Agents module for Alter-5 Origination Engine.

This module contains the 6 specialized AI agents:
- Buscador_Empresas: Search for companies matching criteria
- Enriquecedor_Datos: Enrich company data from web sources
- Evaluador_FEI: Evaluate FEI eligibility
- Analizador_Contexto: Analyze market context and triggers
- Selector_Targets: Select optimal campaign targets
- Redactor_Mensajes: Generate personalized email messages
"""

from agents.buscador import (
    BuscadorEmpresas,
    SearchCriteria,
    CompanyCandidate,
    SearchResult,
    get_buscador,
)

from agents.enriquecedor import (
    EnriquecedorDatos,
    EnrichmentResult,
    CompanyInfo,
    FinancialInfo,
    KeyPersonInfo,
    get_enriquecedor,
)

from agents.evaluador_fei import (
    EvaluadorFEI,
    EvaluationResult,
    CertificateEvidence,
    PrizeEvidence,
    GreenActivityEvidence,
    CriterionResult,
    get_evaluador_fei,
)

from agents.analizador import (
    AnalizadorContexto,
    AnalysisResult,
    NewsItem,
    ImpactAnalysis,
    Urgency,
    get_analizador,
)

from agents.selector import (
    SelectorTargets,
    SelectionResult,
    TargetCandidate,
    get_selector,
    COOLING_OFF_DAYS,
    MAX_TARGETS_PER_CAMPAIGN,
    MIN_FIT_SCORE,
)

from agents.redactor import (
    RedactorMensajes,
    GeneratedMessage,
    GenerationResult,
    BatchGenerationResult,
    TargetContext,
    get_redactor,
    MAX_EMAIL_WORDS,
)

__all__ = [
    # Buscador Empresas (Agent 1)
    "BuscadorEmpresas",
    "SearchCriteria",
    "CompanyCandidate",
    "SearchResult",
    "get_buscador",
    # Enriquecedor (Agent 2)
    "EnriquecedorDatos",
    "EnrichmentResult",
    "CompanyInfo",
    "FinancialInfo",
    "KeyPersonInfo",
    "get_enriquecedor",
    # Evaluador FEI (Agent 3)
    "EvaluadorFEI",
    "EvaluationResult",
    "CertificateEvidence",
    "PrizeEvidence",
    "GreenActivityEvidence",
    "CriterionResult",
    "get_evaluador_fei",
    # Analizador Contexto (Agent 4)
    "AnalizadorContexto",
    "AnalysisResult",
    "NewsItem",
    "ImpactAnalysis",
    "Urgency",
    "get_analizador",
    # Selector Targets (Agent 5)
    "SelectorTargets",
    "SelectionResult",
    "TargetCandidate",
    "get_selector",
    "COOLING_OFF_DAYS",
    "MAX_TARGETS_PER_CAMPAIGN",
    "MIN_FIT_SCORE",
    # Redactor Mensajes (Agent 6)
    "RedactorMensajes",
    "GeneratedMessage",
    "GenerationResult",
    "BatchGenerationResult",
    "TargetContext",
    "get_redactor",
    "MAX_EMAIL_WORDS",
]
