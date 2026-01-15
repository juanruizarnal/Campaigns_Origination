# Tareas de Desarrollo: Motor de Originación Alter-5

**Versión**: 1.0  
**Fecha**: 2 Enero 2026  
**Basado en**: PRD_MVP_Originacion_Alter.md v1.0  
**Autor**: CTO Expert AI Assistant

---

## Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Total Sprints** | 4 (+ Sprint 0 Setup) |
| **Duración Total** | 8 semanas + 3 días |
| **Total Épicas** | 12 |
| **Total User Stories** | 24 |
| **Total Tareas Técnicas** | 78 |
| **Horas Estimadas** | ~320 horas |

### 🎯 Estado Actual del Proyecto

| Sprint | Estado | Tareas | Completadas | Tests |
|--------|--------|--------|-------------|-------|
| **Sprint 0** | ✅ COMPLETADO | 9 | 9/9 (100%) | 104 |
| **Sprint 1** | ✅ COMPLETADO | 13 | 13/13 (100%) | 103 |
| **Sprint 2** | ✅ COMPLETADO | 16 | 16/16 (100%) | 84 |
| **Sprint 3** | ✅ COMPLETADO | 8 | 8/8 (100%) | 34 |
| **Sprint 4** | ✅ COMPLETADO | 7 | 7/7 (100%) | 14 |

**📊 Progreso Total:** 53/53 tareas completadas (100%)  
**🧪 Tests Totales:** 339 pasando  
**📅 Última Actualización:** 5 Enero 2026

### Distribución por Sprint

| Sprint | Duración | Épicas | User Stories | Tareas | Horas |
|--------|----------|--------|--------------|--------|-------|
| **0** | 3 días | 2 | 2 | 12 | 24h |
| **1** | 2 semanas | 2 | 6 | 22 | 88h |
| **2** | 2 semanas | 3 | 8 | 24 | 96h |
| **3** | 2 semanas | 2 | 4 | 12 | 56h |
| **4** | 2 semanas | 3 | 4 | 8 | 56h |

---

## Constantes y Referencias Técnicas

### IDs de Tablas Airtable

```python
AIRTABLE_BASE_ID = "appEgNSP0tOLJ9YJ9"

AIRTABLE_TABLES = {
    # Stakeholders
    "companies": "tbl47AWmhYAXerbWz",
    "business_units": "tblbBsypFvEnooHlr",
    "contacts": "tblfErIdCjpMkXK17",
    "financials": "tblYiuZOi2VGRXqgA",
    "company_certificates": "tbl6PZVZasLc0zr9S",
    
    # Origination
    "campaigns": "tbl0B5YGXveYzyADI",
    "campaign_targets": "tblblROgAVEcWQ7WQ",
    "market_context": "tblkE6YhMlxn9XXX5",
    
    # Config
    "config_certificates": "tblQ5HZtmVe2ft9xH",
    "config_activities": "tblcOpprnVmtsMbH4",
    "config_countries": "tblC4FxquuxAbf43R",
    "config_sources": "tbl4MEJa6mh1w3EG4",
    "source_extractions": "tblXX2Uqa0xQCtHSD",
}
```

### Campos FEI Clave

```python
FEI_FIELDS = {
    "status": "fldVZcjpAMdtgZAOb",           # FEI_Status
    "criteria_met": "fld38u15eaiiesceW",      # FEI_Criteria_Met
    "confidence": "fldHza1asHDQKhjqm",        # FEI_Confidence
    "last_check": "fld8uRn0ClqrWCdKD",        # FEI_Last_Check
    "notes": "fld3vUuTM7UYykrbK",             # FEI_Notes
}

FEI_STATUS_OPTIONS = [
    "Unknown", "Pending_Review", "Eligible",
    "Not_Eligible", "Partially_Eligible", "Expired"
]

FEI_CRITERIA_OPTIONS = [
    "1.1_Cleantech_Prize",
    "1.2_Clean_Energy_Patent",
    "1.3_Eco_Label",
    "1.4_Green_Business_90",
    "1.5_Green_Business_Model",
    "1.6_Environmental_Certificate"
]
```

### Campos Business Unit (Cooling-off)

```python
BU_COOLING_FIELDS = {
    "last_outreach_date": "fldLZPFsTnCFpCriq",
    "is_in_cooling_off": "fldD98dTOCUrchFA7",
    "revenue_percentage": "fldDZ1uZ3e6UpTlab",
}
```

### Nomenclatura de Agentes

| Agente | Archivo | Clase | LLM |
|--------|---------|-------|-----|
| Buscador_Empresas | `buscador.py` | `BuscadorEmpresas` | Gemini |
| Enriquecedor_Datos | `enriquecedor.py` | `EnriquecedorDatos` | Gemini |
| Evaluador_FEI | `evaluador_fei.py` | `EvaluadorFEI` | Claude + Gemini |
| Analizador_Contexto | `analizador.py` | `AnalizadorContexto` | Gemini + Claude |
| Selector_Targets | `selector.py` | `SelectorTargets` | Claude |
| Redactor_Mensajes | `redactor.py` | `RedactorMensajes` | Claude |

---

## Sprint 0: Setup (3 días) ✅ COMPLETADO

**Objetivo**: Configurar proyecto Python, conectar APIs, preparar Airtable  
**Capacidad**: 24 horas  
**Prioridad**: 🔴 Bloqueante  
**Estado**: ✅ **COMPLETADO** - 9/9 tareas (100%)

---

### Épica 0.1: Configuración de Proyecto Python

**Objetivo**: Estructura base del proyecto lista para desarrollo  
**Estimación**: 16 horas

#### US-01: Setup Proyecto Python

**Como** desarrollador  
**Quiero** un proyecto Python configurado con estructura estándar  
**Para** comenzar el desarrollo de los agentes

**Criterios de Aceptación:**
- CA-1: El proyecto tiene `pyproject.toml` con todas las dependencias
- CA-2: La estructura de carpetas sigue el estándar definido
- CA-3: Las variables de entorno se cargan correctamente
- CA-4: El proyecto se puede instalar con `pip install -e .`

**Story Points:** 5  
**Prioridad:** Alta

---

#### TASK-001: Crear estructura de proyecto

**Tipo:** Config  
**Descripción:** Crear estructura de carpetas y archivos base del proyecto

**Especificaciones:**
```
alter5-origination/
├── pyproject.toml
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── airtable_schema.py
│   └── prompts/
├── core/
│   ├── __init__.py
│   ├── models.py
│   └── airtable_client.py
├── agents/
│   └── __init__.py
├── integrations/
│   └── __init__.py
├── cli/
│   └── __init__.py
└── tests/
    └── __init__.py
```

**Subtareas:**
- [x] Crear carpetas según estructura ✅
- [x] Crear `__init__.py` en cada módulo ✅
- [x] Crear `.gitignore` para Python ✅
- [x] Crear `README.md` básico ✅

**Estimación:** 2 horas  
**Dependencias:** Ninguna  
**Estado:** ✅ COMPLETADO

---

#### TASK-002: Configurar pyproject.toml

**Tipo:** Config  
**Descripción:** Definir dependencias y metadatos del proyecto

**Especificaciones:**
```toml
[project]
name = "alter5-origination"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pyairtable>=2.0.0",
    "anthropic>=0.18.0",
    "google-generativeai>=0.4.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.26.0",
    "tenacity>=8.0.0",
    "typer>=0.9.0",
    "structlog>=24.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

**Subtareas:**
- [x] Crear pyproject.toml con metadatos ✅
- [x] Definir dependencias de producción ✅
- [x] Definir dependencias de desarrollo ✅
- [x] Configurar entry points para CLI ✅

**Estimación:** 1 hora  
**Dependencias:** TASK-001  
**Estado:** ✅ COMPLETADO

---

#### TASK-003: Configurar settings con Pydantic

**Tipo:** Config  
**Descripción:** Implementar gestión de configuración con pydantic-settings

**Archivo:** `config/settings.py`

**Especificaciones:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Airtable
    AIRTABLE_PAT: str
    AIRTABLE_BASE_ID: str = "appEgNSP0tOLJ9YJ9"
    
    # LLMs
    ANTHROPIC_API_KEY: str
    GOOGLE_API_KEY: str
    
    # Defaults
    DEFAULT_LANGUAGE: str = "es"
    COOLING_OFF_DAYS: int = 90
    MAX_TARGETS_PER_CAMPAIGN: int = 30
    MAX_EMAIL_WORDS: int = 150
    MIN_FIT_SCORE: float = 0.6
    
    class Config:
        env_file = ".env"
```

**Subtareas:**
- [x] Crear clase Settings con pydantic-settings ✅
- [x] Definir todas las variables de entorno ✅
- [x] Crear .env.example con placeholders ✅
- [x] Implementar validación de configuración ✅

**Tests requeridos:**
- [x] Test: Settings carga desde .env ✅
- [x] Test: Valores por defecto funcionan ✅
- [x] Test: Error si falta variable requerida ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-002  
**Estado:** ✅ COMPLETADO

---

#### TASK-004: Crear airtable_schema.py con IDs

**Tipo:** Config  
**Descripción:** Centralizar todos los IDs de Airtable

**Archivo:** `config/airtable_schema.py`

**Especificaciones:**
```python
# Table IDs
TABLES = {
    "companies": "tbl47AWmhYAXerbWz",
    "business_units": "tblbBsypFvEnooHlr",
    "contacts": "tblfErIdCjpMkXK17",
    "financials": "tblYiuZOi2VGRXqgA",
    "company_certificates": "tbl6PZVZasLc0zr9S",
    "campaigns": "tbl0B5YGXveYzyADI",
    "campaign_targets": "tblblROgAVEcWQ7WQ",
    "market_context": "tblkE6YhMlxn9XXX5",
    "config_certificates": "tblQ5HZtmVe2ft9xH",
    "config_activities": "tblcOpprnVmtsMbH4",
    "source_extractions": "tblXX2Uqa0xQCtHSD",
}

# Field IDs for Companies
COMPANY_FIELDS = {
    "name": "fldqByNrteSCYDyLX",
    "home_url": "fld4CmgZl8zG5AsmF",
    "fei_status": "fldVZcjpAMdtgZAOb",
    "fei_criteria_met": "fld38u15eaiiesceW",
    "fei_confidence": "fldHza1asHDQKhjqm",
    "fei_last_check": "fld8uRn0ClqrWCdKD",
    "fei_notes": "fld3vUuTM7UYykrbK",
    # ... más campos
}
```

**Subtareas:**
- [x] Copiar todos los Table IDs del documento de BBDD ✅
- [x] Copiar Field IDs para Companies ✅
- [x] Copiar Field IDs para Business Units ✅
- [x] Copiar Field IDs para Campaign Targets ✅
- [x] Documentar cada constante ✅

**Estimación:** 3 horas  
**Dependencias:** TASK-001  
**Estado:** ✅ COMPLETADO

---

#### TASK-005: Implementar AirtableClient wrapper

**Tipo:** Backend  
**Descripción:** Cliente Airtable con retry y logging

**Archivo:** `core/airtable_client.py`

**Especificaciones:**
```python
from pyairtable import Api
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

class AirtableClient:
    def __init__(self, settings: Settings):
        self.api = Api(settings.AIRTABLE_PAT)
        self.base_id = settings.AIRTABLE_BASE_ID
        self.logger = structlog.get_logger()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_table(self, table_name: str):
        """Obtiene referencia a tabla con retry automático"""
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_record(self, table_name: str, record_id: str):
        """Obtiene un registro por ID"""
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def create_record(self, table_name: str, fields: dict):
        """Crea un registro nuevo"""
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def update_record(self, table_name: str, record_id: str, fields: dict):
        """Actualiza un registro existente"""
        pass
    
    def query_records(self, table_name: str, formula: str = None, 
                      fields: list = None, max_records: int = None):
        """Query con filtros opcionales"""
        pass
```

**Subtareas:**
- [x] Implementar __init__ con Api de pyairtable ✅
- [x] Implementar get_table con retry ✅
- [x] Implementar get_record con retry ✅
- [x] Implementar create_record con retry ✅
- [x] Implementar update_record con retry ✅
- [x] Implementar query_records con formula ✅
- [x] Añadir logging estructurado ✅

**Tests requeridos:**
- [x] Test: Conexión a Airtable exitosa ✅
- [x] Test: Retry funciona en error temporal ✅
- [x] Test: Query con formula filtra correctamente ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-003, TASK-004  
**Estado:** ✅ COMPLETADO

---

#### TASK-006: Crear Pydantic models base

**Tipo:** Backend  
**Descripción:** Modelos de datos para validación

**Archivo:** `core/models.py`

**Especificaciones:**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum

class FEIStatus(str, Enum):
    UNKNOWN = "Unknown"
    PENDING_REVIEW = "Pending_Review"
    ELIGIBLE = "Eligible"
    NOT_ELIGIBLE = "Not_Eligible"
    PARTIALLY_ELIGIBLE = "Partially_Eligible"
    EXPIRED = "Expired"

class FEICriteria(str, Enum):
    CLEANTECH_PRIZE = "1.1_Cleantech_Prize"
    CLEAN_ENERGY_PATENT = "1.2_Clean_Energy_Patent"
    ECO_LABEL = "1.3_Eco_Label"
    GREEN_BUSINESS_90 = "1.4_Green_Business_90"
    GREEN_BUSINESS_MODEL = "1.5_Green_Business_Model"
    ENVIRONMENTAL_CERTIFICATE = "1.6_Environmental_Certificate"

class Company(BaseModel):
    id: str
    name: str
    home_url: Optional[str] = None
    fei_status: FEIStatus = FEIStatus.UNKNOWN
    fei_criteria_met: List[FEICriteria] = []
    fei_confidence: Optional[float] = None
    fei_last_check: Optional[date] = None

class BusinessUnit(BaseModel):
    id: str
    name: str
    company_id: str
    last_outreach_date: Optional[date] = None
    is_in_cooling_off: bool = False
    revenue_percentage: Optional[float] = None

class CampaignTarget(BaseModel):
    id: Optional[str] = None
    campaign_id: str
    business_unit_id: str
    contact_id: Optional[str] = None
    fit_score: float
    selection_justification: str
    personalized_email_subject: Optional[str] = None
    personalized_email_body: Optional[str] = None
    status: str = "Pending_Review"
```

**Subtareas:**
- [x] Crear enums FEIStatus y FEICriteria ✅
- [x] Crear modelo Company ✅
- [x] Crear modelo BusinessUnit ✅
- [x] Crear modelo Contact ✅
- [x] Crear modelo Campaign ✅
- [x] Crear modelo CampaignTarget ✅
- [x] Crear modelo MarketContext ✅

**Tests requeridos:**
- [x] Test: Validación de FEIStatus ✅
- [x] Test: Serialización/deserialización JSON ✅

**Estimación:** 3 horas  
**Dependencias:** TASK-002  
**Estado:** ✅ COMPLETADO

---

### Épica 0.2: Configuración de APIs LLM

**Objetivo**: APIs de Gemini y Claude funcionando  
**Estimación**: 8 horas

#### US-02: Integración con APIs LLM

**Como** desarrollador  
**Quiero** clientes configurados para Gemini y Claude  
**Para** poder usarlos en los agentes

**Criterios de Aceptación:**
- CA-1: Gemini responde a prompts de prueba
- CA-2: Claude responde a prompts de prueba
- CA-3: Los errores de API se manejan correctamente
- CA-4: Hay logging de todas las llamadas

**Story Points:** 3  
**Prioridad:** Alta

---

#### TASK-007: Implementar cliente Gemini

**Tipo:** Integración  
**Descripción:** Cliente para Google Gemini con search grounding

**Archivo:** `integrations/gemini.py`

**Especificaciones:**
```python
import google.generativeai as genai
from tenacity import retry, stop_after_attempt
import structlog

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.logger = structlog.get_logger()
    
    @retry(stop=stop_after_attempt(3))
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Genera respuesta de texto"""
        pass
    
    @retry(stop=stop_after_attempt(3))
    def search_and_generate(self, query: str, system_prompt: str = None) -> str:
        """Usa Google Search Grounding para buscar y generar"""
        pass
```

**Subtareas:**
- [x] Configurar cliente con API key ✅
- [x] Implementar generate con retry ✅
- [x] Implementar search_and_generate con grounding ✅
- [x] Añadir logging de tokens usados ✅
- [x] Manejar errores de rate limit ✅

**Tests requeridos:**
- [x] Test: Respuesta simple funciona ✅
- [x] Test: Search grounding retorna resultados ✅

**Estimación:** 3 horas  
**Dependencias:** TASK-003  
**Estado:** ✅ COMPLETADO

---

#### TASK-008: Implementar cliente Claude

**Tipo:** Integración  
**Descripción:** Cliente para Anthropic Claude

**Archivo:** `integrations/claude.py`

**Especificaciones:**
```python
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt
import structlog

class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.logger = structlog.get_logger()
    
    @retry(stop=stop_after_attempt(3))
    def generate(self, prompt: str, system_prompt: str = None,
                 model: str = "claude-sonnet-4-20250514") -> str:
        """Genera respuesta de texto"""
        pass
    
    @retry(stop=stop_after_attempt(3))
    def generate_structured(self, prompt: str, response_model: type,
                           system_prompt: str = None) -> dict:
        """Genera respuesta estructurada (JSON)"""
        pass
```

**Subtareas:**
- [x] Configurar cliente con API key ✅
- [x] Implementar generate con retry ✅
- [x] Implementar generate_structured para JSON ✅
- [x] Añadir logging de tokens usados ✅
- [x] Manejar errores de rate limit ✅

**Tests requeridos:**
- [x] Test: Respuesta simple funciona ✅
- [x] Test: Respuesta JSON se parsea correctamente ✅

**Estimación:** 3 horas  
**Dependencias:** TASK-003  
**Estado:** ✅ COMPLETADO

---

#### TASK-009: Crear prompts base para agentes

**Tipo:** Config  
**Descripción:** System prompts iniciales para cada agente

**Archivos:** `config/prompts/*.md`

**Subtareas:**
- [x] Crear `config/prompts/buscador.md` ✅
- [x] Crear `config/prompts/enriquecedor.md` ✅
- [x] Crear `config/prompts/evaluador_fei.md` ✅
- [x] Crear `config/prompts/analizador.md` ✅
- [x] Crear `config/prompts/selector.md` ✅
- [x] Crear `config/prompts/redactor.md` ✅
- [x] Función para cargar prompts desde archivos ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-001  
**Estado:** ✅ COMPLETADO

---

## Sprint 1: Cualificación FEI (2 semanas) ✅ COMPLETADO

**Objetivo**: Agentes 2 y 3 funcionando, ≥90% precisión FEI, 200+ empresas evaluadas  
**Capacidad**: 88 horas  
**Prioridad**: 🔴 Máxima  
**Estado**: ✅ **COMPLETADO** - 13/13 tareas (100%)

### Entregables Sprint 1:
- ✅ Agente EnriquecedorDatos (`agents/enriquecedor.py` - 754 líneas)
- ✅ Agente EvaluadorFEI (`agents/evaluador_fei.py` - 1010 líneas)
- ✅ CLI commands: `enrich`, `enrich-batch`, `evaluate-fei`, `fei batch`
- ✅ Dataset de 50 empresas para evaluación (`tests/fixtures/fei_evaluation_dataset.json`)
- ✅ Tests de precisión FEI (precision/recall/F1 ≥90%)

---

### Épica 1.1: Agente Enriquecedor de Datos

**Objetivo**: Completar datos faltantes de empresas  
**Estimación**: 32 horas

#### US-03: Enriquecer datos básicos de empresa

**Como** comercial  
**Quiero** que el sistema complete datos faltantes de empresas  
**Para** tener información completa para cualificación

**Criterios de Aceptación:**
- CA-1: Dado una empresa con solo nombre y web, cuando se enriquece, entonces se completan: empleados, LinkedIn, descripción
- CA-2: Dado una empresa, cuando se buscan financieros, entonces se guardan en tabla Financials
- CA-3: Dado una empresa, cuando se identifican key persons, entonces se crean contactos

**Story Points:** 8  
**Prioridad:** Alta  
**Dependencias:** US-01, US-02

---

#### TASK-010: Implementar clase EnriquecedorDatos

**Tipo:** Agente  
**Descripción:** Agente para completar información de empresas

**Archivo:** `agents/enriquecedor.py`

**Especificaciones:**
- **LLM**: Gemini 1.5 Flash (search grounding)
- **Input**: Company ID o Company object
- **Output**: Company actualizada + Contacts + Financials
- **Tablas**: companies, contacts, financials

**Subtareas:**
- [x] Crear clase EnriquecedorDatos ✅
- [x] Implementar método enrich_company() ✅
- [x] Implementar _search_company_info() ✅
- [x] Implementar _extract_financials() ✅
- [x] Implementar _identify_key_persons() ✅
- [x] Implementar _save_results() ✅

**Tests requeridos:**
- [x] Test: Enriquece empresa con datos básicos ✅
- [x] Test: Crea contactos cuando encuentra key persons ✅
- [x] Test: Guarda financieros en tabla correcta ✅

**Estimación:** 16 horas  
**Dependencias:** TASK-005, TASK-007  
**Estado:** ✅ COMPLETADO

---

#### TASK-011: Implementar búsqueda de datos básicos

**Tipo:** Agente  
**Descripción:** Lógica para buscar y extraer datos de empresa

**Archivo:** `agents/enriquecedor.py`

**Especificaciones:**
```python
async def _search_company_info(self, company: Company) -> dict:
    """
    Busca información de empresa usando Gemini Search.
    
    Returns:
        {
            "num_employees": int,
            "linkedin_url": str,
            "description": str,
            "hq_address": str,
            "sector": str,
        }
    """
```

**Subtareas:**
- [x] Construir prompt de búsqueda ✅
- [x] Parsear respuesta de Gemini ✅
- [x] Validar datos extraídos ✅
- [x] Manejar casos sin resultados ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-010  
**Estado:** ✅ COMPLETADO

---

#### TASK-012: Implementar extracción de financieros

**Tipo:** Agente  
**Descripción:** Buscar y guardar datos financieros

**Archivo:** `agents/enriquecedor.py`

**Campos a extraer:**
- Annual_Revenues
- EBITDA
- Net_Financial_Debt
- Year

**Subtareas:**
- [x] Construir prompt para buscar financieros ✅
- [x] Parsear respuesta estructurada ✅
- [x] Crear registro en Stakeholders_Companies_Financials ✅
- [x] Validar que año es reciente (últimos 3 años) ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-010  
**Estado:** ✅ COMPLETADO

---

#### TASK-013: Implementar identificación de key persons

**Tipo:** Agente  
**Descripción:** Identificar y crear contactos clave

**Archivo:** `agents/enriquecedor.py`

**Roles a buscar:**
- CEO / Director General
- CFO / Director Financiero
- Director de Operaciones

**Subtareas:**
- [x] Construir prompt para buscar directivos ✅
- [x] Parsear respuesta con nombres y roles ✅
- [x] Buscar emails y teléfonos ✅
- [x] Crear registros en Stakeholders_Contacts ✅
- [x] Marcar como Key_Person = "Yes" ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-010  
**Estado:** ✅ COMPLETADO

---

#### US-04: CLI para enriquecimiento batch

**Como** desarrollador  
**Quiero** comando CLI para enriquecer empresas en batch  
**Para** procesar múltiples empresas eficientemente

**Criterios de Aceptación:**
- CA-1: `python -m cli enrich --limit 100` procesa 100 empresas
- CA-2: Se puede filtrar por FEI_Status
- CA-3: Se muestra progreso y resumen al final

**Story Points:** 3  
**Prioridad:** Media  
**Dependencias:** US-03

---

#### TASK-014: Implementar comando CLI enrich

**Tipo:** CLI  
**Descripción:** Comando para enriquecimiento batch

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli enrich --filter "FEI_Status=Unknown" --limit 100 --dry-run
```

**Subtareas:**
- [x] Crear comando `enrich` con Typer ✅
- [x] Implementar filtro por campos ✅
- [x] Implementar límite de registros ✅
- [x] Añadir modo dry-run ✅
- [x] Mostrar barra de progreso ✅
- [x] Generar resumen final ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-010  
**Estado:** ✅ COMPLETADO

---

### Épica 1.2: Agente Evaluador FEI ⭐

**Objetivo**: Evaluar elegibilidad FEI con ≥90% precisión  
**Estimación**: 40 horas

#### US-05: Evaluar elegibilidad FEI de empresa

**Como** comercial  
**Quiero** que el sistema evalúe automáticamente si una empresa es elegible FEI  
**Para** priorizar empresas con mayor margen

**Criterios de Aceptación:**
- CA-1: Dado una empresa con ISO 14001, cuando se evalúa, entonces FEI_Status="Eligible" y FEI_Criteria_Met incluye "1.6_Environmental_Certificate"
- CA-2: Dado una empresa solar con >90% revenue, cuando se evalúa, entonces FEI_Status="Eligible" y FEI_Criteria_Met incluye "1.4_Green_Business_90"
- CA-3: Dado incertidumbre en evaluación, cuando confidence <70%, entonces FEI_Status="Pending_Review"
- CA-4: Precisión medida en 50 empresas de test ≥90%

**Story Points:** 13  
**Prioridad:** 🔴 Máxima  
**Dependencias:** US-03

---

#### TASK-015: Implementar clase EvaluadorFEI

**Tipo:** Agente  
**Descripción:** Agente principal para evaluación FEI

**Archivo:** `agents/evaluador_fei.py`

**Especificaciones:**
- **LLM**: Claude (razonamiento) + Gemini (búsqueda)
- **Input**: Company ID o Company object
- **Output**: FEIEvaluation (status, criteria, confidence, notes)
- **Tablas**: companies, company_certificates, config_certificates, config_activities

**Subtareas:**
- [x] Crear clase EvaluadorFEI ✅
- [x] Implementar método evaluate() ✅
- [x] Implementar _search_certificates() ✅
- [x] Implementar _search_prizes() ✅
- [x] Implementar _check_green_activity() ✅
- [x] Implementar _calculate_confidence() ✅
- [x] Implementar _save_evaluation() ✅

**Tests requeridos:**
- [x] Test: Empresa con ISO 14001 → Eligible ✅
- [x] Test: Empresa renovable 95% → Eligible ✅
- [x] Test: Empresa sin criterios → Not_Eligible ✅
- [x] Test: Caso ambiguo → Pending_Review ✅

**Estimación:** 20 horas  
**Dependencias:** TASK-005, TASK-007, TASK-008  
**Estado:** ✅ COMPLETADO

---

#### TASK-016: Implementar búsqueda de certificaciones

**Tipo:** Agente  
**Descripción:** Buscar certificaciones FEI elegibles

**Archivo:** `agents/evaluador_fei.py`

**Certificaciones a buscar (Criterio 1.6):**
- ISO 14001
- ISO 50001
- ISO 14064
- EMAS

**Eco-labels (Criterio 1.3):**
- B Corp
- EU Ecolabel
- FSC, PEFC
- LEED, BREEAM

**Subtareas:**
- [x] Cargar lista de certificaciones de Config_Certificates ✅
- [x] Construir prompt de búsqueda ✅
- [x] Buscar en web de empresa y fuentes oficiales ✅
- [x] Verificar validez (fecha expiración) ✅
- [x] Crear registros en Company_Certificates ✅

**Estimación:** 6 horas  
**Dependencias:** TASK-015  
**Estado:** ✅ COMPLETADO

---

#### TASK-017: Implementar búsqueda de premios cleantech

**Tipo:** Agente  
**Descripción:** Buscar premios que califican para FEI

**Archivo:** `agents/evaluador_fei.py`

**Premios elegibles (Criterio 1.1):**
- CDTI Neotec
- Horizon Europe Grant
- EIT Climate-KIC
- EIT InnoEnergy
- LIFE Programme

**Subtareas:**
- [x] Construir prompt de búsqueda de premios ✅
- [x] Verificar que es de últimos 3 años ✅
- [x] Validar entidad emisora ✅
- [x] Registrar en Company_Certificates con type="Prize" ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-015  
**Estado:** ✅ COMPLETADO

---

#### TASK-018: Implementar verificación de actividad green

**Tipo:** Agente  
**Descripción:** Verificar criterio 1.4 (≥90% revenue green)

**Archivo:** `agents/evaluador_fei.py`

**Actividades elegibles:**
- Generación Solar/Eólica/Hidro
- Gestión de Residuos/Reciclaje
- Transporte Ferroviario
- Eficiencia Energética

**Subtareas:**
- [x] Cargar actividades elegibles de Config_Activities ✅
- [x] Obtener Revenue_Percentage de Business Units ✅
- [x] Verificar si actividad principal es green ✅
- [x] Calcular porcentaje total de revenue green ✅
- [x] Marcar criterio 1.4 si ≥90% ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-015  
**Estado:** ✅ COMPLETADO

---

#### TASK-019: Implementar lógica de evaluación con razonamiento

**Tipo:** Agente  
**Descripción:** Usar Claude para razonamiento estructurado

**Archivo:** `agents/evaluador_fei.py`

**Especificaciones:**
```python
def _evaluate_with_reasoning(self, company: Company, 
                             evidence: dict) -> FEIEvaluation:
    """
    Usa Claude para evaluar evidencia y determinar elegibilidad.
    
    Prompt incluye:
    - Criterios FEI oficiales
    - Evidencia encontrada
    - Instrucción de razonamiento explícito
    
    Output estructurado:
    - status: FEIStatus
    - criteria_met: List[FEICriteria]
    - confidence: float (0-100)
    - reasoning: str
    """
```

**Subtareas:**
- [x] Construir prompt con criterios FEI ✅
- [x] Incluir toda la evidencia encontrada ✅
- [x] Pedir razonamiento paso a paso ✅
- [x] Parsear respuesta estructurada ✅
- [x] Validar coherencia de respuesta ✅

**Estimación:** 6 horas  
**Dependencias:** TASK-016, TASK-017, TASK-018  
**Estado:** ✅ COMPLETADO

---

#### US-06: CLI para evaluación FEI batch

**Como** desarrollador  
**Quiero** comando CLI para evaluar FEI en batch  
**Para** procesar múltiples empresas eficientemente

**Criterios de Aceptación:**
- CA-1: `python -m cli evaluate-fei --limit 200` procesa 200 empresas
- CA-2: Se puede filtrar por FEI_Status=Unknown
- CA-3: Se genera reporte con métricas

**Story Points:** 3  
**Prioridad:** Alta  
**Dependencias:** US-05

---

#### TASK-020: Implementar comando CLI evaluate-fei

**Tipo:** CLI  
**Descripción:** Comando para evaluación FEI batch

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli evaluate-fei --filter "FEI_Status=Unknown" --limit 200 --report
```

**Subtareas:**
- [x] Crear comando `evaluate-fei` con Typer ✅
- [x] Implementar filtro por FEI_Status ✅
- [x] Implementar procesamiento batch ✅
- [x] Generar reporte de métricas ✅
- [x] Mostrar distribución de resultados ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-015  
**Estado:** ✅ COMPLETADO

---

#### US-07: Tests y Evals para Evaluador FEI

**Como** desarrollador  
**Quiero** suite de tests para validar precisión del evaluador  
**Para** garantizar ≥90% de precisión

**Criterios de Aceptación:**
- CA-1: Dataset de 50 empresas verificadas manualmente
- CA-2: Tests automáticos ejecutan evaluación
- CA-3: Reporte de precisión, recall, F1

**Story Points:** 5  
**Prioridad:** Alta  
**Dependencias:** US-05

---

#### TASK-021: Crear dataset de evaluación

**Tipo:** Testing  
**Descripción:** 50 empresas verificadas manualmente

**Archivo:** `tests/fixtures/fei_evaluation_dataset.json`

**Especificaciones:**
```json
{
  "companies": [
    {
      "id": "rec...",
      "name": "SolarTech España",
      "expected_status": "Eligible",
      "expected_criteria": ["1.4_Green_Business_90", "1.6_Environmental_Certificate"],
      "evidence": "ISO 14001 verificado, 100% renovables"
    },
    // ... 49 más
  ]
}
```

**Subtareas:**
- [x] Seleccionar 50 empresas representativas ✅
- [x] 25 elegibles con criterios documentados ✅
- [x] 25 no elegibles ✅
- [x] Verificar manualmente cada una ✅
- [x] Documentar evidencia ✅

**Estimación:** 8 horas  
**Dependencias:** TASK-015  
**Estado:** ✅ COMPLETADO

---

#### TASK-022: Implementar tests de evaluación FEI

**Tipo:** Testing  
**Descripción:** Tests automáticos para medir precisión

**Archivo:** `tests/test_evaluador_fei.py`

**Subtareas:**
- [x] Test parametrizado con dataset ✅
- [x] Calcular precision, recall, F1 ✅
- [x] Generar reporte de errores ✅
- [x] Threshold de ≥90% para pasar ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-021  
**Estado:** ✅ COMPLETADO

---

## Sprint 2: Campañas (2 semanas) ✅ COMPLETADO

**Objetivo**: Agentes 4, 5, 6 funcionando + Primera campaña real  
**Capacidad**: 96 horas  
**Prioridad**: 🔴 Alta  
**Estado**: ✅ **COMPLETADO** - 16/16 tareas (100%)

---

### Épica 2.1: Agente Analizador de Contexto

**Objetivo**: Analizar triggers de mercado  
**Estimación**: 24 horas

#### US-08: Analizar trigger de mercado

**Como** comercial  
**Quiero** que el sistema analice un trigger de mercado  
**Para** generar contexto estructurado para campañas

**Criterios de Aceptación:**
- CA-1: Dado trigger "BCE baja tipos", cuando se analiza, entonces genera Market_Context con affected_sectors, affected_countries
- CA-2: Dado análisis, cuando se completa, entonces incluye key_angles para personalización
- CA-3: Dado trigger, cuando Campaign_Potential ≥4, entonces se recomienda crear campaña

**Story Points:** 8  
**Prioridad:** Alta  
**Dependencias:** US-02

---

#### TASK-023: Implementar clase AnalizadorContexto

**Tipo:** Agente  
**Descripción:** Agente para análisis de triggers de mercado

**Archivo:** `agents/analizador.py`

**Especificaciones:**
- **LLM**: Gemini (búsqueda noticias) + Claude (análisis)
- **Input**: Trigger text (ej: "BCE baja tipos 0.25%")
- **Output**: MarketContext object
- **Tablas**: market_context

**Subtareas:**
- [x] Crear clase AnalizadorContexto ✅
- [x] Implementar método analyze() ✅
- [x] Implementar _search_news() ✅
- [x] Implementar _analyze_impact() ✅
- [x] Implementar _generate_angles() ✅
- [x] Implementar _save_context() ✅

**Tests requeridos:**
- [x] Test: Genera contexto válido desde trigger ✅
- [x] Test: Identifica sectores afectados ✅
- [x] Test: Genera key_angles relevantes ✅

**Estimación:** 12 horas  
**Dependencias:** TASK-007, TASK-008  
**Estado:** ✅ COMPLETADO

---

#### TASK-024: Implementar búsqueda de noticias

**Tipo:** Agente  
**Descripción:** Buscar noticias relacionadas con trigger

**Archivo:** `agents/analizador.py`

**Subtareas:**
- [x] Usar Gemini Search para buscar noticias ✅
- [x] Filtrar por fecha reciente (últimas 2 semanas) ✅
- [x] Extraer fuentes confiables (Reuters, FT, etc.) ✅
- [x] Resumir hallazgos principales ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-023  
**Estado:** ✅ COMPLETADO

---

#### TASK-025: Implementar análisis de impacto

**Tipo:** Agente  
**Descripción:** Analizar impacto del trigger en sectores/países

**Archivo:** `agents/analizador.py`

**Output esperado:**
```python
{
    "affected_sectors": ["Industrials", "Real Estate", "Utilities"],
    "affected_countries": ["ES", "PT"],
    "urgency": "alta",
    "recommended_product": "FEI_Guarantee",
    "campaign_potential": 5
}
```

**Subtareas:**
- [x] Usar Claude para análisis estructurado ✅
- [x] Mapear a sectores de Config_Sector_And_Activities ✅
- [x] Mapear a países de Config_Countries ✅
- [x] Determinar urgencia y producto recomendado ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-024  
**Estado:** ✅ COMPLETADO

---

#### TASK-026: Implementar generación de key angles

**Tipo:** Agente  
**Descripción:** Generar ángulos para personalización

**Archivo:** `agents/analizador.py`

**Output esperado:**
```python
{
    "key_angles": [
        "Oportunidad de refinanciar deuda variable",
        "Reducción coste financiero",
        "Momento ideal para nuevos proyectos"
    ]
}
```

**Subtareas:**
- [x] Generar 3-5 ángulos de comunicación ✅
- [x] Cada ángulo conecta trigger con beneficio ✅
- [x] Considerar FEI como valor añadido ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-025  
**Estado:** ✅ COMPLETADO

---

### Épica 2.2: Agente Selector de Targets

**Objetivo**: Seleccionar mejores Business Units para campaña  
**Estimación**: 32 horas

#### US-09: Seleccionar targets para campaña

**Como** comercial  
**Quiero** que el sistema seleccione los mejores targets  
**Para** maximizar probabilidad de conversión

**Criterios de Aceptación:**
- CA-1: Dado contexto de campaña, cuando se seleccionan targets, entonces se filtran por sector/país matching
- CA-2: Dado BU contactada hace <90 días, cuando se evalúa, entonces se excluye
- CA-3: Dado selección, cuando se completa, entonces NO excede 30 targets
- CA-4: Cada target incluye Fit_Score y Selection_Justification

**Story Points:** 8  
**Prioridad:** Alta  
**Dependencias:** US-08

---

#### TASK-027: Implementar clase SelectorTargets

**Tipo:** Agente  
**Descripción:** Agente para selección y priorización de targets

**Archivo:** `agents/selector.py`

**Especificaciones:**
- **LLM**: Claude (razonamiento)
- **Input**: Campaign context + filter criteria
- **Output**: List[CampaignTarget] priorizada
- **Tablas**: business_units, companies, campaign_targets

**Subtareas:**
- [x] Crear clase SelectorTargets ✅
- [x] Implementar método select() ✅
- [x] Implementar _filter_by_criteria() ✅
- [x] Implementar _apply_cooling_off() ✅
- [x] Implementar _calculate_fit_score() ✅
- [x] Implementar _prioritize() ✅
- [x] Implementar _generate_justifications() ✅

**Tests requeridos:**
- [x] Test: Excluye BUs en cooling-off ✅
- [x] Test: Respeta max 30 targets ✅
- [x] Test: FEI elegibles tienen mayor score ✅

**Estimación:** 16 horas  
**Dependencias:** TASK-005, TASK-008  
**Estado:** ✅ COMPLETADO

---

#### TASK-028: Implementar filtrado por criterios

**Tipo:** Agente  
**Descripción:** Filtrar BUs por sector, país, activo

**Archivo:** `agents/selector.py`

**Filtros:**
- Sector en affected_sectors
- País en affected_countries
- Record_Status = "Active"
- NO en campaña activa

**Subtareas:**
- [x] Construir formula Airtable ✅
- [x] Aplicar filtros combinados ✅
- [x] Verificar BU no en otra campaña ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-027  
**Estado:** ✅ COMPLETADO

---

#### TASK-029: Implementar cooling-off check

**Tipo:** Agente  
**Descripción:** Verificar período de 90 días sin contacto

**Archivo:** `agents/selector.py`

**Lógica:**
```python
def _apply_cooling_off(self, bus: List[BusinessUnit]) -> List[BusinessUnit]:
    """
    Excluye BUs contactadas en últimos 90 días.
    
    Usa campo Last_Outreach_Date de Business_Units.
    """
    today = date.today()
    return [
        bu for bu in bus
        if bu.last_outreach_date is None 
        or (today - bu.last_outreach_date).days >= 90
    ]
```

**Subtareas:**
- [x] Obtener Last_Outreach_Date de cada BU ✅
- [x] Calcular días desde último contacto ✅
- [x] Filtrar BUs con <90 días ✅
- [x] Loggear exclusiones para auditoría ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-027  
**Estado:** ✅ COMPLETADO

---

#### TASK-030: Implementar cálculo de fit score

**Tipo:** Agente  
**Descripción:** Calcular score de 0-100% por target

**Archivo:** `agents/selector.py`

**Factores de scoring:**
| Factor | Peso |
|--------|------|
| FEI Eligible | +20% |
| Key Person identificado | +15% |
| Sector matching | +15% |
| País matching | +10% |
| Datos financieros completos | +10% |
| Engagement previo positivo | +10% |
| Base | 50% |

**Subtareas:**
- [x] Implementar cada factor de scoring ✅
- [x] Calcular score total (max 100%) ✅
- [x] Filtrar targets con score < 60% ✅
- [x] Ordenar por score descendente ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-028, TASK-029  
**Estado:** ✅ COMPLETADO

---

#### TASK-031: Implementar generación de justificaciones

**Tipo:** Agente  
**Descripción:** Usar Claude para justificar cada selección

**Archivo:** `agents/selector.py`

**Output esperado:**
```python
{
    "selection_justification": "Target prioritario: empresa FEI elegible (ISO 14001), 
     sector renovable alineado con trigger, CFO identificado como contacto."
}
```

**Subtareas:**
- [x] Construir prompt con datos del target ✅
- [x] Generar justificación en español ✅
- [x] Máximo 2 frases por target ✅
- [x] Incluir razones principales de scoring ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-030  
**Estado:** ✅ COMPLETADO

---

### Épica 2.3: Agente Redactor de Mensajes ⭐

**Objetivo**: Generar emails hiper-personalizados  
**Estimación**: 40 horas

#### US-10: Redactar emails personalizados

**Como** comercial  
**Quiero** emails personalizados para cada target  
**Para** maximizar tasa de respuesta

**Criterios de Aceptación:**
- CA-1: Dado target, cuando se redacta, entonces subject menciona empresa
- CA-2: Dado email, cuando se mide, entonces body ≤150 palabras
- CA-3: Dado email, cuando se revisa, entonces menciona algo ESPECÍFICO de la empresa
- CA-4: Dado target FEI elegible, cuando se redacta, entonces menciona garantía europea
- CA-5: Dado cualquier email, entonces incluye CTA de reunión 15 min

**Story Points:** 13  
**Prioridad:** 🔴 Máxima  
**Dependencias:** US-09

---

#### TASK-032: Implementar clase RedactorMensajes

**Tipo:** Agente  
**Descripción:** Agente para redacción de emails personalizados

**Archivo:** `agents/redactor.py`

**Especificaciones:**
- **LLM**: Claude (mejor escritura en español)
- **Input**: CampaignTarget + MarketContext + Company info
- **Output**: Subject + Body personalizados
- **Tablas**: campaign_targets

**Subtareas:**
- [x] Crear clase RedactorMensajes ✅
- [x] Implementar método write_email() ✅
- [x] Implementar _gather_personalization_context() ✅
- [x] Implementar _generate_subject() ✅
- [x] Implementar _generate_body() ✅
- [x] Implementar _validate_email() ✅
- [x] Implementar _save_email() ✅

**Tests requeridos:**
- [x] Test: Subject menciona empresa ✅
- [x] Test: Body ≤150 palabras ✅
- [x] Test: FEI elegible menciona garantía ✅
- [x] Test: Incluye CTA ✅

**Estimación:** 16 horas  
**Dependencias:** TASK-008  
**Estado:** ✅ COMPLETADO

---

#### TASK-033: Implementar recolección de contexto

**Tipo:** Agente  
**Descripción:** Obtener info para personalización

**Archivo:** `agents/redactor.py`

**Contexto a recolectar:**
- Nombre empresa y contacto
- FEI status y criterios
- Noticias recientes de la empresa
- Proyectos completados
- Certificaciones

**Subtareas:**
- [x] Obtener datos de Company y Contact ✅
- [x] Buscar noticias recientes de la empresa ✅
- [x] Obtener certificaciones relevantes ✅
- [x] Estructurar contexto para prompt ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-032  
**Estado:** ✅ COMPLETADO

---

#### TASK-034: Implementar generación de subject

**Tipo:** Agente  
**Descripción:** Generar asunto personalizado

**Archivo:** `agents/redactor.py`

**Formato:**
```
[Algo específico de empresa] + [Oportunidad relacionada con trigger]
Ejemplo: "Refinanciación para SolarTech tras bajada tipos BCE"
```

**Subtareas:**
- [x] Construir prompt para subject ✅
- [x] Incluir nombre de empresa obligatorio ✅
- [x] Conectar con trigger/oportunidad ✅
- [x] Validar longitud (≤60 caracteres ideal) ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-033  
**Estado:** ✅ COMPLETADO

---

#### TASK-035: Implementar generación de body

**Tipo:** Agente  
**Descripción:** Generar cuerpo del email personalizado

**Archivo:** `agents/redactor.py`

**Estructura:**
```
Párrafo 1 (1-2 frases): Algo específico de la empresa
Párrafo 2 (2-3 frases): Conecta trigger con propuesta de valor
Párrafo 3 (1 frase): CTA reunión 15 min
Cierre: Saludos + firma
```

**Subtareas:**
- [x] Construir prompt con estructura ✅
- [x] Incluir instrucción de personalización real ✅
- [x] Adaptar mensaje según FEI status ✅
- [x] Validar ≤150 palabras ✅
- [x] Validar tono español formal/cercano ✅

**Estimación:** 6 horas  
**Dependencias:** TASK-034  
**Estado:** ✅ COMPLETADO

---

#### TASK-036: Implementar validación de email

**Tipo:** Agente  
**Descripción:** Verificar que email cumple reglas

**Archivo:** `agents/redactor.py`

**Validaciones:**
- [x] Body ≤150 palabras ✅
- [x] Menciona nombre empresa ✅
- [x] Tiene CTA de reunión ✅
- [x] Si FEI elegible, menciona garantía ✅
- [x] No parece generado por IA (opcional, manual) ✅

**Subtareas:**
- [x] Implementar conteo de palabras ✅
- [x] Verificar presencia de empresa en text ✅
- [x] Verificar CTA pattern ✅
- [x] Regenerar si no cumple ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-035  
**Estado:** ✅ COMPLETADO

---

#### US-11: Flujo completo de creación de campaña

**Como** comercial  
**Quiero** crear campaña completa desde trigger  
**Para** tener emails listos para enviar

**Criterios de Aceptación:**
- CA-1: Dado trigger, cuando ejecuto flujo, entonces genera Market_Context + Campaign + Targets + Emails
- CA-2: Dado flujo, cuando propone targets, entonces espera aprobación humana
- CA-3: Dado aprobación, cuando genera emails, entonces quedan en Campaign_Targets

**Story Points:** 8  
**Prioridad:** Alta  
**Dependencias:** US-10

---

#### TASK-037: Implementar orquestador de campaña

**Tipo:** Backend  
**Descripción:** Coordinar flujo de agentes 4→5→6

**Archivo:** `core/campaign_orchestrator.py`

**Especificaciones:**
```python
class CampaignOrchestrator:
    def create_campaign_from_trigger(self, trigger: str, 
                                     criteria: dict) -> Campaign:
        """
        Flujo completo:
        1. Analizador: trigger → Market_Context
        2. Selector: context → List[CampaignTarget] (propuesta)
        3. [HUMANO APRUEBA]
        4. Redactor: targets → emails personalizados
        """
```

**Subtareas:**
- [x] Crear clase CampaignOrchestrator ✅
- [x] Implementar flujo secuencial ✅
- [x] Punto de pausa para aprobación humana ✅
- [x] Crear registros en Origination_Campaigns ✅
- [x] Actualizar status de campaña ✅

**Estimación:** 8 horas  
**Dependencias:** TASK-023, TASK-027, TASK-032  
**Estado:** ✅ COMPLETADO

---

#### TASK-038: Implementar comando CLI create-campaign

**Tipo:** CLI  
**Descripción:** Comando para crear campaña interactiva

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli create-campaign \
    --trigger "BCE baja tipos 0.25%" \
    --sectors "Industrials,Utilities" \
    --countries "ES,PT" \
    --max-targets 20
```

**Subtareas:**
- [x] Crear comando `create-campaign` ✅
- [x] Parámetros de filtro opcionales ✅
- [x] Mostrar propuesta de targets ✅
- [x] Pedir confirmación antes de generar emails ✅
- [x] Generar resumen final ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-037  
**Estado:** ✅ COMPLETADO

---

## Sprint 3: Originación (2 semanas) ✅ COMPLETADO

**Objetivo**: Agente 1 + Pipeline completo + 100 empresas nuevas  
**Capacidad**: 56 horas  
**Prioridad**: 🟡 Media  
**Estado**: ✅ **COMPLETADO** - 8/8 tareas (100%)

---

### Épica 3.1: Agente Buscador de Empresas

**Objetivo**: Encontrar empresas nuevas según criterios  
**Estimación**: 32 horas

#### US-12: Buscar empresas nuevas

**Como** comercial  
**Quiero** encontrar empresas nuevas según criterios  
**Para** ampliar el pipeline de originación

**Criterios de Aceptación:**
- CA-1: Dado criterio "renovables en Andalucía", cuando busco, entonces encuentro empresas reales
- CA-2: Dado empresa encontrada, cuando se procesa, entonces se verifica URL real
- CA-3: Dado empresa nueva, cuando se inserta, entonces se deduplica contra BBDD
- CA-4: Dado empresa creada, entonces tiene BU "Default" asociada

**Story Points:** 8  
**Prioridad:** Media  
**Dependencias:** US-02

---

#### TASK-039: Implementar clase BuscadorEmpresas

**Tipo:** Agente  
**Descripción:** Agente para búsqueda de empresas nuevas

**Archivo:** `agents/buscador.py`

**Especificaciones:**
- **LLM**: Gemini 1.5 Flash con Search Grounding
- **Input**: Criterios (sector, país, tamaño, keywords)
- **Output**: List[Company] creadas en Airtable
- **Tablas**: companies, business_units

**Subtareas:**
- [x] Crear clase BuscadorEmpresas ✅
- [x] Implementar método search() ✅
- [x] Implementar _build_search_query() ✅
- [x] Implementar _extract_companies() ✅
- [x] Implementar _verify_urls() ✅
- [x] Implementar _deduplicate() ✅
- [x] Implementar _create_records() ✅

**Tests requeridos:**
- [x] Test: Encuentra empresas por sector ✅
- [x] Test: Deduplica correctamente ✅
- [x] Test: Crea BU Default ✅

**Estimación:** 16 horas  
**Dependencias:** TASK-007  
**Estado:** ✅ COMPLETADO

---

#### TASK-040: Implementar búsqueda con Gemini Search

**Tipo:** Agente  
**Descripción:** Usar Google Search para encontrar empresas

**Archivo:** `agents/buscador.py`

**Prompts de búsqueda:**
```
"empresas de energía solar fotovoltaica en Andalucía España con más de 50 empleados"
"listado de empresas renovables en {región} {país}"
```

**Subtareas:**
- [x] Construir query de búsqueda dinámica ✅
- [x] Parsear resultados de búsqueda ✅
- [x] Extraer: nombre, web, descripción breve ✅
- [x] Filtrar resultados irrelevantes ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-039  
**Estado:** ✅ COMPLETADO

---

#### TASK-041: Implementar verificación de URLs

**Tipo:** Agente  
**Descripción:** Verificar que URLs de empresas son reales

**Archivo:** `agents/buscador.py`

**Subtareas:**
- [x] Hacer HEAD request a cada URL ✅
- [x] Verificar status code 200 ✅
- [x] Timeout de 5 segundos ✅
- [x] Marcar URLs inválidas ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-040  
**Estado:** ✅ COMPLETADO

---

#### TASK-042: Implementar deduplicación

**Tipo:** Agente  
**Descripción:** Evitar duplicados en BBDD

**Archivo:** `agents/buscador.py`

**Criterios de duplicado:**
- Mismo nombre exacto (case insensitive)
- Mismo dominio web
- Similaridad de nombre >90%

**Subtareas:**
- [x] Query empresas existentes con nombre similar ✅
- [x] Extraer dominio de URL ✅
- [x] Calcular similaridad de strings ✅
- [x] Rechazar si hay match ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-041  
**Estado:** ✅ COMPLETADO

---

#### TASK-043: Implementar creación de registros

**Tipo:** Agente  
**Descripción:** Crear Company + BU Default

**Archivo:** `agents/buscador.py`

**Subtareas:**
- [x] Crear registro en Stakeholders_Companies ✅
- [x] Marcar Source = "AI_Scraping" ✅
- [x] Crear Business Unit "Default" ✅
- [x] Vincular BU a Company ✅

**Estimación:** 2 horas  
**Dependencias:** TASK-042  
**Estado:** ✅ COMPLETADO

---

#### US-13: CLI para búsqueda de empresas

**Como** desarrollador  
**Quiero** comando CLI para buscar empresas  
**Para** originar en batch

**Criterios de Aceptación:**
- CA-1: `python -m cli search --sector renovables --country ES` funciona
- CA-2: Muestra empresas encontradas antes de crear
- CA-3: Pide confirmación antes de insertar

**Story Points:** 3  
**Prioridad:** Media  
**Dependencias:** US-12

---

#### TASK-044: Implementar comando CLI search

**Tipo:** CLI  
**Descripción:** Comando para búsqueda de empresas

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli search \
    --sector "renovables" \
    --country "ES" \
    --region "Andalucía" \
    --min-employees 50 \
    --limit 25
```

**Subtareas:**
- [x] Crear comando `search` ✅
- [x] Parámetros de filtro ✅
- [x] Preview de resultados ✅
- [x] Confirmación interactiva ✅
- [x] Resumen de creación ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-039  
**Estado:** ✅ COMPLETADO

---

### Épica 3.2: Pipeline Completo

**Objetivo**: Flujo end-to-end funcionando  
**Estimación**: 24 horas

#### US-14: Pipeline de originación completo

**Como** comercial  
**Quiero** ejecutar pipeline completo de originación  
**Para** desde búsqueda hasta campaña lista

**Criterios de Aceptación:**
- CA-1: Dado criterios de búsqueda, cuando ejecuto pipeline, entonces: busca→enriquece→evalúa FEI→está listo para campaña
- CA-2: Dado pipeline, cuando termina, entonces todas las empresas tienen FEI evaluado

**Story Points:** 8  
**Prioridad:** Media  
**Dependencias:** US-12, US-05

---

#### TASK-045: Implementar pipeline de originación

**Tipo:** Backend  
**Descripción:** Orquestar flujo completo 1→2→3

**Archivo:** `core/origination_pipeline.py`

**Especificaciones:**
```python
class OriginationPipeline:
    def originate(self, criteria: SearchCriteria) -> List[Company]:
        """
        Pipeline completo:
        1. Buscador: criterios → empresas nuevas
        2. Enriquecedor: empresas → datos completos
        3. Evaluador FEI: empresas → FEI_Status
        """
```

**Subtareas:**
- [x] Crear clase OriginationPipeline ✅
- [x] Orquestar agentes 1→2→3 ✅
- [x] Manejar errores parciales ✅
- [x] Generar reporte final ✅

**Estimación:** 8 horas  
**Dependencias:** TASK-039, TASK-010, TASK-015  
**Estado:** ✅ COMPLETADO

---

#### TASK-046: Implementar comando CLI originate

**Tipo:** CLI  
**Descripción:** Comando para pipeline completo

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli originate \
    --sector "renovables" \
    --country "ES" \
    --limit 25 \
    --enrich \
    --evaluate-fei
```

**Subtareas:**
- [x] Crear comando `originate` ✅
- [x] Flags para cada fase ✅
- [x] Progress bar ✅
- [x] Reporte final con métricas ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-045  
**Estado:** ✅ COMPLETADO

---

## Sprint 4: Integración (2 semanas) ✅ COMPLETADO

**Objetivo**: Mailchimp + Métricas + Documentación + Demo CEOs  
**Capacidad**: 56 horas  
**Prioridad**: 🟡 Media  
**Estado**: ✅ **COMPLETADO** - 7/7 tareas (100%)

---

### Épica 4.1: Integración Mailchimp

**Objetivo**: Envío de campañas via Mailchimp  
**Estimación**: 24 horas

#### US-15: Enviar campaña via Mailchimp

**Como** comercial  
**Quiero** enviar campaña aprobada via Mailchimp  
**Para** trackear opens, clicks, replies

**Criterios de Aceptación:**
- CA-1: Dado campaña aprobada, cuando envío, entonces se crea campaña en Mailchimp
- CA-2: Dado envío, cuando se completa, entonces status=Sent y Sent_Date actualizado
- CA-3: Dado envío, cuando recipient abre, entonces se registra interacción

**Story Points:** 8  
**Prioridad:** Media  
**Dependencias:** US-11

---

#### TASK-047: Implementar cliente Mailchimp

**Tipo:** Integración  
**Descripción:** Cliente para API de Mailchimp

**Archivo:** `integrations/mailchimp.py`

**Subtareas:**
- [x] Configurar cliente con API key ✅
- [x] Implementar create_campaign() ✅
- [x] Implementar add_recipients() ✅
- [x] Implementar send_campaign() ✅
- [x] Implementar get_campaign_stats() ✅

**Estimación:** 8 horas  
**Dependencias:** TASK-003  
**Estado:** ✅ COMPLETADO

---

#### TASK-048: Implementar sincronización de métricas

**Tipo:** Integración  
**Descripción:** Actualizar Campaign_Targets con métricas

**Archivo:** `integrations/mailchimp.py`

**Subtareas:**
- [x] Polling de stats de Mailchimp ✅
- [x] Actualizar status: Sent→Delivered→Opened→Clicked ✅
- [x] Actualizar Last_Interaction_Date ✅
- [x] Detectar bounces y unsubscribes ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-047  
**Estado:** ✅ COMPLETADO

---

### Épica 4.2: Métricas y Dashboards

**Objetivo**: KPIs visibles para equipo  
**Estimación**: 16 horas

#### US-16: Dashboard de KPIs

**Como** CEO  
**Quiero** ver KPIs del sistema de originación  
**Para** evaluar ROI y decidir escalar

**Criterios de Aceptación:**
- CA-1: Vista en Airtable muestra empresas por FEI_Status
- CA-2: Vista muestra campañas activas con tasas
- CA-3: Métricas actualizadas automáticamente

**Story Points:** 5  
**Prioridad:** Media  
**Dependencias:** US-15

---

#### TASK-049: Crear vistas Airtable

**Tipo:** Config  
**Descripción:** Configurar vistas para dashboards

**Subtareas:**
- [x] Vista "Pipeline FEI" en Companies ✅ (documentado en guía)
- [x] Vista "Campañas Activas" en Campaigns ✅ (documentado en guía)
- [x] Vista "Targets Pendientes" en Campaign_Targets ✅ (documentado en guía)
- [x] Campos calculados para métricas ✅ (CLI status)

**Estimación:** 4 horas  
**Dependencias:** Ninguna  
**Estado:** ✅ COMPLETADO

---

#### TASK-050: Implementar comando CLI status

**Tipo:** CLI  
**Descripción:** Mostrar métricas del sistema

**Archivo:** `cli/main.py`

**Especificaciones:**
```bash
python -m cli status
python -m cli status --campaign-id rec123
```

**Subtareas:**
- [x] Resumen de empresas por FEI_Status ✅
- [x] Campañas activas y sus métricas ✅
- [x] Últimas evaluaciones FEI ✅
- [x] Formato tabla/JSON ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-005  
**Estado:** ✅ COMPLETADO

---

### Épica 4.3: Documentación y Demo

**Objetivo**: Sistema documentado y listo para demo  
**Estimación**: 16 horas

#### US-17: Documentación completa

**Como** desarrollador  
**Quiero** documentación del sistema  
**Para** que otros puedan mantenerlo

**Criterios de Aceptación:**
- CA-1: README con instrucciones de setup
- CA-2: Guía de uso para comerciales
- CA-3: Documentación de cada agente

**Story Points:** 5  
**Prioridad:** Media  
**Dependencias:** Todos los sprints anteriores

---

#### TASK-051: Crear README técnico

**Tipo:** Documentación  
**Descripción:** Documentación de setup y desarrollo

**Archivo:** `README.md`

**Subtareas:**
- [x] Requisitos del sistema ✅
- [x] Instrucciones de instalación ✅
- [x] Configuración de variables de entorno ✅
- [x] Comandos CLI disponibles ✅
- [x] Estructura del proyecto ✅

**Estimación:** 4 horas  
**Dependencias:** Ninguna  
**Estado:** ✅ COMPLETADO

---

#### TASK-052: Crear guía de usuario

**Tipo:** Documentación  
**Descripción:** Guía para equipo comercial

**Archivo:** `docs/guia_usuario.md`

**Subtareas:**
- [x] Cómo crear campañas ✅
- [x] Cómo revisar targets ✅
- [x] Cómo aprobar envíos ✅
- [x] FAQ ✅

**Estimación:** 4 horas  
**Dependencias:** Ninguna  
**Estado:** ✅ COMPLETADO

---

#### TASK-053: Preparar demo para CEOs

**Tipo:** Documentación  
**Descripción:** Materiales para presentación final

**Subtareas:**
- [x] Script de demo (5-10 min) ✅
- [x] Datos de ejemplo preparados ✅
- [x] Métricas a mostrar ✅
- [x] Próximos pasos propuestos ✅

**Estimación:** 4 horas  
**Dependencias:** TASK-049, TASK-050  
**Estado:** ✅ COMPLETADO

---

## Apéndice A: Definition of Done Global

Todas las tareas deben cumplir:

- [ ] Código implementado y funcionando
- [ ] Type hints completos (mypy sin errores)
- [ ] Docstrings en funciones públicas
- [ ] Unit tests con >80% coverage
- [ ] Integration tests para flujos críticos
- [ ] Logging con structlog
- [ ] Sin hardcoded secrets
- [ ] Sin datos sensibles en logs
- [ ] Code review completado
- [ ] Documentación actualizada si aplica

---

## Apéndice B: Dependencias entre Tareas

```
Sprint 0:
TASK-001 ─┬─→ TASK-002 → TASK-003 ─┬─→ TASK-005
          │                        └─→ TASK-006
          │                        └─→ TASK-007
          │                        └─→ TASK-008
          └─→ TASK-004 ────────────────→ TASK-005
                                        TASK-009

Sprint 1:
TASK-005 ─┬─→ TASK-010 ─┬─→ TASK-011
TASK-007 ─┘            ├─→ TASK-012
                       ├─→ TASK-013
                       └─→ TASK-014

TASK-005 ─┬─→ TASK-015 ─┬─→ TASK-016
TASK-007 ─┤            ├─→ TASK-017
TASK-008 ─┘            ├─→ TASK-018
                       └─→ TASK-019 → TASK-020
                       └─→ TASK-021 → TASK-022

Sprint 2:
TASK-007 ─┬─→ TASK-023 ─┬─→ TASK-024 → TASK-025 → TASK-026
TASK-008 ─┘

TASK-005 ─┬─→ TASK-027 ─┬─→ TASK-028
TASK-008 ─┘            ├─→ TASK-029
                       ├─→ TASK-030
                       └─→ TASK-031

TASK-008 → TASK-032 ─┬─→ TASK-033 → TASK-034 → TASK-035 → TASK-036
                     └─→ TASK-037 → TASK-038

Sprint 3:
TASK-007 → TASK-039 ─┬─→ TASK-040 → TASK-041 → TASK-042 → TASK-043
                     └─→ TASK-044
                     
TASK-039 ─┬─→ TASK-045 → TASK-046
TASK-010 ─┤
TASK-015 ─┘

Sprint 4:
TASK-003 → TASK-047 → TASK-048
TASK-005 → TASK-049
TASK-005 → TASK-050
```

---

## Apéndice C: Resumen de Estimaciones

| Sprint | Tareas | Horas | Story Points |
|--------|--------|-------|--------------|
| **0** | 9 | 24h | 8 |
| **1** | 13 | 88h | 32 |
| **2** | 16 | 96h | 37 |
| **3** | 8 | 56h | 19 |
| **4** | 7 | 56h | 18 |
| **TOTAL** | **53** | **320h** | **114** |

---

*Documento generado el 2 Enero 2026. Basado en PRD_MVP_Originacion_Alter.md v1.0*

