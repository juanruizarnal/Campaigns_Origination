# Motor de Automatización de Originación Alter-5 v2.0

Sistema de IA autónomo 24/7 para automatizar el proceso completo de originación de empresas para intermediación financiera B2B.

## 🎯 Objetivo

Automatizar **completamente** el proceso de originación mediante **8 agentes especializados** que operan en 3 modos:

### Modos de Operación

| Modo | Descripción | Agentes |
|------|-------------|---------|
| **Manual** | Interfaces Airtable + Claude Desktop + MCP | FEI básico |
| **Semiautomático** | App Streamlit con supervisión humana | 1-6 |
| **Automático 24/7** | Sistema autónomo con alertas | 1-8 |

### Agentes del Sistema

1. **Buscador** - Encuentra empresas vía Gemini + scraping
2. **Enriquecedor** - Obtiene datos financieros y LinkedIn
3. **Evaluador FEI** - Determina elegibilidad FEI (≥90% precisión)
4. **Analizador** - Procesa triggers de mercado
5. **Selector** - Elige targets óptimos (ML scoring)
6. **Redactor** - Genera emails hiper-personalizados
7. **Trigger Detector** 🆕 - Monitorea RSS/News 24/7
8. **Follow-up Manager** 🆕 - Gestiona hot leads y seguimientos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    MOTOR DE ORIGINACIÓN ALTER-5 v2.0                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                           FRONTEND (Streamlit)                            │  │
│   │   📊 Dashboard | 🏢 Empresas | 🚀 Campañas | 🏷️ FEI | 📰 Triggers | 📧 Follow│  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                          │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                             8 AGENTES IA                                  │  │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │
│   │  │BUSCADOR │ │ENRIQUEC.│ │   FEI   │ │ANALIZAD.│ │SELECTOR │ │REDACTOR │ │  │
│   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │
│   │  ┌─────────┐ ┌─────────┐                                                 │  │
│   │  │TRIGGER  │ │FOLLOWUP │  🆕 Nuevos agentes para modo 24/7               │  │
│   │  │DETECTOR │ │MANAGER  │                                                 │  │
│   │  └─────────┘ └─────────┘                                                 │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                          │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                          ORQUESTACIÓN 24/7                                │  │
│   │   Celery Worker + Beat | Redis Queue | FastAPI Webhooks | Slack Alerts   │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                       │                                          │
│   ┌──────────────────────────────────────────────────────────────────────────┐  │
│   │                           INTEGRACIONES                                   │  │
│   │   Airtable │ Gemini │ Claude │ Proxycurl │ Playwright │ Mailchimp       │  │
│   └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📋 Requisitos

- Python 3.11+
- Docker & Docker Compose (para modo 24/7)
- Cuentas API: Anthropic (Claude), Google AI (Gemini), Airtable, Proxycurl (opcional)

## 🚀 Instalación

### Opción A: Desarrollo Local

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Origination_Campaigns_V2

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -e .

# 4. Instalar browsers de Playwright
playwright install chromium

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 6. Ejecutar Streamlit
streamlit run frontend/app.py
```

### Opción B: Docker (Recomendado para 24/7)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 2. Levantar servicios
docker-compose up -d

# Servicios disponibles:
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:8000
# - Redis: localhost:6379
# - MongoDB: localhost:27017
```

## 🔧 Configuración

Variables de entorno requeridas en `.env`:

```bash
# APIs Principales
ANTHROPIC_API_KEY=sk-ant-api03-...    # Claude
GOOGLE_API_KEY=AIzaSy...               # Gemini
AIRTABLE_PAT=pat...                    # Airtable
AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9

# APIs Opcionales (para modo avanzado)
PROXYCURL_API_KEY=...                  # LinkedIn data
SLACK_BOT_TOKEN=xoxb-...               # Alertas
MAILCHIMP_API_KEY=...                  # Email marketing

# Infraestructura (modo 24/7)
REDIS_URI=redis://localhost:6379/0
MONGO_URI=mongodb://localhost:27017/alter5
```

## 📁 Estructura del Proyecto

```
Origination_Campaigns_V2/
├── config/                     # Configuración
│   ├── settings.py             # Pydantic Settings
│   ├── airtable_schema.py      # Schema Airtable
│   └── prompts/                # System prompts
├── core/                       # Core components
│   ├── models.py               # Pydantic models (50+ modelos)
│   ├── airtable_client.py      # Cliente Airtable
│   └── campaign_orchestrator.py
├── agents/                     # 8 Agentes IA
│   ├── buscador.py             # Agente 1: BuscadorEmpresas
│   ├── enriquecedor.py         # Agente 2: EnriquecedorDatos
│   ├── evaluador_fei.py        # Agente 3: EvaluadorFEI
│   ├── analizador.py           # Agente 4: AnalizadorContexto
│   ├── selector.py             # Agente 5: SelectorTargets
│   ├── redactor.py             # Agente 6: RedactorMensajes
│   ├── trigger_detector.py     # Agente 7: TriggerDetector 🆕
│   └── followup_manager.py     # Agente 8: FollowupManager 🆕
├── integrations/               # Clientes APIs
│   ├── gemini.py               # Cliente Gemini
│   ├── claude.py               # Cliente Claude
│   ├── mailchimp.py            # Cliente Mailchimp
│   ├── proxycurl.py            # LinkedIn API 🆕
│   ├── scraper.py              # Playwright scraper 🆕
│   └── slack.py                # Slack alerts 🆕
├── orchestration/              # Modo 24/7 🆕
│   └── tasks.py                # Celery tasks
├── api/                        # API REST 🆕
│   └── webhooks.py             # FastAPI webhooks
├── frontend/                   # Streamlit App
│   ├── app.py                  # Entry point
│   └── pages/                  # 8 páginas
├── docker-compose.yml          # Docker config 🆕
├── Dockerfile                  # Container 🆕
└── pyproject.toml              # Dependencies
```

## 💻 Uso

### Modo Semiautomático (Streamlit)

```bash
streamlit run frontend/app.py
```

Navega a http://localhost:8501 para acceder a:
- 📊 Dashboard - KPIs y métricas
- 🔄 Originación - Pipeline búsqueda → enriquecimiento → FEI
- 🚀 Nueva Campaña - Crear campañas desde triggers
- 📰 Triggers - Monitorear eventos de mercado
- 📧 Follow-up - Gestionar hot leads

### Modo 24/7 Automático (Docker)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f celery-worker

# Ver estado de tareas
docker-compose exec app celery -A orchestration.tasks inspect active
```

Tareas programadas automáticamente:
- **Cada hora**: Escaneo de triggers (RSS feeds)
- **Cada 30 min**: Ejecución de follow-ups pendientes
- **Cada 2 horas**: Creación automática de campañas desde triggers
- **8:00 AM**: Resumen diario en Slack

### CLI (Para testing)

```bash
# Buscar empresas
python -m cli.main search companies --sector "renovables" --country ES --limit 10

# Evaluar FEI
python -m cli.main fei evaluate recXXXXXXX

# Pipeline completo
python -m cli.main originate --sector "tecnología" --country ES --enrich --fei
```

## 📊 Métricas de Éxito

| Métrica | Baseline | Target v2.0 |
|---------|----------|-------------|
| Tiempo crear campaña | 4-8h | ≤15 min |
| Precisión FEI | ~50% | ≥90% |
| Empresas/día (auto) | 0 | 500+ |
| Hot leads/semana | 2-3 | ≥15 |
| Reuniones/mes | 2-3 | ≥12 |

## 🔑 Criterios FEI

Elegibilidad FEI (AL MENOS UN criterio):

| Código | Criterio |
|--------|----------|
| 1.1 | Premio Cleantech (últimos 3 años) |
| 1.2 | Patente Clean Energy (últimos 3 años) |
| 1.3 | Eco-Label EU/Nacional/Internacional |
| 1.4 | Green Business ≥90% revenue |
| 1.5 | Green Business Model con impacto |
| 1.6 | Certificado Ambiental válido (ISO 14001, etc.) |

## 📚 Documentación

- [PRD Motor Autónomo](C.Deliverables/PRD_Motor_Originacion_Autonomo_24-7.md)
- [Plan de Desarrollo](C.Deliverables/TASK_motor_originacion.md)
- [Evaluación Código](C.Deliverables/04-Evaluacion-Adaptacion-Sistema-Autonomo.md)
- [Arquitectura Sistema](C.Deliverables/02-Arquitectura-Sistema-Autonomo.md)

## 🔄 Changelog v2.0

### Nuevos Agentes
- ✅ **Trigger Detector** (Agente 7) - Monitoreo 24/7 de RSS/News
- ✅ **Follow-up Manager** (Agente 8) - Gestión automática de hot leads

### Nuevas Integraciones
- ✅ **Playwright Scraper** - Deep scraping de websites
- ✅ **Proxycurl** - Datos de LinkedIn
- ✅ **Slack** - Sistema de alertas
- ✅ **FastAPI Webhooks** - Recepción eventos Mailchimp

### Nueva Infraestructura
- ✅ **Celery + Redis** - Task queue para 24/7
- ✅ **Docker Compose** - Entorno completo containerizado
- ✅ **Streamlit v2** - 8 páginas con nuevas funcionalidades

## 📝 Licencia

Propietario - Alter-5 © 2026
