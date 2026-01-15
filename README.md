# Motor de Automatización de Originación Alter-5

Sistema de IA para automatizar el proceso de originación de empresas para intermediación financiera B2B.

## 🎯 Objetivo

Automatizar el proceso de originación mediante 6 agentes especializados que:
1. **Buscan** empresas que potencialmente necesitan financiación
2. **Enriquecen** datos con información financiera y contactos
3. **Evalúan** elegibilidad FEI (Fondo Europeo de Inversiones)
4. **Analizan** triggers de mercado para campañas
5. **Seleccionan** los mejores targets por campaña
6. **Redactan** emails hiper-personalizados

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MOTOR DE ORIGINACIÓN ALTER-5                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ORIGINACIÓN          CUALIFICACIÓN           CAMPAÑAS                 │
│   ┌──────────┐      ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│   │ BUSCADOR │      │ENRIQUECE.│  │EVALUADOR │  │ANALIZADOR│           │
│   │ EMPRESAS │      │  DATOS   │  │   FEI    │  │ CONTEXTO │           │
│   └──────────┘      └──────────┘  └──────────┘  └──────────┘           │
│                                                  ┌──────────┐           │
│                                                  │ SELECTOR │           │
│                                                  │ TARGETS  │           │
│                                                  └──────────┘           │
│                                                  ┌──────────┐           │
│                                                  │ REDACTOR │           │
│                                                  │ MENSAJES │           │
│                                                  └──────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📋 Requisitos

- Python 3.11+
- Cuentas API: Anthropic (Claude), Google AI (Gemini), Airtable

## 🚀 Instalación

### 1. Clonar y crear entorno virtual

```bash
git clone <repo-url>
cd alter5-origination
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt

# Para desarrollo:
pip install -r requirements-dev.txt
```

### 3. Configurar variables de entorno

```bash
cp env.example.txt .env
# Editar .env con tus API keys
```

### 4. Verificar APIs

```bash
python test_apis/run_all_tests.py
```

## 🔧 Configuración

Variables de entorno requeridas en `.env`:

```bash
# APIs
ANTHROPIC_API_KEY=sk-ant-api03-...
GOOGLE_API_KEY=AIzaSy...
AIRTABLE_PAT=pat...
AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9

# Configuración
DEFAULT_LANGUAGE=es
COOLING_OFF_DAYS=90
MAX_TARGETS_PER_CAMPAIGN=30
MAX_EMAIL_WORDS=150
MIN_FIT_SCORE=0.6
```

## 📁 Estructura del Proyecto

```
alter5-origination/
├── config/                 # Configuración y prompts
│   ├── settings.py         # Pydantic Settings
│   ├── airtable_schema.py  # IDs de tablas y campos
│   └── prompts/            # System prompts de agentes
├── core/                   # Modelos y cliente Airtable
│   ├── models.py           # Pydantic models
│   └── airtable_client.py  # Wrapper con retry
├── agents/                 # 6 agentes especializados
│   ├── buscador.py         # Agente 1: BuscadorEmpresas
│   ├── enriquecedor.py     # Agente 2: EnriquecedorDatos
│   ├── evaluador_fei.py    # Agente 3: EvaluadorFEI
│   ├── analizador.py       # Agente 4: AnalizadorContexto
│   ├── selector.py         # Agente 5: SelectorTargets
│   └── redactor.py         # Agente 6: RedactorMensajes
├── integrations/           # Clientes de APIs externas
│   ├── gemini.py           # Cliente Gemini
│   ├── claude.py           # Cliente Claude
│   └── mailchimp.py        # Cliente Mailchimp
├── cli/                    # CLI con Typer
└── tests/                  # Tests unitarios y de integración
```

## 💻 Uso

### CLI Completo

```bash
# ============================================================
# BÚSQUEDA DE EMPRESAS (Agente 1: BuscadorEmpresas)
# ============================================================

# Buscar empresas nuevas en un sector y país
python -m cli.main search companies --sector "renovables" --country ES --region "Andalucía" --limit 25

# Buscar con keywords adicionales
python -m cli.main search companies --sector "energía" --keywords "solar,fotovoltaica" --min-employees 50

# ============================================================
# ENRIQUECIMIENTO DE DATOS (Agente 2: EnriquecedorDatos)
# ============================================================

# Enriquecer una empresa específica
python -m cli.main company enrich recXXXXXXXXXXXXXXX --verbose

# Enriquecer batch de empresas
python -m cli.main company enrich-batch --fei-status Unknown --limit 100

# ============================================================
# EVALUACIÓN FEI (Agente 3: EvaluadorFEI)
# ============================================================

# Evaluar FEI de una empresa
python -m cli.main fei evaluate recXXXXXXXXXXXXXXX --verbose

# Evaluación batch
python -m cli.main fei batch --status Unknown --limit 200

# ============================================================
# ANÁLISIS DE CONTEXTO (Agente 4: AnalizadorContexto)
# ============================================================

# Analizar un trigger de mercado
python -m cli.main context analyze "BCE baja tipos de interés 0.25%" --sectors Industrials,Renewables

# ============================================================
# SELECCIÓN DE TARGETS (Agente 5: SelectorTargets)
# ============================================================

# Seleccionar targets para una campaña
python -m cli.main campaign select recCampaignXXX --sectors Industrials --countries ES,PT --max 30

# ============================================================
# GENERACIÓN DE MENSAJES (Agente 6: RedactorMensajes)
# ============================================================

# Generar mensaje para un target
python -m cli.main message generate recTargetXXX --tone professional

# Generación batch para campaña
python -m cli.main message batch recCampaignXXX --tone friendly

# ============================================================
# PIPELINE COMPLETO DE ORIGINACIÓN
# ============================================================

# Buscar + Enriquecer + Evaluar FEI en un solo comando
python -m cli.main originate --sector "renovables" --country ES --limit 25 --enrich --fei

# Solo búsqueda (sin enriquecer ni evaluar)
python -m cli.main originate --sector "tecnología" --country ES --no-enrich --no-fei

# ============================================================
# CREACIÓN DE CAMPAÑAS
# ============================================================

# Crear campaña completa desde un trigger
python -m cli.main campaign create "BCE baja tipos 0.25%" \
    --sectors Industrials,Renewables \
    --countries ES,PT \
    --max 20 \
    --auto-approve

# ============================================================
# SISTEMA Y MÉTRICAS
# ============================================================

# Ver estado y KPIs del sistema
python -m cli.main status

# Ver métricas de una campaña específica
python -m cli.main status --campaign-id recXXXXXXXXXXXXXXX --verbose

# Ver versión
python -m cli.main version
```

## 📊 Métricas de Éxito

| Métrica | Baseline | Target MVP |
|---------|----------|------------|
| Tiempo crear campaña | 4-8h | ≤45 min |
| Precisión FEI | ~50% | ≥90% |
| Tasa de respuesta | 2-3% | ≥8% |
| Reuniones/mes | 2-3 | ≥8 |

## 🔑 Criterios FEI

Una empresa es elegible para garantía FEI si cumple AL MENOS UNO de estos criterios:

| Código | Criterio |
|--------|----------|
| 1.1 | Premio Cleantech (últimos 3 años) |
| 1.2 | Patente Clean Energy (últimos 3 años) |
| 1.3 | Eco-Label EU/Nacional/Internacional |
| 1.4 | Green Business ≥90% revenue |
| 1.5 | Green Business Model con impacto verificable |
| 1.6 | Certificado Ambiental válido |

## 📚 Documentación

- [PRD Completo](C.Deliverables/PRD_MVP_Originacion_Alter.md)
- [Tareas de Desarrollo](C.Deliverables/MVP_Origination_Alter_Development_Tasks.md)
- [Contexto Maestro](B.Project_Context/B.1.ContextoGeneral/Main_Promt_Origination.md)
- [Esquema BBDD](B.Project_Context/B.1.ContextoGeneral/Origination_Campaigns_Full_Database_COMPLETE.md)

## 📝 Licencia

Propietario - Alter-5 © 2026

