"""Main FastAPI application for Alter-5 Origination Engine.

Combines all API routes:
- Webhooks (Mailchimp, Slack)
- REST API endpoints for manual operations
- Streamlit backend integration

Usage:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import asyncio
import secrets
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import structlog
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Depends, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from config.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


# ==============================================================================
# SECURITY - API KEY AUTHENTICATION
# ==============================================================================

# API key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Get API key from environment (generate one if not set)
API_KEY = os.getenv("ALTER5_API_KEY", "")


def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> str:
    """Validate API key from header.

    For production, set ALTER5_API_KEY environment variable.
    If not set, API authentication is disabled (development mode).
    """
    # If no API key configured, allow all requests (development mode)
    if not API_KEY:
        logger.warning("api_auth_disabled", msg="ALTER5_API_KEY not set - API is open")
        return "development"

    if not api_key_header:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header.",
        )

    if not secrets.compare_digest(api_key_header, API_KEY):
        logger.warning("api_auth_failed", provided_key_prefix=api_key_header[:8] + "...")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )

    return api_key_header


# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================

def get_cors_origins() -> list[str]:
    """Get CORS origins based on environment.

    In production, set CORS_ORIGINS environment variable as comma-separated URLs.
    """
    env_origins = os.getenv("CORS_ORIGINS", "")

    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]

    # Default development origins
    return [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",  # If using React frontend
    ]


# ==============================================================================
# REQUEST LOGGING MIDDLEWARE
# ==============================================================================

async def log_requests(request: Request, call_next):
    """Middleware to log all requests with timing."""
    start_time = datetime.now()
    request_id = secrets.token_hex(8)

    # Log request
    logger.info(
        "api_request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown",
    )

    response = await call_next(request)

    # Log response
    duration_ms = (datetime.now() - start_time).total_seconds() * 1000
    logger.info(
        "api_request_completed",
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    return response


# ==============================================================================
# LIFESPAN MANAGER
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info(
        "api_starting",
        version="2.0.0",
        auth_enabled=bool(API_KEY),
        cors_origins=get_cors_origins(),
    )

    # Startup: Initialize resources
    yield

    # Shutdown: Cleanup
    logger.info("api_shutting_down")


# ==============================================================================
# FASTAPI APPLICATION
# ==============================================================================

app = FastAPI(
    title="Alter-5 Origination Engine API",
    description="""
    Motor de automatización de originación de campañas 24/7.

    ## Autenticación

    Todas las rutas (excepto /health y /) requieren un API key.
    Incluir el header `X-API-Key` en todas las peticiones.

    ## Funcionalidades

    - **Webhooks**: Recibe eventos de Mailchimp y Slack
    - **Campaigns**: API REST para gestión de campañas
    - **Triggers**: Detección de triggers de mercado
    - **Companies**: Búsqueda y evaluación FEI
    """,
    version="2.0.0",
    lifespan=lifespan,
)

# Add request logging middleware
app.middleware("http")(log_requests)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ==============================================================================
# INCLUDE WEBHOOK ROUTES
# ==============================================================================

from api.webhooks import app as webhook_app

# Mount webhooks under /webhooks prefix
app.mount("/webhooks", webhook_app)


# ==============================================================================
# REQUEST/RESPONSE MODELS
# ==============================================================================

class TriggerScanRequest(BaseModel):
    """Request to initiate trigger scan."""
    sources: Optional[list[str]] = Field(
        default=None,
        description="Specific sources to scan (None = all)",
    )


class TriggerScanResponse(BaseModel):
    """Response from trigger scan."""
    task_id: str
    status: str
    message: str


class CampaignCreateRequest(BaseModel):
    """Request to create a campaign from trigger."""
    trigger_text: str = Field(..., description="Market trigger or context")
    products: Optional[list[str]] = Field(default=None)
    countries: Optional[list[str]] = Field(default=None)
    sectors: Optional[list[str]] = Field(default=None)
    campaign_type: str = Field(default="micro_targeted")
    max_targets: int = Field(default=20, ge=1, le=100)


class CompanySearchRequest(BaseModel):
    """Request to search for companies."""
    query: str = Field(..., description="Search query")
    countries: Optional[list[str]] = Field(default=None)
    sectors: Optional[list[str]] = Field(default=None)
    fei_eligible_only: bool = Field(default=False)
    limit: int = Field(default=50, ge=1, le=500)


class FEIEvaluationRequest(BaseModel):
    """Request to evaluate company FEI eligibility."""
    company_id: str
    force: bool = Field(default=False, description="Force re-evaluation")
    dry_run: bool = Field(default=False, description="Don't save results")


class FollowupExecutionRequest(BaseModel):
    """Request to execute scheduled follow-ups."""
    limit: Optional[int] = Field(default=None, description="Max follow-ups to execute")


# ==============================================================================
# HEALTH & STATUS ENDPOINTS (No auth required)
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Alter-5 Origination Engine",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "auth_required": bool(API_KEY),
        "endpoints": {
            "GET /health": "Health check (no auth)",
            "GET /status": "System status",
            "POST /triggers/scan": "Scan for market triggers",
            "GET /triggers": "List detected triggers",
            "POST /campaigns/create": "Create campaign from trigger",
            "GET /campaigns": "List campaigns",
            "POST /companies/search": "Search companies",
            "POST /companies/{id}/evaluate": "Evaluate FEI eligibility",
            "POST /followups/execute": "Execute scheduled follow-ups",
            "/webhooks/*": "Webhook endpoints",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring.

    No authentication required.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components": {
            "api": "up",
            "airtable": "configured" if settings.AIRTABLE_PAT else "not_configured",
            "gemini": "configured" if settings.GOOGLE_API_KEY else "not_configured",
            "claude": "configured" if settings.ANTHROPIC_API_KEY else "not_configured",
        },
    }


@app.get("/status")
async def system_status(api_key: str = Depends(get_api_key)):
    """Get detailed system status and metrics.

    Requires authentication.
    """
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "configuration": {
            "cooling_off_days": settings.COOLING_OFF_DAYS,
            "max_targets_per_campaign": settings.MAX_TARGETS_PER_CAMPAIGN,
            "min_fit_score": settings.MIN_FIT_SCORE,
            "followup_1_days": settings.FOLLOWUP_1_DAYS,
            "followup_2_days": settings.FOLLOWUP_2_DAYS,
            "max_followups": settings.MAX_FOLLOWUPS,
        },
        "integrations": {
            "airtable": bool(settings.AIRTABLE_PAT),
            "gemini": bool(settings.GOOGLE_API_KEY),
            "claude": bool(settings.ANTHROPIC_API_KEY),
            "proxycurl": bool(settings.PROXYCURL_API_KEY),
            "slack": bool(settings.SLACK_BOT_TOKEN),
            "mailchimp": bool(settings.MAILCHIMP_API_KEY),
        },
    }


# ==============================================================================
# TRIGGER ENDPOINTS
# ==============================================================================

@app.post("/triggers/scan", response_model=TriggerScanResponse)
async def scan_triggers(
    request: TriggerScanRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    """Initiate a market trigger scan.

    Scans configured RSS feeds and other sources for market events
    relevant to Alter-5's origination activities.
    """
    try:
        from orchestration.tasks import scan_triggers as scan_triggers_task

        # Dispatch Celery task
        task = scan_triggers_task.delay()

        return TriggerScanResponse(
            task_id=task.id,
            status="started",
            message="Trigger scan initiated in background",
        )
    except Exception:
        # Fallback: run synchronously if Celery not available
        from agents.trigger_detector import get_trigger_detector

        detector = get_trigger_detector()
        background_tasks.add_task(_run_trigger_scan, detector)

        return TriggerScanResponse(
            task_id="local-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            status="started",
            message="Trigger scan initiated (local mode)",
        )


async def _run_trigger_scan(detector):
    """Run trigger scan in background."""
    try:
        triggers = await detector.scan_feeds()
        logger.info("trigger_scan_completed", count=len(triggers))
    except Exception as e:
        logger.error("trigger_scan_failed", error=str(e))


@app.get("/triggers")
async def list_triggers(
    limit: int = Query(default=50, ge=1, le=200),
    processed: Optional[bool] = Query(default=None),
    min_relevance: float = Query(default=0.0, ge=0.0, le=1.0),
    api_key: str = Depends(get_api_key),
):
    """List detected market triggers.

    Returns triggers sorted by detection date (newest first).
    """
    try:
        from core.airtable_client import get_airtable_client

        airtable = get_airtable_client()

        # Build filter formula
        filters = []
        if processed is not None:
            filters.append(f"{{Processed}} = {1 if processed else 0}")
        if min_relevance > 0:
            filters.append(f"{{Relevance_Score}} >= {min_relevance}")

        formula = None
        if filters:
            formula = "AND(" + ", ".join(filters) + ")"

        records = airtable.query_records(
            "Detected_Triggers",
            formula=formula,
            max_records=limit,
            sort=[{"field": "Published_At", "direction": "desc"}],
        )

        return {
            "count": len(records),
            "triggers": [
                {
                    "id": r["id"],
                    **r["fields"],
                }
                for r in records
            ],
        }
    except Exception as e:
        logger.error("list_triggers_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# CAMPAIGN ENDPOINTS
# ==============================================================================

@app.post("/campaigns/create")
async def create_campaign(
    request: CampaignCreateRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    """Create a new campaign from a market trigger.

    Orchestrates the full campaign creation flow:
    1. Analyze trigger context
    2. Select targets
    3. Generate personalized messages
    """
    try:
        from core.campaign_orchestrator import get_campaign_orchestrator

        orchestrator = get_campaign_orchestrator()

        # Start campaign creation in background
        background_tasks.add_task(
            _create_campaign_task,
            orchestrator,
            request.trigger_text,
            request.products,
            request.countries,
            request.sectors,
            request.campaign_type,
            request.max_targets,
        )

        return {
            "status": "started",
            "message": "Campaign creation initiated",
            "trigger_preview": request.trigger_text[:100] + "..." if len(request.trigger_text) > 100 else request.trigger_text,
        }
    except Exception as e:
        logger.error("create_campaign_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def _create_campaign_task(
    orchestrator,
    trigger_text: str,
    products: Optional[list],
    countries: Optional[list],
    sectors: Optional[list],
    campaign_type: str,
    max_targets: int,
):
    """Background task to create campaign."""
    try:
        result = await orchestrator.create_campaign(
            trigger=trigger_text,
            products=products,
            countries=countries,
            sectors=sectors,
            campaign_type=campaign_type,
            max_targets=max_targets,
        )
        logger.info("campaign_created", campaign_id=result.get("campaign_id"))
    except Exception as e:
        logger.error("campaign_creation_failed", error=str(e))


@app.get("/campaigns")
async def list_campaigns(
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
    api_key: str = Depends(get_api_key),
):
    """List campaigns with optional status filter."""
    try:
        from core.airtable_client import get_airtable_client

        airtable = get_airtable_client()

        formula = None
        if status:
            formula = f"{{Campaign Status}} = '{status}'"

        records = airtable.query_records(
            "Campaigns",
            formula=formula,
            max_records=limit,
            sort=[{"field": "Created At", "direction": "desc"}],
        )

        return {
            "count": len(records),
            "campaigns": [
                {
                    "id": r["id"],
                    **r["fields"],
                }
                for r in records
            ],
        }
    except Exception as e:
        logger.error("list_campaigns_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# COMPANY ENDPOINTS
# ==============================================================================

@app.post("/companies/search")
async def search_companies(
    request: CompanySearchRequest,
    api_key: str = Depends(get_api_key),
):
    """Search for companies matching criteria.

    Uses Gemini for intelligent search with grounding.
    """
    try:
        from agents.buscador import get_buscador_empresas

        buscador = get_buscador_empresas()

        results = await buscador.search(
            query=request.query,
            countries=request.countries,
            sectors=request.sectors,
            fei_eligible_only=request.fei_eligible_only,
            limit=request.limit,
        )

        return {
            "count": len(results),
            "companies": results,
        }
    except Exception as e:
        logger.error("search_companies_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/companies/{company_id}/evaluate")
async def evaluate_fei_eligibility(
    company_id: str,
    request: FEIEvaluationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    """Evaluate a company's FEI eligibility.

    Performs deep analysis including:
    - Certificate search
    - Eco-label verification
    - Green activity assessment
    - AI-powered reasoning
    """
    try:
        from agents.evaluador_fei import get_evaluador_fei

        evaluator = get_evaluador_fei()

        # Run evaluation in background if not dry_run
        if not request.dry_run:
            background_tasks.add_task(
                _evaluate_fei_task,
                evaluator,
                company_id,
                request.force,
            )
            return {
                "status": "started",
                "message": f"FEI evaluation initiated for company {company_id}",
            }
        else:
            # Dry run: execute synchronously
            result = await asyncio.to_thread(
                evaluator.evaluate,
                company_id=company_id,
                force=request.force,
                dry_run=True,
            )
            return {
                "status": "completed",
                "result": result.model_dump() if hasattr(result, 'model_dump') else vars(result),
            }
    except Exception as e:
        logger.error("evaluate_fei_failed", error=str(e), company_id=company_id)
        raise HTTPException(status_code=500, detail=str(e))


async def _evaluate_fei_task(evaluator, company_id: str, force: bool):
    """Background task to evaluate FEI eligibility."""
    try:
        result = await asyncio.to_thread(
            evaluator.evaluate,
            company_id=company_id,
            force=force,
            dry_run=False,
        )
        logger.info(
            "fei_evaluation_completed",
            company_id=company_id,
            status=result.status.value if hasattr(result.status, 'value') else str(result.status),
        )
    except Exception as e:
        logger.error("fei_evaluation_failed", error=str(e), company_id=company_id)


# ==============================================================================
# FOLLOW-UP ENDPOINTS
# ==============================================================================

@app.post("/followups/execute")
async def execute_followups(
    request: FollowupExecutionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key),
):
    """Execute scheduled follow-up emails.

    Processes follow-up tasks that are due for execution.
    """
    try:
        from orchestration.tasks import execute_scheduled_followups

        # Dispatch Celery task
        task = execute_scheduled_followups.delay()

        return {
            "task_id": task.id,
            "status": "started",
            "message": "Follow-up execution initiated",
        }
    except Exception:
        # Fallback: run synchronously
        from agents.followup_manager import get_followup_manager

        manager = get_followup_manager()
        background_tasks.add_task(_execute_followups_task, manager, request.limit)

        return {
            "task_id": "local-" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "status": "started",
            "message": "Follow-up execution initiated (local mode)",
        }


async def _execute_followups_task(manager, limit: Optional[int]):
    """Background task to execute follow-ups."""
    try:
        executed = await manager.execute_scheduled_followups(limit=limit)
        logger.info("followups_executed", count=len(executed) if executed else 0)
    except Exception as e:
        logger.error("followups_execution_failed", error=str(e))


@app.get("/followups")
async def list_followups(
    limit: int = Query(default=50, ge=1, le=200),
    executed: Optional[bool] = Query(default=None),
    api_key: str = Depends(get_api_key),
):
    """List scheduled follow-up tasks."""
    try:
        from core.airtable_client import get_airtable_client

        airtable = get_airtable_client()

        formula = None
        if executed is not None:
            formula = f"{{Executed}} = {1 if executed else 0}"

        records = airtable.query_records(
            "Followup_Tasks",
            formula=formula,
            max_records=limit,
            sort=[{"field": "Scheduled_For", "direction": "asc"}],
        )

        return {
            "count": len(records),
            "followups": [
                {
                    "id": r["id"],
                    **r["fields"],
                }
                for r in records
            ],
        }
    except Exception as e:
        logger.error("list_followups_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
