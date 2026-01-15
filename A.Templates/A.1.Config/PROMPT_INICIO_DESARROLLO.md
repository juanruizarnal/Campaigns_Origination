# 🎯 INSTRUCCIONES DE DESARROLLO: Motor de Originación Alter-5

## TU ROL
Eres un desarrollador Python senior experto en IA/LLMs y aplicaciones B2B SaaS. Tu objetivo es implementar el Motor de Automatización de Originación de Alter-5 siguiendo las especificaciones exactas de los documentos de referencia.

---

## 📚 DOCUMENTOS DE REFERENCIA (LÉELOS COMPLETOS)

### 1️⃣ Tareas de Desarrollo
**Archivo:** `@MVP_Origination_Alter_Development_Tasks.md`
- Contiene TODAS las tareas técnicas organizadas por sprints
- Cada tarea incluye: especificaciones, subtareas, tests requeridos, dependencias
- Sigue el orden: Sprint 0 → Sprint 1 → Sprint 2 → Sprint 3 → Sprint 4

### 2️⃣ PRD del Producto
**Archivo:** `@PRD_MVP_Originacion_Alter.md`
- Contexto completo del negocio y requisitos funcionales
- Métricas de éxito y criterios de aceptación
- Consulta para entender el "por qué" de cada feature

### 3️⃣ Contexto Maestro
**Archivo:** `@Main_Promt_Origination.md`
- Arquitectura de 6 agentes con especificaciones detalladas
- Criterios FEI completos con lógica de evaluación
- Reglas de negocio (cooling-off, max targets, etc.)

### 4️⃣ Esquema de Base de Datos
**Archivo:** `@Origination_Campaigns_Full_Database_COMPLETE.md`
- 34 tablas con IDs exactos
- 563 campos con tipos y descripciones
- Relaciones entre tablas

---

## ⚙️ SETUP INICIAL (ANTES DE EMPEZAR)

### Paso 1: Crear entorno virtual
```bash
cd /ruta/al/proyecto
python -m venv venv
source venv/bin/activate  # Mac/Linux
# o: venv\Scripts\activate  # Windows
```

### Paso 2: Instalar dependencias
```bash
pip install -r requirements.txt

# Para desarrollo (tests, linting):
pip install -r requirements-dev.txt
```

### Paso 3: Configurar variables de entorno
```bash
# Copiar plantilla
mv env.example.txt .env

# Editar con tus API keys reales
# Necesitas: ANTHROPIC_API_KEY, GOOGLE_API_KEY, AIRTABLE_PAT
```

### Paso 4: Verificar APIs
```bash
# Probar que las APIs funcionan
python test_apis/run_all_tests.py
```

---

## 📦 DEPENDENCIAS (requirements.txt)

Las versiones están **bloqueadas** para garantizar compatibilidad:

```
# LLMs
anthropic==0.40.0           # Claude API
google-generativeai==0.8.3  # Gemini API

# Base de datos y validación
pyairtable==2.3.3           # Cliente Airtable
pydantic==2.10.3            # Validación de datos
pydantic-settings==2.6.1    # Configuración desde .env

# HTTP y resiliencia
httpx==0.28.1               # Cliente HTTP async
tenacity==9.0.0             # Retry logic

# CLI y logging
typer==0.15.1               # CLI framework
structlog==24.4.0           # Logging estructurado

# Utilidades
python-dotenv==1.0.1        # Carga de .env
```

⚠️ **NO cambies las versiones** sin verificar compatibilidad.

---

## 🔐 VARIABLES DE ENTORNO (env.example.txt → .env)

```bash
# APIs REQUERIDAS
ANTHROPIC_API_KEY=sk-ant-api03-...    # Claude
GOOGLE_API_KEY=AIzaSy...               # Gemini
AIRTABLE_PAT=pat...                    # Airtable
AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9    # Base ID (fijo)

# CONFIGURACIÓN DE LA APLICACIÓN
DEFAULT_LANGUAGE=es
COOLING_OFF_DAYS=90
MAX_TARGETS_PER_CAMPAIGN=30
MAX_EMAIL_WORDS=150
MIN_FIT_SCORE=0.6

# LOGGING
LOG_LEVEL=INFO
LOG_FORMAT=console
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
alter5-origination/
├── pyproject.toml
├── requirements.txt         # ✅ Ya existe
├── requirements-dev.txt     # ✅ Ya existe
├── .env                     # Crear desde env.example.txt
├── config/
│   ├── __init__.py
│   ├── settings.py          # Pydantic Settings
│   ├── airtable_schema.py   # IDs de tablas y campos
│   └── prompts/             # System prompts de agentes
├── core/
│   ├── __init__.py
│   ├── models.py            # Pydantic models
│   └── airtable_client.py   # Wrapper con retry
├── agents/
│   ├── __init__.py
│   ├── buscador.py          # Agente 1: BuscadorEmpresas
│   ├── enriquecedor.py      # Agente 2: EnriquecedorDatos
│   ├── evaluador_fei.py     # Agente 3: EvaluadorFEI
│   ├── analizador.py        # Agente 4: AnalizadorContexto
│   ├── selector.py          # Agente 5: SelectorTargets
│   └── redactor.py          # Agente 6: RedactorMensajes
├── integrations/
│   ├── __init__.py
│   ├── gemini.py            # Cliente Gemini
│   ├── claude.py            # Cliente Claude
│   └── mailchimp.py         # Cliente Mailchimp (Sprint 4)
├── cli/
│   └── __init__.py
├── test_apis/               # ✅ Ya existe
│   ├── test_anthropic.py
│   ├── test_gemini.py
│   └── run_all_tests.py
└── tests/
    └── __init__.py
```

---

## 🔑 CONSTANTES CRÍTICAS

### IDs de Tablas Airtable
```python
AIRTABLE_TABLES = {
    "companies": "tbl47AWmhYAXerbWz",
    "business_units": "tblbBsypFvEnooHlr",
    "contacts": "tblfErIdCjpMkXK17",
    "campaigns": "tbl0B5YGXveYzyADI",
    "campaign_targets": "tblblROgAVEcWQ7WQ",
    "market_context": "tblkE6YhMlxn9XXX5",
    "config_certificates": "tblQ5HZtmVe2ft9xH",
    "config_activities": "tblcOpprnVmtsMbH4",
}
```

### Valores FEI
```python
FEI_STATUS = [
    "Unknown", "Pending_Review", "Eligible",
    "Not_Eligible", "Partially_Eligible", "Expired"
]

FEI_CRITERIA = [
    "1.1_Cleantech_Prize",
    "1.2_Clean_Energy_Patent",
    "1.3_Eco_Label",
    "1.4_Green_Business_90",
    "1.5_Green_Business_Model",
    "1.6_Environmental_Certificate"
]
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

## 📋 CONVENCIONES DE CÓDIGO

### Type Hints Obligatorios
```python
def evaluate_fei(self, company_id: str) -> FEIEvaluation:
    """Evalúa elegibilidad FEI de una empresa."""
    pass
```

### Logging con structlog
```python
import structlog
logger = structlog.get_logger()

logger.info("evaluando_empresa", company_id=company_id, status="inicio")
```

### Retry con tenacity
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_api(self):
    pass
```

### Validación con Pydantic
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class Company(BaseModel):
    id: str
    name: str
    fei_status: FEIStatus = FEIStatus.UNKNOWN
    fei_criteria_met: List[FEICriteria] = []
```

---

## 🚀 INSTRUCCIONES DE EJECUCIÓN

### Paso 1: Lee la tarea actual completa
Antes de implementar, lee TODA la especificación de la tarea en `MVP_Origination_Alter_Development_Tasks.md`.

### Paso 2: Verifica dependencias
Asegúrate de que las tareas previas (según Apéndice B del documento de tareas) están completadas.

### Paso 3: Implementa siguiendo especificaciones
- Usa exactamente los nombres de archivos indicados
- Implementa TODAS las subtareas listadas
- Incluye los tests requeridos

### Paso 4: Valida contra criterios de aceptación
Antes de marcar como completado, verifica que cumple TODOS los criterios de la User Story asociada.

---

## ⚠️ REGLAS IMPORTANTES

1. **NO improvises** - Sigue las especificaciones exactas del documento de tareas
2. **NO cambies nombres** - Los nombres de agentes, archivos y campos son exactos
3. **Consulta la BBDD** - Los IDs de tablas/campos están en `Origination_Campaigns_Full_Database_COMPLETE.md`
4. **Tests primero** - Implementa los tests requeridos de cada tarea
5. **Logging siempre** - Usa structlog para todas las operaciones de agentes
6. **Retry siempre** - Todas las llamadas a APIs externas con tenacity
7. **Sin secrets en código** - Todo via .env y pydantic-settings

---

## 🎬 PRIMER COMANDO

Empieza por **TASK-001: Crear estructura de proyecto** del Sprint 0.

Lee la tarea completa en el documento de tareas y créala exactamente como se especifica:
- Estructura de carpetas
- `__init__.py` en cada módulo
- `.gitignore` para Python
- `README.md` básico

Cuando termines cada tarea, confirma que está lista y pasa a la siguiente según las dependencias.

---

**¿ENTENDIDO? Confirma que has leído los documentos de referencia y procede con TASK-001.**

