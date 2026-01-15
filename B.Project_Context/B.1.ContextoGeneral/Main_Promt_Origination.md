# Contexto Maestro: Motor de Automatización de Originación Alter-5

**Versión**: 3.0 (Final)  
**Fecha**: 29 Diciembre 2025  
**Propósito**: Documento base definitivo para todos los agentes de IA, PRDs y desarrollos del proyecto  
**Alcance**: Sistema de Originación completo con arquitectura de 6 agentes especializados

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Contexto de la Empresa](#2-contexto-de-la-empresa)
3. [Productos de Alter-5](#3-productos-de-alter-5)
4. [Acuerdo FEI y Criterios de Elegibilidad](#4-acuerdo-fei-y-criterios-de-elegibilidad)
5. [Situación Actual](#5-situación-actual)
6. [Objetivos del Proyecto](#6-objetivos-del-proyecto)
7. [Arquitectura de 6 Agentes Especializados](#7-arquitectura-de-6-agentes-especializados)
8. [Flujos de Trabajo](#8-flujos-de-trabajo)
9. [Reglas de Negocio](#9-reglas-de-negocio)
10. [Stack Tecnológico](#10-stack-tecnológico)
11. [Estructura de Datos](#11-estructura-de-datos)
12. [Restricciones y Consideraciones](#12-restricciones-y-consideraciones)
13. [Plan de Implementación](#13-plan-de-implementación)
14. [Métricas de Éxito](#14-métricas-de-éxito)
15. [Referencias](#15-referencias)
16. [Instrucciones para Agentes de IA](#16-instrucciones-para-agentes-de-ia)

---

## 1. Resumen Ejecutivo

### 1.1 Visión del Proyecto

**Alter-5** es una empresa española de intermediación financiera que conecta empresas que buscan financiación (promotores) con financiadores (inversores). Este proyecto implementa un **Motor de Automatización de Originación** basado en IA que:

1. **Identifica** empresas que potencialmente necesitan financiación
2. **Cualifica** empresas con datos verificables
3. **Evalúa elegibilidad FEI** con alta precisión (≥90%)
4. **Genera campañas** hiper-personalizadas basadas en contexto de mercado
5. **Maximiza** tasa de respuesta mediante micro-segmentación

### 1.2 Diferenciador Competitivo Único

Alter-5 tiene un acuerdo exclusivo con el **Fondo Europeo de Inversiones (FEI)** que permite ofrecer financiación con garantía europea a empresas elegibles. Este diferenciador requiere:

- Identificación precisa de empresas elegibles (criterios Green Checker)
- Priorización de estas empresas en campañas (mayor margen)
- Comunicación del valor diferencial en mensajes

### 1.3 Arquitectura de Solución

El sistema implementa **6 agentes especializados** siguiendo el principio de responsabilidad única:

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

### 1.4 Resultado Esperado

| Métrica | Antes | Después |
|---------|-------|---------|
| Tiempo crear campaña | 4-8 horas | 30-45 min |
| Precisión evaluación FEI | ~50% manual | ≥90% |
| Tasa de respuesta | 2-3% | 8%+ |
| Reuniones/mes | 2-3 | 8-10 |

---

## 2. Contexto de la Empresa

### 2.1 Identidad

| Atributo | Valor |
|----------|-------|
| **Nombre** | Alter-5 |
| **Sector** | Intermediación financiera B2B |
| **Ubicación** | España (operaciones en Europa) |
| **Web** | alter-5.com |
| **Modelo de negocio** | Comisión por operaciones cerradas |

### 2.2 Clientes Objetivo

| Tipo | Descripción | Tamaño | Ticket típico |
|------|-------------|--------|---------------|
| **Promotores** | Pymes y mid-caps que buscan financiación | 10-500 empleados | €2M-50M |
| **Inversores** | Fondos, family offices, bancos | Institucionales | €2M-50M |

### 2.3 Mercados Geográficos

| Fase | Mercados | Timeline |
|------|----------|----------|
| **Actual** | España, Portugal | Ahora |
| **Corto plazo** | UK, Francia, Alemania, Italia | 6-12 meses |
| **Largo plazo** | USA, Canadá, LATAM | 12-24 meses |

### 2.4 Sectores Prioritarios

1. **Energías Renovables** (principal): Solar, eólica, almacenamiento
2. **Real Estate**: Desarrollo, rehabilitación, proyectos sostenibles
3. **Defensa**: En crecimiento por rearme europeo (2026+)
4. **Industriales**: Manufactura, componentes, maquinaria
5. **Tecnología**: Cleantech, software sostenibilidad

---

## 3. Productos de Alter-5

### 3.1 Catálogo Completo

| Producto | Código | Descripción | Target | Margen | Prioridad |
|----------|--------|-------------|--------|--------|-----------|
| **Garantía FEI** | `FEI_Guarantee` | Financiación corporativa con garantía del Fondo Europeo de Inversiones | Empresas Green Checker elegibles | **Alto** | 🔴 Máxima |
| **Deuda Corporativa** | `Corporate_Debt` | Financiación corporativa sin garantía FEI | Empresas sólidas no FEI | Medio | 🟡 Alta |
| **Project Finance LT** | `Project_Finance_LongTerm` | Financiación de proyectos largo plazo | Renovables, Real Estate | Medio | 🟡 Alta |
| **Bridge Loan** | `Project_Finance_Bridge` | Financiación puente corto plazo | Proyectos con exit claro | Medio | 🟢 Media |
| **M&A Advisory** | `M&A_Advisory` | Asesoramiento compraventa empresas | Buy-side y sell-side | Variable | 🟢 Media |

### 3.2 Lógica de Asignación de Producto

```
SI empresa.FEI_Status == "Eligible":
    producto_principal = "FEI_Guarantee"
    producto_alternativo = "Corporate_Debt"
SINO SI empresa.sector IN ["Renovables", "Real Estate", "Infraestructura"]:
    producto_principal = "Project_Finance_LongTerm"
SINO:
    producto_principal = "Corporate_Debt"
```

---

## 4. Acuerdo FEI y Criterios de Elegibilidad

### 4.1 Qué es el Acuerdo FEI

Alter-5 tiene un **acuerdo exclusivo** con el Fondo Europeo de Inversiones (FEI) del grupo BEI:

| Característica | Detalle |
|----------------|---------|
| **Tipo** | Garantía europea para financiación |
| **Capacidad actual** | €50M |
| **En negociación** | €200M |
| **Beneficios** | Menor tipo de interés, mayor plazo, acceso a capital |
| **Exclusividad** | Pocos intermediarios tienen este acuerdo |

### 4.2 Criterios de Elegibilidad FEI (Green Checker)

Una empresa es **elegible para garantía FEI** si cumple **AL MENOS UNO** de estos 6 criterios:

| Código | Criterio | Descripción | Verificación | Automatizable |
|--------|----------|-------------|--------------|---------------|
| **1.1** | Premio Cleantech | Premio clean-tech/green en últimos 3 años de institución EU/Nacional | Lista de premios conocidos | ✅ Sí |
| **1.2** | Patente Clean Energy | Patente energía renovable/cleantech registrada últimos 3 años | IPC Codes específicos | ⚠️ Parcial |
| **1.3** | Eco-Label | Eco-label EU/Nacional/Internacional registrado | Lista de eco-labels | ✅ Sí |
| **1.4** | Green Business 90% | Actividad principal "green" con ≥90% revenue | Lista de actividades | ✅ Sí |
| **1.5** | Green Business Model | Modelo de negocio "green" con impacto verificable | Análisis cualitativo | ❌ No |
| **1.6** | Certificado Ambiental | Certificado ambiental de lista predefinida válido | Lista de certificados | ✅ Sí |

**Fuente oficial**: https://alter-5-es.greenchecker.eib-group.org/eif-sustainable/1.3/sustainable-enterprise/categories

### 4.3 Certificaciones FEI Elegibles

#### 4.3.1 ISOs y Sistemas de Gestión (Criterio 1.6)

| Certificación | Descripción | Validez |
|---------------|-------------|---------|
| **ISO 14001** | Sistema de gestión ambiental | 3 años |
| **ISO 50001** | Sistema de gestión de la energía | 3 años |
| **ISO 14064** | Gases de efecto invernadero / Huella carbono | 3 años |
| **EMAS** | Eco-Management and Audit Scheme (EU) | 3 años |

#### 4.3.2 Eco-Labels (Criterio 1.3)

| Certificación | Emisor | Descripción |
|---------------|--------|-------------|
| **B Corp** | B Lab | Certified B Corporation |
| **EU Ecolabel** | European Commission | Etiqueta ecológica europea |
| **FSC** | FSC International | Certificación forestal |
| **PEFC** | PEFC Council | Certificación forestal |
| **Cradle to Cradle** | C2C Products Innovation | Economía circular |
| **LEED** | USGBC | Edificios sostenibles |
| **BREEAM** | BRE | Edificios sostenibles |

#### 4.3.3 Premios Cleantech (Criterio 1.1)

| Premio | Emisor | Validez |
|--------|--------|---------|
| **CDTI Neotec** | CDTI (España) | 3 años |
| **Horizon Europe Grant** | European Commission | 3 años |
| **EIT Climate-KIC** | EIT | 3 años |
| **EIT InnoEnergy** | EIT | 3 años |
| **LIFE Programme** | European Commission | 3 años |
| **Premio Europeo Medio Ambiente** | European Commission | 3 años |

### 4.4 Actividades FEI Elegibles (Criterio 1.4)

Sectores donde ≥90% del revenue hace elegible:

| Actividad | GICS Sector | NACE Code |
|-----------|-------------|-----------|
| Generación Solar Fotovoltaica | Utilities | D35.11 |
| Generación Eólica | Utilities | D35.11 |
| Generación Hidroeléctrica | Utilities | D35.11 |
| Generación Biomasa | Utilities | D35.11 |
| Distribución Eléctrica Renovable | Utilities | D35.13 |
| Gestión de Residuos | Industrials | E38 |
| Reciclaje | Industrials | E38.3 |
| Tratamiento de Aguas | Utilities | E36 |
| Transporte Ferroviario | Industrials | H49.1 |
| Componentes Vehículos Eléctricos | Consumer Discretionary | C29.32 |
| Eficiencia Energética Edificios | Industrials | C27.51 |
| Agricultura Ecológica | Consumer Staples | A01 |
| Software Cleantech | Information Technology | J62 |
| Materiales Construcción Sostenible | Materials | C23 |

### 4.5 Códigos IPC para Patentes (Criterio 1.2)

| Código IPC | Descripción |
|------------|-------------|
| Y02E | Reducción emisiones GHG - Energía |
| Y02T | Reducción emisiones GHG - Transporte |
| Y02B | Reducción emisiones GHG - Edificios |
| Y02W | Reducción emisiones GHG - Residuos |
| H02S | Generación de energía eléctrica por conversión de radiación infrarroja, luz visible o ultravioleta |
| F03D | Motores de viento |

### 4.6 Evolución Prevista (2026+)

Se espera ampliación de criterios FEI para incluir:
- **Sector Defensa**: Plan de rearme europeo
- **Nuevos criterios de sostenibilidad**: Alineados con EU Taxonomy

---

## 5. Situación Actual

### 5.1 Datos Disponibles

| Fuente | Registros | Estado | Calidad | Acción |
|--------|-----------|--------|---------|--------|
| Airtable/Pipedrive | ~1.000 empresas | Activo | Variable | Enriquecer |
| Hojas de cálculo | ~1.000 empresas | Pendiente | Baja-Media | Cargar + limpiar |
| **Total** | **~2.000 empresas** | - | - | - |

### 5.2 Características de los Datos

- ✅ Mayoría empresas españolas del sector renovables
- ✅ ~1.000 promotores, ~200 inversores
- ⚠️ Obtenidos por scraping con LLMs sin proceso estandarizado
- ⚠️ Contienen errores y campos incompletos
- ❌ **NO son 100% fiables**
- ❌ FEI_Status mayoritariamente sin evaluar

### 5.3 Herramientas Actuales

| Herramienta | Uso Actual | Estado | Futuro |
|-------------|------------|--------|--------|
| Pipedrive | CRM | Legacy | Eliminar |
| **Airtable** | Base de datos | **Activo** | **Hub central** |
| Mailchimp | Campañas email | Activo | Mantener |
| Claude Desktop | Interacción comercial | Activo | Expandir con MCP |
| Hojas de cálculo | Gestión campañas | Legacy | Eliminar |

### 5.4 Proceso Actual (Problemas)

| Tarea | Tiempo Actual | Problema |
|-------|---------------|----------|
| Búsqueda de empresas | 4-8 horas/campaña | Manual, inconsistente |
| Cualificación | Variable | Sin datos financieros (~60% incompletos) |
| Identificación FEI | Manual | Oportunidades perdidas |
| Personalización emails | 30 min/email | No escala |
| Segmentación | Básica | Tasa respuesta 2-3% |

**Resultado**: Equipo comercial dedica **>70% tiempo a tareas operativas**.

### 5.5 Activos Valiosos

| Activo | Valor | Uso Propuesto |
|--------|-------|---------------|
| Historial de emails | Preferencias de clientes | Personalización de mensajes |
| Deals cerrados | Validación del modelo | Ejemplos de éxito |
| Acuerdo FEI | Diferenciador único | Priorización en campañas |
| Conocimiento sectorial | Experiencia del equipo | Prompts y reglas de negocio |

---

## 6. Objetivos del Proyecto

### 6.1 Objetivo Principal

**Automatizar el proceso de Originación** mediante IA, permitiendo al equipo comercial dedicar su tiempo a cerrar deals en lugar de tareas operativas.

### 6.2 Objetivos Específicos Cuantificados

| Objetivo | Métrica | Baseline | Target MVP | Target 6 meses |
|----------|---------|----------|------------|----------------|
| Reducir tiempo campaña | Horas | 4-8h | **≤45 min** | ≤30 min |
| Precisión FEI | % correctas | ~50% | **≥90%** | ≥95% |
| Empresas FEI identificadas | /mes | ~50 | **200+** | 500+ |
| Tasa de apertura | % | 15% | **≥25%** | ≥35% |
| Tasa de respuesta | % | 2-3% | **≥8%** | ≥12% |
| Reuniones conseguidas | /mes | 2-3 | **≥8** | ≥15 |
| Campañas simultáneas | Número | 1-2 | **≥4** | ≥10 |

### 6.3 Prioridades por Fase

#### Corto Plazo (0-3 meses) - MVP
- ✅ Sistema de 6 agentes funcionando
- ✅ Evaluación FEI automatizada con ≥90% precisión
- ✅ Primera campaña real enviada
- ✅ Validación con métricas reales

#### Medio Plazo (3-6 meses) - Escala
- Escalar a 10.000+ empresas
- Expandir a UK, Francia
- Integrar SABI (datos financieros)
- Integrar Apollo.io (contactos)

#### Largo Plazo (6-12 meses) - Expansión
- 50.000+ empresas en Europa
- Automatización completa del pipeline
- Sistema de alertas automáticas
- Expansión a USA/LATAM

---

## 7. Arquitectura de 6 Agentes Especializados

### 7.1 Principio de Diseño

La arquitectura sigue el **principio de responsabilidad única**: cada agente tiene una misión específica, un prompt focalizado y es fácilmente iterable de forma independiente.

**Beneficios**:
- ✅ Mayor calidad de resultados (prompts focalizados)
- ✅ Facilidad de debugging (saber qué falló)
- ✅ Iteración independiente (mejorar sin romper)
- ✅ Menor complejidad por agente
- ✅ Prompts más cortos = mejor rendimiento LLM

### 7.2 Diagrama de Arquitectura Completa

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MOTOR DE ORIGINACIÓN ALTER-5                              │
│                     Arquitectura de 6 Agentes Especializados                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         CAPA DE INTERACCIÓN                               │  │
│  │                                                                           │  │
│  │   ┌─────────────────────────┐       ┌─────────────────────────┐          │  │
│  │   │  CLAUDE DESKTOP + MCP   │       │    CLI PYTHON/TYPER     │          │  │
│  │   │                         │       │                         │          │  │
│  │   │  • Equipo comercial     │       │  • Desarrollador        │          │  │
│  │   │  • Consultas naturales  │       │  • Batch processing     │          │  │
│  │   │  • Campañas ad-hoc      │       │  • Scraping masivo      │          │  │
│  │   └────────────┬────────────┘       └────────────┬────────────┘          │  │
│  │                │                                 │                        │  │
│  └────────────────┼─────────────────────────────────┼────────────────────────┘  │
│                   │                                 │                           │
│                   ▼                                 ▼                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE ORQUESTACIÓN (Coordinador)                     │  │
│  │                                                                           │  │
│  │    Recibe instrucciones → Determina flujo → Coordina agentes → Output    │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                           │
│         ┌───────────────────────────┼───────────────────────────┐              │
│         │                           │                           │              │
│         ▼                           ▼                           ▼              │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐        │
│  │   ORIGINACIÓN   │      │  CUALIFICACIÓN  │      │    CAMPAÑAS     │        │
│  │   (1 agente)    │      │   (2 agentes)   │      │   (3 agentes)   │        │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘        │
│         │                         │                         │                  │
│         ▼                         ▼                         ▼                  │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐        │
│  │                 │      │                 │      │                 │        │
│  │   1. BUSCADOR   │      │ 2. ENRIQUECEDOR │      │ 4. ANALIZADOR   │        │
│  │   DE EMPRESAS   │      │    DE DATOS     │      │   DE CONTEXTO   │        │
│  │                 │      │                 │      │                 │        │
│  │  ┌───────────┐  │      │  ┌───────────┐  │      │  ┌───────────┐  │        │
│  │  │  Gemini   │  │      │  │  Gemini   │  │      │  │Gemini+    │  │        │
│  │  │  Search   │  │      │  │  Search   │  │      │  │Claude     │  │        │
│  │  └───────────┘  │      │  └───────────┘  │      │  └───────────┘  │        │
│  │                 │      │                 │      │                 │        │
│  │  • Buscar       │      │  • Completar    │      │  • Analizar     │        │
│  │    empresas     │      │    datos básicos│      │    triggers     │        │
│  │  • Deduplicar   │      │  • Financieros  │      │  • Buscar       │        │
│  │  • Crear en AT  │      │  • Contactos    │      │    noticias     │        │
│  │                 │      │                 │      │  • Market_Ctx   │        │
│  └─────────────────┘      └────────┬────────┘      └────────┬────────┘        │
│                                    │                        │                  │
│                                    ▼                        │                  │
│                           ┌─────────────────┐               │                  │
│                           │                 │               │                  │
│                           │ 3. EVALUADOR    │               │                  │
│                           │      FEI        │               │                  │
│                           │                 │               │                  │
│                           │  ┌───────────┐  │               │                  │
│                           │  │  Claude   │  │               │                  │
│                           │  │  +Gemini  │  │               │                  │
│                           │  └───────────┘  │               │                  │
│                           │                 │               │                  │
│                           │  • Buscar certs │               │                  │
│                           │  • Evaluar 1.1- │               │                  │
│                           │    1.6          │               │                  │
│                           │  • FEI_Status   │               │                  │
│                           │  • Confidence   │               │                  │
│                           └─────────────────┘               │                  │
│                                                             │                  │
│                                                             ▼                  │
│                                                    ┌─────────────────┐        │
│                                                    │                 │        │
│                                                    │ 5. SELECTOR     │        │
│                                                    │   DE TARGETS    │        │
│                                                    │                 │        │
│                                                    │  ┌───────────┐  │        │
│                                                    │  │  Claude   │  │        │
│                                                    │  └───────────┘  │        │
│                                                    │                 │        │
│                                                    │  • Filtrar BUs  │        │
│                                                    │  • Cooling-off  │        │
│                                                    │  • Scoring      │        │
│                                                    │  • Priorizar    │        │
│                                                    └────────┬────────┘        │
│                                                             │                  │
│                                                             ▼                  │
│                                                    ┌─────────────────┐        │
│                                                    │                 │        │
│                                                    │ 6. REDACTOR     │        │
│                                                    │   DE MENSAJES   │        │
│                                                    │                 │        │
│                                                    │  ┌───────────┐  │        │
│                                                    │  │  Claude   │  │        │
│                                                    │  │  (best    │  │        │
│                                                    │  │  writing) │  │        │
│                                                    │  └───────────┘  │        │
│                                                    │                 │        │
│                                                    │  • Personalizar │        │
│                                                    │  • Subject+Body │        │
│                                                    │  • FEI/Corporate│        │
│                                                    │  • Tono perfecto│        │
│                                                    └─────────────────┘        │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                           CAPA DE DATOS                                   ││
│  │                                                                           ││
│  │   ┌─────────────────────────────────────────────────────────────────────┐││
│  │   │                          AIRTABLE                                   │││
│  │   │                                                                     │││
│  │   │  STAKEHOLDERS          ORIGINATION          CONFIG                  │││
│  │   │  ├─ Companies          ├─ Campaigns         ├─ Certificates        │││
│  │   │  ├─ Business_Units     ├─ Targets           ├─ Activities          │││
│  │   │  ├─ Contacts           └─ Market_Context    ├─ Countries           │││
│  │   │  └─ Financials                              └─ Products            │││
│  │   │                                                                     │││
│  │   │  NUEVA: Company_Certificates                                       │││
│  │   │                                                                     │││
│  │   └─────────────────────────────────────────────────────────────────────┘││
│  │                                                                           ││
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                        CAPA DE COMUNICACIÓN                               ││
│  │                                                                           ││
│  │      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐            ││
│  │      │   MAILCHIMP  │    │    GMAIL     │    │     CSV      │            ││
│  │      │              │    │  (opcional)  │    │  (fallback)  │            ││
│  │      │  • Masivo    │    │  • 1-to-1    │    │  • Manual    │            ││
│  │      │  • Tracking  │    │  • Personal  │    │  • Export    │            ││
│  │      └──────────────┘    └──────────────┘    └──────────────┘            ││
│  │                                                                           ││
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Especificación de Cada Agente

#### 7.3.1 Agente 1: BUSCADOR DE EMPRESAS

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Encontrar empresas nuevas que cumplan criterios especificados |
| **Input** | Criterios de búsqueda (sector, país, tamaño, keywords) |
| **Output** | Lista de empresas con datos básicos en Airtable |
| **LLM** | Gemini 1.5 Flash con Google Search Grounding |
| **Tablas** | `Stakeholders_Companies`, `Stakeholders_Business_Units` |

**Responsabilidades ÚNICAS**:
```
✅ Buscar empresas según criterios
✅ Extraer: nombre, web, sector, ciudad, descripción
✅ Verificar que URLs son reales
✅ Deduplicar contra BBDD existente
✅ Crear registros con Source="AI_Scraping"
✅ Crear Business Unit "Default" por empresa

❌ NO completa datos adicionales (eso es Agente 2)
❌ NO evalúa FEI (eso es Agente 3)
```

**Prompt Focus**: Solo búsqueda web y extracción de datos básicos verificables.

---

#### 7.3.2 Agente 2: ENRIQUECEDOR DE DATOS

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Completar información faltante de empresas |
| **Input** | Empresa con datos básicos |
| **Output** | Empresa con datos enriquecidos + contactos |
| **LLM** | Gemini 1.5 Flash |
| **Tablas** | `Stakeholders_Companies`, `Stakeholders_Companies_Financials`, `Stakeholders_Contacts` |

**Responsabilidades ÚNICAS**:
```
✅ Completar: empleados, LinkedIn, estructura corporativa
✅ Buscar datos financieros (revenue, EBITDA, deuda)
✅ Identificar key persons (CEO, CFO, Director Financiero)
✅ Buscar emails y teléfonos de contactos
✅ Guardar financieros por año

❌ NO busca certificaciones (eso es Agente 3)
❌ NO evalúa FEI (eso es Agente 3)
```

**Prompt Focus**: Data augmentation - completar campos faltantes con datos verificables.

---

#### 7.3.3 Agente 3: EVALUADOR FEI ⭐ (Crítico)

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Determinar elegibilidad FEI con alta precisión |
| **Input** | Empresa + datos enriquecidos |
| **Output** | FEI_Status + FEI_Criteria_Met + Confidence |
| **LLM** | Claude (razonamiento) + Gemini (búsqueda certs) |
| **Tablas** | `Stakeholders_Companies`, `Company_Certificates`, `Config_Certificates`, `Config_Activities` |

**Responsabilidades ÚNICAS**:
```
✅ Buscar certificaciones (ISO 14001, B Corp, etc.)
✅ Buscar premios cleantech (CDTI, Horizon, EIT)
✅ Verificar actividad principal vs lista FEI
✅ Evaluar cada criterio (1.1 a 1.6)
✅ Determinar status: Eligible/Not_Eligible/Pending_Review/Unknown
✅ Calcular confidence score (0-100%)
✅ Guardar certificaciones encontradas en Company_Certificates
✅ Actualizar campos FEI en Stakeholders_Companies

❌ NO selecciona targets (eso es Agente 5)
❌ NO genera mensajes (eso es Agente 6)
```

**Prompt Focus**: Evaluación rigurosa de criterios FEI con razonamiento explícito.

**Lógica de Evaluación**:
```python
def evaluate_fei(empresa):
    criteria_met = []
    
    # Criterio 1.1: Premios cleantech (últimos 3 años)
    for cert in empresa.certificates:
        if cert.type == "Prize" and cert.fei_eligible:
            if cert.issue_date >= (today - 3_years):
                criteria_met.append("1.1")
    
    # Criterio 1.3: Eco-labels
    for cert in empresa.certificates:
        if cert.type == "Eco-label" and cert.fei_eligible:
            criteria_met.append("1.3")
    
    # Criterio 1.4: Actividad green (≥90% revenue)
    for bu in empresa.business_units:
        if bu.activity.fei_eligible and bu.revenue_pct >= 90:
            criteria_met.append("1.4")
    
    # Criterio 1.6: Certificados ambientales
    for cert in empresa.certificates:
        if cert.type == "ISO" and cert.fei_eligible:
            criteria_met.append("1.6")
    
    return {
        "status": "Eligible" if criteria_met else "Not_Eligible",
        "criteria_met": list(set(criteria_met)),
        "confidence": calculate_confidence(criteria_met)
    }
```

---

#### 7.3.4 Agente 4: ANALIZADOR DE CONTEXTO

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Analizar triggers de mercado y generar contexto estructurado |
| **Input** | Trigger de mercado o empresa específica |
| **Output** | Análisis estructurado en `Market_Context` |
| **LLM** | Gemini (búsqueda noticias) + Claude (análisis) |
| **Tablas** | `Market_Context` |

**Responsabilidades ÚNICAS**:
```
✅ Buscar noticias recientes relacionadas con trigger
✅ Analizar impacto del trigger en sectores/países
✅ Identificar sectores afectados
✅ Determinar producto recomendado
✅ Evaluar urgencia (alta/media/baja)
✅ Extraer ángulos para personalización
✅ Crear registro en Market_Context

❌ NO selecciona targets (eso es Agente 5)
❌ NO genera mensajes (eso es Agente 6)
```

**Prompt Focus**: Análisis de mercado y estructuración de información contextual.

**Output Estructurado**:
```json
{
    "trigger": "BCE baja tipos 0.25%",
    "summary": "Reducción de tipos beneficia refinanciación",
    "affected_sectors": ["Industrials", "Real Estate", "Utilities"],
    "affected_countries": ["ES", "PT"],
    "recommended_product": "FEI_Guarantee",
    "urgency": "alta",
    "key_angles": [
        "Oportunidad de refinanciar deuda variable",
        "Reducción coste financiero",
        "Momento ideal para nuevos proyectos"
    ]
}
```

---

#### 7.3.5 Agente 5: SELECTOR DE TARGETS

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Seleccionar las mejores Business Units para cada campaña |
| **Input** | Contexto de campaña + pool de BUs disponibles |
| **Output** | Lista priorizada de targets con fit score |
| **LLM** | Claude (razonamiento) |
| **Tablas** | `Stakeholders_Business_Units`, `Origination_Campaigns`, `Campaign_Targets` |

**Responsabilidades ÚNICAS**:
```
✅ Filtrar BUs por criterios (sector, país, activo)
✅ Aplicar cooling-off (90 días sin contacto)
✅ Verificar que BU no está en otra campaña activa
✅ Calcular fit score (0-100%)
✅ Aplicar priorización (FEI > key_person > datos_completos)
✅ Limitar a max 30 targets
✅ Proponer lista para aprobación humana
✅ Explicar justificación de cada selección

❌ NO genera mensajes (eso es Agente 6)
❌ NO envía nada sin aprobación
```

**Prompt Focus**: Evaluación y priorización aplicando todas las reglas de negocio.

**Lógica de Scoring**:
```python
def calculate_fit_score(bu, campaign_context):
    score = 0.5  # Base
    reasons = []
    
    # FEI elegible: +20%
    if bu.company.fei_status == "Eligible":
        score += 0.20
        reasons.append("Elegible FEI")
    
    # Key person identificado: +15%
    if bu.has_key_person:
        score += 0.15
        reasons.append("Key person identificado")
    
    # Sector matching: +15%
    if bu.sector in campaign_context.affected_sectors:
        score += 0.15
        reasons.append(f"Sector afectado: {bu.sector}")
    
    # País matching: +10%
    if bu.country in campaign_context.affected_countries:
        score += 0.10
        reasons.append(f"Opera en {bu.country}")
    
    # Datos financieros completos: +10%
    if bu.company.has_financials:
        score += 0.10
        reasons.append("Datos financieros completos")
    
    # Engagement previo positivo: +10%
    if bu.company.previous_engagement == "positive":
        score += 0.10
        reasons.append("Engagement previo positivo")
    
    return min(score, 1.0), reasons
```

---

#### 7.3.6 Agente 6: REDACTOR DE MENSAJES ⭐ (Crítico)

| Atributo | Especificación |
|----------|----------------|
| **Misión** | Escribir emails hiper-personalizados de alta calidad |
| **Input** | Target + contexto campaña + info empresa |
| **Output** | Subject + Body personalizado |
| **LLM** | Claude (el mejor en escritura en español) |
| **Tablas** | `Campaign_Targets` |

**Responsabilidades ÚNICAS**:
```
✅ Redactar asunto personalizado (mencionar empresa)
✅ Escribir cuerpo (máximo 150 palabras)
✅ Mencionar algo ESPECÍFICO de la empresa
✅ Conectar trigger con situación de la empresa
✅ Adaptar producto según FEI status
✅ Incluir propuesta de valor clara
✅ CTA: reunión de 15 minutos
✅ Tono: profesional pero cercano
✅ NO parecer generado por IA
✅ Idioma: Español formal

❌ NO decide a quién enviar (eso es Agente 5)
❌ NO envía sin aprobación
```

**Prompt Focus**: Redacción de calidad con personalización real.

**Template de Mensaje**:
```markdown
## Estructura del Email

ASUNTO: [Algo específico de la empresa] + [Oportunidad relacionada con trigger]
Ejemplo: "Refinanciación para [Empresa] tras bajada tipos BCE"

CUERPO (máx 150 palabras):

Párrafo 1 (1-2 frases):
- Algo específico de la empresa (noticia, certificación, proyecto)
- Muestra que has investigado

Párrafo 2 (2-3 frases):
- Conecta el trigger de mercado con su situación
- Propuesta de valor clara
- Si FEI elegible: mencionar garantía europea

Párrafo 3 (1 frase):
- CTA claro: "¿Tienes 15 minutos esta semana para una llamada?"

Cierre:
- Saludos,
- [Firma del comercial]
```

**Ejemplo Real**:
```
Asunto: Financiación con garantía europea para SolarTech - Oportunidad post-BCE

Hola María,

He visto que SolarTech ha completado el parque solar de Almería de 50MW. 
Enhorabuena por el proyecto.

Con la reciente bajada de tipos del BCE, es un momento óptimo para empresas 
del sector renovable para refinanciar o acceder a nueva financiación. En 
Alter-5 tenemos acceso a líneas con garantía del Fondo Europeo de Inversiones, 
con condiciones especialmente favorables para empresas con vuestra certificación 
ISO 14001.

¿Tienes 15 minutos esta semana para una llamada rápida?

Saludos,
Carlos García
Alter-5
```

---

## 8. Flujos de Trabajo

### 8.1 Flujo 1: Originar Empresas Nuevas

```
┌────────────────────────────────────────────────────────────────────────────┐
│  FLUJO: ORIGINAR EMPRESAS NUEVAS                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Usuario: "Busca empresas de renovables en Andalucía con >50 empleados"    │
│                                                                             │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  1. BUSCADOR    │                                        │
│                 │    EMPRESAS     │                                        │
│                 │                 │                                        │
│                 │  • Busca en web │                                        │
│                 │  • Deduplica    │                                        │
│                 │  • Crea en AT   │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          │ Lista de 25 empresas nuevas                     │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │ 2. ENRIQUECEDOR │                                        │
│                 │     DATOS       │                                        │
│                 │                 │                                        │
│                 │  • Completa     │                                        │
│                 │  • Financieros  │                                        │
│                 │  • Contactos    │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          │ Empresas enriquecidas                           │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  3. EVALUADOR   │                                        │
│                 │      FEI        │                                        │
│                 │                 │                                        │
│                 │  • Busca certs  │                                        │
│                 │  • Evalúa 1.1-6 │                                        │
│                 │  • FEI_Status   │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                                                                             │
│  OUTPUT: 25 empresas con datos completos + FEI_Status evaluado             │
│          12 elegibles FEI, 13 no elegibles                                 │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Flujo 2: Cualificar Empresas Existentes

```
┌────────────────────────────────────────────────────────────────────────────┐
│  FLUJO: CUALIFICAR EMPRESAS EXISTENTES                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Usuario: "Evalúa elegibilidad FEI de empresas con FEI_Status='Unknown'"   │
│                                                                             │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │ 2. ENRIQUECEDOR │  ← Solo si faltan datos                │
│                 │     DATOS       │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  3. EVALUADOR   │                                        │
│                 │      FEI        │                                        │
│                 │                 │                                        │
│                 │  Para cada emp: │                                        │
│                 │  • Busca certs  │                                        │
│                 │  • Evalúa       │                                        │
│                 │  • Actualiza    │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                                                                             │
│  OUTPUT: 200 empresas evaluadas                                            │
│          85 Eligible, 95 Not_Eligible, 20 Pending_Review                   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Flujo 3: Crear Campaña desde Trigger de Mercado

```
┌────────────────────────────────────────────────────────────────────────────┐
│  FLUJO: CREAR CAMPAÑA DESDE TRIGGER                                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Usuario: "El BCE ha bajado tipos 0.25%. Crea campaña para industriales"   │
│                                                                             │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │ 4. ANALIZADOR   │                                        │
│                 │    CONTEXTO     │                                        │
│                 │                 │                                        │
│                 │  • Busca news   │                                        │
│                 │  • Analiza      │                                        │
│                 │  • Market_Ctx   │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          │ Contexto estructurado                           │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  5. SELECTOR    │                                        │
│                 │    TARGETS      │                                        │
│                 │                 │                                        │
│                 │  • Filtra BUs   │                                        │
│                 │  • Cooling-off  │                                        │
│                 │  • Scoring      │                                        │
│                 │  • Top 20       │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          │ Lista de 20 targets propuestos                  │
│                          │                                                  │
│                          ▼                                                  │
│            ┌─────────────────────────────┐                                 │
│            │   ¿USUARIO APRUEBA LISTA?   │                                 │
│            └─────────────┬───────────────┘                                 │
│                          │                                                  │
│                   [Sí, con ajustes]                                        │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  6. REDACTOR    │                                        │
│                 │    MENSAJES     │                                        │
│                 │                 │                                        │
│                 │  Para cada:     │                                        │
│                 │  • Subject      │                                        │
│                 │  • Body 150w    │                                        │
│                 │  • FEI mention  │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          │ 20 emails personalizados                        │
│                          │                                                  │
│                          ▼                                                  │
│            ┌─────────────────────────────┐                                 │
│            │  CAMPAÑA LISTA EN AIRTABLE  │                                 │
│            │  Status: "Pending_Review"   │                                 │
│            └─────────────────────────────┘                                 │
│                                                                             │
│  OUTPUT: 1 Origination_Campaign + 20 Campaign_Targets con mensajes         │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Flujo 4: Crear Campaña para Empresas Específicas

```
┌────────────────────────────────────────────────────────────────────────────┐
│  FLUJO: CAMPAÑA PARA EMPRESAS ESPECÍFICAS                                   │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Usuario: "Quiero contactar a SolarTech, WindPower y GreenEnergy"          │
│                                                                             │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │ 4. ANALIZADOR   │                                        │
│                 │    CONTEXTO     │                                        │
│                 │                 │                                        │
│                 │  • Busca news   │                                        │
│                 │    de cada emp  │                                        │
│                 │  • Últimas publ │                                        │
│                 │  • Market_Ctx   │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  5. SELECTOR    │  ← Valida cooling-off y BU activa     │
│                 │    TARGETS      │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                 ┌─────────────────┐                                        │
│                 │  6. REDACTOR    │                                        │
│                 │    MENSAJES     │                                        │
│                 │                 │                                        │
│                 │  • Personaliza  │                                        │
│                 │    con contexto │                                        │
│                 │    específico   │                                        │
│                 └────────┬────────┘                                        │
│                          │                                                  │
│                          ▼                                                  │
│                                                                             │
│  OUTPUT: 3 Campaign_Targets ultra-personalizados                           │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Reglas de Negocio

### 9.1 Reglas de Contacto

| Regla | Valor | Descripción | Consecuencia si se viola |
|-------|-------|-------------|--------------------------|
| **Cooling-off** | 90 días | No contactar empresa contactada recientemente | Ser percibido como spam |
| **Max targets/campaña** | 30 | Límite de targets por campaña | Pérdida de personalización |
| **Min fit score** | 60% | Score mínimo para incluir | Targets irrelevantes |
| **Prioridad FEI** | Siempre | Priorizar empresas FEI elegibles | Perder margen |
| **Aprobación humana** | Siempre | Antes de crear/enviar | Errores no detectados |

### 9.2 Reglas de Mensajes

| Regla | Especificación |
|-------|----------------|
| **Longitud** | Máximo 150 palabras |
| **Personalización** | DEBE mencionar algo específico de la empresa |
| **Conexión** | DEBE conectar trigger con situación de empresa |
| **Producto** | DEBE proponer producto adecuado (FEI si elegible) |
| **CTA** | DEBE incluir propuesta de reunión de 15 min |
| **Tono** | Español formal pero cercano |
| **Detección IA** | NO debe parecer generado por IA |

### 9.3 Reglas de Priorización (Orden)

1. **Key Person identificado** (+15% score)
2. **FEI elegible** (+20% score)
3. **Datos financieros completos** (+10% score)
4. **Engagement previo positivo** (+10% score)
5. **Sector matching con trigger** (+15% score)
6. **País matching** (+10% score)

### 9.4 Reglas de Deduplicación

| Escenario | Acción |
|-----------|--------|
| Mismo nombre exacto | Rechazar |
| Mismo dominio web | Rechazar |
| Nombre muy similar (>90% similitud) | Revisar manualmente |
| Mismo CIF/NIF | Rechazar |

### 9.5 Reglas de Evaluación FEI

| Regla | Detalle |
|-------|---------|
| **Validez premios** | Solo últimos 3 años |
| **Validez certificados** | Según validez de cada tipo |
| **Revenue threshold** | ≥90% para criterio 1.4 |
| **Múltiples criterios** | Registrar todos los cumplidos |
| **Confidence** | Indicar siempre nivel de confianza |
| **Pending_Review** | Si hay duda, marcar para revisión manual |

---

## 10. Stack Tecnológico

### 10.1 Resumen del Stack

| Capa | Tecnología | Versión | Propósito |
|------|------------|---------|-----------|
| **Runtime** | Python | 3.11+ | Lenguaje principal |
| **LLM Búsqueda** | Gemini 1.5 Flash | Latest | Google Search Grounding |
| **LLM Razonamiento** | Claude Sonnet/Opus | Latest | Análisis y redacción |
| **Validación** | Pydantic | 2.0+ | Type safety |
| **Base de datos** | Airtable | - | Hub de datos |
| **Cliente Airtable** | PyAirtable | 2.0+ | API wrapper |
| **HTTP** | httpx | 0.26+ | Async HTTP |
| **Retry** | Tenacity | 8.0+ | Reintentos |
| **CLI** | Typer | 0.9+ | Interfaz CLI |
| **Logging** | Structlog | 24.0+ | Logs estructurados |
| **IDE** | Cursor | Latest | Desarrollo AI-first |

### 10.2 Justificación de Elecciones

| Decisión | Alternativas | Justificación |
|----------|--------------|---------------|
| **Python** | Node.js, Go | Ecosistema IA maduro, PyAirtable |
| **Gemini para búsqueda** | Perplexity, Tavily | Google Search Grounding nativo, gratis |
| **Claude para razonamiento** | GPT-4, Gemini Pro | Superior en español y análisis |
| **Airtable** | Supabase, Notion | Ya en uso, MCP disponible, flexible |
| **Sin Make/n8n** | Make, n8n | Preferir código propio con LangGraph |

### 10.3 APIs y Servicios

| Servicio | Uso | Autenticación | Límites | Coste |
|----------|-----|---------------|---------|-------|
| **Google AI Studio** | Gemini API | API Key | 1500 req/día | Gratis |
| **Anthropic** | Claude API | API Key | Según plan | ~€20/mes |
| **Airtable** | Base de datos | PAT | 5 req/seg | Ya contratado |
| **Mailchimp** | Email campaigns | API Key | 10 req/seg | Ya contratado |

### 10.4 Estructura del Proyecto

```
alter5-origination/
├── pyproject.toml              # Dependencias
├── .env / .env.example         # Variables de entorno
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py             # Pydantic Settings
│   ├── airtable_schema.py      # IDs de tablas y campos
│   └── prompts/                # System prompts por agente
│       ├── buscador.md
│       ├── enriquecedor.md
│       ├── evaluador_fei.md
│       ├── analizador.md
│       ├── selector.md
│       └── redactor.md
│
├── core/
│   ├── __init__.py
│   ├── models.py               # Pydantic models
│   ├── airtable_client.py      # Wrapper con retry
│   └── fei_evaluator.py        # Lógica evaluación FEI
│
├── agents/
│   ├── __init__.py
│   ├── buscador.py             # Agente 1
│   ├── enriquecedor.py         # Agente 2
│   ├── evaluador_fei.py        # Agente 3
│   ├── analizador.py           # Agente 4
│   ├── selector.py             # Agente 5
│   └── redactor.py             # Agente 6
│
├── integrations/
│   ├── __init__.py
│   ├── gemini.py
│   ├── claude.py
│   └── mailchimp.py
│
├── cli/
│   ├── __init__.py
│   └── main.py                 # CLI con Typer
│
└── tests/
    ├── __init__.py
    ├── test_evaluador_fei.py
    ├── test_selector.py
    └── fixtures/
```

---

## 11. Estructura de Datos

### 11.1 Tablas de Airtable

| Grupo | Tabla | Propósito |
|-------|-------|-----------|
| **Stakeholders** | `Stakeholders_Companies` | Empresas |
| | `Stakeholders_Business_Units` | Unidades de negocio |
| | `Stakeholders_Contacts` | Contactos |
| | `Stakeholders_Companies_Financials` | Datos financieros |
| **Origination** | `Origination_Campaigns` | Campañas |
| | `Campaign_Targets` | Targets con mensajes |
| | `Market_Context` | Contexto de mercado |
| **Config** | `Config_Certificates` | Certificaciones conocidas |
| | `Config_Activities` | Actividades GICS |
| | `Config_Countries` | Países |
| | `Config_Products` | Productos Alter-5 |
| **Nueva** | `Company_Certificates` | Certificaciones por empresa |

### 11.2 Campos FEI en `Stakeholders_Companies`

| Campo | Tipo | Valores | Descripción |
|-------|------|---------|-------------|
| `FEI_Status` | Single Select | Unknown, Pending_Review, Eligible, Not_Eligible, Partially_Eligible, Expired | Estado evaluación |
| `FEI_Criteria_Met` | Multi Select | 1.1_Cleantech_Prize, 1.2_Clean_Energy_Patent, 1.3_Eco_Label, 1.4_Green_Business_90, 1.5_Green_Business_Model, 1.6_Environmental_Certificate | Criterios cumplidos |
| `FEI_Confidence` | Percent | 0-100% | Confianza evaluación |
| `FEI_Last_Check` | Date | - | Última evaluación |
| `FEI_Notes` | Long Text | - | Notas |

### 11.3 Documentación Completa

Ver: `B.Project_Context/B.1.ContextoGeneral/Origination_Campaigns_Full_Database_COMPLETE.md`

---

## 12. Restricciones y Consideraciones

### 12.1 Restricciones Técnicas

| Restricción | Detalle | Mitigación |
|-------------|---------|------------|
| **Desarrollador único** | Una persona + IA | Arquitectura simple, modular |
| **Presupuesto limitado** | ~€50/mes fase validación | APIs gratis donde posible |
| **MCP limitaciones** | 1 registro a la vez | Batch via Python para volumen |
| **Airtable límites** | 50K registros, 5 req/seg | Migrar a Supabase si necesario |
| **Sin Make/n8n** | Código propio | Python + LangGraph |

### 12.2 Requisitos No Negociables

1. ✅ **Calidad de datos**: Solo datos reales y verificables
2. ✅ **Personalización**: Cada mensaje único y relevante
3. ✅ **No spam**: Solo contactar empresas relevantes
4. ✅ **Cooling-off**: Respetar 90 días
5. ✅ **Trazabilidad**: Saber origen de cada dato
6. ✅ **Escalabilidad**: Arquitectura multi-país
7. ✅ **Robustez**: Sistema fiable y mantenible
8. ✅ **Precisión FEI**: ≥90% accuracy

### 12.3 Enfoque de Desarrollo

| Principio | Descripción |
|-----------|-------------|
| **AI-First** | Usar Cursor, Claude Code para desarrollo |
| **Iterativo** | MVP → Validar → Mejorar |
| **Value-first** | Aportar valor lo antes posible |
| **State of the art** | Tecnologías modernas probadas |
| **Mejora continua** | Implementar evals para optimizar |
| **Responsabilidad única** | Un agente = una misión |

### 12.4 Consideraciones de Negocio

- **Historial emails**: Usar para personalización futura
- **Acuerdo FEI**: Maximizar identificación elegibles
- **Sectores prioritarios**: Renovables > Real Estate > Defensa
- **Multi-producto**: Adaptar oferta a cada empresa
- **Relaciones previas**: No perder contexto histórico

---

## 13. Plan de Implementación

### 13.1 Resumen de Sprints

| Sprint | Duración | Agentes | Objetivo |
|--------|----------|---------|----------|
| **0** | 3 días | - | Setup proyecto + BBDD |
| **1** | 2 semanas | 2 + 3 | Cualificación FEI funcionando |
| **2** | 2 semanas | 4 + 5 + 6 | Estratega MVP + primera campaña |
| **3** | 2 semanas | 1 | Originador + pipeline completo |
| **4** | 2 semanas | - | Integración email + análisis |

### 13.2 Detalle de Entregables

#### Sprint 0: Setup (3 días)
- Proyecto Python con estructura
- APIs configuradas (Gemini, Claude)
- Tablas nuevas en Airtable
- Config_Certificates poblada (17 certs)
- Config_Activities poblada (14 actividades)
- Claude Project + MCP configurado

#### Sprint 1: Cualificación (Semanas 1-2)
- Agente 2: Enriquecedor funcionando
- Agente 3: Evaluador FEI con ≥90% precisión
- CLI para evaluación batch
- 200+ empresas evaluadas

#### Sprint 2: Campañas (Semanas 3-4)
- Agente 4: Analizador de contexto
- Agente 5: Selector de targets
- Agente 6: Redactor de mensajes
- **Primera campaña real enviada**

#### Sprint 3: Originación (Semanas 5-6)
- Agente 1: Buscador de empresas
- Pipeline completo integrado
- 100+ empresas nuevas originadas

#### Sprint 4: Integración (Semanas 7-8)
- Integración Mailchimp
- Tracking de métricas
- Análisis de resultados
- Documentación completa
- **Presentación a CEOs**

---

## 14. Métricas de Éxito

### 14.1 KPIs de Validación (8 semanas)

| Métrica | Baseline | Target | Método de medición |
|---------|----------|--------|-------------------|
| Tiempo crear campaña | 4-8h | ≤45 min | Cronometrar |
| Precisión FEI | ~50% | ≥90% | Verificación manual 50 empresas |
| Empresas FEI identificadas | 50/mes | 200+/mes | Contador Airtable |
| Tasa apertura | 15% | ≥25% | Mailchimp stats |
| Tasa respuesta | 2-3% | ≥8% | Contador manual |
| Reuniones conseguidas | 2-3/mes | ≥8/mes | CRM |
| Campañas simultáneas | 1-2 | ≥4 | Contador Airtable |

### 14.2 Checklist de Validación

- [ ] Sistema de 6 agentes operativo
- [ ] Evaluación FEI ≥90% precisión (verificar 50 empresas)
- [ ] ≥3 campañas enviadas con sistema
- [ ] ≥1 reunión conseguida con campaña del sistema
- [ ] Equipo comercial usando el sistema sin ayuda técnica
- [ ] Documentación completa
- [ ] Decisión de CEOs: continuar/escalar

---

## 15. Referencias

### 15.1 Documentos del Proyecto

| Documento | Ubicación | Uso |
|-----------|-----------|-----|
| **PRD MVP** | `C.Deliverables/PRD_MVP_Originacion.md` | Requisitos detallados |
| **Tareas Desarrollo** | `C.Deliverables/Origination_Development_Tasks.md` | Implementación código |
| **Tareas BBDD** | `C.Deliverables/Origination_DB_Tasks.md` | Configuración Airtable |
| **Schema BBDD** | `B.Project_Context/B.1.ContextoGeneral/Origination_Campaigns_Full_Database_COMPLETE.md` | Estructura tablas |

### 15.2 URLs Externas

| Recurso | URL |
|---------|-----|
| **Green Checker FEI** | https://alter-5-es.greenchecker.eib-group.org/eif-sustainable/1.3/sustainable-enterprise/categories |
| **Alter-5** | https://alter-5.com |
| **Guía de Evals** | https://hamel.dev/blog/posts/evals-faq/ |

---

## 16. Instrucciones para Agentes de IA

### 16.1 Al Usar Este Documento

1. **Lee el documento completo** antes de actuar
2. **Identifica tu rol** (qué agente eres o qué tarea realizas)
3. **Respeta las reglas de negocio** sin excepción
4. **Verifica elegibilidad FEI** siempre que sea relevante
5. **Consulta documentación específica** según necesidad
6. **Pide aprobación humana** antes de crear registros o enviar

### 16.2 Prioridades Absolutas

1. **Calidad sobre cantidad**: Mejor 10 targets buenos que 50 mediocres
2. **FEI primero**: Siempre evaluar y priorizar elegibilidad
3. **Personalización real**: Cada mensaje DEBE ser único
4. **Transparencia**: Explicar razonamiento de decisiones
5. **Verificabilidad**: Solo datos que se puedan verificar

### 16.3 Qué NUNCA Hacer

- ❌ **Inventar datos** de empresas
- ❌ **Contactar empresas** en cooling-off (<90 días)
- ❌ **Generar mensajes genéricos** sin personalización real
- ❌ **Crear registros sin deduplicar** primero
- ❌ **Ignorar criterios FEI** en evaluación
- ❌ **Actuar sin aprobación** cuando se requiere
- ❌ **Superar límites** (30 targets, 150 palabras)
- ❌ **Usar empresas ya en campañas activas**

### 16.4 Protocolo de Errores

Si encuentras un problema:
1. **Documenta** el error claramente
2. **No inventes** una solución sin validar
3. **Marca como Pending_Review** si hay duda
4. **Informa al usuario** del problema
5. **Continúa con otros registros** si es posible

### 16.5 Formato de Output

Siempre estructurar respuestas con:
- **Resumen** de lo realizado
- **Métricas** (cuántos registros, % éxito)
- **Problemas** encontrados (si los hay)
- **Siguiente paso** recomendado

---

## Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 26-12-2025 | Versión inicial (Main_Promt.md) |
| 2.0 | 29-12-2025 | Reestructuración completa (Main_Promt_2.md) |
| **3.0** | **29-12-2025** | **Arquitectura 6 agentes, versión final (Main_Promt_Origination.md)** |

---

*Este documento es la FUENTE DE VERDAD para el proyecto de automatización de originación de Alter-5. Todo PRD, tarea de desarrollo o agente de IA debe basarse en este documento. Mantener actualizado conforme evolucione el proyecto.*

