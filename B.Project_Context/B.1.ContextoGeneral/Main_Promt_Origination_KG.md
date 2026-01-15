# Contexto Maestro: Evolución a Knowledge Graph - Motor Alter-5

**Versión**: 1.0  
**Fecha**: 29 Diciembre 2025  
**Propósito**: Documento complementario para evolución del sistema a Knowledge Graphs  
**Prerrequisito**: `Main_Promt_Origination.md` v3.0 (Fase 1 completada)  
**Alcance**: Originación + Estructuración + Distribución con arquitectura KG

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Contexto y Justificación](#2-contexto-y-justificación)
3. [Arquitectura Evolutiva](#3-arquitectura-evolutiva)
4. [Ontología Alter-5](#4-ontología-alter-5)
5. [Integración con Sistema Actual](#5-integración-con-sistema-actual)
6. [Casos de Uso Habilitados](#6-casos-de-uso-habilitados)
7. [Pipeline Completo: Originación → Estructuración → Distribución](#7-pipeline-completo)
8. [Stack Tecnológico KG](#8-stack-tecnológico-kg)
9. [Plan de Implementación](#9-plan-de-implementación)
10. [Métricas de Éxito](#10-métricas-de-éxito)
11. [Instrucciones para Agentes de IA](#11-instrucciones-para-agentes-de-ia)

---

## 1. Resumen Ejecutivo

### 1.1 Propósito de Este Documento

Este documento define la **evolución natural** del Motor de Originación Alter-5 hacia una arquitectura basada en **Knowledge Graphs (KG)**. Es **complementario** al `Main_Promt_Origination.md` y debe utilizarse una vez completada la Fase 1 (MVP con 6 agentes + Airtable).

### 1.2 Por Qué Knowledge Graphs

| Limitación Actual (Airtable) | Solución KG |
|------------------------------|-------------|
| Queries multi-hop lentos | Traversal nativo O(1) |
| Relaciones N:M complejas | Edges con propiedades |
| Sin contexto temporal | Versionado de nodos |
| Semántica implícita | Embeddings + similitud |
| Comunicaciones aisladas | Todo es un nodo conectado |

### 1.3 Alcance Expandido

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVOLUCIÓN DEL SISTEMA ALTER-5                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   FASE 1 (MVP - Ya definida)              FASE 2+ (Este documento)          │
│   ─────────────────────────               ────────────────────────          │
│                                                                              │
│   ┌─────────────────────┐                ┌─────────────────────┐            │
│   │    ORIGINACIÓN      │                │    ORIGINACIÓN      │            │
│   │    6 agentes        │       →        │    6 agentes        │            │
│   │    Airtable         │                │    + KG + Vectors   │            │
│   └─────────────────────┘                └──────────┬──────────┘            │
│                                                     │                        │
│                                                     ▼                        │
│                                          ┌─────────────────────┐            │
│                                          │   ESTRUCTURACIÓN    │            │
│                                          │   (nuevo módulo)    │            │
│                                          └──────────┬──────────┘            │
│                                                     │                        │
│                                                     ▼                        │
│                                          ┌─────────────────────┐            │
│                                          │    DISTRIBUCIÓN     │            │
│                                          │   (nuevo módulo)    │            │
│                                          └─────────────────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Resultado Esperado

| Métrica | Fase 1 (MVP) | Fase 2+ (KG) |
|---------|--------------|--------------|
| Empresas gestionadas | ~10,000 | 50,000+ |
| Relaciones por empresa | ~10 | ~50+ |
| Tiempo query complejo | Segundos | Milisegundos |
| Matching inversor-oportunidad | Reglas | ML sobre grafo |
| Historial relación | Parcial | Completo + temporal |
| Predicción de cierre | No | Sí (Link Prediction) |

---

## 2. Contexto y Justificación

### 2.1 Principio Fundamental

> *"AI needs data. Knowledge Graphs transform your data into a connected network by mapping relationships and capturing semantics, reflecting the true identity of your business."*
> — [The Knowledge Graph Guys](https://www.knowledge-graph-guys.com/)

### 2.2 Qué Hace Único a Alter-5 (Relaciones)

| Activo Único | Por Qué es Relacional |
|--------------|----------------------|
| **Acuerdo FEI** | Company → Certificates → FEI_Criteria → Eligibility |
| **Conocimiento sectorial** | Sector → Activities → Companies → Success_Patterns |
| **Historial de deals** | Opportunity → Investors → Feedback → Next_Campaign |
| **Comunicaciones** | Contact → Emails → Campaigns → Responses → Meetings |
| **Red de relaciones** | Company A → Partner_Of → Company B → Investor → Fund |

### 2.3 Cuándo Activar Esta Fase

**Triggers para iniciar Fase 2:**

| Trigger | Umbral | Indicador |
|---------|--------|-----------|
| Volumen de empresas | >5,000 | Airtable lento |
| Expansión geográfica | >2 países | Complejidad relaciones |
| Integrar comunicaciones | Cualquier momento | Emails + datos unidos |
| Necesidad de predicciones | Cuando se requiera | ML sobre relaciones |
| Pipeline completo | Estructuración activa | End-to-end tracking |

### 2.4 Compatibilidad con Fase 1

**CRÍTICO**: Este documento es **100% compatible** con `Main_Promt_Origination.md`:

| Componente Fase 1 | Evolución Fase 2 |
|-------------------|------------------|
| 6 Agentes especializados | Se mantienen, consultan KG |
| Airtable como hub | Airtable = UI/CRUD, KG = queries complejos |
| Evaluación FEI | Misma lógica, enriquecida con paths |
| Reglas de negocio | Se mantienen 100% |
| Estructura de datos | Se replica en KG + se expande |

---

## 3. Arquitectura Evolutiva

### 3.1 Diagrama de Arquitectura Completa (Fase 2)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        MOTOR ALTER-5 CON KNOWLEDGE GRAPH                         │
│                           Arquitectura Fase 2 Completa                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         CAPA DE INTERACCIÓN                               │  │
│  │                                                                           │  │
│  │   ┌─────────────────────────┐       ┌─────────────────────────┐          │  │
│  │   │  CLAUDE DESKTOP + MCP   │       │    CLI PYTHON/TYPER     │          │  │
│  │   │                         │       │                         │          │  │
│  │   │  • Equipo comercial     │       │  • Batch processing     │          │  │
│  │   │  • Consultas naturales  │       │  • Graph queries        │          │  │
│  │   │  • "¿Qué sé de X?"      │       │  • ML predictions       │          │  │
│  │   └────────────┬────────────┘       └────────────┬────────────┘          │  │
│  │                │                                 │                        │  │
│  └────────────────┼─────────────────────────────────┼────────────────────────┘  │
│                   │                                 │                           │
│                   ▼                                 ▼                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                    CAPA DE ORQUESTACIÓN (Coordinador)                     │  │
│  │                                                                           │  │
│  │   ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │   │                     ROUTER INTELIGENTE                          │    │  │
│  │   │                                                                 │    │  │
│  │   │  • Query simple → Airtable                                      │    │  │
│  │   │  • Query complejo → Knowledge Graph                             │    │  │
│  │   │  • Predicción → Graph ML                                        │    │  │
│  │   │  • Similitud → Vector Search                                    │    │  │
│  │   └─────────────────────────────────────────────────────────────────┘    │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                     │                                           │
│         ┌───────────────────────────┼───────────────────────────┐              │
│         │                           │                           │              │
│         ▼                           ▼                           ▼              │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐        │
│  │   ORIGINACIÓN   │      │ ESTRUCTURACIÓN  │      │  DISTRIBUCIÓN   │        │
│  │   (6 agentes)   │      │  (3 agentes)    │      │   (3 agentes)   │        │
│  │                 │      │                 │      │                 │        │
│  │  • Buscador     │      │  • Analista DD  │      │  • Matcher      │        │
│  │  • Enriquecedor │      │  • Estructurador│      │  • Presentador  │        │
│  │  • Evaluador FEI│      │  • Documentador │      │  • Tracker      │        │
│  │  • Analizador   │      │                 │      │                 │        │
│  │  • Selector     │      │                 │      │                 │        │
│  │  • Redactor     │      │                 │      │                 │        │
│  └─────────────────┘      └─────────────────┘      └─────────────────┘        │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                           CAPA DE DATOS                                   ││
│  │                                                                           ││
│  │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      ││
│  │   │    AIRTABLE     │    │   KNOWLEDGE     │    │  VECTOR STORE   │      ││
│  │   │   (UI/CRUD)     │    │     GRAPH       │    │  (Embeddings)   │      ││
│  │   │                 │    │    (Neo4j)      │    │                 │      ││
│  │   │  • Forms        │◄──►│                 │◄──►│  • Similitud    │      ││
│  │   │  • Views        │    │  • Relaciones   │    │  • Semántica    │      ││
│  │   │  • Manual edits │    │  • Traversals   │    │  • RAG          │      ││
│  │   │  • Automations  │    │  • ML/GDS       │    │                 │      ││
│  │   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘      ││
│  │            │                      │                      │                ││
│  │            └──────────────────────┼──────────────────────┘                ││
│  │                                   │                                        ││
│  │                          ┌────────┴────────┐                              ││
│  │                          │   SYNC ENGINE   │                              ││
│  │                          │  (Bidirectional)│                              ││
│  │                          └─────────────────┘                              ││
│  │                                                                           ││
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐│
│  │                     CAPA DE COMUNICACIONES                                ││
│  │                                                                           ││
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     ││
│  │   │  MAILCHIMP  │  │   GMAIL     │  │  CALENDAR   │  │   CALLS     │     ││
│  │   │  Campaigns  │  │   1-to-1    │  │  Meetings   │  │  Tracking   │     ││
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     ││
│  │          │                │                │                │             ││
│  │          └────────────────┴────────────────┴────────────────┘             ││
│  │                                   │                                        ││
│  │                          ┌────────┴────────┐                              ││
│  │                          │ COMMUNICATION   │                              ││
│  │                          │     NODES       │                              ││
│  │                          │  (in KG)        │                              ││
│  │                          └─────────────────┘                              ││
│  │                                                                           ││
│  └───────────────────────────────────────────────────────────────────────────┘│
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Principios de Diseño

| Principio | Implementación |
|-----------|----------------|
| **Airtable = Source of Truth para CRUD** | Operaciones diarias, UI, formularios |
| **KG = Source of Truth para relaciones** | Queries complejos, ML, análisis |
| **Sync bidireccional** | Cambios en Airtable → KG automáticamente |
| **Embeddings para semántica** | Similitud de empresas, búsqueda contextual |
| **Comunicaciones como nodos** | Cada email, call, meeting es un nodo conectado |

---

## 4. Ontología Alter-5

### 4.1 Entidades (Nodos)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ONTOLOGÍA ALTER-5 - NODOS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   STAKEHOLDERS                    DEALS                    CONFIG            │
│   ────────────                    ─────                    ──────            │
│   🏢 Company                      💼 Opportunity           📜 Certificate    │
│   🏬 BusinessUnit                 📊 Deal                  🏭 Activity       │
│   👤 Contact                      📋 Document              🌍 Country        │
│   💰 Investor                     ❓ QA_Item               💱 Currency       │
│   🏦 Fund                                                  📦 Product        │
│                                                                              │
│   ORIGINATION                     COMMUNICATIONS           TEMPORAL          │
│   ───────────                     ──────────────           ────────          │
│   📢 Campaign                     📧 Email                 ⏱️ Event          │
│   🎯 CampaignTarget               📞 Call                  📅 Timestamp      │
│   📰 MarketContext                🤝 Meeting               🔄 Version        │
│   🔍 Source                       📝 Note                                    │
│   📥 Extraction                   💬 Response                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Relaciones (Edges)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ONTOLOGÍA ALTER-5 - RELACIONES                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ESTRUCTURALES                                                             │
│   ─────────────                                                             │
│   Company ──[OWNS]──────────────────────────► BusinessUnit                  │
│   Company ──[HAS_SUBSIDIARY]─────────────────► Company                      │
│   Company ──[PARENT_OF]──────────────────────► Company                      │
│   BusinessUnit ──[EMPLOYS]───────────────────► Contact                      │
│   Contact ──[WORKS_AT]───────────────────────► BusinessUnit                 │
│   Company ──[HAS_CERTIFICATE]────────────────► Certificate                  │
│   BusinessUnit ──[OPERATES_IN]───────────────► Country                      │
│   BusinessUnit ──[PERFORMS_ACTIVITY]─────────► Activity                     │
│   Investor ──[MANAGES]───────────────────────► Fund                         │
│                                                                              │
│   ORIGINACIÓN                                                               │
│   ───────────                                                               │
│   Campaign ──[TRIGGERED_BY]──────────────────► MarketContext                │
│   Campaign ──[TARGETS]───────────────────────► BusinessUnit                 │
│   CampaignTarget ──[SELECTED_CONTACT]────────► Contact                      │
│   Source ──[EXTRACTED_DATA_FOR]──────────────► Company                      │
│   Extraction ──[FROM_SOURCE]─────────────────► Source                       │
│   Extraction ──[UPDATED]─────────────────────► Company|Contact|BU           │
│                                                                              │
│   DEAL FLOW                                                                 │
│   ─────────                                                                 │
│   Company ──[ORIGINATED_OPPORTUNITY]─────────► Opportunity                  │
│   Opportunity ──[PRESENTED_TO]───────────────► Investor                     │
│   Investor ──[GAVE_FEEDBACK]─────────────────► Opportunity                  │
│   Opportunity ──[CONVERTED_TO]───────────────► Deal                         │
│   Deal ──[CLOSED_WITH]───────────────────────► Investor                     │
│   Deal ──[HAS_DOCUMENT]──────────────────────► Document                     │
│                                                                              │
│   COMUNICACIONES                                                            │
│   ──────────────                                                            │
│   Contact ──[RECEIVED]───────────────────────► Email                        │
│   Contact ──[PARTICIPATED_IN]────────────────► Meeting                      │
│   Contact ──[ANSWERED]───────────────────────► Call                         │
│   Email ──[PART_OF]──────────────────────────► Campaign                     │
│   Email ──[GOT_RESPONSE]─────────────────────► Response                     │
│   Meeting ──[RESULTED_IN]────────────────────► Opportunity                  │
│                                                                              │
│   SEMÁNTICAS (calculadas)                                                   │
│   ───────────────────────                                                   │
│   Company ──[SIMILAR_TO {score}]─────────────► Company                      │
│   Investor ──[GOOD_FIT_FOR {score}]──────────► Opportunity                  │
│   Contact ──[KNOWS]──────────────────────────► Contact                      │
│   Company ──[PARTNER_OF]─────────────────────► Company                      │
│   Company ──[COMPETITOR_OF]──────────────────► Company                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Propiedades en Edges

| Relación | Propiedades | Uso |
|----------|-------------|-----|
| `RECEIVED` (Email) | timestamp, opened, clicked, replied | Tracking engagement |
| `PRESENTED_TO` | date, deck_version, feedback_status | Pipeline tracking |
| `GAVE_FEEDBACK` | type (pass/interested/committed), reason, date | Learning |
| `SIMILAR_TO` | score (0-1), method (embedding/rules), computed_at | Similarity search |
| `GOOD_FIT_FOR` | score, factors[], computed_at | Investor matching |
| `HAS_CERTIFICATE` | issue_date, expiry_date, verified, source | FEI evaluation |

### 4.4 Mapeo Airtable → KG

| Tabla Airtable | Nodo KG | Relación con |
|----------------|---------|--------------|
| `Stakeholders_Companies` | `:Company` | BusinessUnit, Certificate, Country |
| `Stakeholders_Business_Units` | `:BusinessUnit` | Company, Contact, Activity |
| `Stakeholders_Contacts` | `:Contact` | BusinessUnit, Email, Meeting |
| `Origination_Campaigns` | `:Campaign` | MarketContext, CampaignTarget |
| `Campaign_Targets` | `:CampaignTarget` | Campaign, BusinessUnit, Contact |
| `Market_Context` | `:MarketContext` | Campaign, Sector, Country |
| `Config_Certificates` | `:Certificate` | Company |
| `Config_Activities` | `:Activity` | BusinessUnit, GICS |
| `Opportunities - Global Overview` | `:Opportunity` | Company, Investor, Deal |
| `Distribution - Investor Selection` | `:InvestorSelection` | Opportunity, Investor |
| **NUEVO** `Communications_Log` | `:Email`, `:Call`, `:Meeting` | Contact, Campaign |

---

## 5. Integración con Sistema Actual

### 5.1 Los 6 Agentes + KG

Los agentes de Fase 1 se **mantienen** pero ganan capacidades:

| Agente | Fase 1 (Airtable) | Fase 2 (+ KG) |
|--------|-------------------|---------------|
| **1. Buscador** | Crea en Airtable | + Verifica duplicados en KG via similitud |
| **2. Enriquecedor** | Completa campos | + Crea relaciones (subsidiaries, partners) |
| **3. Evaluador FEI** | Evalúa criterios | + Path analysis para eligibilidad indirecta |
| **4. Analizador** | Crea Market_Context | + Conecta con noticias como nodos |
| **5. Selector** | Filtra BUs | + **ML scoring via Graph Features** |
| **6. Redactor** | Genera mensajes | + **Contexto completo via KG traversal** |

### 5.2 Router de Queries

```python
class QueryRouter:
    """Decide si query va a Airtable o Knowledge Graph"""
    
    def route(self, query: str, context: dict) -> str:
        # CRUD simple → Airtable
        if self.is_simple_crud(query):
            return "airtable"
        
        # Multi-hop relationships → KG
        if self.needs_traversal(query):
            return "kg"
        
        # Similarity search → Vector + KG
        if self.needs_similarity(query):
            return "vector_kg"
        
        # Predictions → Graph ML
        if self.needs_prediction(query):
            return "graph_ml"
        
        return "airtable"  # default
    
    def is_simple_crud(self, query: str) -> bool:
        """Operaciones CRUD básicas"""
        patterns = ["crear", "actualizar", "eliminar", "listar", "ver"]
        return any(p in query.lower() for p in patterns)
    
    def needs_traversal(self, query: str) -> bool:
        """Queries que requieren navegar relaciones"""
        patterns = [
            "inversores que", "empresas similares", "historial de",
            "todas las interacciones", "conectado con", "path entre",
            "quién conoce a", "deals con empresas como"
        ]
        return any(p in query.lower() for p in patterns)
```

### 5.3 Sync Engine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SYNC ENGINE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   AIRTABLE                              KNOWLEDGE GRAPH                      │
│   ────────                              ───────────────                      │
│                                                                              │
│   ┌─────────────────┐                   ┌─────────────────┐                 │
│   │ Record Created  │──────────────────►│ Node Created    │                 │
│   │ Record Updated  │──────────────────►│ Node Updated    │                 │
│   │ Record Deleted  │──────────────────►│ Node Archived   │                 │
│   │ Link Added      │──────────────────►│ Edge Created    │                 │
│   └─────────────────┘                   └─────────────────┘                 │
│                                                                              │
│   Trigger: Airtable Webhooks + Polling (cada 5 min)                         │
│                                                                              │
│   ┌─────────────────┐                   ┌─────────────────┐                 │
│   │ KG → Airtable   │◄──────────────────│ Computed Props  │                 │
│   │ (selectivo)     │                   │ (similarity,    │                 │
│   │                 │                   │  predictions)   │                 │
│   └─────────────────┘                   └─────────────────┘                 │
│                                                                              │
│   Solo se sincronizan a Airtable:                                           │
│   • similarity_score (para vistas)                                          │
│   • predicted_close_probability                                             │
│   • recommended_investors[]                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Casos de Uso Habilitados

### 6.1 Originación Mejorada

#### 6.1.1 Encontrar Empresas FEI No Identificadas (Path Analysis)

```cypher
// Empresas conectadas a FEI elegibles que no hemos evaluado
MATCH (fei:Company {fei_status: "Eligible"})
MATCH (fei)-[:HAS_CERTIFICATE]->(cert:Certificate {fei_eligible: true})
MATCH (unknown:Company)-[:PARTNER_OF|SUPPLIER_OF|SUBSIDIARY_OF]-(fei)
WHERE unknown.fei_status IS NULL OR unknown.fei_status = "Unknown"
MATCH (unknown)-[:PERFORMS_ACTIVITY]->(act:Activity)
WHERE act.is_green = true
RETURN unknown.name, unknown.airtable_id,
       collect(DISTINCT cert.name) as related_certs,
       collect(DISTINCT act.name) as green_activities
```

#### 6.1.2 Empresas Similares a Deals Cerrados

```cypher
// Encontrar empresas similares a aquellas donde cerramos deals
MATCH (closed:Deal {status: "Closed"})
MATCH (closed)<-[:CONVERTED_TO]-(opp:Opportunity)
MATCH (opp)<-[:ORIGINATED_OPPORTUNITY]-(success:Company)
MATCH (candidate:Company)-[:SIMILAR_TO {score: > 0.7}]->(success)
WHERE NOT (candidate)-[:ORIGINATED_OPPORTUNITY]->(:Opportunity)
RETURN candidate.name, candidate.sector,
       AVG(closed.ticket_size) as avg_ticket_similar,
       collect(success.name) as similar_to
ORDER BY AVG(closed.ticket_size) DESC
LIMIT 20
```

#### 6.1.3 Warm Intros (Conexiones de 2do grado)

```cypher
// Encontrar conexiones para llegar a una empresa target
MATCH (target:Company {name: "Target Corp"})
MATCH (target)<-[:WORKS_AT]-(target_contact:Contact)
MATCH path = shortestPath(
    (our_contact:Contact {is_alter5: true})-[*1..3]-(target_contact)
)
RETURN our_contact.name, target_contact.name,
       length(path) as degrees,
       [n IN nodes(path) | n.name] as connection_path
ORDER BY degrees ASC
```

### 6.2 Campañas Mejoradas

#### 6.2.1 Contexto Completo para Personalización

```cypher
// Todo el contexto de una empresa para redactar email
MATCH (c:Company {airtable_id: $company_id})
OPTIONAL MATCH (c)-[:HAS_CERTIFICATE]->(cert:Certificate)
OPTIONAL MATCH (c)-[:OWNS]->(bu:BusinessUnit)-[:PERFORMS_ACTIVITY]->(act:Activity)
OPTIONAL MATCH (c)<-[:ABOUT]-(news:MarketContext)
WHERE news.publication_date > date() - duration({days: 90})
OPTIONAL MATCH (c)<-[:RECEIVED]-(email:Email)
WHERE email.sent_date > date() - duration({days: 365})
RETURN c,
       collect(DISTINCT cert) as certificates,
       collect(DISTINCT act) as activities,
       collect(DISTINCT news) as recent_news,
       collect(DISTINCT email) as email_history
```

#### 6.2.2 Scoring con Graph Features

```python
def calculate_fit_score_kg(bu_id: str, campaign_context: dict) -> dict:
    """Calcular fit score usando features del grafo"""
    
    query = """
    MATCH (bu:BusinessUnit {airtable_id: $bu_id})
    MATCH (bu)<-[:OWNS]-(company:Company)
    
    // FEI eligibility
    OPTIONAL MATCH (company)-[:HAS_CERTIFICATE]->(cert:Certificate {fei_eligible: true})
    
    // Similarity to successful deals
    OPTIONAL MATCH (company)-[sim:SIMILAR_TO]->(success:Company)
    WHERE (success)-[:ORIGINATED_OPPORTUNITY]->(:Opportunity)-[:CONVERTED_TO]->(:Deal)
    
    // Previous engagement
    OPTIONAL MATCH (company)<-[:WORKS_AT]-(contact:Contact)
    OPTIONAL MATCH (contact)<-[:RECEIVED]-(email:Email)
    WHERE email.replied = true
    
    // Network centrality
    OPTIONAL MATCH (company)-[r]-(connected)
    
    RETURN 
        COUNT(DISTINCT cert) > 0 as is_fei_eligible,
        MAX(sim.score) as max_similarity_to_success,
        COUNT(DISTINCT email) as positive_responses,
        COUNT(DISTINCT r) as network_connections
    """
    
    result = kg.query(query, {"bu_id": bu_id})
    
    # Calcular score compuesto
    score = 0.5  # base
    
    if result.is_fei_eligible:
        score += 0.20
    
    if result.max_similarity_to_success:
        score += result.max_similarity_to_success * 0.15
    
    if result.positive_responses > 0:
        score += min(result.positive_responses * 0.05, 0.15)
    
    if result.network_connections > 10:
        score += 0.10
    
    return {"score": min(score, 1.0), "features": result}
```

### 6.3 Distribución (Nuevo Módulo)

#### 6.3.1 Matching Inversor-Oportunidad

```cypher
// Encontrar mejores inversores para una oportunidad
MATCH (opp:Opportunity {id: $opp_id})
MATCH (opp)<-[:ORIGINATED_OPPORTUNITY]-(company:Company)
MATCH (company)-[:OPERATES_IN]->(sector:Activity)
MATCH (company)-[:LOCATED_IN]->(country:Country)

// Inversores que:
// 1. Invierten en ese sector
// 2. Cubren ese país
// 3. No han rechazado deals similares
MATCH (investor:Investor)
WHERE (investor)-[:INVESTS_IN]->(sector)
  AND (investor)-[:COVERS_REGION]->(country)
  AND NOT (investor)-[:GAVE_FEEDBACK {type: "pass", reason: "sector_mismatch"}]->
      (:Opportunity)<-[:ORIGINATED_OPPORTUNITY]-(:Company)-[:OPERATES_IN]->(sector)

// Calcular fit basado en historial
OPTIONAL MATCH (investor)-[:CLOSED_WITH]->(:Deal)<-[:CONVERTED_TO]-
               (:Opportunity)<-[:ORIGINATED_OPPORTUNITY]-(similar:Company)
WHERE (similar)-[:SIMILAR_TO {score: > 0.6}]->(company)

RETURN investor.name, investor.fund_name,
       COUNT(DISTINCT similar) as similar_deals_closed,
       investor.typical_ticket as ticket_range
ORDER BY similar_deals_closed DESC
LIMIT 10
```

#### 6.3.2 Predicción de Cierre (Link Prediction)

```python
# Usar Neo4j GDS para predecir probabilidad de cierre
def predict_deal_close(opportunity_id: str, investor_id: str) -> float:
    """
    Usar Link Prediction para estimar probabilidad de que
    un inversor cierre un deal específico.
    """
    
    # Crear proyección de grafo
    gds.graph.project(
        "deal_prediction",
        ["Investor", "Opportunity", "Deal", "Company"],
        {
            "CLOSED_WITH": {"orientation": "UNDIRECTED"},
            "PRESENTED_TO": {"orientation": "UNDIRECTED"},
            "SIMILAR_TO": {"orientation": "UNDIRECTED"}
        }
    )
    
    # Calcular features de Link Prediction
    result = gds.linkPrediction.predict.stream(
        "deal_prediction",
        nodeLabels=["Investor", "Opportunity"],
        relationshipTypes=["CLOSED_WITH"],
        # Usar múltiples algoritmos
        linkFeatures=["commonNeighbors", "adamicAdar", "resourceAllocation"],
        topN=100
    )
    
    # Filtrar para nuestro par específico
    prediction = result[
        (result.node1 == opportunity_id) & 
        (result.node2 == investor_id)
    ]
    
    return prediction.probability if not prediction.empty else 0.0
```

---

## 7. Pipeline Completo

### 7.1 Originación → Estructuración → Distribución

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE COMPLETO ALTER-5 (Con KG)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        1. ORIGINACIÓN                               │   │
│   │                                                                     │   │
│   │   Buscador → Enriquecedor → Evaluador FEI                          │   │
│   │      │            │              │                                  │   │
│   │      ▼            ▼              ▼                                  │   │
│   │   ┌──────────────────────────────────┐                             │   │
│   │   │         KNOWLEDGE GRAPH          │                             │   │
│   │   │  • Nodos: Company, BU, Contact   │                             │   │
│   │   │  • Edges: OWNS, WORKS_AT, etc.   │                             │   │
│   │   │  • Props: FEI_Status, Certs      │                             │   │
│   │   └──────────────────────────────────┘                             │   │
│   │                     │                                               │   │
│   │   Analizador ──────►│◄────── Selector ◄────── Redactor             │   │
│   │   (triggers)        │        (scoring KG)     (contexto KG)        │   │
│   │                     │                                               │   │
│   │                     ▼                                               │   │
│   │            [Campaña Enviada]                                       │   │
│   │                     │                                               │   │
│   └─────────────────────┼───────────────────────────────────────────────┘   │
│                         │                                                    │
│                         │ Respuesta positiva → Meeting                      │
│                         │                                                    │
│   ┌─────────────────────▼───────────────────────────────────────────────┐   │
│   │                      2. ESTRUCTURACIÓN                              │   │
│   │                                                                     │   │
│   │   Meeting ──────► Opportunity Created                              │   │
│   │                          │                                          │   │
│   │   ┌──────────────────────┼──────────────────────┐                  │   │
│   │   │                      │                      │                  │   │
│   │   ▼                      ▼                      ▼                  │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │   │
│   │   │  ANALISTA   │  │ESTRUCTURADOR│  │DOCUMENTADOR │               │   │
│   │   │    DD       │  │             │  │             │               │   │
│   │   │             │  │  • Terms    │  │  • Deck     │               │   │
│   │   │  • Info     │  │  • Pricing  │  │  • Teaser   │               │   │
│   │   │    Request  │  │  • Timeline │  │  • Q&A      │               │   │
│   │   │  • Due Dil. │  │             │  │             │               │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘               │   │
│   │          │                │                │                        │   │
│   │          └────────────────┼────────────────┘                        │   │
│   │                           │                                          │   │
│   │                           ▼                                          │   │
│   │   ┌──────────────────────────────────┐                             │   │
│   │   │         KNOWLEDGE GRAPH          │                             │   │
│   │   │  • Nodos: Opportunity, Document  │                             │   │
│   │   │  • Edges: HAS_DOCUMENT, Q&A      │                             │   │
│   │   │  • Timeline completo             │                             │   │
│   │   └──────────────────────────────────┘                             │   │
│   │                           │                                          │   │
│   │                           ▼                                          │   │
│   │            [Opportunity Structured]                                 │   │
│   │                           │                                          │   │
│   └───────────────────────────┼──────────────────────────────────────────┘   │
│                               │                                              │
│                               │ Ready for distribution                      │
│                               │                                              │
│   ┌───────────────────────────▼──────────────────────────────────────────┐   │
│   │                       3. DISTRIBUCIÓN                                │   │
│   │                                                                      │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │   │
│   │   │   MATCHER   │  │ PRESENTADOR │  │   TRACKER   │                │   │
│   │   │             │  │             │  │             │                │   │
│   │   │  • Find     │  │  • Present  │  │  • Follow   │                │   │
│   │   │    best     │  │    to       │  │    up       │                │   │
│   │   │    investors│  │    investors│  │  • Track    │                │   │
│   │   │  • ML       │  │  • Waves    │  │    feedback │                │   │
│   │   │    ranking  │  │             │  │             │                │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘                │   │
│   │          │                │                │                        │   │
│   │          └────────────────┼────────────────┘                        │   │
│   │                           │                                          │   │
│   │                           ▼                                          │   │
│   │   ┌──────────────────────────────────┐                             │   │
│   │   │         KNOWLEDGE GRAPH          │                             │   │
│   │   │  • Nodos: Investor, Selection    │                             │   │
│   │   │  • Edges: PRESENTED_TO, FEEDBACK │                             │   │
│   │   │  • Predictions: LIKELY_TO_CLOSE  │                             │   │
│   │   └──────────────────────────────────┘                             │   │
│   │                           │                                          │   │
│   │                           ▼                                          │   │
│   │              [Deal Closed / Pipeline]                               │   │
│   │                                                                      │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Nuevos Agentes para Fase 2

#### 7.2.1 Agentes de Estructuración

| Agente | Misión | Input | Output |
|--------|--------|-------|--------|
| **Analista DD** | Preparar Information Request y DD checklist | Opportunity | IR document, DD checklist |
| **Estructurador** | Definir términos, pricing, timeline | IR responses | Term sheet draft |
| **Documentador** | Generar deck, teaser, Q&A | Opportunity data | Investment materials |

#### 7.2.2 Agentes de Distribución

| Agente | Misión | Input | Output |
|--------|--------|-------|--------|
| **Matcher** | Encontrar mejores inversores usando KG+ML | Opportunity | Ranked investor list |
| **Presentador** | Gestionar presentaciones y waves | Investor list | Presentation schedule |
| **Tracker** | Seguimiento feedback y pipeline | Presentations | Updated statuses, follow-ups |

---

## 8. Stack Tecnológico KG

### 8.1 Componentes

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Graph Database** | Neo4j AuraDB | Latest | Knowledge Graph managed |
| **Vector Index** | Neo4j Vector | Integrated | Embeddings para similitud |
| **Graph ML** | Neo4j GDS | 2.x | Link prediction, clustering |
| **Python Driver** | neo4j-python | 5.x | Conexión a Neo4j |
| **OGM** | neomodel | 5.x | Object-Graph Mapping |
| **Embeddings** | OpenAI / Cohere | Latest | Generar vectors |
| **Sync** | Custom Python | - | Airtable ↔ Neo4j |
| **LLM Integration** | LangChain | 0.1+ | KG + LLM queries |

### 8.2 Estructura del Proyecto (Extensión)

```
alter5-origination/
├── ... (estructura Fase 1)
│
├── kg/                            # NUEVO: Knowledge Graph
│   ├── __init__.py
│   ├── client.py                  # Neo4j client wrapper
│   ├── models/                    # Neomodel definitions
│   │   ├── __init__.py
│   │   ├── stakeholders.py        # Company, BU, Contact
│   │   ├── deals.py               # Opportunity, Deal
│   │   ├── communications.py      # Email, Call, Meeting
│   │   └── config.py              # Certificate, Activity
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── airtable_to_kg.py      # Sync AT → KG
│   │   └── kg_to_airtable.py      # Sync KG → AT (selectivo)
│   ├── queries/
│   │   ├── __init__.py
│   │   ├── similarity.py          # Similar companies
│   │   ├── paths.py               # Path analysis
│   │   ├── predictions.py         # ML predictions
│   │   └── context.py             # Full context retrieval
│   └── embeddings/
│       ├── __init__.py
│       └── generator.py           # Generate company embeddings
│
├── agents/
│   ├── ... (agentes Fase 1)
│   │
│   ├── structuring/               # NUEVO: Estructuración
│   │   ├── __init__.py
│   │   ├── analista_dd.py
│   │   ├── estructurador.py
│   │   └── documentador.py
│   │
│   └── distribution/              # NUEVO: Distribución
│       ├── __init__.py
│       ├── matcher.py
│       ├── presentador.py
│       └── tracker.py
│
└── tests/
    ├── ... (tests Fase 1)
    └── kg/
        ├── test_sync.py
        ├── test_queries.py
        └── test_predictions.py
```

### 8.3 Costes Estimados

| Servicio | Plan | Coste/mes | Uso |
|----------|------|-----------|-----|
| Neo4j AuraDB | Free/Professional | €0-65 | 50K-200K nodos |
| OpenAI Embeddings | Pay-as-you-go | ~€10-30 | 50K empresas |
| Neo4j GDS | Included in AuraDB | €0 | ML features |
| **Total adicional** | | **€10-95/mes** | |

---

## 9. Plan de Implementación

### 9.1 Prerequisitos

- ✅ Fase 1 completada (6 agentes + Airtable funcionando)
- ✅ >5,000 empresas en sistema
- ✅ Al menos 3 campañas exitosas
- ✅ Equipo comercial usando el sistema

### 9.2 Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ROADMAP FASE 2 (Knowledge Graph)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   MES 1                MES 2                MES 3                MES 4+     │
│   ─────                ─────                ─────                ─────      │
│                                                                              │
│   Sprint KG-0          Sprint KG-1          Sprint KG-2          Sprint KG-3│
│   Setup                Sync + Queries       ML + Agents          Full       │
│                                                                              │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌────────┐│
│   │• Neo4j setup│      │• Full sync  │      │• Link pred  │      │• Struct││
│   │• Schema     │      │• Basic      │      │• Embeddings │      │• Distro││
│   │• Initial    │      │  queries    │      │• Selector   │      │• Full  ││
│   │  sync       │      │• Router     │      │  enhanced   │      │  pipe  ││
│   │• Test data  │      │• Redactor   │      │• Matcher    │      │        ││
│   │             │      │  enhanced   │      │  agent      │      │        ││
│   └─────────────┘      └─────────────┘      └─────────────┘      └────────┘│
│                                                                              │
│   Inversión:           Inversión:           Inversión:           Inversión: │
│   €0-15                €30-50               €50-75               €75-100    │
│   (setup)              (AuraDB Pro)         (+ embeddings)       (scale)    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Sprint KG-0: Setup (2 semanas)

| Tarea | Entregable |
|-------|------------|
| Crear cuenta Neo4j AuraDB | Instancia funcionando |
| Definir schema en Cypher | Constraints + Indexes |
| Implementar neomodel | Models para todas entidades |
| Sync inicial AT → KG | Datos migrados |
| Tests básicos | Suite de tests |

### 9.4 Sprint KG-1: Sync + Queries (2 semanas)

| Tarea | Entregable |
|-------|------------|
| Sync bidireccional | Engine funcionando |
| Queries de similitud | `similar_companies()` |
| Queries de contexto | `full_context()` |
| Router inteligente | Decidir AT vs KG |
| Mejorar Redactor | Usar contexto KG |

### 9.5 Sprint KG-2: ML + Agents (2 semanas)

| Tarea | Entregable |
|-------|------------|
| Generar embeddings | Vectors para empresas |
| Link Prediction setup | GDS configurado |
| Mejorar Selector | Scoring con graph features |
| Agente Matcher | Distribución básica |

### 9.6 Sprint KG-3+: Full Pipeline (Ongoing)

| Tarea | Entregable |
|-------|------------|
| Agentes Estructuración | 3 agentes funcionando |
| Agentes Distribución | 3 agentes funcionando |
| Comunicaciones integradas | Emails/Calls como nodos |
| Dashboard métricas KG | Visualización Neo4j Bloom |

---

## 10. Métricas de Éxito

### 10.1 KPIs Fase 2

| Métrica | Target Fase 1 | Target Fase 2 |
|---------|---------------|---------------|
| Tiempo query complejo | N/A (manual) | <100ms |
| Empresas similares encontradas | N/A | 10+ por empresa |
| Precisión matching inversor | Reglas 60% | ML 80%+ |
| Contexto para personalización | 3-5 datos | 15+ datos |
| Cobertura comunicaciones | 0% | 100% integradas |
| Predicción de cierre | No | AUC >0.75 |

### 10.2 Checklist de Validación

- [ ] Sync Airtable ↔ KG funcionando sin errores
- [ ] Queries de similitud retornan resultados relevantes
- [ ] Selector usa graph features (verificar mejora)
- [ ] Redactor genera emails con más contexto
- [ ] Matcher propone inversores correctos (verificar 10 deals)
- [ ] Comunicaciones integradas como nodos
- [ ] Link Prediction funciona con AUC >0.7

---

## 11. Instrucciones para Agentes de IA

### 11.1 Cuándo Usar Este Documento

Este documento se activa **DESPUÉS** de completar Fase 1:

```
SI Fase 1 NO completada:
    usar → Main_Promt_Origination.md
    ignorar → este documento

SI Fase 1 completada Y trigger activado:
    usar → Main_Promt_Origination.md (base)
    usar → Main_Promt_Origination_KG.md (extensión)
```

### 11.2 Compatibilidad

**Todo lo definido en `Main_Promt_Origination.md` sigue vigente:**
- ✅ 6 agentes de originación
- ✅ Reglas de negocio (cooling-off, FEI, etc.)
- ✅ Estructura de datos Airtable
- ✅ Evaluación FEI
- ✅ Formato de mensajes

**Este documento AÑADE:**
- Knowledge Graph como capa de queries
- Nuevos agentes para Estructuración y Distribución
- Comunicaciones integradas
- ML para predicciones

### 11.3 Router de Queries

```python
# Lógica para agentes:
def should_use_kg(query_type: str) -> bool:
    """Determinar si usar Knowledge Graph"""
    
    kg_queries = [
        "similar_companies",      # Similitud semántica
        "full_context",           # Timeline completo
        "path_to_contact",        # Warm intros
        "investor_matching",      # ML ranking
        "fei_indirect",           # Elegibilidad por relación
        "predict_close",          # Link prediction
        "communication_history",  # Emails + calls + meetings
    ]
    
    return query_type in kg_queries
```

### 11.4 Prioridades de Implementación

1. **Primero**: Sync sin errores (fundamental)
2. **Segundo**: Queries de similitud (quick win visible)
3. **Tercero**: Contexto mejorado para Redactor
4. **Cuarto**: Scoring mejorado para Selector
5. **Quinto**: Matcher para distribución
6. **Sexto**: Comunicaciones integradas

### 11.5 Qué NUNCA Hacer

- ❌ **Romper compatibilidad** con Fase 1
- ❌ **Duplicar datos** sin sync
- ❌ **Ignorar Airtable** (sigue siendo UI principal)
- ❌ **Sobre-optimizar** antes de validar basics
- ❌ **ML sin datos suficientes** (<1000 deals para link prediction)

---

## Control de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **1.0** | **29-12-2025** | **Versión inicial - Complemento a Main_Promt_Origination.md** |

---

## Referencias

| Documento | Relación |
|-----------|----------|
| `Main_Promt_Origination.md` | **PREREQUISITO** - Fase 1 completa |
| `Origination_Campaigns_Database_Documentation_Complete.md` | Schema Airtable |
| [The Knowledge Graph Guys](https://www.knowledge-graph-guys.com/) | Inspiración arquitectura |
| [Neo4j Documentation](https://neo4j.com/docs/) | Referencia técnica |

---

*Este documento es COMPLEMENTARIO a `Main_Promt_Origination.md`. Debe usarse únicamente después de completar la Fase 1 y cuando se active uno de los triggers definidos. Mantiene 100% compatibilidad con la arquitectura existente.*

