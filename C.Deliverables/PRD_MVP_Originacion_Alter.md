# PRD: MVP Motor de Automatización de Originación Alter-5

**Versión**: 1.0  
**Fecha**: 2 Enero 2026  
**Autor**: CPO Expert AI Assistant  
**Revisores**: CEO Alter-5, CTO, Equipo Comercial  
**Estado**: Draft

---

## Índice

1. [Executive Summary](#1-executive-summary)
2. [Contexto y Justificación](#2-contexto-y-justificación)
3. [Definición del Usuario](#3-definición-del-usuario)
4. [Requisitos Funcionales](#4-requisitos-funcionales)
5. [Requisitos No Funcionales](#5-requisitos-no-funcionales)
6. [Especificaciones Técnicas](#6-especificaciones-técnicas)
7. [Diseño y UX](#7-diseño-y-ux)
8. [Plan de Implementación](#8-plan-de-implementación)
9. [Testing y QA](#9-testing-y-qa)
10. [Métricas y Monitoreo](#10-métricas-y-monitoreo)
11. [Go-to-Market](#11-go-to-market)

---

## 1. Executive Summary

### 1.1 Problema a Resolver

Alter-5 es una empresa española de intermediación financiera B2B que conecta empresas (promotores) con financiadores (inversores). Actualmente, el equipo comercial dedica **>70% de su tiempo a tareas operativas** en lugar de cerrar deals:

| Problema | Impacto |
|----------|---------|
| Búsqueda manual de empresas | 4-8 horas por campaña |
| Cualificación sin datos financieros | ~60% datos incompletos |
| Identificación FEI manual | Oportunidades perdidas, ~50% precisión |
| Personalización emails | 30 min/email, no escala |
| Segmentación básica | Tasa respuesta 2-3% |

Además, la empresa tiene un **acuerdo exclusivo con el Fondo Europeo de Inversiones (FEI)** que permite ofrecer financiación con garantía europea, pero la identificación manual de empresas elegibles tiene una precisión de solo ~50%.

### 1.2 Propuesta de Valor

Implementar un **Motor de Automatización de Originación** basado en IA con 6 agentes especializados que:

1. **Identifica** empresas que potencialmente necesitan financiación mediante web scraping inteligente
2. **Cualifica** empresas con datos verificables (financieros, contactos, certificaciones)
3. **Evalúa elegibilidad FEI** con alta precisión (≥90%) aplicando los 6 criterios Green Checker
4. **Genera campañas** hiper-personalizadas basadas en triggers de mercado
5. **Maximiza** tasa de respuesta mediante micro-segmentación y mensajes contextualizados

**Diferenciador único**: Automatización de evaluación FEI que maximiza el uso del acuerdo con garantía europea de €50M (€200M en negociación).

### 1.3 Métricas de Éxito

| Métrica | Baseline | Target MVP | Target 6 meses |
|---------|----------|------------|----------------|
| Tiempo crear campaña | 4-8h | **≤45 min** | ≤30 min |
| Precisión evaluación FEI | ~50% | **≥90%** | ≥95% |
| Empresas FEI identificadas/mes | ~50 | **200+** | 500+ |
| Tasa de apertura | 15% | **≥25%** | ≥35% |
| Tasa de respuesta | 2-3% | **≥8%** | ≥12% |
| Reuniones conseguidas/mes | 2-3 | **≥8** | ≥15 |
| Campañas simultáneas | 1-2 | **≥4** | ≥10 |

### 1.4 Inversión Requerida

| Recurso | Detalle |
|---------|---------|
| **Desarrollo** | 8 semanas (4 sprints de 2 semanas) |
| **Equipo** | 1 desarrollador + IA (Cursor/Claude) |
| **Presupuesto APIs** | ~€50/mes (Anthropic ~€20, resto gratis) |
| **Infraestructura** | Airtable (ya contratado), Mailchimp (ya contratado) |

---

## 2. Contexto y Justificación

### 2.1 Análisis del Mercado

**Alter-5 opera en el mercado de intermediación financiera B2B:**

| Atributo | Valor |
|----------|-------|
| **Clientes Promotores** | Pymes y mid-caps (10-500 empleados) |
| **Ticket típico** | €2M-50M |
| **Mercados actuales** | España, Portugal |
| **Mercados corto plazo** | UK, Francia, Alemania, Italia |
| **Sectores prioritarios** | Renovables, Real Estate, Defensa, Industriales, Tecnología |

**Competidores**: La mayoría de intermediarios financieros realizan originación de forma manual. La automatización con IA y la capacidad de evaluar elegibilidad FEI de forma sistemática representa una ventaja competitiva significativa.

### 2.2 Diferenciador FEI

El **Fondo Europeo de Inversiones (FEI)** del grupo BEI ofrece garantías europeas para financiación:

| Característica | Detalle |
|----------------|---------|
| Capacidad actual | €50M |
| En negociación | €200M |
| Beneficios | Menor tipo de interés, mayor plazo, acceso a capital |
| Exclusividad | Pocos intermediarios tienen este acuerdo |

**Criterios de Elegibilidad (Green Checker)**:

Una empresa es elegible si cumple **AL MENOS UNO** de estos criterios:

| Código | Criterio | Automatizable |
|--------|----------|---------------|
| **1.1** | Premio Cleantech (últimos 3 años) | ✅ Sí |
| **1.2** | Patente Clean Energy (últimos 3 años) | ⚠️ Parcial |
| **1.3** | Eco-Label EU/Nacional/Internacional | ✅ Sí |
| **1.4** | Green Business ≥90% revenue | ✅ Sí |
| **1.5** | Green Business Model con impacto verificable | ❌ No |
| **1.6** | Certificado Ambiental válido | ✅ Sí |

### 2.3 Alineación Estratégica

Este proyecto se alinea directamente con los objetivos de Alter-5:

- **Escalar operaciones** sin aumentar headcount
- **Maximizar uso del acuerdo FEI** (mayor margen)
- **Expandir geográficamente** de forma eficiente
- **Mejorar tasa de conversión** mediante personalización

### 2.4 Riesgos de No Hacer

| Riesgo | Consecuencia |
|--------|--------------|
| Seguir con proceso manual | Equipo comercial saturado en tareas operativas |
| No identificar empresas FEI | Pérdida de margen y oportunidades exclusivas |
| Mensajes genéricos | Tasa de respuesta estancada en 2-3% |
| Sin escalabilidad | Imposible expandir a nuevos mercados |

---

## 3. Definición del Usuario

### 3.1 Personas Objetivo

#### Persona 1: Carlos García - Director Comercial

| Atributo | Detalle |
|----------|---------|
| **Rol** | Director Comercial Alter-5 |
| **Responsabilidades** | Cerrar deals, gestionar pipeline, relaciones con promotores |
| **Pain Points** | Dedica >70% tiempo a tareas operativas, emails genéricos, pierde oportunidades FEI |
| **Objetivos** | Más reuniones, mejor tasa de cierre, identificar empresas FEI |
| **Uso del sistema** | Claude Desktop + MCP para crear campañas, consultar datos |
| **Frecuencia** | Diaria |

#### Persona 2: Miguel Rodríguez - CEO

| Atributo | Detalle |
|----------|---------|
| **Rol** | CEO Alter-5 |
| **Responsabilidades** | Estrategia, decisiones de inversión, relación con FEI |
| **Pain Points** | Falta visibilidad del pipeline, uso subóptimo del acuerdo FEI |
| **Objetivos** | Escalar negocio, maximizar uso FEI, expandir geográficamente |
| **Uso del sistema** | Dashboards Airtable, reportes de campañas |
| **Frecuencia** | Semanal |

#### Persona 3: Ana López - Desarrolladora

| Atributo | Detalle |
|----------|---------|
| **Rol** | Desarrolladora / Administradora del sistema |
| **Responsabilidades** | Mantener el sistema, ejecutar batch processing, debugging |
| **Pain Points** | Sistema actual es manual, sin trazabilidad |
| **Objetivos** | Sistema mantenible, logs claros, fácil de iterar |
| **Uso del sistema** | CLI Python/Typer, acceso directo a Airtable |
| **Frecuencia** | Según necesidad |

### 3.2 User Journey: Crear Campaña desde Trigger

```
1. TRIGGER
   Carlos lee que el BCE ha bajado tipos 0.25%
   
2. INTERACCIÓN
   Abre Claude Desktop y escribe:
   "El BCE ha bajado tipos. Crea campaña para industriales en España"
   
3. ANÁLISIS (Agentes 4)
   Sistema analiza el trigger:
   - Busca noticias relacionadas
   - Identifica sectores afectados
   - Determina urgencia y ángulos
   
4. SELECCIÓN (Agente 5)
   Sistema selecciona targets:
   - Filtra por sector industrial + España
   - Aplica cooling-off (90 días)
   - Prioriza FEI elegibles
   - Propone 20 targets con justificación
   
5. APROBACIÓN
   Carlos revisa lista, ajusta si necesario, aprueba
   
6. REDACCIÓN (Agente 6)
   Sistema genera emails personalizados:
   - Subject específico por empresa
   - Body máx 150 palabras
   - Menciona algo específico de cada empresa
   - CTA: reunión 15 min
   
7. REVISIÓN FINAL
   Carlos revisa mensajes, hace ajustes menores
   
8. LISTO PARA ENVÍO
   Campaña lista en Airtable, status "Pending_Review"
```

### 3.3 Casos de Uso Principales

| # | Caso de Uso | Actor | Frecuencia |
|---|-------------|-------|------------|
| **CU-01** | Originar empresas nuevas por criterio | Comercial | Semanal |
| **CU-02** | Cualificar empresas existentes | Comercial/Sistema | Diaria |
| **CU-03** | Evaluar elegibilidad FEI batch | Sistema | Diaria |
| **CU-04** | Crear campaña desde trigger de mercado | Comercial | 2-3x/semana |
| **CU-05** | Crear campaña para empresas específicas | Comercial | Semanal |
| **CU-06** | Consultar estado FEI de empresa | Comercial | Ad-hoc |

---

## 4. Requisitos Funcionales

### 4.1 Arquitectura de 6 Agentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MOTOR DE ORIGINACIÓN ALTER-5                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ORIGINACIÓN          CUALIFICACIÓN           CAMPAÑAS                 │
│   ┌──────────┐      ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│   │ BUSCADOR │      │ENRIQUECE.│  │EVALUADOR │  │ANALIZADOR│           │
│   │ EMPRESAS │      │  DATOS   │  │   FEI    │  │ CONTEXTO │           │
│   │  (Ag.1)  │      │  (Ag.2)  │  │  (Ag.3)  │  │  (Ag.4)  │           │
│   └──────────┘      └──────────┘  └──────────┘  └──────────┘           │
│                                                  ┌──────────┐           │
│                                                  │ SELECTOR │           │
│                                                  │ TARGETS  │           │
│                                                  │  (Ag.5)  │           │
│                                                  └──────────┘           │
│                                                  ┌──────────┐           │
│                                                  │ REDACTOR │           │
│                                                  │ MENSAJES │           │
│                                                  │  (Ag.6)  │           │
│                                                  └──────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Agente 1: Buscador de Empresas

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Buscador_Empresas` |
| **Misión** | Encontrar empresas nuevas que cumplan criterios especificados |
| **LLM** | Gemini 1.5 Flash con Google Search Grounding |
| **Input** | Criterios de búsqueda (sector, país, tamaño, keywords) |
| **Output** | Lista de empresas con datos básicos en Airtable |
| **Tablas** | `Stakeholders_Companies`, `Stakeholders_Business_Units` |
| **Prioridad** | Alta |
| **Complejidad** | Media |

**Criterios de Aceptación:**

- **CA-1.1**: Dado que el usuario solicita "busca empresas de renovables en Andalucía con >50 empleados"
  - Cuando el agente ejecuta la búsqueda
  - Entonces retorna lista de empresas con: nombre, web, sector, ciudad, descripción
  
- **CA-1.2**: Dado que se encuentran empresas
  - Cuando se procesan los resultados
  - Entonces se verifica que las URLs son reales y accesibles
  
- **CA-1.3**: Dado que hay empresas encontradas
  - Cuando se insertan en Airtable
  - Entonces se deduplica contra BBDD existente (mismo nombre, dominio o CIF)
  
- **CA-1.4**: Dado que se crea una empresa nueva
  - Cuando se inserta en `Stakeholders_Companies`
  - Entonces se crea automáticamente Business Unit "Default" asociada

**Responsabilidades ÚNICAS:**
- ✅ Buscar empresas según criterios
- ✅ Extraer: nombre, web, sector, ciudad, descripción
- ✅ Verificar que URLs son reales
- ✅ Deduplicar contra BBDD existente
- ✅ Crear registros con Source="AI_Scraping"
- ❌ NO completa datos adicionales (eso es Agente 2)
- ❌ NO evalúa FEI (eso es Agente 3)

---

### 4.3 Agente 2: Enriquecedor de Datos

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Enriquecedor_Datos` |
| **Misión** | Completar información faltante de empresas |
| **LLM** | Gemini 1.5 Flash |
| **Input** | Empresa con datos básicos |
| **Output** | Empresa con datos enriquecidos + contactos |
| **Tablas** | `Stakeholders_Companies`, `Stakeholders_Companies_Financials`, `Stakeholders_Contacts` |
| **Prioridad** | Alta |
| **Complejidad** | Media |

**Criterios de Aceptación:**

- **CA-2.1**: Dada una empresa con datos básicos
  - Cuando el agente enriquece
  - Entonces completa: Num_Employees, Linkedin_URL, estructura corporativa
  
- **CA-2.2**: Dada una empresa
  - Cuando se buscan datos financieros
  - Entonces se guardan en `Stakeholders_Companies_Financials`: Year, Annual_Revenues, EBITDA, Net_Financial_Debt
  
- **CA-2.3**: Dada una empresa
  - Cuando se identifican key persons
  - Entonces se crean contactos en `Stakeholders_Contacts` con: nombre, rol, email, teléfono

**Responsabilidades ÚNICAS:**
- ✅ Completar: empleados, LinkedIn, estructura corporativa
- ✅ Buscar datos financieros (revenue, EBITDA, deuda)
- ✅ Identificar key persons (CEO, CFO, Director Financiero)
- ✅ Buscar emails y teléfonos de contactos
- ❌ NO busca certificaciones (eso es Agente 3)
- ❌ NO evalúa FEI (eso es Agente 3)

---

### 4.4 Agente 3: Evaluador FEI ⭐ (Crítico)

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Evaluador_FEI` |
| **Misión** | Determinar elegibilidad FEI con alta precisión (≥90%) |
| **LLM** | Claude (razonamiento) + Gemini (búsqueda certificaciones) |
| **Input** | Empresa + datos enriquecidos |
| **Output** | FEI_Status + FEI_Criteria_Met + FEI_Confidence |
| **Tablas** | `Stakeholders_Companies`, `Company_Certificates`, `Config_Certificates`, `Config_Activities` |
| **Prioridad** | 🔴 Máxima |
| **Complejidad** | Alta |

**Campos FEI en `Stakeholders_Companies`:**

| Campo | Tipo | Valores |
|-------|------|---------|
| `FEI_Status` | Single Select | `Unknown`, `Pending_Review`, `Eligible`, `Not_Eligible`, `Partially_Eligible`, `Expired` |
| `FEI_Criteria_Met` | Multi Select | `1.1_Cleantech_Prize`, `1.2_Clean_Energy_Patent`, `1.3_Eco_Label`, `1.4_Green_Business_90`, `1.5_Green_Business_Model`, `1.6_Environmental_Certificate` |
| `FEI_Confidence` | Percent | 0-100% |
| `FEI_Last_Check` | Date | Fecha última evaluación |
| `FEI_Notes` | Long Text | Notas y documentación |

**Criterios de Aceptación:**

- **CA-3.1**: Dada una empresa con certificación ISO 14001 válida
  - Cuando el agente evalúa
  - Entonces `FEI_Status` = "Eligible", `FEI_Criteria_Met` incluye "1.6_Environmental_Certificate"
  
- **CA-3.2**: Dada una empresa del sector solar con >90% revenue en renovables
  - Cuando el agente evalúa
  - Entonces `FEI_Status` = "Eligible", `FEI_Criteria_Met` incluye "1.4_Green_Business_90"
  
- **CA-3.3**: Dada una empresa sin criterios identificables
  - Cuando el agente evalúa
  - Entonces `FEI_Status` = "Not_Eligible", `FEI_Confidence` indica nivel de certeza
  
- **CA-3.4**: Dado que hay duda sobre elegibilidad
  - Cuando el agente no puede determinar con confianza
  - Entonces `FEI_Status` = "Pending_Review" para revisión manual
  
- **CA-3.5**: Dada la evaluación FEI
  - Cuando se completa
  - Entonces `FEI_Last_Check` se actualiza a fecha actual

**Certificaciones FEI Elegibles:**

| Tipo | Certificaciones |
|------|-----------------|
| **ISOs (1.6)** | ISO 14001, ISO 50001, ISO 14064, EMAS |
| **Eco-Labels (1.3)** | B Corp, EU Ecolabel, FSC, PEFC, Cradle to Cradle, LEED, BREEAM |
| **Premios (1.1)** | CDTI Neotec, Horizon Europe Grant, EIT Climate-KIC, EIT InnoEnergy, LIFE Programme |

**Responsabilidades ÚNICAS:**
- ✅ Buscar certificaciones (ISO 14001, B Corp, etc.)
- ✅ Buscar premios cleantech (CDTI, Horizon, EIT)
- ✅ Verificar actividad principal vs lista FEI
- ✅ Evaluar cada criterio (1.1 a 1.6)
- ✅ Determinar status: Eligible/Not_Eligible/Pending_Review/Unknown
- ✅ Calcular confidence score (0-100%)
- ✅ Guardar certificaciones en `Company_Certificates`
- ❌ NO selecciona targets (eso es Agente 5)
- ❌ NO genera mensajes (eso es Agente 6)

---

### 4.5 Agente 4: Analizador de Contexto

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Analizador_Contexto` |
| **Misión** | Analizar triggers de mercado y generar contexto estructurado |
| **LLM** | Gemini (búsqueda noticias) + Claude (análisis) |
| **Input** | Trigger de mercado o empresa específica |
| **Output** | Análisis estructurado en `Market_Context` |
| **Tablas** | `Market_Context` |
| **Prioridad** | Alta |
| **Complejidad** | Media |

**Criterios de Aceptación:**

- **CA-4.1**: Dado un trigger "BCE baja tipos 0.25%"
  - Cuando el agente analiza
  - Entonces crea registro en `Market_Context` con: Context_Title, Context_Type, Summary, Key_Implications
  
- **CA-4.2**: Dado un análisis de contexto
  - Cuando se completa
  - Entonces identifica: Affected_Sectors, Affected_Countries, Campaign_Potential (1-5)
  
- **CA-4.3**: Dado un trigger analizado
  - Cuando hay alto potencial de campaña
  - Entonces genera key_angles para personalización de mensajes

**Output Estructurado:**

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

### 4.6 Agente 5: Selector de Targets

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Selector_Targets` |
| **Misión** | Seleccionar las mejores Business Units para cada campaña |
| **LLM** | Claude (razonamiento) |
| **Input** | Contexto de campaña + pool de BUs disponibles |
| **Output** | Lista priorizada de targets con fit score |
| **Tablas** | `Stakeholders_Business_Units`, `Origination_Campaigns`, `Campaign_Targets` |
| **Prioridad** | Alta |
| **Complejidad** | Alta |

**Criterios de Aceptación:**

- **CA-5.1**: Dado un contexto de campaña
  - Cuando el agente selecciona targets
  - Entonces filtra BUs por criterios: sector, país, activo=true
  
- **CA-5.2**: Dada una BU contactada hace <90 días
  - Cuando se evalúa para campaña
  - Entonces se EXCLUYE (cooling-off obligatorio)
  
- **CA-5.3**: Dada una BU en campaña activa
  - Cuando se evalúa para nueva campaña
  - Entonces se EXCLUYE
  
- **CA-5.4**: Dada la selección de targets
  - Cuando se completa
  - Entonces NO excede 30 targets por campaña
  
- **CA-5.5**: Dado cada target seleccionado
  - Cuando se incluye en la lista
  - Entonces incluye: Fit_Score (0-100%), Selection_Justification

**Lógica de Scoring:**

| Factor | Peso | Descripción |
|--------|------|-------------|
| FEI Elegible | +20% | Empresa con FEI_Status="Eligible" |
| Key Person identificado | +15% | Tiene contacto CEO/CFO/Dir.Financiero |
| Sector matching | +15% | Sector en affected_sectors del trigger |
| País matching | +10% | País en affected_countries del trigger |
| Datos financieros completos | +10% | Tiene revenue, EBITDA, deuda |
| Engagement previo positivo | +10% | Historial de interacciones positivas |
| Base | 50% | Score base |

**Fit Score mínimo**: 60% para inclusión en campaña.

---

### 4.7 Agente 6: Redactor de Mensajes ⭐ (Crítico)

| Atributo | Especificación |
|----------|----------------|
| **ID** | `Redactor_Mensajes` |
| **Misión** | Escribir emails hiper-personalizados de alta calidad |
| **LLM** | Claude (el mejor en escritura en español) |
| **Input** | Target + contexto campaña + info empresa |
| **Output** | Subject + Body personalizado |
| **Tablas** | `Campaign_Targets` |
| **Prioridad** | 🔴 Máxima |
| **Complejidad** | Alta |

**Criterios de Aceptación:**

- **CA-6.1**: Dado un target con contexto
  - Cuando el agente redacta
  - Entonces genera `Personalized_Email_Subject` que menciona la empresa
  
- **CA-6.2**: Dado un email generado
  - Cuando se mide
  - Entonces el body NO excede 150 palabras
  
- **CA-6.3**: Dado un email generado
  - Cuando se revisa contenido
  - Entonces menciona algo ESPECÍFICO de la empresa (proyecto, noticia, certificación)
  
- **CA-6.4**: Dado un target con FEI_Status="Eligible"
  - Cuando se genera el mensaje
  - Entonces menciona la garantía europea como propuesta de valor
  
- **CA-6.5**: Dado cualquier email generado
  - Cuando se revisa
  - Entonces incluye CTA claro: "¿Tienes 15 minutos esta semana para una llamada?"

**Estructura del Email:**

```
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

**Ejemplo Real:**

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

### 4.8 Flujos de Trabajo

#### Flujo 1: Originar Empresas Nuevas

```
Usuario: "Busca empresas de renovables en Andalucía con >50 empleados"
                          │
                          ▼
                 ┌─────────────────┐
                 │  1. BUSCADOR    │  → Lista 25 empresas nuevas
                 │    EMPRESAS     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ 2. ENRIQUECEDOR │  → Empresas enriquecidas
                 │     DATOS       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  3. EVALUADOR   │  → FEI_Status evaluado
                 │      FEI        │
                 └─────────────────┘

OUTPUT: 25 empresas con datos completos
        12 elegibles FEI, 13 no elegibles
```

#### Flujo 2: Cualificar Empresas Existentes

```
Usuario: "Evalúa elegibilidad FEI de empresas con FEI_Status='Unknown'"
                          │
                          ▼
                 ┌─────────────────┐
                 │ 2. ENRIQUECEDOR │  ← Solo si faltan datos
                 │     DATOS       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  3. EVALUADOR   │
                 │      FEI        │
                 └─────────────────┘

OUTPUT: 200 empresas evaluadas
        85 Eligible, 95 Not_Eligible, 20 Pending_Review
```

#### Flujo 3: Crear Campaña desde Trigger de Mercado

```
Usuario: "El BCE ha bajado tipos 0.25%. Crea campaña para industriales"
                          │
                          ▼
                 ┌─────────────────┐
                 │ 4. ANALIZADOR   │  → Contexto estructurado
                 │    CONTEXTO     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  5. SELECTOR    │  → 20 targets propuestos
                 │    TARGETS      │
                 └────────┬────────┘
                          │
            ┌─────────────────────────────┐
            │   ¿USUARIO APRUEBA LISTA?   │
            └─────────────┬───────────────┘
                          │ [Sí, con ajustes]
                          ▼
                 ┌─────────────────┐
                 │  6. REDACTOR    │  → 20 emails personalizados
                 │    MENSAJES     │
                 └─────────────────┘

OUTPUT: 1 Origination_Campaign + 20 Campaign_Targets con mensajes
        Status: "Pending_Review"
```

#### Flujo 4: Crear Campaña para Empresas Específicas

```
Usuario: "Quiero contactar a SolarTech, WindPower y GreenEnergy"
                          │
                          ▼
                 ┌─────────────────┐
                 │ 4. ANALIZADOR   │  → Contexto específico por empresa
                 │    CONTEXTO     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  5. SELECTOR    │  ← Valida cooling-off y BU activa
                 │    TARGETS      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  6. REDACTOR    │  → Emails ultra-personalizados
                 │    MENSAJES     │
                 └─────────────────┘

OUTPUT: 3 Campaign_Targets ultra-personalizados
```

---

### 4.9 Reglas de Negocio

#### Reglas de Contacto

| Regla | Valor | Consecuencia si se viola |
|-------|-------|--------------------------|
| **Cooling-off** | 90 días | Ser percibido como spam |
| **Max targets/campaña** | 30 | Pérdida de personalización |
| **Min fit score** | 60% | Targets irrelevantes |
| **Prioridad FEI** | Siempre | Perder margen |
| **Aprobación humana** | Siempre antes de crear/enviar | Errores no detectados |

#### Reglas de Mensajes

| Regla | Especificación |
|-------|----------------|
| Longitud | Máximo 150 palabras |
| Personalización | DEBE mencionar algo específico de la empresa |
| Conexión | DEBE conectar trigger con situación de empresa |
| Producto | DEBE proponer producto adecuado (FEI si elegible) |
| CTA | DEBE incluir propuesta de reunión de 15 min |
| Tono | Español formal pero cercano |
| Detección IA | NO debe parecer generado por IA |

#### Reglas de Deduplicación

| Escenario | Acción |
|-----------|--------|
| Mismo nombre exacto | Rechazar |
| Mismo dominio web | Rechazar |
| Nombre muy similar (>90% similitud) | Revisar manualmente |
| Mismo CIF/NIF | Rechazar |

---

## 5. Requisitos No Funcionales

### 5.1 Performance

| Métrica | Especificación |
|---------|----------------|
| **Búsqueda empresas** | ≤30 seg por empresa |
| **Enriquecimiento** | ≤60 seg por empresa |
| **Evaluación FEI** | ≤45 seg por empresa |
| **Generación mensaje** | ≤30 seg por target |
| **Campaña completa (20 targets)** | ≤15 min total |

### 5.2 Escalabilidad

| Dimensión | MVP | 6 meses |
|-----------|-----|---------|
| Empresas en BBDD | 2.000 | 50.000 |
| Empresas procesadas/día | 100 | 500 |
| Campañas simultáneas | 4 | 10 |
| Países soportados | 2 (ES, PT) | 6 |

### 5.3 Disponibilidad

| Servicio | SLA |
|----------|-----|
| Airtable | 99.9% (garantizado por proveedor) |
| APIs LLM | Best effort (reintentos automáticos) |
| Sistema global | 95% durante horario laboral |

### 5.4 Seguridad

| Aspecto | Implementación |
|---------|----------------|
| **API Keys** | Variables de entorno, nunca en código |
| **Datos empresas** | Solo en Airtable (ya cumple GDPR) |
| **Logs** | Sin datos sensibles (PIIs) |
| **Acceso** | PAT de Airtable con permisos mínimos |

### 5.5 Trazabilidad

| Requisito | Implementación |
|-----------|----------------|
| Origen de datos | Campo `Source` en cada registro |
| Extracciones | Tabla `Source_Extractions` con trazabilidad completa |
| Agente usado | Campo `AI_Agent_Used` en extracciones |
| Modificaciones manuales | Campo `Manual_Override` + `Override_Notes` |

### 5.6 Integración

| Sistema | Método | Estado |
|---------|--------|--------|
| **Airtable** | PyAirtable 2.0+ | Obligatorio |
| **Gemini** | Google AI SDK | Obligatorio |
| **Claude** | Anthropic SDK | Obligatorio |
| **Mailchimp** | API REST | Fase 2 |
| **Apollo.io** | API REST | Futuro |
| **SABI** | Manual/API | Futuro |

---

## 6. Especificaciones Técnicas

### 6.1 Stack Tecnológico

| Capa | Tecnología | Versión | Justificación |
|------|------------|---------|---------------|
| **Runtime** | Python | 3.11+ | Ecosistema IA maduro, PyAirtable |
| **LLM Búsqueda** | Gemini 1.5 Flash | Latest | Google Search Grounding nativo, gratis |
| **LLM Razonamiento** | Claude Sonnet/Opus | Latest | Superior en español y análisis |
| **Validación** | Pydantic | 2.0+ | Type safety |
| **Base de datos** | Airtable | - | Ya en uso, MCP disponible |
| **Cliente Airtable** | PyAirtable | 2.0+ | API wrapper oficial |
| **HTTP** | httpx | 0.26+ | Async HTTP |
| **Retry** | Tenacity | 8.0+ | Reintentos robustos |
| **CLI** | Typer | 0.9+ | Interfaz CLI moderna |
| **Logging** | Structlog | 24.0+ | Logs estructurados |

### 6.2 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MOTOR DE ORIGINACIÓN ALTER-5                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         CAPA DE INTERACCIÓN                               │  │
│  │                                                                           │  │
│  │   ┌─────────────────────────┐       ┌─────────────────────────┐          │  │
│  │   │  CLAUDE DESKTOP + MCP   │       │    CLI PYTHON/TYPER     │          │  │
│  │   │  • Equipo comercial     │       │  • Batch processing     │          │  │
│  │   │  • Consultas naturales  │       │  • Scraping masivo      │          │  │
│  │   └─────────────────────────┘       └─────────────────────────┘          │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         CAPA DE AGENTES (6)                               │  │
│  │                                                                           │  │
│  │   Buscador → Enriquecedor → Evaluador_FEI                                │  │
│  │                              Analizador → Selector → Redactor             │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                           CAPA DE DATOS                                   │  │
│  │                                                                           │  │
│  │   AIRTABLE (34 tablas, 563 campos)                                       │  │
│  │   • Stakeholders (Companies, BUs, Contacts, Financials)                  │  │
│  │   • Origination (Campaigns, Targets, Market_Context)                     │  │
│  │   • Config (Certificates, Activities, Countries, Products)               │  │
│  │   • Company_Certificates (nueva)                                         │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 Modelo de Datos Principal

#### Tablas Core para Originación

| Tabla | Campos | Propósito |
|-------|--------|-----------|
| `Stakeholders_Companies` | 59 | Empresas con campos FEI |
| `Stakeholders_Business_Units` | 38 | Unidades de negocio (target real) |
| `Stakeholders_Contacts` | 33 | Contactos para envío |
| `Stakeholders_Companies_Financials` | 13 | Datos financieros por año |
| `Company_Certificates` | 11 | Certificaciones por empresa |
| `Origination_Campaigns` | 23 | Campañas de originación |
| `Campaign_Targets` | 20 | Targets con mensajes personalizados |
| `Market_Context` | 19 | Triggers de mercado |
| `Config_Certificates` | 11 | Catálogo de certificaciones FEI |
| `Config_Activities` | 10 | Actividades elegibles FEI |

#### Campos FEI en Stakeholders_Companies

```
FEI_Status          : Select   [Unknown, Pending_Review, Eligible, 
                                Not_Eligible, Partially_Eligible, Expired]
FEI_Criteria_Met    : Multi    [1.1_Cleantech_Prize, 1.2_Clean_Energy_Patent,
                                1.3_Eco_Label, 1.4_Green_Business_90,
                                1.5_Green_Business_Model, 1.6_Environmental_Certificate]
FEI_Confidence      : Percent  [0-100%]
FEI_Last_Check      : Date
FEI_Notes           : LongText
```

### 6.4 Estructura del Proyecto

```
alter5-origination/
├── pyproject.toml              # Dependencias
├── .env.example                # Variables de entorno
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

### 6.5 APIs y Límites

| Servicio | Límites | Coste |
|----------|---------|-------|
| **Google AI Studio** | 1500 req/día | Gratis |
| **Anthropic** | Según plan | ~€20/mes |
| **Airtable** | 5 req/seg, 50K registros | Ya contratado |
| **Mailchimp** | 10 req/seg | Ya contratado |

---

## 7. Diseño y UX

### 7.1 Principios de Diseño

| Principio | Descripción |
|-----------|-------------|
| **Conversacional** | Interacción vía lenguaje natural (Claude Desktop) |
| **Transparente** | El sistema explica su razonamiento y decisiones |
| **Controlable** | Siempre hay aprobación humana antes de acciones críticas |
| **Eficiente** | Minimizar clics, maximizar automatización |

### 7.2 Interfaces

#### 7.2.1 Claude Desktop + MCP (Equipo Comercial)

**Casos de uso:**
- Crear campañas con lenguaje natural
- Consultar estado de empresas
- Evaluar elegibilidad FEI ad-hoc
- Revisar y aprobar targets

**Ejemplo de interacción:**

```
Usuario: ¿Cuántas empresas tenemos elegibles FEI en el sector renovables?

Claude: He consultado la base de datos. Hay 85 empresas con FEI_Status="Eligible" 
en el sector renovables:
- 45 en España
- 28 en Portugal  
- 12 en otros países

¿Quieres que genere una campaña para algún segmento específico?
```

#### 7.2.2 CLI Python/Typer (Desarrollador)

**Comandos principales:**

```bash
# Búsqueda de empresas
python -m cli search --sector "renovables" --country "ES" --min-employees 50

# Enriquecimiento batch
python -m cli enrich --filter "FEI_Status=Unknown" --limit 100

# Evaluación FEI batch
python -m cli evaluate-fei --filter "FEI_Status=Unknown" --limit 200

# Crear campaña
python -m cli create-campaign --trigger "BCE bajada tipos" --sectors "Industrials"

# Ver estado
python -m cli status --campaign-id "rec123456"
```

#### 7.2.3 Airtable (Visualización y Gestión)

**Vistas principales:**

| Vista | Tabla | Propósito |
|-------|-------|-----------|
| Pipeline FEI | Companies | Empresas por estado FEI |
| Campañas Activas | Campaigns | Campañas en curso |
| Targets Pendientes | Campaign_Targets | Pendientes de aprobación |
| Dashboard CEO | Multiple | KPIs consolidados |

### 7.3 Flujo de Aprobación

```
┌─────────────────────────────────────────────────────────────────┐
│  FLUJO DE APROBACIÓN DE CAMPAÑA                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. IA propone targets          → Status: "Draft"               │
│              ↓                                                   │
│  2. Comercial revisa            → Puede ajustar lista           │
│              ↓                                                   │
│  3. Comercial aprueba targets   → Status: "Pending_Review"      │
│              ↓                                                   │
│  4. IA genera mensajes          → Emails en Campaign_Targets    │
│              ↓                                                   │
│  5. Comercial revisa mensajes   → Puede editar                  │
│              ↓                                                   │
│  6. Comercial aprueba envío     → Status: "Approved"            │
│              ↓                                                   │
│  7. Envío (manual o Mailchimp)  → Status: "Sent"                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Plan de Implementación

### 8.1 Resumen de Sprints (8 semanas)

| Sprint | Duración | Agentes | Objetivo |
|--------|----------|---------|----------|
| **0** | 3 días | - | Setup proyecto + BBDD |
| **1** | 2 semanas | 2 + 3 | Cualificación FEI funcionando |
| **2** | 2 semanas | 4 + 5 + 6 | Campañas MVP + primera campaña real |
| **3** | 2 semanas | 1 | Originador + pipeline completo |
| **4** | 2 semanas | - | Integración email + análisis |

### 8.2 Sprint 0: Setup (3 días)

**Objetivos:**
- Proyecto Python configurado
- APIs conectadas
- Tablas Airtable preparadas

**Entregables:**

| # | Entregable | Criterio de Éxito |
|---|------------|-------------------|
| 0.1 | Proyecto Python con estructura | pyproject.toml, estructura de carpetas |
| 0.2 | APIs configuradas | Gemini y Claude respondiendo |
| 0.3 | Airtable conectado | PyAirtable lee/escribe |
| 0.4 | Config_Certificates poblada | 17 certificaciones FEI |
| 0.5 | Config_Activities poblada | 14 actividades elegibles |
| 0.6 | Claude Project + MCP | Acceso a Airtable desde Claude Desktop |

### 8.3 Sprint 1: Cualificación (Semanas 1-2)

**Objetivos:**
- Agente 2 (Enriquecedor) operativo
- Agente 3 (Evaluador FEI) con ≥90% precisión
- 200+ empresas evaluadas

**Entregables:**

| # | Entregable | Criterio de Éxito |
|---|------------|-------------------|
| 1.1 | Agente 2: Enriquecedor | Completa datos de 100 empresas |
| 1.2 | Agente 3: Evaluador FEI | ≥90% precisión en 50 empresas verificadas |
| 1.3 | CLI evaluación batch | `python -m cli evaluate-fei` funciona |
| 1.4 | 200+ empresas evaluadas | FEI_Status != Unknown |
| 1.5 | Evals automatizados | Suite de tests para evaluador FEI |

**Dependencias:**
- Sprint 0 completado
- Acceso a webs de empresas (no bloqueado)

### 8.4 Sprint 2: Campañas (Semanas 3-4)

**Objetivos:**
- Agentes 4, 5, 6 operativos
- **Primera campaña real enviada**

**Entregables:**

| # | Entregable | Criterio de Éxito |
|---|------------|-------------------|
| 2.1 | Agente 4: Analizador | Genera Market_Context desde trigger |
| 2.2 | Agente 5: Selector | Selecciona ≤30 targets con scoring |
| 2.3 | Agente 6: Redactor | Genera emails ≤150 palabras personalizados |
| 2.4 | Flujo completo | Desde trigger hasta emails listos |
| 2.5 | **Primera campaña real** | Enviada y trackeable |

**Dependencias:**
- Sprint 1 completado
- Pool de empresas con FEI_Status evaluado

### 8.5 Sprint 3: Originación (Semanas 5-6)

**Objetivos:**
- Agente 1 (Buscador) operativo
- Pipeline completo integrado
- 100+ empresas nuevas originadas

**Entregables:**

| # | Entregable | Criterio de Éxito |
|---|------------|-------------------|
| 3.1 | Agente 1: Buscador | Encuentra y crea empresas desde criterios |
| 3.2 | Deduplicación | 0% duplicados en búsquedas |
| 3.3 | Pipeline completo | Flujo 1 (originar) end-to-end |
| 3.4 | 100+ empresas nuevas | Originadas y cualificadas |

**Dependencias:**
- Sprints 1-2 completados

### 8.6 Sprint 4: Integración (Semanas 7-8)

**Objetivos:**
- Integración Mailchimp funcional
- Tracking de métricas
- Documentación completa
- **Presentación a CEOs**

**Entregables:**

| # | Entregable | Criterio de Éxito |
|---|------------|-------------------|
| 4.1 | Integración Mailchimp | Envío desde sistema |
| 4.2 | Tracking métricas | Opens, clicks, replies trackeable |
| 4.3 | Dashboard Airtable | KPIs visibles |
| 4.4 | Documentación | README, guía de uso |
| 4.5 | **Presentación CEOs** | Demo + decisión Go/No-Go |

### 8.7 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Precisión FEI <90% | Media | Alto | Iteración rápida de prompts, más ejemplos |
| Rate limits APIs | Baja | Medio | Batch processing, reintentos |
| Datos incompletos | Alta | Medio | Enriquecedor robusto, fuentes múltiples |
| Webs bloqueadas | Media | Bajo | Proxies, user-agent rotation |
| Airtable 50K límite | Baja | Alto | Migrar a Supabase si necesario |

---

## 9. Testing y QA

### 9.1 Estrategia de Testing para LLMs

**Enfoque: Evals (Evaluations)**

A diferencia del software tradicional, los sistemas basados en LLM requieren "evals" - evaluaciones sistemáticas de la calidad de outputs.

Referencia: [Guía de Evals](https://hamel.dev/blog/posts/evals-faq/)

### 9.2 Evals para Evaluador FEI (Crítico)

| Eval | Descripción | Target |
|------|-------------|--------|
| **Precision** | % de empresas marcadas Eligible que realmente lo son | ≥90% |
| **Recall** | % de empresas elegibles que son identificadas | ≥85% |
| **Confidence Calibration** | FEI_Confidence correlaciona con precisión real | R² > 0.7 |
| **Criterio Correcto** | FEI_Criteria_Met identifica el criterio correcto | ≥95% |

**Dataset de evaluación:**
- 50 empresas manualmente verificadas
- 25 elegibles (con criterio documentado)
- 25 no elegibles

### 9.3 Evals para Redactor de Mensajes

| Eval | Descripción | Target |
|------|-------------|--------|
| **Longitud** | Mensajes ≤150 palabras | 100% |
| **Personalización** | Menciona algo específico de empresa | ≥95% |
| **CTA presente** | Incluye propuesta de reunión | 100% |
| **Tono adecuado** | Español formal pero cercano | Subjetivo, revisión manual |
| **No parece IA** | Evaluación ciega | ≥80% pasa |

### 9.4 Tests Automatizados

```python
# tests/test_evaluador_fei.py

def test_empresa_con_iso14001_es_elegible():
    """Empresa con ISO 14001 válida debe ser Eligible"""
    empresa = crear_empresa_test(certificates=["ISO 14001"])
    resultado = evaluador_fei.evaluar(empresa)
    assert resultado.fei_status == "Eligible"
    assert "1.6_Environmental_Certificate" in resultado.fei_criteria_met

def test_empresa_renovables_90_revenue_es_elegible():
    """Empresa con >90% revenue en renovables debe ser Eligible"""
    empresa = crear_empresa_test(sector="Solar", revenue_pct=95)
    resultado = evaluador_fei.evaluar(empresa)
    assert resultado.fei_status == "Eligible"
    assert "1.4_Green_Business_90" in resultado.fei_criteria_met

def test_cooling_off_excluye_empresa():
    """Empresa contactada hace <90 días debe excluirse"""
    empresa = crear_empresa_test(last_contact=hace_30_dias)
    targets = selector.seleccionar(campaña, [empresa])
    assert empresa not in targets
```

### 9.5 Checklist de Validación MVP

**Funcionales:**
- [ ] 6 agentes implementados y funcionando
- [ ] Evaluación FEI ≥90% precisión (verificar 50 empresas)
- [ ] Flujos 1-4 completos
- [ ] Cooling-off respetado (0 violaciones)
- [ ] Máximo 30 targets por campaña enforceado

**No Funcionales:**
- [ ] Performance dentro de límites
- [ ] Trazabilidad completa (Source_Extractions)
- [ ] Logs estructurados sin PIIs
- [ ] Reintentos automáticos funcionando

**Negocio:**
- [ ] ≥3 campañas enviadas con sistema
- [ ] ≥1 reunión conseguida con campaña del sistema
- [ ] Equipo comercial usando sin ayuda técnica

---

## 10. Métricas y Monitoreo

### 10.1 KPIs de Negocio

| KPI | Baseline | Target MVP | Medición |
|-----|----------|------------|----------|
| Tiempo crear campaña | 4-8h | ≤45 min | Cronómetro |
| Precisión FEI | ~50% | ≥90% | Verificación manual 50 empresas |
| Empresas FEI/mes | 50 | 200+ | Contador Airtable |
| Tasa apertura | 15% | ≥25% | Mailchimp stats |
| Tasa respuesta | 2-3% | ≥8% | Contador manual |
| Reuniones/mes | 2-3 | ≥8 | CRM |
| Campañas simultáneas | 1-2 | ≥4 | Contador Airtable |

### 10.2 KPIs Técnicos

| KPI | Target | Medición |
|-----|--------|----------|
| Uptime sistema | ≥95% | Logs de errores |
| Latencia búsqueda | ≤30 seg | Structlog |
| Latencia evaluación FEI | ≤45 seg | Structlog |
| Tasa de error APIs | ≤5% | Contador reintentos |
| Empresas procesadas/día | ≥100 | Contador |

### 10.3 Dashboards

#### Dashboard Comercial (Airtable)

| Vista | Métricas |
|-------|----------|
| Pipeline FEI | Empresas por FEI_Status, tendencia |
| Campañas Activas | Status, targets, conversiones |
| Performance | Aperturas, respuestas, reuniones |

#### Dashboard Técnico (Logs)

| Métrica | Alerta si |
|---------|-----------|
| Errores API | >10% en 1 hora |
| Latencia | >2x target |
| Evaluaciones fallidas | >5% |

### 10.4 Herramientas de Monitoreo

| Herramienta | Uso |
|-------------|-----|
| **Structlog** | Logs estructurados |
| **Airtable Views** | Dashboards de negocio |
| **Mailchimp Reports** | Tracking emails |
| **Python logging** | Debugging local |

---

## 11. Go-to-Market

### 11.1 Estrategia de Lanzamiento

**Fase 1: Validación Interna (Semanas 1-8)**
- Desarrollo MVP
- Testing con equipo comercial
- Iteración basada en feedback

**Fase 2: Producción Controlada (Semanas 9-12)**
- Uso en campañas reales
- Monitoreo intensivo
- Ajustes de prompts y reglas

**Fase 3: Escala (Post-validación)**
- Expansión a más usuarios
- Integración completa Mailchimp
- Nuevos mercados (UK, Francia)

### 11.2 Comunicación Interna

| Audiencia | Formato | Frecuencia |
|-----------|---------|------------|
| CEOs | Demo + métricas | Fin Sprint 4 |
| Equipo comercial | Training hands-on | Semana 4 |
| Desarrolladores | Documentación técnica | Continua |

### 11.3 Training Equipo Comercial

**Contenido:**
1. Introducción al sistema y arquitectura
2. Uso de Claude Desktop + MCP
3. Flujo de creación de campañas
4. Revisión y aprobación de targets
5. Edición de mensajes
6. Interpretación de métricas

**Formato:**
- 2 sesiones de 1 hora
- Práctica guiada
- Documentación de referencia

### 11.4 Documentación

| Documento | Audiencia | Estado |
|-----------|-----------|--------|
| README técnico | Desarrolladores | Por crear |
| Guía de usuario | Comerciales | Por crear |
| Prompts de referencia | Todos | Por crear |
| FAQ | Todos | Por crear |

### 11.5 Criterios de Éxito para Decisión Go/No-Go

Al final de las 8 semanas, los CEOs decidirán continuar si:

- [ ] Sistema de 6 agentes operativo
- [ ] Evaluación FEI ≥90% precisión (verificar 50 empresas)
- [ ] ≥3 campañas enviadas con sistema
- [ ] ≥1 reunión conseguida con campaña del sistema
- [ ] Equipo comercial usando sin ayuda técnica
- [ ] Documentación completa

---

## Checklist de Calidad del PRD

### Completitud
- [x] Todos los elementos de la estructura están presentes (11 secciones)
- [x] Información suficiente para comenzar desarrollo
- [x] Criterios de aceptación claros y medibles para cada agente
- [x] 4 flujos de trabajo documentados

### Claridad
- [x] Lenguaje claro y sin ambigüedades
- [x] Diagramas de arquitectura incluidos
- [x] Ejemplos concretos (emails, interacciones)
- [x] Terminología consistente (6 agentes con nombres específicos)

### Viabilidad
- [x] Técnicamente factible con recursos disponibles (1 dev + IA)
- [x] Alineado con capacidades del equipo
- [x] Realista en términos de tiempo (8 semanas) y presupuesto (~€50/mes)

### Alineación
- [x] Alineado con estrategia de producto (maximizar FEI)
- [x] Valores FEI exactos del Main_Promt
- [x] Stack tecnológico definido en Main_Promt
- [x] Reglas de negocio respetadas (90 días cooling-off, 30 targets, 150 palabras)

---

## Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **1.0** | **02-01-2026** | **Versión inicial del PRD** |

---

*Este documento es la especificación de producto para el MVP del Motor de Automatización de Originación de Alter-5. Todo desarrollo debe basarse en este PRD. Consultar `Main_Promt_Origination.md` como fuente de verdad para cualquier clarificación.*

