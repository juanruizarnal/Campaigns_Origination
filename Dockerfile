# =============================================================================
# Motor de Originación Alter-5 - Dockerfile
# =============================================================================
# Multi-stage build optimizado para producción
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    # Dependencias para Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Stage 2: Dependencies
# -----------------------------------------------------------------------------
FROM base as dependencies

# Copiar solo archivos de dependencias primero (mejor cache)
COPY pyproject.toml requirements.txt ./

# Instalar dependencias de Python
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && playwright install chromium --with-deps

# -----------------------------------------------------------------------------
# Stage 3: Production
# -----------------------------------------------------------------------------
FROM dependencies as production

# Copiar código fuente
COPY config/ ./config/
COPY core/ ./core/
COPY agents/ ./agents/
COPY integrations/ ./integrations/
COPY frontend/ ./frontend/
COPY api/ ./api/
COPY orchestration/ ./orchestration/
COPY cli/ ./cli/

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser \
    && chown -R appuser:appuser /app

USER appuser

# Puertos (Streamlit: 8501, API: 8000)
EXPOSE 8501 8000

# Health check para Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || curl -f http://localhost:8000/health || exit 1

# Variables de entorno por defecto
ENV LOG_LEVEL=INFO \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Comando por defecto: Streamlit
CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port", "8501", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true", \
     "--browser.gatherUsageStats", "false"]

# -----------------------------------------------------------------------------
# Stage 4: API (alternativa para el servidor API)
# -----------------------------------------------------------------------------
FROM production as api

# Health check para API
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Stage 5: Worker (para Celery)
# -----------------------------------------------------------------------------
FROM production as worker

# Sin health check HTTP para workers
HEALTHCHECK NONE

# Comando para Celery worker
CMD ["celery", "-A", "orchestration.tasks", "worker", "-l", "info", "-c", "2"]

# -----------------------------------------------------------------------------
# Stage 6: Beat (para Celery scheduler)
# -----------------------------------------------------------------------------
FROM production as beat

# Sin health check HTTP para beat
HEALTHCHECK NONE

# Comando para Celery beat
CMD ["celery", "-A", "orchestration.tasks", "beat", "-l", "info"]
