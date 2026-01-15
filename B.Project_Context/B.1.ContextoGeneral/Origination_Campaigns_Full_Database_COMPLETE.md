# 📊 ORIGINATION_CAMPAIGNS DATABASE
# DOCUMENTACIÓN TÉCNICA EXHAUSTIVA

> **Generado:** 2025-12-30 11:45:12 UTC
> **Base ID:** `appEgNSP0tOLJ9YJ9`
> **Total Tablas:** 34
> **Total Campos:** 563

## MÉTRICAS

| Tipo | Cantidad |
|------|----------|
| Record Links | 139 |
| Lookups | 44 |
| Rollups | 13 |
| Fórmulas | 11 |
| Campos AI | 16 |
| Campos Select | 69 |

---

## ÍNDICE DE TABLAS

1. [Stakeholders_Companies](#stakeholders-companies) (59 campos)
2. [Stakeholders_Companies_Financials](#stakeholders-companies-financials) (13 campos)
3. [Stakeholders_Business_Units](#stakeholders-business-units) (38 campos)
4. [Stakeholders_Contacts](#stakeholders-contacts) (33 campos)
5. [Opportunities - Global Overview](#opportunities---global-overview) (21 campos)
6. [Opportunity - Adaptation](#opportunity---adaptation) (6 campos)
7. [Opportunity - Q&A](#opportunity---qa) (11 campos)
8. [Distribution - Investor Selection](#distribution---investor-selection) (28 campos)
9. [Distribution - Waves](#distribution---waves) (23 campos)
10. [Investor Workstreams](#investor-workstreams) (19 campos)
11. [Internal - Initiatives](#internal---initiatives) (17 campos)
12. [Internal - Tasks](#internal---tasks) (24 campos)
13. [Help & Feedback - Suggestions](#help--feedback---suggestions) (9 campos)
14. [Config - Email Templates](#config---email-templates) (16 campos)
15. [Config - Email Activity](#config---email-activity) (17 campos)
16. [Config - Users](#config---users) (12 campos)
17. [Config - Variables](#config---variables) (7 campos)
18. [Config_General_Fields](#config-general-fields) (3 campos)
19. [Config_Currencies](#config-currencies) (6 campos)
20. [Config_Countries](#config-countries) (21 campos)
21. [Config_Stakeholder_Types](#config-stakeholder-types) (5 campos)
22. [Config_Stakeholder_SubTypes](#config-stakeholder-subtypes) (9 campos)
23. [Config_Sector_And_Activities](#config-sector-and-activities) (14 campos)
24. [Config_Languages](#config-languages) (6 campos)
25. [GICS_Standard](#gics-standard) (8 campos)
26. [Config_Certificates](#config-certificates) (11 campos)
27. [Config_Activities](#config-activities) (10 campos)
28. [Market_Context](#market-context) (19 campos)
29. [Origination_Campaigns](#origination-campaigns) (23 campos)
30. [Campaign_Targets](#campaign-targets) (20 campos)
31. [Config_Credit_Strategies](#config-credit-strategies) (3 campos)
32. [Config_Sources](#config-sources) (19 campos)
33. [Source_Extractions](#source-extractions) (22 campos)
34. [Company_Certificates](#company-certificates) (11 campos)

---
## ARQUITECTURA Y FLUJOS DE DATOS

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           ORIGINATION_CAMPAIGNS DATABASE                            │
│                                  (34 tablas)                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐│
│   │     STAKEHOLDERS      │   │     OPPORTUNITIES     │   │     ORIGINATION       ││
│   │     ────────────      │   │     ─────────────     │   │     ───────────       ││
│   │ • Companies        (59)│   │ • Global Overview (21)│   │ • Campaigns       (23)││
│   │ • Business Units   (38)│   │ • Adaptation       (6)│   │ • Campaign_Targets(20)││
│   │ • Contacts         (33)│   │ • Q&A             (11)│   │ • Market_Context  (19)││
│   │ • Financials       (13)│   │                       │   │                       ││
│   │ • Company_Certs    (11)│   │                       │   │                       ││
│   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘│
│                                                                                     │
│   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐│
│   │     DISTRIBUTION      │   │    INTERNAL OPS       │   │    DATA SOURCES       ││
│   │     ────────────      │   │    ────────────       │   │    ────────────       ││
│   │ • Investor Select (28)│   │ • Tasks           (24)│   │ • Config_Sources  (19)││
│   │ • Waves           (23)│   │ • Initiatives     (17)│   │ • Source_Extract  (22)││
│   │ • Workstreams     (19)│   │ • Feedback         (9)│   │                       ││
│   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘│
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                          CONFIGURATION TABLES (15)                          │  │
│   ├─────────────────────────────────────────────────────────────────────────────┤  │
│   │ Countries(21) │ Currencies(6) │ Languages(6) │ Stakeholder_Types(5)        │  │
│   │ Stakeholder_SubTypes(9) │ Sector_And_Activities(14) │ Activities(10)       │  │
│   │ Certificates(11) │ Credit_Strategies(3) │ GICS_Standard(8)                 │  │
│   │ Users(12) │ Variables(7) │ General_Fields(3) │ Email_Templates(16)        │  │
│   │ Email_Activity(17)                                                         │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos: Stakeholders

```
                         ┌─────────────────────┐
                         │   Config_Sources    │
                         │    (tbl4MEJa...)    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Source_Extractions  │
                         │    (tblXX2Uq...)    │
                         └──────────┬──────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│Stakeholders_Companies│  │Stakeholders_Bus_Unit│  │Stakeholders_Contacts│
│   (tbl47AWm...)     │  │   (tblbBsyp...)     │  │   (tblfErId...)     │
│                     │  │                     │  │                     │
│ NEW FEI FIELDS:     │  │ NEW COOLING-OFF:    │  │                     │
│ • FEI_Status        │  │ • Last_Outreach_Date│  │                     │
│ • FEI_Criteria_Met  │  │ • Is_In_Cooling_Off │  │                     │
│ • FEI_Confidence    │  │                     │  │                     │
│ • FEI_Last_Check    │  │                     │  │                     │
│ • FEI_Notes         │  │                     │  │                     │
└──────────┬──────────┘  └─────────────────────┘  └─────────────────────┘
           │
           ├──────────────────────────┐
           │                          │
           ▼                          ▼
┌─────────────────────┐  ┌─────────────────────┐
│Companies_Financials │  │ Company_Certificates│
│   (tblYiuZO...)     │  │   (tbl6PZVZ...)     │ ◄── NUEVA TABLA
└─────────────────────┘  └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Config_Certificates │
                         │   (tblQ5HZt...)     │
                         │ • FEI_Eligible ✓    │
                         └─────────────────────┘
```

### Flujo de Datos: Campañas de Originación

```
┌─────────────────────┐         ┌─────────────────────┐
│    Market_Context   │         │Config_Credit_Strat. │
│   (tblkE6Yh...)     │         │   (tbla0eiBSm...)   │
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
               ┌─────────────────────┐
               │Origination_Campaigns│
               │   (tbl0B5YG...)     │
               └──────────┬──────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │  Campaign_Targets   │
               │   (tblblROg...)     │
               │                     │
               │ • Sent_Date         │
               │ • Last_Interaction  │
               │ • Target_Status     │
               └──────────┬──────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────┐ ┌─────────────────┐
│  Business_Units │ │  Contacts │ │ Email_Templates │
└─────────────────┘ └───────────┘ └─────────────────┘
```

### Flujo de Datos: Distribución

```
┌─────────────────────┐
│ Opportunities_Global│
│   (tblMA730...)     │
└──────────┬──────────┘
           │
   ┌───────┼───────────────────────────┐
   │       │                           │
   ▼       ▼                           ▼
┌───────┐ ┌─────────────────────┐ ┌─────────────────────┐
│  Q&A  │ │ Opportunity_Adapt.  │ │Dist_Inv_Selection   │
└───────┘ └─────────────────────┘ └──────────┬──────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │  Distribution_Waves │
                                  │   (tblQlEQn...)     │
                                  └──────────┬──────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │ Investor_Workstreams│
                                  │   (tblbdMCG...)     │
                                  └──────────┬──────────┘
                                             │
                                             ▼
                                  ┌─────────────────────┐
                                  │ Config_Email_Activity│
                                  │   (tblFY14T...)     │
                                  └─────────────────────┘
```

---
## ESPECIFICACIÓN COMPLETA DE TABLAS

### 1. Stakeholders_Companies

**ID:** `tbl47AWmhYAXerbWz` | **Campos:** 59

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Company Name | `fldqByNrteSCYDyLX` | Text |  |
| 2 | Home URL | `fld4CmgZl8zG5AsmF` | Text |  |
| 3 | Linkedin URL | `fldDJki7CHM7qzlA9` | URL |  |
| 4 | HQ Country | `fldUmivMZQDejw7ZS` | Link→Config_Countries(n) |  |
| 5 | HQ Address | `fldCYJOZjzm1SsSvP` | Rich Text |  |
| 6 | Closest Office | `fldZcCzw5pHVqhxJf` | Rich Text | The address of the company's office that is the closest to o |
| 7 | Tax ID | `fldpA5HI4NrqBRt8w` | Text | The official tax identification number assigned to the compa |
| 8 | Company_Type | `fldw3mJsSPxdiXCpL` | Rollup |  |
| 9 | Sector | `fldbPI0GGuKcLAFsB` | Rollup |  |
| 10 | Activities | `flduPFvPTEyGqWSP5` | Rollup |  |
| 11 | Focus Regions | `fldkhsm4kClK5pLqi` | Rollup |  |
| 12 | Focus Countries | `fldTwcXQj3fhbiLak` | Rollup | Deduplicates and joins GICS_Sectors values, removing extra s |
| 13 | GICS Sectors AI | `fldUYmcWYfZxpYGHj` | AI |  |
| 14 | GICS Industries AI | `fldZfawXl9lndkhse` | AI |  |
| 15 | GICS Subindustries AI | `fld6PxsHtI5vN2pBr` | AI |  |
| 16 | Green Checker | `fldIwHzk6bzYr68Wa` | Checkbox |  |
| 17 | Certifications | `fldt2QHbmbcW2vHtW` | Rich Text |  |
| 18 | Description | `fldar7tqE2pLCXPaA` | Rich Text |  |
| 19 | Num Employees | `fldRYVqXRaVG1uLT8` | Number |  |
| 20 | Currency | `flde6s7SlSY4sR7xD` | Link→Config_Currencies(1) |  |
| 21 | Latest Financials Year | `fldnJDBrPshftU0Ip` | Lookup |  |
| 22 | Latest Available Year | `fldNr5ea3TJigNP2T` | Lookup |  |
| 23 | EBITDA | `fldGMWA2OZsE8161S` | Lookup |  |
| 24 | Debt / EBITDA | `fldda9mVx6VT8O7A8` | Lookup |  |
| 25 | Revenues | `fldMpGZqi1oZhJyKS` | Lookup |  |
| 26 | Parent Company | `fldYNfAxCbPYR5cAF` | Link→Stakeholders_Compa..(1) |  |
| 27 | Parent Is Ultimate | `fldmaTjHO5spDaOSo` | Checkbox | This field indicates whether the parent company consolidates |
| 28 | Parent Latest Financials | `fldbFxeciwfT9M8b2` | Lookup |  |
| 29 | Parent Currency | `fldetE3rT2r7QYoPJ` | Lookup |  |
| 30 | Parent EBITDA | `fldzPfL1rWZBvHl4a` | Lookup |  |
| 31 | Parent Debt / EBITDA | `fldT5Fd2J21gnoxjP` | Lookup |  |
| 32 | Parent Revenues | `fldfbXf8Dw6Q1zWiL` | Lookup |  |
| 33 | Ultimate Parent Company | `fldkecnUX1x0YIrHE` | Link→Stakeholders_Compa..(1) |  |
| 34 | U Parent Latest Financials | `fld2kH7JZf0xkfKH1` | Lookup |  |
| 35 | U_Parent_Currency | `fldb9tnJVw8E6QSI5` | Lookup |  |
| 36 | U_Parent_EBITDA | `fld1prBjXTYt6dhXa` | Lookup |  |
| 37 | U_Parent_Debt / EBITDA | `fld37IC4wRbQOcvMA` | Lookup |  |
| 38 | U_Parent_Revenues | `fldPAhFdwohB04HUE` | Lookup |  |
| 39 | Creation Date | `fldf0qiaTEQ0kYZqb` | CreatedTime |  |
| 40 | Update Date | `fldeQA4OE4loBXcRz` | ModifiedTime |  |
| 41 | Children_Companies | `fldyLCkTaP8hOXn30` | Link→Stakeholders_Compa..(n) |  |
| 42 | Company_Logo | `fldZx8nRJdGqHOKiw` | Attachments |  |
| 43 | Business Units | `fldTS0EXfmBYkDxkc` | Link→Stakeholders_Busin..(n) |  |
| 44 | Contacts | `fldb0auT2qhqTugrc` | Lookup |  |
| 45 | Config_Certificates | `fldbNeEImVsEkV224` | Link→Config_Certificates(n) |  |
| 46 | Pipedrive_ID | `fld0OKxtgyr0MLnUq` | Text | ID original de la organización en Pipedrive para trazabilida |
| 47 | Source | `fldiTFfi6bEszI0aH` | MultiSelect | Origen de la compañía en el CRM |
| 48 | GICS_Sectors_Rollup | `fldgOU0xOhYBCvrYB` | Rollup |  |
| 49 | GICS_Industries_Rollup | `fldj6NRvuRO9qDkKq` | Rollup |  |
| 50 | GICS_Subindustries_Rollup | `fldKRaAOqGF2uVzVN` | Rollup |  |
| 51 | From field: Ultimate_Parent_Co | `fldNhcQB4YkyHqc1K` | Link→Stakeholders_Compa..(n) |  |
| 52 | Stakeholders_Companies_Financi | `fld5zdHuT2IsinUsx` | Link→Stakeholders_Compa..(n) |  |
| 53 | Source_Extractions | `fldorLYZxfipbMcJi` | Link→Source_Extractions(n) |  |
| 54 | FEI_Status | `fldVZcjpAMdtgZAOb` | Select | Estado de elegibilidad FEI de la empresa. Determina si calif |
| 55 | FEI_Criteria_Met | `fld38u15eaiiesceW` | MultiSelect | Criterios FEI específicos que cumple la empresa. Múltiples c |
| 56 | FEI_Confidence | `fldHza1asHDQKhjqm` | Percent | Nivel de confianza en la evaluación FEI (0-100%). Calculado  |
| 57 | FEI_Last_Check | `fld8uRn0ClqrWCdKD` | Date | Fecha de la última verificación de elegibilidad FEI. Debe re |
| 58 | FEI_Notes | `fld3vUuTM7UYykrbK` | Long Text | Notas adicionales sobre la evaluación FEI, excepciones, o do |
| 59 | Company_Certificates | `fldqpfAdKxmxTD1Z4` | Link→Company_Certificates(n) |  |

**Opciones Select:**

- **Source:** `Research`, `Internal Referral`, `Web Scraping`, `Web Form`, `Partner Referral`, `LinkedIn Outreach`, `Event`, `CRM Migration`, `Phone Call`, `Other`, `Source`
- **FEI_Status:** `Unknown`, `Pending_Review`, `Eligible`, `Not_Eligible`, `Partially_Eligible`, `Expired`
- **FEI_Criteria_Met:** `1.1_Cleantech_Prize`, `1.2_Clean_Energy_Patent`, `1.3_Eco_Label`, `1.4_Green_Business_90`, `1.5_Green_Business_Model`, `1.6_Environmental_Certificate`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| HQ Country | Config_Countries | Stakeholders_Compani |  |
| Currency | Config_Currencies | Stakeholders_Compani | ✓ |
| Parent Company | Stakeholders_Companies | Children_Companies | ✓ |
| Ultimate Parent Company | Stakeholders_Companies | From field: Ultimate | ✓ |
| Children_Companies | Stakeholders_Companies | Parent Company |  |
| Business Units | Stakeholders_Business_Uni | Company |  |
| Config_Certificates | Config_Certificates | Companies |  |
| From field: Ultimate_Pare | Stakeholders_Companies | Ultimate Parent Comp |  |
| Stakeholders_Companies_Fi | Stakeholders_Companies_Fi | Company |  |
| Source_Extractions | Source_Extractions | Target_Company |  |
| Company_Certificates | Company_Certificates | Company |  |

**Lookups:**

- **Latest Financials Year**: via `Stakeholders_Compani` → `Yearly Results - Com`
- **Latest Available Year**: via `Stakeholders_Compani` → `Year`
- **EBITDA**: via `Stakeholders_Compani` → `EBITDA`
- **Debt / EBITDA**: via `Stakeholders_Compani` → `Debt / EBITDA`
- **Revenues**: via `Stakeholders_Compani` → `Annual_Revenues`
- **Parent Latest Financials**: via `Parent Company` → `Latest Financials Ye`
- **Parent Currency**: via `Parent Company` → `Currency`
- **Parent EBITDA**: via `Parent Company` → `EBITDA`
- **Parent Debt / EBITDA**: via `Parent Company` → `Debt / EBITDA`
- **Parent Revenues**: via `Parent Company` → `Revenues`
- **U Parent Latest Financials**: via `Ultimate Parent Comp` → `Latest Financials Ye`
- **U_Parent_Currency**: via `Ultimate Parent Comp` → `Currency`
- **U_Parent_EBITDA**: via `Ultimate Parent Comp` → `EBITDA`
- **U_Parent_Debt / EBITDA**: via `Ultimate Parent Comp` → `Debt / EBITDA`
- **U_Parent_Revenues**: via `Ultimate Parent Comp` → `Revenues`
- **Contacts**: via `Business Units` → `Business Unit Contac`

**Rollups:**

- **Company_Type**: via `Business Units` → `Business_Unit_Type_N`
- **Sector**: via `Business Units` → `Sector_Names`
- **Activities**: via `Business Units` → `Activities_Names`
- **Focus Regions**: via `Business Units` → `Focus Region`
- **Focus Countries**: via `Business Units` → `Focus_Countries_Name`
- **GICS_Sectors_Rollup**: via `Business Units` → `GICS Sector`
- **GICS_Industries_Rollup**: via `Business Units` → `GICS Industry`
- **GICS_Subindustries_Rollup**: via `Business Units` → `GICS Subindustry`

**Campos AI:**

- **GICS Sectors AI**: `*** TASK ***
Extract, deduplicate, and sort all un
...`
- **GICS Industries AI**: `*** TASK ***
Extract, deduplicate, and sort all un
...`
- **GICS Subindustries AI**: `*** TASK ***
Extract, deduplicate, and sort all un
...`

---

### 2. Stakeholders_Companies_Financials

**ID:** `tblYiuZOi2VGRXqgA` | **Campos:** 13

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Yearly Results - Company | `fldGciO4h9XmpPyqk` | Formula | Concatenates the Year and Company fields with a space in bet |
| 2 | Year | `fldtFQK6pnOGg8NiT` | Text |  |
| 3 | Company | `fld6cJ1oSRiDzDTH6` | Link→Stakeholders_Compa..(1) |  |
| 4 | Company_Currency | `fld7Z2RN1DwMQs0cY` | Lookup |  |
| 5 | Annual_Revenues | `fld5B70kDv5mxDnmz` | Number |  |
| 6 | EBITDA | `fldyKupWEWhoBSP1I` | Number |  |
| 7 | Depreciation | `flditYESbQwvfoX52` | Number |  |
| 8 | Impairment | `fldwiAK9N74UqZCRo` | Number |  |
| 9 | EBIT | `fld0vQKBrPU37AFe5` | Number |  |
| 10 | FCF | `fld47tJBqJfHlNBMj` | Number |  |
| 11 | Net_Financial_Debt | `fldAbKTlEtTlMW2SA` | Number |  |
| 12 | Debt / EBITDA | `fldjfnA6iVZdwwY4Z` | Formula | Calculates the ratio of Net Financial Debt to EBITDA, blank  |
| 13 | Interest Coverage | `fldcQVUZ0tC8CmASj` | Formula | Calculates the ratio of EBIT to Net Financial Debt, blank if |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Company | Stakeholders_Companies | Stakeholders_Compani | ✓ |

**Fórmulas:**

- **Yearly Results - Company** ✓: `{fldtFQK6pnOGg8NiT} & " - " & {fld6cJ1oSRiDzDTH6}`
- **Debt / EBITDA** ✓: `IF({fldyKupWEWhoBSP1I} != 0, {fldAbKTlEtTlMW2SA} / {fldyKupWEWhoBSP1I}, BLANK())`
- **Interest Coverage** ✓: `IF({fldAbKTlEtTlMW2SA} != 0, {fld0vQKBrPU37AFe5} / {fldAbKTlEtTlMW2SA}, BLANK())`

**Lookups:**

- **Company_Currency**: via `Company` → `Currency`

---

### 3. Stakeholders_Business_Units

**ID:** `tblbBsypFvEnooHlr` | **Campos:** 38

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Business Unit Name | `fldrcFl2yl9ZeVbtW` | Text | A business unit is a team (or team of teams) of a company th |
| 2 | Company | `fldwOiPSVOdeRuIIJ` | Link→Stakeholders_Compa..(1) |  |
| 3 | Business Unit Type | `fldddMbIJ1cyQz6Ut` | Link→Config_Stakeholder..(n) | The business unit type identifies which market role the busi |
| 4 | Sector | `fldqhylfII6O9tJnd` | Link→Config_Sector_And_..(1) | The sector is the category applied to the business focus of  |
| 5 | Sector_Formula | `fldGTP0Ok69Wokvsy` | Formula |  |
| 6 | Activities | `fld5QXiROXeJw0LVx` | Link→Config_Sector_And_..(n) | The activities are the subcategory of business operations th |
| 7 | Focus Region | `fldJP1OgYxEgSmanj` | MultiSelect |  |
| 8 | Focus Countries | `fldhg7U43jc6UDNtG` | Link→Config_Countries(n) |  |
| 9 | Business Unit Contacts | `fldLYlKr4gmjDiXeA` | Link→Stakeholders_Conta..(n) |  |
| 10 | GICS AI Summary | `fld2lG6Q14GiQ9NER` | AI |  |
| 11 | GICS Sector | `fldhHSTO6MR2GMVva` | AI | This field is created automatically by AI. It can be edited  |
| 12 | GICS Industry | `fldXbSsvRapRrIwOC` | AI | This field is created automatically by AI. It can be edited  |
| 13 | GICS Subindustry | `fldGOGeS64n2AJfOk` | AI | This field is created automatically by AI. It can be edited  |
| 14 | Additional Info | `fldaHfKYyvw4fc0oO` | Rich Text |  |
| 15 | Creation Date | `fldrvgDGryCSGVF0U` | CreatedTime |  |
| 16 | Last Update Date | `fldKWDLHVCULsiMdz` | ModifiedTime |  |
| 17 | Record Status | `fldJhTwJFUY576ZdB` | Select |  |
| 18 | Company Logo | `fldKSo5sDgYw7YZeX` | Lookup |  |
| 19 | Main Currency | `fldQC8u63vi1tBIHC` | Link→Config_Currencies(n) |  |
| 20 | Ticket Size Minimum | `fldjJgE49UbJLsW3u` | Number |  |
| 21 | Ticket Size Maximum | `fldmU9ZxftIVReJJr` | Number |  |
| 22 | Trust Level | `fldNSLKOxJ5uTcxAJ` | Percent |  |
| 23 | Debt Operations of Interest | `fldKL9NrPkap8so3g` | MultiSelect |  |
| 24 | M&A - Renovables - Tamaño de i | `fldxo5TAGV6MPv03C` | Text | Indica el rango, o múltiples rangos, de potencia que deben t |
| 25 | M&A - Renovables - Status de i | `fldcLihVvSK4PPl5B` | Text | Para los proyectos de energía renovable, este campo indica e |
| 26 | M&A - Renovables - Interés de  | `fldcegB5HYWquP8wc` | Text | Cómo se conseguirá rentabilizar el negocio. |
| 27 | Business_Unit_Type_Names | `fld5PKHw7wXJQ8UgD` | Lookup |  |
| 28 | Sector_Names | `fld6mjaJNYq5FtDCD` | Lookup |  |
| 29 | Activities_Names | `fld7ayPbKNYYDkHeR` | Lookup |  |
| 30 | Focus_Countries_Name | `fldSGOcoaBp8URANS` | Lookup |  |
| 31 | Company_Home_URL | `fldNByYOWvoUzhAs0` | Lookup |  |
| 32 | Company_Linkedin_URL | `fldvHaPr8S9eJfNWd` | Lookup |  |
| 33 | Config_Activities | `flddnKI79EcwFAHv5` | Link→Config_Activities(n) |  |
| 34 | Campaign_Targets | `fldKdevQzGADcGlXJ` | Link→Campaign_Targets(n) |  |
| 35 | Source_Extractions | `fldeZmDmf1ju2yce5` | Link→Source_Extractions(n) |  |
| 36 | Last_Outreach_Date | `fldLZPFsTnCFpCriq` | Date | Fecha del último contacto de campaña. Usado para calcular co |
| 37 | Is_In_Cooling_Off | `fldD98dTOCUrchFA7` | Checkbox | TRUE si han pasado menos de 90 días desde Last_Outreach_Date |
| 38 | Revenue_Percentage | `fldDZ1uZ3e6UpTlab` | Percent | Porcentaje de revenue de la empresa que representa esta BU. Usado para criterio FEI 1.4 (≥90%) |

**Opciones Select:**

- **Focus Region:** `AMER`, `EMEA`, `APAC`
- **Record Status:** `Active`, `Inactive`
- **Debt Operations of Interest:** `Junior`, `Senior Bridge`, `Senior L/T`, `Mezzanine`, `Subordinated`, `Unitranche`, `Convertible`, `HoldCo`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Company | Stakeholders_Companies | Business Units | ✓ |
| Business Unit Type | Config_Stakeholder_SubTyp | Stakeholders_Busines |  |
| Sector | Config_Sector_And_Activit | Relationships_Level_ | ✓ |
| Activities | Config_Sector_And_Activit | Relationships_Level_ |  |
| Focus Countries | Config_Countries | Stakeholders_Busines |  |
| Business Unit Contacts | Stakeholders_Contacts | Business Unit |  |
| Main Currency | Config_Currencies | Stakeholders_Busines |  |
| Config_Activities | Config_Activities | Business_Units |  |
| Campaign_Targets | Campaign_Targets | Business_Unit |  |
| Source_Extractions | Source_Extractions | Target_Business_Unit |  |

**Fórmulas:**

- **Sector_Formula** ✓: `{fldqhylfII6O9tJnd}`

**Lookups:**

- **Company Logo**: via `Company` → `Company_Logo`
- **Business_Unit_Type_Names**: via `Business Unit Type` → `Name`
- **Sector_Names**: via `Sector` → `Name`
- **Activities_Names**: via `Activities` → `Name`
- **Focus_Countries_Name**: via `Focus Countries` → `Name`
- **Company_Home_URL**: via `Company` → `Home URL`
- **Company_Linkedin_URL**: via `Company` → `Linkedin URL`

**Campos AI:**

- **GICS AI Summary**: `*** ROLE ***
You are a financial analyst specializ
- **Parent Company:** ...`
- **GICS Sector**: `*** TASK ***
Extract the Sector value(s) from a GI
...`
- **GICS Industry**: `*** TASK ***
Extract the Industry value(s) from a 
...`
- **GICS Subindustry**: `*** TASK ***
Extract the Sub-Industry value(s) fro
...`

---

### 4. Stakeholders_Contacts

**ID:** `tblfErIdCjpMkXK17` | **Campos:** 33

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Full Name | `fldsvzjNGXEWybta7` | Formula | Combines the first and last name fields with a space. |
| 2 | First Name | `fldB8pziOzHr497Qv` | Text |  |
| 3 | Last Name | `fldf9d2QGtovb61rd` | Text |  |
| 4 | Email | `fldEeqx5EiGaDdN6C` | Email |  |
| 5 | Phoner Number | `fldSoyxV4vFnFtNSM` | Phone |  |
| 6 | Linkedin URL | `fldOgb4YX2BWw5UFH` | URL |  |
| 7 | Key Person | `fldc0Az3Vlf6Rk683` | Select |  |
| 8 | Role | `fldV2aedlZ542QL8j` | Text |  |
| 9 | Role Level | `fld6j4LRqyZdzx8b4` | Link→Config_General_Fie..(1) |  |
| 10 | Business Unit | `fldCDSDNQj5rlKpJ8` | Link→Stakeholders_Busin..(n) |  |
| 11 | Company (from Assigned_Busines | `fldW9uYKs3VBiVQQP` | Lookup |  |
| 12 | Company_Logo | `fldYrNUPmoSiHby6f` | Lookup |  |
| 13 | Contact Type | `fldBJ0IGtlqRTZkHc` | Link→Config_Stakeholder..(n) |  |
| 14 | Has Responded Before | `fld53Fcjg7Xxgn6QU` | Checkbox |  |
| 15 | Focus Countries | `fldvII7gcJ1IVMtsa` | Link→Config_Countries(n) |  |
| 16 | Focus Region | `fldMPzqpbzWuN25au` | MultiSelect |  |
| 17 | Sector | `fldSCgzHyhX25NC5C` | Link→Config_Sector_And_..(n) |  |
| 18 | Sector_Formula | `fld9zQzt1u0YNaYbD` | Formula |  |
| 19 | Activities | `fldLXKP9SdLdtT1e8` | Link→Config_Sector_And_..(n) |  |
| 20 | GICS Sector | `fldyqVFSk8fF9KEZP` | Text |  |
| 21 | GICS Industry | `fldSFo8y8wGCa8U1d` | Text |  |
| 22 | GICS Subindustry | `fldtOfqkToO8pZzdg` | Text |  |
| 23 | Contact Languages | `fldmUAt8QbFj4G8UN` | Link→Config_Languages(n) |  |
| 24 | Communication Interests | `fldn29Dt3WKZkwCUF` | MultiSelect |  |
| 25 | Description | `fldlYYfhZneAItof8` | Rich Text |  |
| 26 | Professional Experience | `fldNvAAQEUbQYYrAn` | Rich Text |  |
| 27 | Educational Background | `fldvL39LimmP4e0Mc` | Rich Text |  |
| 28 | Age | `fldIwVuwh1QfdfAMR` | Number |  |
| 29 | Creation Date | `fldqxh41eZFPquyvJ` | CreatedTime |  |
| 30 | Update Date | `fldpnrQFZpadHtLW7` | ModifiedTime |  |
| 31 | Validator | `fldfk5nYeDeOaC5qv` | AI |  |
| 32 | Campaign_Targets | `flda1jv9LpoCCBfvF` | Link→Campaign_Targets(n) |  |
| 33 | Source_Extractions | `fldcEaWE66xggw5ME` | Link→Source_Extractions(n) |  |

**Opciones Select:**

- **Key Person:** `Yes`, `No`
- **Focus Region:** `AMER`, `EMEA`, `APAC`
- **Communication Interests:** `Newsletter_General`, `Newsletter_Renewables`, `Newsletter_Corporate_Deals`, `Newsletter_RealEstate_Deals`, `Event_Invitations`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Role Level | Config_General_Fields | Contacts | ✓ |
| Business Unit | Stakeholders_Business_Uni | Business Unit Contac |  |
| Contact Type | Config_Stakeholder_SubTyp | Stakeholders_Contact |  |
| Focus Countries | Config_Countries | Stakeholders_Contact |  |
| Sector | Config_Sector_And_Activit | Stakeholders_Contact |  |
| Activities | Config_Sector_And_Activit | Stakeholders_Contact |  |
| Contact Languages | Config_Languages | Stakeholders_Contact |  |
| Campaign_Targets | Campaign_Targets | Contact |  |
| Source_Extractions | Source_Extractions | Target_Contact |  |

**Fórmulas:**

- **Full Name** ✓: `{fldB8pziOzHr497Qv} & " " & {fldf9d2QGtovb61rd}`
- **Sector_Formula** ✓: `{fldSCgzHyhX25NC5C}`

**Lookups:**

- **Company (from Assigned_Business_Unit)**: via `Business Unit` → `Company`
- **Company_Logo**: via `Business Unit` → `Company Logo`

**Campos AI:**

- **Validator**: `sd
...`

---

### 5. Opportunities - Global Overview

**ID:** `tblMA730dbXi0Qgqf` | **Campos:** 21

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Opportunity Name | `fld1t7zALZO3f97E9` | Text |  |
| 2 | Type | `fldCVWCaI75n9lDQC` | Select |  |
| 3 | Type of asset | `fldkdiS6JsbXAh61Z` | Select |  |
| 4 | Currency | `fldkf5cBoYIJj13ne` | Text |  |
| 5 | Ticket size | `fldd0A7mTnhA5V9iS` | Number |  |
| 6 | Opportunity Status (High level | `fldWsJ7sjf1BQ0jgm` | Select |  |
| 7 | Country | `fldSpa1yi3ljyIe1H` | MultiSelect |  |
| 8 | Sector | `fldsktqGSY2utWtL4` | MultiSelect |  |
| 9 | Description | `fldW675uMGn2RlXZD` | Long Text |  |
| 10 | Region | `fldY91aG9YZd7cWLC` | Select |  |
| 11 | Promoters | `fldSCc3FfiyyTJd5i` | Text |  |
| 12 | Contact Persons (from Promoter | `fldyNVonjZ6OPAmJv` | Lookup |  |
| 13 | Distribution Race | `fldgmiRIxjgZjSzp7` | Link→Distribution - Inv..(n) |  |
| 14 | Distribution Waves | `fldq1P5js6ul7Jy8G` | Link→Distribution - Waves(n) |  |
| 15 | Q&A | `fldmg660fyyP1I04t` | Link→Opportunity - Q&A(n) |  |
| 16 | Distribution Investor Selectio | `fld9e6tCjtncufJca` | Link→Investor Workstreams(n) |  |
| 17 | Deadline | `flddfK6ybmeAIkfx4` | Date |  |
| 18 | Email Activity | `fldWMwCWTdI6bKaKQ` | Link→Config - Email Act..(n) |  |
| 19 | Internal - Tasks | `fldzgyDA01Z6yMdlB` | Text |  |
| 20 | Internal - Tasks 2 | `fldQ280qlIphspfI7` | Link→Internal - Tasks(n) |  |
| 21 | Internal - Tasks copy | `fldN8MMTsMpHJpCZz` | Link→Internal - Initiat..(n) |  |

**Opciones Select:**

- **Type:** `Debt`, `M&A`
- **Type of asset:** `Renewable`, `IT Infrastructure`
- **Opportunity Status (High level):** `Origination`, `Structuration`, `Distribution`
- **Country:** `Spain`
- **Sector:** `Energy`, `IT Infrastructure`
- **Region:** `Europe`, `Asia`, `America`, `Africa`, `Oceania`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Distribution Race | Distribution - Investor S | Opportunities |  |
| Distribution Waves | Distribution - Waves | Opportunity |  |
| Q&A | Opportunity - Q&A | Opportunity |  |
| Distribution Investor Sel | Investor Workstreams | Opportunities |  |
| Email Activity | Config - Email Activity | Opportunity |  |
| Internal - Tasks 2 | Internal - Tasks | Opportunity |  |
| Internal - Tasks copy | Internal - Initiatives | Opportunity |  |

**Lookups:**

- **Contact Persons (from Promoters)**: via `Promoters` → `N/A`

---

### 6. Opportunity - Adaptation

**ID:** `tbl6LzYm86cOmOZp9` | **Campos:** 6

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fld8VrilYf9ZfWRmS` | Text |  |
| 2 | Notes | `fldvDbPAyJaHsYuIC` | Long Text |  |
| 3 | Assignee | `fldoV7pGWSuqnbO8z` | User |  |
| 4 | Status | `fld9jq4X5PRKMIiIa` | Select |  |
| 5 | Attachments | `fldkXN05ew4tPXtyT` | Attachments |  |
| 6 | Attachment Summary | `fldYUc6hMVTia7uJ1` | AI | An AI generated summary of the Attachments field. Upload fil |

**Opciones Select:**

- **Status:** `Todo`, `In progress`, `Done`

**Campos AI:**

- **Attachment Summary**: `You are a professional document analyst specializi...`

---

### 7. Opportunity - Q&A

**ID:** `tblUJJNmQweYnYJC7` | **Campos:** 11

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Question | `fld5PMLb07noDIgoJ` | Long Text |  |
| 2 | Answer | `fld3JobxbLgRG8ZlA` | Long Text |  |
| 3 | Company_Type | `fldGjZvPbx6tU8OHd` | Link→Config - Variables(n) |  |
| 4 | Company | `fldXwAiRCSP1EGPdh` | Text |  |
| 5 | Opportunity | `fldKyvOK8Lh3T9Ysk` | Link→Opportunities - Gl..(1) |  |
| 6 | Reused answer | `fldRD1tW1zwcZa84K` | Checkbox |  |
| 7 | Used Answer | `fldA7kWqL1Xi5Lu1G` | Link→Opportunity - Q&A(n) |  |
| 8 | Hidden field: Used Answer | `flddGRDJWqZCeIjqJ` | Link→Opportunity - Q&A(n) |  |
| 9 | AI Generated | `fldGWK7J8hALsDKfx` | Checkbox |  |
| 10 | Reviewed | `fldmcW1pop1GbIe0p` | Checkbox |  |
| 11 | Source of Answer | `fldF59yHxeniz64iA` | Long Text |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Company_Type | Config - Variables | Q&A |  |
| Opportunity | Opportunities - Global Ov | Q&A | ✓ |
| Used Answer | Opportunity - Q&A | Hidden field: Used A |  |
| Hidden field: Used Answer | Opportunity - Q&A | Used Answer |  |

---

### 8. Distribution - Investor Selection

**ID:** `tblilY0MuymFNdUGA` | **Campos:** 28

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldqows77nGCbTKTH` | Text |  |
| 2 | Opportunities | `fldPkYigQe0Wc4Ano` | Link→Opportunities - Gl..(n) |  |
| 3 | Developers | `fldDf7DoeOrGukN15` | Lookup |  |
| 4 | Investor | `fldyYwd0qeXwmWgHw` | Text |  |
| 5 | Investor Country | `fldsmMuIVB5rPjKNa` | Lookup |  |
| 6 | Distribution Decision | `flddXQIiWURjDgYFR` | Select |  |
| 7 | Wave | `fldpJa0dcRorQR2jr` | Number |  |
| 8 | Wave Link | `flduDSVDW3479JDi7` | Link→Distribution - Waves(1) |  |
| 9 | Wave status | `fldBzDKvwME5mumws` | Lookup |  |
| 10 | Chosen Contact | `fldHJO2FbzRLffct2` | Text |  |
| 11 | IA Recommendation Reasoning | `fld4JYUPTN55o1SPF` | AI |  |
| 12 | Opportunity - Ticket Size | `fldOK2vtD5dGn7Lwb` | Lookup |  |
| 13 | Investor - Min Ticket | `fldJncHYkN82R8nAd` | Lookup |  |
| 14 | Investor - Sector | `fld7LhJBkVqIdEiFH` | Lookup |  |
| 15 | Investor - Previous feedback | `fldsr2fB66Qi06kG7` | Lookup |  |
| 16 | Investor - Financials | `fldkILp43j1kEOv5K` | Lookup |  |
| 17 | Opportunity - Type of asset | `flddFVaJWiHOjmoTH` | Lookup |  |
| 18 | Opportunity - Financials | `fldENCllli3Bqhmip` | Lookup |  |
| 19 | IA scorer | `fldH2isnfog7bosXj` | Percent |  |
| 20 | Created | `fldty55wTQJJxEk1G` | CreatedTime |  |
| 21 | Last Modified | `fld5R0ye9wE32DnQj` | ModifiedTime |  |
| 22 | Tipo de operación | `fld7T24Mfk1XYgHyg` | Text |  |
| 23 | Nurture need | `fld9Qd4DNh5LOzAtr` | Text |  |
| 24 | Nivel de confianza | `fld3zEKBL4R4TObM6` | Text |  |
| 25 | Garantías | `flddRvUOFj0iyJ5zp` | Text |  |
| 26 | Customized email (section) | `fldoHqMPZKEY7ryY4` | Long Text |  |
| 27 | Customized Body - Which inject | `fldjxxzo0Wlbt29f1` | Number |  |
| 28 | Customized email | `fldZWC7ZrE11kcrHS` | Checkbox |  |

**Opciones Select:**

- **Distribution Decision:** `Send`, `Ignore`, `Future consideration`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Opportunities | Opportunities - Global Ov | Distribution Race |  |
| Wave Link | Distribution - Waves | Assigned Investor Pr | ✓ |

**Lookups:**

- **Developers**: via `Opportunities` → `Promoters`
- **Investor Country**: via `Investor` → `N/A`
- **Wave status**: via `Wave Link` → `Status`
- **Opportunity - Ticket Size**: via `Opportunities` → `Ticket size`
- **Investor - Min Ticket**: via `Investor` → `N/A`
- **Investor - Sector**: via `Investor` → `N/A`
- **Investor - Previous feedback**: via `Investor` → `N/A`
- **Investor - Financials**: via `Investor` → `N/A`
- **Opportunity - Type of asset**: via `Opportunities` → `Type of asset`
- **Opportunity - Financials**: via `Opportunities` → `Type`

**Campos AI:**

- **IA Recommendation Reasoning**: `*** WHO YOU ARE ***
You are a highly senior financ
Opportunity Name: ...`

---

### 9. Distribution - Waves

**ID:** `tblQlEQn1vBmN2MKQ` | **Campos:** 23

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldzdU70TFOLIDp4n` | Text |  |
| 2 | Opportunity | `fldYpZF030W8XrO7c` | Link→Opportunities - Gl..(1) |  |
| 3 | # Targeted Investors | `fldLGfCtE3l1F9FJz` | Rollup |  |
| 4 | Wave Number | `fld0gfHQcBlCO8au0` | Number |  |
| 5 | Automatic launch | `fldPPktztnWd4RSQp` | Checkbox |  |
| 6 | Launch date | `fldU2SVQcIl5Pflx9` | Date |  |
| 7 | Email Template - Presentation | `fldauKmw8O2kDhksO` | Link→Config - Email Tem..(n) |  |
| 8 | Status | `fldgug6Ncb2h5tweU` | Select |  |
| 9 | Launch Wave CTA | `fldyvaYqZU6UVTywG` | Text |  |
| 10 | Comments | `fldWYIq6KNQobdJrK` | Long Text |  |
| 11 | Assigned Investor Presentation | `fldL5EoAH6XD40thl` | Link→Distribution - Inv..(n) |  |
| 12 | Created Time | `fldr3OFZoQkM3f7fi` | CreatedTime |  |
| 13 | Investor (from Assigned Invest | `fldFf17hTB7OgPboG` | Lookup |  |
| 14 | Generated workstreams | `fldxtx88ToknvPDxX` | Link→Investor Workstreams(n) |  |
| 15 | Email Activity | `fldAng4EoXPLB7emJ` | Link→Config - Email Act..(n) |  |
| 16 | # Received Emails | `fldWZkpsnHGg08NYd` | Rollup |  |
| 17 | # Opened Emails | `fldRfVSggd6Xv9ObT` | Rollup |  |
| 18 | # Answered | `fldytF2n1MwHF8Xwg` | Rollup |  |
| 19 | # Interested | `fldKXCOGhRqYBhqd0` | Rollup |  |
| 20 | Global Sentiment (IA) | `fldsUfpySgWHjbNDE` | Long Text |  |
| 21 | % Opened | `fldhHsKrijLecl1TK` | Formula |  |
| 22 | % Answered | `fldrZVq1wYG9cfFHr` | Formula |  |
| 23 | % Interested | `fldaMMIPKTGiPQyWC` | Formula |  |

**Opciones Select:**

- **Status:** `Not launched yet`, `In progress`, `Successful launch`, `Error - Not launched`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Opportunity | Opportunities - Global Ov | Distribution Waves | ✓ |
| Email Template - Presenta | Config - Email Templates | Distribution Waves |  |
| Assigned Investor Present | Distribution - Investor S | Wave Link |  |
| Generated workstreams | Investor Workstreams | Distribution - Waves |  |
| Email Activity | Config - Email Activity | Wave link |  |

**Fórmulas:**

- **% Opened** ✓: `IF({fldLGfCtE3l1F9FJz}, {fldRfVSggd6Xv9ObT} / {fldLGfCtE3l1F9FJz}, BLANK())`
- **% Answered** ✓: `IF({fldRfVSggd6Xv9ObT}, {fldytF2n1MwHF8Xwg} / {fldRfVSggd6Xv9ObT}, BLANK())`
- **% Interested** ✓: `IF({fldytF2n1MwHF8Xwg}, {fldKXCOGhRqYBhqd0} / {fldytF2n1MwHF8Xwg}, BLANK())`

**Lookups:**

- **Investor (from Assigned Investor Presentations)**: via `Assigned Investor Pr` → `Investor`

**Rollups:**

- **# Targeted Investors**: via `Assigned Investor Pr` → `Name`
- **# Received Emails**: via `Email Activity` → `Received the wave em`
- **# Opened Emails**: via `Email Activity` → `Opened/read the wave`
- **# Answered**: via `Generated workstream` → `Flow Phase`
- **# Interested**: via `Generated workstream` → `Flow Phase`

---

### 10. Investor Workstreams

**ID:** `tblbdMCGgItSYA4tD` | **Campos:** 19

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldjgk41TxNPmgUGK` | Text |  |
| 2 | Opportunities | `fldIcMUaCo79nrKar` | Link→Opportunities - Gl..(n) |  |
| 3 | Promoters (from Opportunities) | `fldw7Vfi0YyTFHXO8` | Lookup |  |
| 4 | Investor | `fldrQkPUco4Jxjquz` | Text |  |
| 5 | Rejection Feedback | `fldKo8QjKF7Mi7ebd` | Rich Text |  |
| 6 | Status - Last Time of Modifica | `fldPPXEf5Ap7hJVz2` | ModifiedTime |  |
| 7 | Global Flow Status | `fldRYcjEmudqL0lqg` | Select |  |
| 8 | Flow Phase | `fld3aKV8DNdwe6dcb` | Select |  |
| 9 | Status Duration (days) | `fldQ9uyAjAXj9lgAb` | Formula |  |
| 10 | Whose turn is it? | `fldUPTvzlcekYXgaW` | Select |  |
| 11 | Last email read by investor | `fldswdg0oI71JQBdL` | Select |  |
| 12 | Urgent action | `fldAfUE9Hq109VIfu` | Select |  |
| 13 | Next Task Owner | `fldtIzexx4kJRoDAk` | Link→Config - Variables(n) |  |
| 14 | Workstream Owner | `fldTrlvqciZcVYq5G` | Link→Config - Variables(n) |  |
| 15 | Internal - Tasks | `fldqmgyCJh7Q9gfNe` | Link→Internal - Tasks(n) |  |
| 16 | Ticket Size | `fldKpXC570bzMLC7k` | Lookup |  |
| 17 | Type of assets | `fldumwqQALdXbrf7O` | Lookup |  |
| 18 | Distribution - Waves | `fldiEvj3Ck7FauPVP` | Link→Distribution - Waves(n) |  |
| 19 | Internal - Tasks copy | `fldnsUk5Ql7gqgC4G` | Text |  |

**Opciones Select:**

- **Global Flow Status:** `Paused`, `Ongoing`, `Rejected`, `Success`
- **Flow Phase:** `To send`, `Waiting reply`, `Declined consideration`, `NDA`, `Declined NDA`, `Analysis & Q&A`, `Declined TermSheet`, `TermSheet Signed`, `Stand-by`
- **Whose turn is it?:** `Alter5`, `Investor`
- **Last email read by investor:** `True`, `False`
- **Urgent action:** `True`, `False`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Opportunities | Opportunities - Global Ov | Distribution Investo |  |
| Next Task Owner | Config - Variables | Investor Workstreams |  |
| Workstream Owner | Config - Variables | Investor Workstreams |  |
| Internal - Tasks | Internal - Tasks | Investor Workstream |  |
| Distribution - Waves | Distribution - Waves | Generated workstream |  |

**Fórmulas:**

- **Status Duration (days)** ✓: `DATETIME_DIFF(NOW(), {fldPPXEf5Ap7hJVz2}, 'minutes')`

**Lookups:**

- **Promoters (from Opportunities)**: via `Opportunities` → `Promoters`
- **Ticket Size**: via `Opportunities` → `Ticket size`
- **Type of assets**: via `Opportunities` → `Type of asset`

---

### 11. Internal - Initiatives

**ID:** `tbl20Bnxshef5bgCe` | **Campos:** 17

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Initiative Title | `fldScHB51Y5UVtAuK` | Text |  |
| 2 | Scope | `fldNhPGid8Y412MsD` | Select |  |
| 3 | Type | `fldcRVQ77zSQ3axpv` | Select |  |
| 4 | Priority | `fldfbsLqC3N7hFt5y` | Select |  |
| 5 | Description | `fldXp1lSlOMq0RIHC` | Long Text |  |
| 6 | Initiative Leader | `flda8PC0Jbm9t3MKj` | Link→Config - Users(n) |  |
| 7 | Status | `fldqSmwWjqBHLdFB3` | Select |  |
| 8 | Parent Initiative | `fldhypZIYc3joenD2` | Link→Internal - Initiat..(n) |  |
| 9 | Children Initiatives | `fldx4xfjQGgR7JjVE` | Link→Internal - Initiat..(n) |  |
| 10 | Start Date | `fldXoc5DD6zBMigZ8` | Date |  |
| 11 | Targeted End Date | `fldEC8d5Hx48aBobR` | Date |  |
| 12 | Attachments | `fld2cjfVu1F6Sd3sS` | Attachments |  |
| 13 | Additional Information | `fldfCcHnCrzZv9naE` | Long Text |  |
| 14 | Main Team | `fldWl60nmd4LowqeY` | MultiSelect |  |
| 15 | Opportunity | `fldSIuFoGqgoHEtW1` | Link→Opportunities - Gl..(n) |  |
| 16 | Created | `fldXK2QQKF1zW0JR3` | CreatedTime |  |
| 17 | Last modified time | `fld4HamHCtT3W3CsB` | ModifiedTime |  |

**Opciones Select:**

- **Scope:** `Small Initiative`, `Long Horizon`
- **Type:** `Revenue Operations`, `Marketing Strategy`, `Technology Development`
- **Priority:** `Critical`, `High`, `Medium`, `Low`
- **Status:** `To do`, `In progress`, `Standby`, `Done`, `Discarded`
- **Main Team:** `Product & Tech`, `Origination`, `Structuring`, `Distribution`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Initiative Leader | Config - Users | Internal - Tasks cop |  |
| Parent Initiative | Internal - Initiatives | Children Initiatives |  |
| Children Initiatives | Internal - Initiatives | Parent Initiative |  |
| Opportunity | Opportunities - Global Ov | Internal - Tasks cop |  |

---

### 12. Internal - Tasks

**ID:** `tbl5UXB4ldePObTlM` | **Campos:** 24

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Task Title | `fldV63PCUU5uEtddi` | Text |  |
| 2 | Priority | `fldi5OZXvZNH0F6O6` | Select |  |
| 3 | Description | `fld0jnzpeKM0JRlqa` | Long Text |  |
| 4 | Owner | `fldd2bQxC7mJc3ptR` | Link→Config - Users(n) |  |
| 5 | Reminder by email | `fldJyJpcFsmGIxZSH` | Lookup |  |
| 6 | Reminder by Calendar | `fldcYuCWE0I5KSTXF` | Lookup |  |
| 7 | Status | `fldtMIKtcmBhudikB` | Select |  |
| 8 | Deadline | `fld0iyjaw2zbviTIG` | DateTime |  |
| 9 | Reminder | `fldeIflMyFIqsFSfW` | Checkbox |  |
| 10 | Attachments | `fld56FtsnXFGBdGbq` | Attachments |  |
| 11 | Additional Information | `fldiwyVUvnzze90Tc` | Long Text |  |
| 12 | Team | `fldZfseUf94l7w3Xw` | MultiSelect |  |
| 13 | Opportunity | `fldVCQTVzmgYqE6Fz` | Link→Opportunities - Gl..(n) |  |
| 14 | Sponsor | `fldwz8BoWuv2KS2D5` | Text |  |
| 15 | Investor | `fldSwPqSKGYG3cSA8` | Text |  |
| 16 | Needs first (Tasks) | `fldiDDq4i3N0LR1VI` | Link→Internal - Tasks(n) |  |
| 17 | Created | `fld0Eo4nDB19F0mAB` | CreatedTime |  |
| 18 | Last modified time | `fld7BwAevpTDF3fb9` | ModifiedTime |  |
| 19 | Completion Date | `fldJHz6UOBB8xU071` | DateTime |  |
| 20 | Days Since Creation (If Active | `fldUKpql2RDqysKXn` | Formula |  |
| 21 | From field: Related Tasks | `fld2pLlQ3fJPm8tnK` | Link→Internal - Tasks(n) |  |
| 22 | Investor Workstream | `fldiekc6eKEOodzEt` | Link→Investor Workstreams(n) |  |
| 23 | Email (from Owner) | `fldIbPQEDd0X6V2iX` | Lookup |  |
| 24 | Manual sort | `fld4TzfbSKfKL7oNf` | manualSort |  |

**Opciones Select:**

- **Priority:** `Critical`, `High`, `Medium`, `Low`
- **Status:** `To do`, `In progress`, `Standby`, `Done`, `Discarded`
- **Team:** `Origination`, `Structuring`, `Distribution`, `Product & Tech`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Owner | Config - Users | Internal - Tasks |  |
| Opportunity | Opportunities - Global Ov | Internal - Tasks 2 |  |
| Needs first (Tasks) | Internal - Tasks | From field: Related  |  |
| From field: Related Tasks | Internal - Tasks | Needs first (Tasks) |  |
| Investor Workstream | Investor Workstreams | Internal - Tasks |  |

**Fórmulas:**

- **Days Since Creation (If Active)** ✓: `IF(
  AND({fldtMIKtcmBhudikB} != "Done", {fldtMIKtcmBhudikB} != "Discarded"),
  DATETIME_DIFF(TODAY(), {fld0Eo4nDB19F0mAB}, "days"),
  BLANK()
)`

**Lookups:**

- **Reminder by email**: via `Owner` → `Remind by Email`
- **Reminder by Calendar**: via `Owner` → `Remind by Calendar`
- **Email (from Owner)**: via `Owner` → `Email`

---

### 13. Help & Feedback - Suggestions

**ID:** `tblh42ZHkAoptEXlZ` | **Campos:** 9

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Suggestion | `fldw7uHGu1LlJGMY5` | Text |  |
| 2 | Area | `fldBvJQzKlxTNI951` | Select |  |
| 3 | Idea description | `fldJxjSGAqyozWWVx` | Long Text |  |
| 4 | Priority | `fldeS5ULDrieHMuIg` | Select |  |
| 5 | Submitted By | `fldh4kX7asV4JR2f0` | Link→Config - Users(n) |  |
| 6 | Type | `fld6s8uu88Ah3qZ8d` | Select |  |
| 7 | Status | `fldKOeMARBhDRUtzl` | Select |  |
| 8 | Submission Date | `fldtqduipV3maKnUR` | CreatedTime |  |
| 9 | Answer by Tech | `fldMCXSZtTxbbzQ9G` | Long Text |  |

**Opciones Select:**

- **Area:** `Distribution Launch`, `Investor Workstreams`, `DB of Companies and Contacts`, `Task Management`, `Opportunities`, `Origination`
- **Priority:** `Urgent`, `High`, `Medium`, `Low`
- **Type:** `Improvement`, `New Feature`, `Bug`
- **Status:** `To review`, `In study`, `In progress`, `Done`, `Rejected`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Submitted By | Config - Users | Help & Feedback - Su |  |

---

### 14. Config - Email Templates

**ID:** `tblywzQ8HedD1nHKF` | **Campos:** 16

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fld1KVo8IjNKhUTRm` | Text |  |
| 2 | Phase | `fldDnGI1UviG7sQYw` | Select |  |
| 3 | Activity | `fldpTz4WADzKAoRVK` | Select |  |
| 4 | Default Template | `flddo6PNmyHaksQzj` | Checkbox |  |
| 5 | AI Customization | `fldr2RrJdukHN1ax0` | Checkbox |  |
| 6 | Description | `fldXyBCbaFLpcTTGz` | Long Text |  |
| 7 | Subject - ES | `fldOZ0b2tvnt13ZEd` | Long Text |  |
| 8 | Subject - EN | `fldCKOSTn70MNl5Zf` | AI |  |
| 9 | Subject - IT | `fldzpB8LLk1LgityG` | AI |  |
| 10 | Body 1 - ES | `fldfuOzZb0p92r2eB` | Long Text |  |
| 11 | Body 1 - EN | `fldXSi9vY6DQ33cID` | AI |  |
| 12 | Body 1 - IT | `fldobmkup53xgrvLl` | AI |  |
| 13 | Body 2 - ES | `fld5ZNMUSxQAegt2T` | Rich Text |  |
| 14 | Body 2 - EN | `fld0pEtmdEwCFT1MM` | AI |  |
| 15 | Body 2 - IT | `fld4CJukyF9Vo98oM` | AI |  |
| 16 | Distribution Waves | `fldqa4SEBbIIB5apM` | Link→Distribution - Waves(n) |  |

**Opciones Select:**

- **Phase:** `Origination`, `Structuration`, `Distribution`
- **Activity:** `Present opportunity`, `Thank despite rejection`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Distribution Waves | Distribution - Waves | Email Template - Pre |  |

**Campos AI:**

- **Subject - EN**: `You are a professional translator specializing in 

Output:
...`
- **Subject - IT**: `You are a professional translator with expertise i

Output:
...`
- **Body 1 - EN**: `You are a professional translator specializing in 

Output:
...`
- **Body 1 - IT**: `You are a professional translator specializing in 

Output:
...`
- **Body 2 - EN**: `You are a professional translator specializing in 

Output:
...`
- **Body 2 - IT**: `You are a professional translator specializing in 

Output:
...`

---

### 15. Config - Email Activity

**ID:** `tblFY14T1zGnPpitb` | **Campos:** 17

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | ID email | `fldni7YvFKSJm1IjK` | Text |  |
| 2 | Date | `fldZO19Kwga3xkR3q` | Date |  |
| 3 | Sender | `fldDjoXZpZSgGYpSh` | Text |  |
| 4 | Recipient(s) | `fldYGa7o6ZoaB36lc` | Text |  |
| 5 | Language | `fldAjPeSkQwwLv5Hy` | Select |  |
| 6 | Phase | `fld3UJzDYWyPjrQzI` | Select |  |
| 7 | Activity | `fldPI3iwsFZp2r8ZR` | Select |  |
| 8 | Company | `fldPP3fP9Rd2SVt0Q` | Text |  |
| 9 | Opportunity | `fldetA4KUFYz2LjFo` | Link→Opportunities - Gl..(1) |  |
| 10 | Wave link | `fldjgJiOiz1Oagne6` | Link→Distribution - Waves(1) |  |
| 11 | Subject | `fldoZTyq8gwjmtGwk` | Text |  |
| 12 | Body | `fldxGx9FPdjynJVHZ` | Long Text |  |
| 13 | Received the wave email | `fldYBKlFr4wjuxslz` | Checkbox |  |
| 14 | Opened/read the wave email | `fld5RX4mdOzH8fcnG` | Checkbox |  |
| 15 | Date - Received the wave email | `fldPZQ9WFCsIgkngJ` | DateTime |  |
| 16 | Date - Opened/read the wave em | `fldPjFjHmJ2SKJfNz` | DateTime |  |
| 17 | Campaign_Targets | `fldEpOhisC8aA0r35` | Link→Campaign_Targets(n) |  |

**Opciones Select:**

- **Language:** `EN`, `ES`, `IT`
- **Phase:** `Origination`, `Structuration`, `Distribution`
- **Activity:** `Present opportunity`, `Thank despite rejection`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Opportunity | Opportunities - Global Ov | Email Activity | ✓ |
| Wave link | Distribution - Waves | Email Activity | ✓ |
| Campaign_Targets | Campaign_Targets | Email_Activity |  |

---

### 16. Config - Users

**ID:** `tblb3kyXSnXS0GPjy` | **Campos:** 12

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldQBWehpb7TSz7kn` | Text |  |
| 2 | Email | `fldjX9aOGrXTQ1bjA` | Email |  |
| 3 | Type | `fld9LEmVJwYry6Kgy` | Select |  |
| 4 | Internal - Tasks | `fldR9Uqr7CVTzvAYW` | Link→Internal - Tasks(n) |  |
| 5 | Remind by Email | `fldr4A9rd5UN806Py` | Select |  |
| 6 | Remind by Calendar | `fldDrRx6UvPnnmhoO` | Select |  |
| 7 | Internal - Tasks copy | `fldPcZMzd0sabKy4A` | Text |  |
| 8 | Help & Feedback - Suggestions | `fldkToZ3OK6LJvEoU` | Link→Help & Feedback - ..(n) |  |
| 9 | Internal - Tasks copy | `fldOfycUeGVjQvXfo` | Link→Internal - Initiat..(n) |  |
| 10 | Origination_Campaigns | `fldBNeusAjEUc7HYN` | Link→Origination_Campai..(n) |  |
| 11 | Source_Extractions | `fldDUUzhzNFdOcw3h` | Link→Source_Extractions(n) |  |
| 12 | Source_Extractions | `fldCIdLL87t1QjisH` | Link→Source_Extractions(n) |  |

**Opciones Select:**

- **Type:** `Internal`, `External`
- **Remind by Email:** `True`, `False`
- **Remind by Calendar:** `True`, `False`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Internal - Tasks | Internal - Tasks | Owner |  |
| Help & Feedback - Suggest | Help & Feedback - Suggest | Submitted By |  |
| Internal - Tasks copy | Internal - Initiatives | Initiative Leader |  |
| Origination_Campaigns | Origination_Campaigns | Owner |  |
| Source_Extractions | Source_Extractions | Extracted_By |  |
| Source_Extractions | Source_Extractions | Validated_By |  |

---

### 17. Config - Variables

**ID:** `tblVWtmUZSjitPmOS` | **Campos:** 7

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Values | `fldWGflr27Icdw5sw` | Text |  |
| 2 | Field | `fld55MVFtM2b2yXxF` | Text |  |
| 3 | Q&A | `fldUNQ9tTHkat9lpR` | Link→Opportunity - Q&A(n) |  |
| 4 | Investor Workstreams | `fldAlpeCCZCHYz8J5` | Link→Investor Workstreams(n) |  |
| 5 | Investor Workstreams copy | `fldAvaw7HarNY14aJ` | Link→Investor Workstreams(n) |  |
| 6 | Internal - Tasks | `fldCDIny6LNqKnpS1` | Text |  |
| 7 | Help & Feedback - Suggestions | `fld4DqEYvennzTmXs` | Text |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Q&A | Opportunity - Q&A | Company_Type |  |
| Investor Workstreams | Investor Workstreams | Workstream Owner |  |
| Investor Workstreams copy | Investor Workstreams | Next Task Owner |  |

---

### 18. Config_General_Fields

**ID:** `tblMrM2E16GXu1VGi` | **Campos:** 3

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Values | `fld587uSSAynIMNUL` | Text |  |
| 2 | Field | `fldXyLoXO8zaLvckH` | Text |  |
| 3 | Contacts | `fldUErRvW27JkWSLc` | Link→Stakeholders_Conta..(n) |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Contacts | Stakeholders_Contacts | Role Level |  |

---

### 19. Config_Currencies

**ID:** `tblTYGiICGBehlRZg` | **Campos:** 6

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Currency Name | `fldTN5zQ9r6VPFmI2` | Text |  |
| 2 | Currency ISO Two-letter Code | `fldRpa6Sxrk6w1fza` | Text |  |
| 3 | Common_Use | `fld1vg3DYMch8eECN` | Checkbox |  |
| 4 | Countries | `fldueeAJVnl9RaHGI` | Link→Config_Countries(n) |  |
| 5 | Stakeholders_Companies | `fld59e5eFfDTJdwep` | Link→Stakeholders_Compa..(n) |  |
| 6 | Stakeholders_Business_Units | `fldttq4kfezcSlk7N` | Link→Stakeholders_Busin..(n) |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Countries | Config_Countries | N/A |  |
| Stakeholders_Companies | Stakeholders_Companies | Currency |  |
| Stakeholders_Business_Uni | Stakeholders_Business_Uni | Main Currency |  |

---

### 20. Config_Countries

**ID:** `tblC4FxquuxAbf43R` | **Campos:** 21

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldbJwGQivqJmd2vj` | Text |  |
| 2 | ISO Code | `fldv4eoZgkM2JaIGq` | Text |  |
| 3 | Region | `fldD2MqBrnoIrEEYj` | Select |  |
| 4 | UTC Region | `fldP1HPmmbhNErk80` | Select |  |
| 5 | Created | `fld3uNz6tWwtetYnx` | DateTime |  |
| 6 | Last Modified | `fldAyboVw8hV7Odp3` | DateTime |  |
| 7 | Related_Currencies | `fld59YheM5ktoRaXk` | Link→Config_Currencies(n) |  |
| 8 | Stakeholders_Companies | `fld6FpyFxkmfC4o3q` | Text |  |
| 9 | Stakeholders_Companies 2 | `fldJzPn9kbPSxa8Iw` | Link→Stakeholders_Compa..(n) |  |
| 10 | Capital City | `fldbsedDCxED8xwhD` | Text |  |
| 11 | Stakeholders_Business_Units | `fldnUSq8LYjrxUuDl` | Link→Stakeholders_Busin..(n) |  |
| 12 | Stakeholders_Business_Units co | `fldY1zbiKBM7rCNLp` | Text |  |
| 13 | Stakeholders_Business_Units co | `fld7RtQYQE15KLhLu` | Text |  |
| 14 | Stakeholders_Business_Units co | `fld2e7MnV48pG8nQP` | Text |  |
| 15 | Stakeholders_Business_Units co | `fldNtJVRDp8V3iihr` | Text |  |
| 16 | Stakeholders_Contacts | `fldWGNsI6NOwZWLdJ` | Link→Stakeholders_Conta..(n) |  |
| 17 | Config_Certificates | `fldztjIKadoE97MX8` | Link→Config_Certificates(n) |  |
| 18 | Config_Certificates 2 | `fldgVYP88kTvAB3Gq` | Link→Config_Certificates(n) |  |
| 19 | Market_Context | `fldieOAeVKNHIsr07` | Link→Market_Context(n) |  |
| 20 | Origination_Campaigns | `fldwJ6oOpwxpXHNGD` | Link→Origination_Campai..(n) |  |
| 21 | Config_Sources | `fld1WskmkT9L2Dv6c` | Link→Config_Sources(n) |  |

**Opciones Select:**

- **Region:** `Europe`, `North America`, `Oceania`, `South America`, `Asia`, `Africa`
- **UTC Region:** `UTC+12`, `UTC+11`, `UTC+10`, `UTC+9`, `UTC+8`, `UTC+7`, `UTC+6`, `UTC+5`, `UTC+4`, `UTC+3`, `UTC+2`, `UTC+1`, `UTC+0`, `UTC-1`, `UTC-1` (+12 más)

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Related_Currencies | Config_Currencies | N/A |  |
| Stakeholders_Companies 2 | Stakeholders_Companies | HQ Country |  |
| Stakeholders_Business_Uni | Stakeholders_Business_Uni | Focus Countries |  |
| Stakeholders_Contacts | Stakeholders_Contacts | Focus Countries |  |
| Config_Certificates | Config_Certificates | Eligible_Countries |  |
| Config_Certificates 2 | Config_Certificates | Valid_Countries |  |
| Market_Context | Market_Context | Affected_Countries |  |
| Origination_Campaigns | Origination_Campaigns | Target_Countries |  |
| Config_Sources | Config_Sources | Countries_Covered |  |

---

### 21. Config_Stakeholder_Types

**ID:** `tbl7R8gjn6KcBYGQj` | **Campos:** 5

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldGZmQLKTBAI85vW` | Text |  |
| 2 | Sub Types | `fldebnFzq91bOWqkt` | Link→Config_Stakeholder..(n) |  |
| 3 | Created | `fld0BetkzowlDJBSU` | DateTime |  |
| 4 | Last Modified | `fldz0zLRiI45pGhdG` | DateTime |  |
| 5 | Stakeholders_Contacts | `fldn4HsXQXB5uymkC` | Text |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Sub Types | Config_Stakeholder_SubTyp | N/A |  |

---

### 22. Config_Stakeholder_SubTypes

**ID:** `tblV2bTQNIYcVULi3` | **Campos:** 9

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldfjzfUR02Az9oW9` | Text |  |
| 2 | Dependencies | `fldQ4l6Mp67mDtAjs` | Link→Config_Stakeholder..(n) |  |
| 3 | Created | `fldKKi1j1x2pVZT7F` | DateTime |  |
| 4 | Last Modified | `fld34AgE1CO0eCszy` | DateTime |  |
| 5 | Stakeholders_Contacts | `fldkWJacCOWfXt3Q8` | Link→Stakeholders_Conta..(n) |  |
| 6 | Stakeholders_Companies | `fldCjk6UwUG9g8zhf` | Text |  |
| 7 | Stakeholders_Business_Units | `fldPljzmRpvT6jJiX` | Link→Stakeholders_Busin..(n) |  |
| 8 | Stakeholders_Business_Units co | `fldJCJgt0c6g2dWOO` | Text |  |
| 9 | Origination_Campaigns | `fldOFK7kCwnZE4CoK` | Link→Origination_Campai..(n) |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Dependencies | Config_Stakeholder_Types | N/A |  |
| Stakeholders_Contacts | Stakeholders_Contacts | Contact Type |  |
| Stakeholders_Business_Uni | Stakeholders_Business_Uni | Business Unit Type |  |
| Origination_Campaigns | Origination_Campaigns | Target_Stakeholder_T |  |

---

### 23. Config_Sector_And_Activities

**ID:** `tblo8dIgdxNMJmcx7` | **Campos:** 14

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fldmviGcGjOeCPteT` | Text |  |
| 2 | Parent | `fldlRCwT7OnS7Wy61` | Text |  |
| 3 | Level | `fldJG2dlHcCa4lbUe` | Select |  |
| 4 | Relationships_Level_1 | `fldRvcd5e6JpiaDED` | Link→Stakeholders_Busin..(n) |  |
| 5 | Relationships_Level_2 | `fldlPZgwfNo59w8eN` | Link→Stakeholders_Busin..(n) |  |
| 6 | Stakeholders_Contacts | `fldadQ1sx8yZRNumD` | Link→Stakeholders_Conta..(n) |  |
| 7 | Stakeholders_Contacts 2 | `fldmUELg0pwAa8iSK` | Link→Stakeholders_Conta..(n) |  |
| 8 | Relationships_Level_1 copy | `fldrRM8iSgqe5pBaf` | Text |  |
| 9 | Relationships_Level_1 copy 2 | `fldUz9US6HMYZtnjV` | Text |  |
| 10 | Relationships_Level_1 copy 3 | `fldodx7lxCAx7zc1c` | Text |  |
| 11 | Stakeholders_Contacts copy | `fldsbaHgppQGQldZu` | Text |  |
| 12 | Market_Context | `fldY7yPsHWq9IE58o` | Link→Market_Context(n) |  |
| 13 | Origination_Campaigns | `fldOCRmyepVTSOucN` | Link→Origination_Campai..(n) |  |
| 14 | Config_Sources | `fldvcW2m5yCQyS3o0` | Link→Config_Sources(n) |  |

**Opciones Select:**

- **Level:** `Sector`, `Activities`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Relationships_Level_1 | Stakeholders_Business_Uni | Sector |  |
| Relationships_Level_2 | Stakeholders_Business_Uni | Activities |  |
| Stakeholders_Contacts | Stakeholders_Contacts | Sector |  |
| Stakeholders_Contacts 2 | Stakeholders_Contacts | Activities |  |
| Market_Context | Market_Context | Affected_Sectors |  |
| Origination_Campaigns | Origination_Campaigns | Target_Sectors |  |
| Config_Sources | Config_Sources | Sectors_Covered |  |

---

### 24. Config_Languages

**ID:** `tblXrAdnl3O16AAyE` | **Campos:** 6

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Language | `fldMQUd7PuC2xBKOf` | Text |  |
| 2 | ISO Code | `fldLlBYWOwf4cmBoo` | Text |  |
| 3 | Related_Countries | `fldKXNEhR58unfCG3` | Link→Config_Countries(n) |  |
| 4 | Created | `fldDV2Y5VUtq2qTbc` | DateTime |  |
| 5 | Last Modified | `fldkxS4CSatPMdsot` | DateTime |  |
| 6 | Stakeholders_Contacts | `fldCLFVXcaG4OhH71` | Link→Stakeholders_Conta..(n) |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Related_Countries | Config_Countries | N/A |  |
| Stakeholders_Contacts | Stakeholders_Contacts | Contact Languages |  |

---

### 25. GICS_Standard

**ID:** `tblNjc8JHcC6jT9H9` | **Campos:** 8
**Descripción:** Estándar oficial de clasificación industrial GICS con 4 niveles jerárquicos (Sector, Industry Group, Industry, Sub-Industry). Sirve como referencia maestra para clasificar Activities y Business Units 

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Sector | `fldTfyjquIJptTvA9` | Text | Nombre oficial del sector/industry/sub-industry en inglés se |
| 2 | Sector_Code | `fldFGNTZXWPE3GiZi` | Link→Config_Activities(n) |  |
| 3 | IndustryGroup_Code copy | `fldfTwJ4Ly1DMigUn` | Text |  |
| 4 | Industry Group | `fldqg8thx5azZ9NTu` | Text |  |
| 5 | Industry_Code | `fldmYhtgLd2Ja8L9o` | Text |  |
| 6 | Industry | `fldYq8nuotLTPugGt` | Text |  |
| 7 | Sub-Industry_Code | `fldcZp3B23zXmdw3K` | Text |  |
| 8 | Sub-Industry | `fldeT6zRIPLsZQTbp` | Text |  |

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Sector_Code | Config_Activities | GICS_Sub_Industry |  |

---

### 26. Config_Certificates

**ID:** `tblQ5HZtmVe2ft9xH` | **Campos:** 11
**Descripción:** Catálogo de certificaciones, estándares ISO, eco-labels y premios que pueden tener las empresas. Permite tracking de sostenibilidad, validez geográfica y elegibilidad para garantías FEI/InvestEU.

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Certificate_Name | `fldJf03i94SxYJ1pj` | Text | Nombre oficial del certificado, ISO, eco-label o premio (3-5 |
| 2 | Certificate_Type | `fldXWCzGxKspCLef7` | MultiSelect | Tipo de certificación |
| 3 | Certificate_Origin | `fldcIvHSqBc77Li5U` | Select | Tipo de entidad que concede el certificado |
| 4 | URL | `flda8c73vwRLdCXRU` | URL | Página web oficial del certificado/estándar |
| 5 | Description | `fldu0aKjrNR630vk0` | Rich Text | Descripción del certificado y criterios de obtención (200-30 |
| 6 | FEI_Eligible | `fldZYcfaOMMS8rUB2` | Checkbox | Indica si cumple criterios para aplicar garantía Fondo Europ |
| 7 | Sustainability_Criteria | `fldcRov3Kc2vKYvYt` | Long Text | Criterios de sostenibilidad que valida este certificado |
| 8 | Eligible_Countries | `fldL6bBDHHq5t5gfT` | Link→Config_Countries(n) | Países en los que se puede obtener/solicitar el certificado |
| 9 | Valid_Countries | `fld70Q2InixSMvqsX` | Link→Config_Countries(n) | Países en los que el certificado tiene validez/reconocimient |
| 10 | Companies | `fldoAs4RlkqwAn3c6` | Link→Stakeholders_Compa..(n) | Empresas que poseen este certificado |
| 11 | Company_Certificates | `fldidWXxiBuaAbQwN` | Link→Company_Certificates(n) |  |

**Opciones Select:**

- **Certificate_Type:** `ISO`, `Eco-label`, `Prize`, `PI`
- **Certificate_Origin:** `Private`, `NGO`, `Government`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Eligible_Countries | Config_Countries | Config_Certificates |  |
| Valid_Countries | Config_Countries | Config_Certificates  |  |
| Companies | Stakeholders_Companies | Config_Certificates |  |
| Company_Certificates | Company_Certificates | Certificate_Type |  |

---

### 27. Config_Activities

**ID:** `tblcOpprnVmtsMbH4` | **Campos:** 10
**Descripción:** Catálogo de actividades específicas que puede realizar una empresa, clasificadas según el estándar GICS (Sub-Industry nivel 4). Incluye información sobre elegibilidad FEI/InvestEU, actividades verdes 

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Activity_Name | `fldIMTBOcb47ai97r` | Text | Nombre de la actividad específica (en español o idioma origi |
| 2 | Activity_Name_EN | `fldKkXGqg3iDathN0` | Text | Nombre de la actividad en inglés |
| 3 | Activity_Type | `fldA1z78UTJe5GoMN` | MultiSelect | Clasificación del tipo de relación con Alter5 |
| 4 | Activity_Sub_Type | `fld5QI2PEaYrVYduU` | MultiSelect | Subtipo detallado de la relación |
| 5 | FEI_Eligible | `fldFOWaouV3pPpZdR` | Checkbox | Indica si la actividad cumple criterios para garantía FEI/In |
| 6 | Is_Green_Activity | `fld5P5XCmvxGX5zH8` | Checkbox | Indica si es una actividad verde según taxonomía EU |
| 7 | EU_Taxonomy_Category | `fldfymxGFvEhHDCHw` | Select | Categoría de taxonomía EU si es actividad verde |
| 8 | Description | `fldhhFOJSrkHclbis` | Rich Text | Descripción detallada de la actividad y ejemplos de empresas |
| 9 | GICS_Sub_Industry | `fldWdshLWcL91BrdW` | Link→GICS_Standard(n) | Clasificación GICS Sub-Industry (nivel 4) a la que pertenece |
| 10 | Business_Units | `fldFtj8R3rVwNHrz3` | Link→Stakeholders_Busin..(n) | Business Units que realizan esta actividad |

**Opciones Select:**

- **Activity_Type:** `Sponsor`, `Investor`, `Partner`, `Service_Provider`
- **Activity_Sub_Type:** `Sponsor_Seller`, `Sponsor_Operating`, `Investor_Debt`, `Investor_Equity`, `Partner`, `Service_Provider`
- **EU_Taxonomy_Category:** `Climate_Mitigation`, `Climate_Adaptation`, `Water_Protection`, `Circular_Economy`, `Pollution_Prevention`, `Biodiversity`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| GICS_Sub_Industry | GICS_Standard | Sector_Code |  |
| Business_Units | Stakeholders_Business_Uni | Config_Activities |  |

---

### 28. Market_Context

**ID:** `tblkE6YhMlxn9XXX5` | **Campos:** 19
**Descripción:** Repositorio de inteligencia de mercado: noticias sectoriales, cambios regulatorios, movimientos empresariales, M&A y otros eventos que pueden servir como trigger para campañas de originación. El agent

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Context_Title | `fld6e7BHO9eKWL2m0` | Text | Título descriptivo del evento/noticia/cambio regulatorio |
| 2 | Context_Type | `fldl4JUDnznJ0jbHP` | Select | Categoría del contexto de mercado |
| 3 | Source_URL | `fldrkFQcovZzh5VER` | URL | URL de la fuente original de la información |
| 4 | Source_Name | `fldFPpNyjJuiXw0kJ` | Text | Nombre de la fuente (ej: Reuters, BOE, Financial Times) |
| 5 | Publication_Date | `fldMqbroY0j8xAcN8` | Date | Fecha de publicación del evento/noticia |
| 6 | Summary | `fld3vxTpETjggyozB` | Rich Text | Resumen ejecutivo del contexto y su relevancia para originac |
| 7 | Key_Implications | `fldHLDHrVflPzZEe0` | Rich Text | Implicaciones clave para el negocio de financiación de deuda |
| 8 | Campaign_Potential | `fldzf400oERFtimBS` | Rating | Potencial para generar campañas de originación (1-5) |
| 9 | Status | `fldTSwNYaFCYMN2Bt` | Select | Estado del procesamiento del contexto |
| 10 | Relevance_Expiry | `flden4dljrQSR5Mld` | Date | Fecha estimada hasta la cual el contexto sigue siendo releva |
| 11 | Tags | `fld2ASfCovMT5dZu5` | MultiSelect | Etiquetas para facilitar búsqueda y filtrado |
| 12 | AI_Generated | `fldR8yAK9qU6r67lj` | Checkbox | Indica si el contexto fue encontrado/generado por el agente  |
| 13 | Notes | `fldtBFfxLnYplhayZ` | Rich Text | Notas adicionales del equipo sobre este contexto |
| 14 | Affected_Sectors | `fldbj45oHTaWap8A5` | Link→Config_Sector_And_..(n) | Sectores y actividades afectados por este contexto de mercad |
| 15 | Affected_Countries | `fldiGPvAi2vQFrOms` | Link→Config_Countries(n) | Países afectados por este contexto de mercado |
| 16 | Origination_Campaigns | `fldnM2RSuR6yRDDDq` | Link→Origination_Campai..(n) |  |
| 17 | Created Time | `fldZ4TToxiUjHHwcI` | CreatedTime |  |
| 18 | Last Modified | `flde1QeRqanFDHBEi` | ModifiedTime |  |
| 19 | Source_Extractions | `fldFDk0VlvfmTZYww` | Link→Source_Extractions(n) |  |

**Opciones Select:**

- **Context_Type:** `News_Sectoral`, `Regulatory_Change`, `M&A_Movement`, `Earnings_Report`, `Funding_Round`, `Leadership_Change`, `Market_Trend`, `Policy_Announcement`, `Industry_Event`, `Other`
- **Status:** `New`, `Analyzed`, `Campaign_Created`, `Archived`, `Discarded`
- **Tags:** `Renewables`, `Infrastructure`, `Real_Estate`, `Technology`, `Healthcare`, `ESG`, `FEI_Eligible`, `Cross_Border`, `Refinancing`, `Growth_Capital`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Affected_Sectors | Config_Sector_And_Activit | Market_Context |  |
| Affected_Countries | Config_Countries | Market_Context |  |
| Origination_Campaigns | Origination_Campaigns | Market_Context |  |
| Source_Extractions | Source_Extractions | Target_Market_Contex |  |

---

### 29. Origination_Campaigns

**ID:** `tbl0B5YGXveYzyADI` | **Campos:** 23
**Descripción:** Tabla maestra de campañas de originación. Define la configuración general de cada campaña incluyendo targeting por sectores, países y tipos de stakeholder. Conecta con Market_Context como trigger y ge

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Campaign_Name | `fld4jRij88sR67xZI` | Text | Nombre interno descriptivo de la campaña (debe ser único y d |
| 2 | Description | `flddAgLjzUMofuCCF` | Rich Text | Descripción detallada del objetivo y alcance de la campaña |
| 3 | Campaign_Size | `fldfUzmKxhuowqqTQ` | Select | Tamaño y tipo de segmentación de la campaña |
| 4 | Status | `fldV8ZQO4UMGVD6CT` | Select | Estado actual de la campaña |
| 5 | Product_Line | `fldGkiulw5ynBfixM` | MultiSelect | Línea de producto que se promociona en la campaña |
| 6 | Scheduled_Start_Date | `fldsSFYfDKIpuQFnX` | Date | Fecha programada para inicio de la campaña |
| 7 | Scheduled_End_Date | `fldg4320nhYpnopDZ` | Date | Fecha programada para fin de la campaña |
| 8 | Campaign_Rationale | `fldDBd06rWNFmNmTs` | Rich Text | Justificación estratégica de por qué se crea esta campaña (p |
| 9 | Email_Subject_Template_ES | `fldPYfxPnhrDuz46M` | Text | Plantilla de asunto de email en español |
| 10 | Email_Subject_Template_EN | `fldu9QpiLH9P1ZNFz` | Text | Plantilla de asunto de email en inglés |
| 11 | Email_Body_Template_ES | `fldz6t0pTdPFbKVtP` | Rich Text | Plantilla base del cuerpo del email en español (con placehol |
| 12 | Email_Body_Template_EN | `fldhtxiC2uHnjf8W9` | Rich Text | Plantilla base del cuerpo del email en inglés (con placehold |
| 13 | Target_Ticket_Min | `fldFGGz8IPZnhwdlJ` | Number | Tamaño mínimo de ticket objetivo (en EUR) |
| 14 | Target_Ticket_Max | `fldYo2bpB8QxjlR0c` | Number | Tamaño máximo de ticket objetivo (en EUR) |
| 15 | Priority | `fldaCnwBMBfYp2pOt` | Select | Prioridad de ejecución de la campaña |
| 16 | AI_Generated | `fldRRtKgjRyO991SH` | Checkbox | Indica si la campaña fue generada por el agente IA |
| 17 | Notes | `fldluXqZGlSTzmayH` | Rich Text | Notas internas adicionales sobre la campaña |
| 18 | Market_Context | `fldB7BZaXkvO4w0Pw` | Link→Market_Context(n) | Contexto de mercado que motiva/trigger esta campaña |
| 19 | Target_Stakeholder_Types | `flddGkHXploEHiV75` | Link→Config_Stakeholder..(n) | Tipos de stakeholder objetivo (Investor_Debt, Sponsor_Operat |
| 20 | Target_Sectors | `fldv4yljMidf9Gqw1` | Link→Config_Sector_And_..(n) | Sectores y actividades objetivo de la campaña |
| 21 | Target_Countries | `fldIwGau3bZwGgIV3` | Link→Config_Countries(n) | Países objetivo de la campaña |
| 22 | Owner | `fldrA5YjXct4UFzug` | Link→Config - Users(n) | Responsable de la campaña |
| 23 | Campaign_Targets | `fldH2x2gIFQrVo3is` | Link→Campaign_Targets(n) |  |

**Opciones Select:**

- **Campaign_Size:** `Massive`, `Micro-Targeting`, `Personal`
- **Status:** `Draft`, `Pending_Review`, `Approved`, `Scheduled`, `Active`, `Paused`, `Completed`, `Cancelled`
- **Product_Line:** `Corporate_Debt`, `Project_Finance`, `M&A_Advisory`, `FEI_Guarantee`, `Refinancing`, `Bridge_Loan`
- **Priority:** `Critical`, `High`, `Medium`, `Low`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Market_Context | Market_Context | Origination_Campaign |  |
| Target_Stakeholder_Types | Config_Stakeholder_SubTyp | Origination_Campaign |  |
| Target_Sectors | Config_Sector_And_Activit | Origination_Campaign |  |
| Target_Countries | Config_Countries | Origination_Campaign |  |
| Owner | Config - Users | Origination_Campaign |  |
| Campaign_Targets | Campaign_Targets | Campaign |  |

---

### 30. Campaign_Targets

**ID:** `tblblROgAVEcWQ7WQ` | **Campos:** 20
**Descripción:** Registros individuales de cada Business Unit seleccionado para una campaña. Contiene la justificación de selección personalizada, el email adaptado a cada target, scoring de fit y tracking del estado 

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Target_Name | `fldL9UkpndZJl7Jln` | Text | Identificador del target (se genera automáticamente: Campaig |
| 2 | Selection_Justification | `fldX0Yb8PgjOUSb4q` | Rich Text | Justificación detallada de por qué se seleccionó este Busine |
| 3 | Personalization_Context | `fldh23ONjOWUO7yoU` | Rich Text | Contexto específico usado para personalizar el mensaje (noti |
| 4 | Personalized_Email_Subject | `fldpVFN3JQTNwfsu5` | Text | Asunto del email personalizado para este target |
| 5 | Personalized_Email_Body | `fldKLrufQL71l5gWP` | Rich Text | Cuerpo del email completamente personalizado para este Busin |
| 6 | Fit_Score | `fldvmDvYtLDDlMaOd` | Percent | Puntuación de fit entre la campaña y el Business Unit (0-100 |
| 7 | Status | `fld0FUxnxP7gftj5B` | Select | Estado del target en el proceso de campaña |
| 8 | Sent_Date | `fldIepgOOJaadqL2C` | DateTime | Fecha y hora de envío del email |
| 9 | Last_Interaction_Date | `fldAXCBy7kqef9KuT` | DateTime | Fecha de la última interacción (apertura, click, respuesta) |
| 10 | Response_Summary | `fldKyQCN8priavqD7` | Rich Text | Resumen de la respuesta recibida (si aplica) |
| 11 | Follow_Up_Required | `fldQWBapzlAhAX36E` | Checkbox | Indica si requiere seguimiento |
| 12 | Follow_Up_Notes | `fldoe4pOxUBFZGmTa` | Rich Text | Notas sobre el seguimiento requerido |
| 13 | AI_Confidence | `fld61Ui1vNKDUk2vP` | Percent | Nivel de confianza del agente IA en esta selección (0-100%) |
| 14 | Manual_Override | `fldbcMfEDJ9Hv3vj9` | Checkbox | Indica si un humano modificó la selección o contenido genera |
| 15 | Override_Notes | `fldn6RaLu0fquzdZl` | Rich Text | Notas explicando las modificaciones manuales realizadas |
| 16 | Campaign | `fldhSdahm4INjtOI1` | Link→Origination_Campai..(n) | Campaña a la que pertenece este target |
| 17 | Business_Unit | `fldqbbRiQx87Wis8H` | Link→Stakeholders_Busin..(n) | Business Unit seleccionado como target de la campaña |
| 18 | Contact | `fldGP9ex0wKhGNJl6` | Link→Stakeholders_Conta..(n) | Contacto seleccionado para recibir la comunicación |
| 19 | Email_Activity | `fld90h66w4y3BCfa3` | Link→Config - Email Act..(n) | Registro de actividad de email asociado (para tracking) |
| 20 | Source_Extractions | `fld6Crde3ts0u2dmF` | Link→Source_Extractions(n) |  |

**Opciones Select:**

- **Status:** `Pending_Review`, `Approved`, `Scheduled`, `Sent`, `Delivered`, `Opened`, `Clicked`, `Replied`, `Meeting_Scheduled`, `Converted`, `Bounced`, `Unsubscribed`, `Rejected`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Campaign | Origination_Campaigns | Campaign_Targets |  |
| Business_Unit | Stakeholders_Business_Uni | Campaign_Targets |  |
| Contact | Stakeholders_Contacts | Campaign_Targets |  |
| Email_Activity | Config - Email Activity | Campaign_Targets |  |
| Source_Extractions | Source_Extractions | Campaign_Target |  |

---

### 31. Config_Credit_Strategies

**ID:** `tbla0eiBSmhIg4lU7` | **Campos:** 3

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Name | `fld8DJkp73bY0vNm3` | Text |  |
| 2 | Common Use | `fldveaHyiXxyLEdSC` | Checkbox |  |
| 3 | Source of Credit | `fldy3hVFMQ4ZgcFG0` | Text |  |

---

### 32. Config_Sources

**ID:** `tbl4MEJa6mh1w3EG4` | **Campos:** 19
**Descripción:** Catálogo de fuentes de datos para extracción de información sobre empresas, contactos y mercado. Define qué fuentes están disponibles, su fiabilidad, cobertura y método de acceso.

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Source_Name | `fldDTKy3Py98SqEKG` | Text | Nombre único de la fuente de datos (3-25 caracteres) |
| 2 | Home_URL | `fldXkPsmWoINZK9bZ` | URL | URL principal de acceso a la fuente |
| 3 | Relevant_URLs | `fldZXwrOlWmI2Jqlh` | Long Text | URLs adicionales relevantes para consultas específicas |
| 4 | Source_Type | `fld2CCZuzVWY0JLBj` | Select | Tipo de publicación o fuente |
| 5 | Information_Type | `fldspeXlqjRjamjAx` | MultiSelect | Tipos de información disponibles en esta fuente |
| 6 | Related_Entities | `fld3dy5DzAhmSMHHl` | MultiSelect | Entidades sobre las que la fuente proporciona información |
| 7 | Countries_Covered | `fldtOZoGUxf2dsjCh` | Link→Config_Countries(n) | Países sobre los que la fuente tiene información |
| 8 | Sectors_Covered | `fldU51Kvywt2ayKww` | Link→Config_Sector_And_..(n) | Sectores que cubre la fuente |
| 9 | Reliability_Score | `fldgJMdk3PWBZptpS` | Rating | Puntuación de fiabilidad de la fuente (1-5 estrellas) |
| 10 | Data_Freshness | `fldRnZaFrsfjOaoXk` | Select | Frecuencia de actualización de los datos en la fuente |
| 11 | Access_Method | `fldfJO57Z6TmLjX32` | Select | Método de acceso a los datos de la fuente |
| 12 | Requires_Subscription | `fldCUp25fp4CvA7gj` | Checkbox | Indica si la fuente requiere suscripción de pago o login |
| 13 | API_Documentation_URL | `flduouWGlTnYWIiDM` | URL | URL de la documentación de API si aplica |
| 14 | Rate_Limits | `fldb3MNm8Dhnw8fGn` | Text | Límites de consultas (ej: 100/hora, 1000/día) |
| 15 | Is_Active | `fldrZvOhEF4Hfaxt3` | Checkbox | Indica si la fuente está activa y disponible para uso |
| 16 | Last_Verified | `fldJV5ju1lSbYoIqQ` | Date | Fecha de última verificación de disponibilidad |
| 17 | Description | `fldtEXXfkgiGERGjv` | Long Text | Descripción detallada de la fuente y su utilidad (200-300 ca |
| 18 | Usage_Notes | `fldhqyRJvuqhR1NqY` | Long Text | Notas sobre cómo usar la fuente, trucos, limitaciones conoci |
| 19 | Source_Extractions | `fld9OBhWUJLkCQ0UQ` | Link→Source_Extractions(n) |  |

**Opciones Select:**

- **Source_Type:** `Cluster`, `Official`, `Expert_Publication`, `Social_Media`, `Internal_Report`, `Press`, `Database`, `Registry`, `Association`
- **Information_Type:** `General`, `Financials`, `ESG`, `Ownership`, `Contacts`, `News`, `Legal`, `Certifications`, `M&A`, `Market_Data`
- **Related_Entities:** `Companies`, `Contacts`, `Market`
- **Data_Freshness:** `Real-time`, `Daily`, `Weekly`, `Monthly`, `Quarterly`, `Annual`
- **Access_Method:** `API`, `Web_Scraping`, `Manual`, `RSS`, `Database_Query`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Countries_Covered | Config_Countries | Config_Sources |  |
| Sectors_Covered | Config_Sector_And_Activit | Config_Sources |  |
| Source_Extractions | Source_Extractions | Source |  |

---

### 33. Source_Extractions

**ID:** `tblXX2Uqa0xQCtHSD` | **Campos:** 22
**Descripción:** Registro de cada extracción de datos realizada desde las fuentes configuradas. Proporciona trazabilidad completa de cuándo se usó cada fuente, qué datos se extrajeron, para qué entidad, y el estado de

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Extraction_Name | `fld3vBsvBJDpbpSSZ` | Text | Identificador de la extracción (auto-generado: Source + Date |
| 2 | Source | `fldX4yyOdGBVfd9rg` | Link→Config_Sources(n) | Fuente de datos utilizada para la extracción |
| 3 | Extraction_Date | `fldRd8WZGH5K9cXd7` | DateTime | Fecha y hora de la extracción |
| 4 | Extracted_By | `fldAKHAXYbftXzO4N` | Link→Config - Users(n) | Usuario o agente que realizó la extracción |
| 5 | Target_Company | `fld8WxB2IiftVvAGQ` | Link→Stakeholders_Compa..(n) | Empresa destino de los datos extraídos |
| 6 | Target_Business_Unit | `fldQSaOPpKvD6h2LY` | Link→Stakeholders_Busin..(n) | Unidad de negocio destino de los datos extraídos |
| 7 | Target_Contact | `fldspSyFrhTopYmfn` | Link→Stakeholders_Conta..(n) | Contacto destino de los datos extraídos |
| 8 | Target_Market_Context | `fldX3e8RGBrFUwIDq` | Link→Market_Context(n) | Contexto de mercado destino de los datos extraídos |
| 9 | Fields_Updated | `fldyTBYmN8HscvcqD` | MultiSelect | Campos que fueron actualizados con esta extracción |
| 10 | Extraction_URL | `flddVZXWx4Mm6FQvY` | URL | URL específica consultada para esta extracción |
| 11 | Raw_Data_Snapshot | `fldMcgLwNya5G7ury` | Long Text | Snapshot de los datos crudos extraídos (JSON o texto) |
| 12 | Extraction_Status | `fldcwuHScjXCEeIKG` | Select | Estado de la extracción |
| 13 | Data_Quality_Score | `fldFvQoIsP6BgKdVX` | Rating | Puntuación de calidad de los datos extraídos (1-5) |
| 14 | Validated | `fldB8L1MZLM0AC3wg` | Checkbox | Indica si la extracción ha sido validada por un humano |
| 15 | Validated_By | `fldkkXWDL8PrRBwJI` | Link→Config - Users(n) | Usuario que validó la extracción |
| 16 | Validation_Date | `fldaLoeFfO7taz869` | Date | Fecha de validación |
| 17 | Validation_Notes | `fldbz5UCr955Q6l0b` | Long Text | Notas del validador sobre la calidad o problemas encontrados |
| 18 | Campaign_Target | `fldDXvfRtUc9IxEeP` | Link→Campaign_Targets(n) | Campaign Target asociado si la extracción fue para una campa |
| 19 | Extraction_Trigger | `fldnT9iGkcCzHbbRu` | Select | Qué disparó la extracción |
| 20 | AI_Agent_Used | `flduxGMW8ZcdHi9yk` | Select | Agente IA que realizó la extracción si aplica |
| 21 | Error_Message | `fldiBNLDUMdFoLRmL` | Long Text | Mensaje de error si la extracción falló |
| 22 | Processing_Time_Seconds | `fldgzP4c7KrDZjNkX` | Number | Tiempo de procesamiento en segundos |

**Opciones Select:**

- **Fields_Updated:** `Revenue`, `EBITDA`, `Debt`, `Email`, `Phone`, `Address`, `LinkedIn`, `Website`, `ESG_Score`, `Ownership`, `Certifications`, `Description`, `Employees`, `Sector`, `Activities` (+4 más)
- **Extraction_Status:** `Success`, `Partial_Success`, `Failed`, `Pending_Review`
- **Extraction_Trigger:** `Manual`, `Campaign`, `Scheduled`, `AI_Agent`
- **AI_Agent_Used:** `Buscador_Empresas`, `Enriquecedor_Datos`, `Evaluador_FEI`, `Analizador_Contexto`, `Selector_Targets`, `Redactor_Mensajes`, `None`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Source | Config_Sources | Source_Extractions |  |
| Extracted_By | Config - Users | Source_Extractions |  |
| Target_Company | Stakeholders_Companies | Source_Extractions |  |
| Target_Business_Unit | Stakeholders_Business_Uni | Source_Extractions |  |
| Target_Contact | Stakeholders_Contacts | Source_Extractions |  |
| Target_Market_Context | Market_Context | Source_Extractions |  |
| Validated_By | Config - Users | Source_Extractions |  |
| Campaign_Target | Campaign_Targets | Source_Extractions |  |

---

### 34. Company_Certificates

**ID:** `tbl6PZVZasLc0zr9S` | **Campos:** 11
**Descripción:** Registro de certificaciones obtenidas por cada empresa. Tabla de unión entre Stakeholders_Companies y Config_Certificates con datos de vigencia y verificación.

| # | Campo | ID | Tipo | Descripción |
|--:|-------|-----|------|-------------|
| 1 | Certificate_Record_Name | `fldr8cGkSkDplk8fp` | Text | Nombre descriptivo del registro: [Empresa] - [Certificado] |
| 2 | Company | `fldOO7EhwQ77fB47d` | Link→Stakeholders_Compa..(n) | Empresa que posee esta certificación |
| 3 | Certificate_Type | `fldsHf8izpzoA3eJ5` | Link→Config_Certificates(n) | Tipo de certificación del catálogo Config_Certificates |
| 4 | Certificate_Number | `fldKdPOIY2C5VjDDR` | Text | Número o código del certificado emitido |
| 5 | Issue_Date | `fldjeIF31YggnwvXO` | Date | Fecha de emisión del certificado |
| 6 | Expiry_Date | `fldYpXd9gKtZAfNqj` | Date | Fecha de expiración del certificado |
| 7 | Status | `fldB8RBIO9NKwZTpn` | Select | Estado actual de la certificación |
| 8 | Verification_URL | `fldkoVsTlChYhXrr0` | URL | URL para verificar autenticidad del certificado |
| 9 | Evidence_Attachments | `fldmAA55tQROljUhf` | Attachments | Documentos adjuntos como evidencia (PDF, imágenes) |
| 10 | Verification_Date | `fldyEsraqrw2tp86m` | Date | Fecha de última verificación |
| 11 | Notes | `fldCaeKha6H0jK8mI` | Long Text | Observaciones adicionales sobre la certificación |

**Opciones Select:**

- **Status:** `Active`, `Expired`, `Pending_Renewal`, `Revoked`, `Under_Review`

**Relaciones:**

| Campo | Destino | Inverso | Single? |
|-------|---------|---------|---------|
| Company | Stakeholders_Companies | Company_Certificates |  |
| Certificate_Type | Config_Certificates | Company_Certificates |  |

---
## MATRIZ DE RELACIONES COMPLETA

> Todas las relaciones Record Link en la base de datos

**Total relaciones:** 139

| Desde | Campo | → Hacia | Inverse Field ID | Single? |
|-------|-------|---------|------------------|---------|
| Stakeholders_Companies | HQ Country | Config_Countries | `fldJzPn9kbPSxa8` |  |
| Stakeholders_Companies | Currency | Config_Currencies | `fld59e5eFfDTJdw` | ✓ |
| Stakeholders_Companies | Parent Company | Stakeholders_Companies | `fldyLCkTaP8hOXn` | ✓ |
| Stakeholders_Companies | Ultimate Parent Comp | Stakeholders_Companies | `fldNhcQB4YkyHqc` | ✓ |
| Stakeholders_Companies | Children_Companies | Stakeholders_Companies | `fldYNfAxCbPYR5c` |  |
| Stakeholders_Companies | Business Units | Stakeholders_Business_Uni | `fldwOiPSVOdeRuI` |  |
| Stakeholders_Companies | Config_Certificates | Config_Certificates | `fldoAs4RlkqwAn3` |  |
| Stakeholders_Companies | From field: Ultimate | Stakeholders_Companies | `fldkecnUX1x0YIr` |  |
| Stakeholders_Companies | Stakeholders_Compani | Stakeholders_Companies_Fi | `fld6cJ1oSRiDzDT` |  |
| Stakeholders_Companies | Source_Extractions | Source_Extractions | `fld8WxB2IiftVvA` |  |
| Stakeholders_Companies | Company_Certificates | Company_Certificates | `fldOO7EhwQ77fB4` |  |
| Stakeholders_Companies_Fi | Company | Stakeholders_Companies | `fld5zdHuT2IsinU` | ✓ |
| Stakeholders_Business_Uni | Company | Stakeholders_Companies | `fldTS0EXfmBYkDx` | ✓ |
| Stakeholders_Business_Uni | Business Unit Type | Config_Stakeholder_SubTyp | `fldPljzmRpvT6jJ` |  |
| Stakeholders_Business_Uni | Sector | Config_Sector_And_Activit | `fldRvcd5e6JpiaD` | ✓ |
| Stakeholders_Business_Uni | Activities | Config_Sector_And_Activit | `fldlPZgwfNo59w8` |  |
| Stakeholders_Business_Uni | Focus Countries | Config_Countries | `fldnUSq8LYjrxUu` |  |
| Stakeholders_Business_Uni | Business Unit Contac | Stakeholders_Contacts | `fldCDSDNQj5rlKp` |  |
| Stakeholders_Business_Uni | Main Currency | Config_Currencies | `fldttq4kfezcSlk` |  |
| Stakeholders_Business_Uni | Config_Activities | Config_Activities | `fldFtj8R3rVwNHr` |  |
| Stakeholders_Business_Uni | Campaign_Targets | Campaign_Targets | `fldqbbRiQx87Wis` |  |
| Stakeholders_Business_Uni | Source_Extractions | Source_Extractions | `fldQSaOPpKvD6h2` |  |
| Stakeholders_Contacts | Role Level | Config_General_Fields | `fldUErRvW27JkWS` | ✓ |
| Stakeholders_Contacts | Business Unit | Stakeholders_Business_Uni | `fldLYlKr4gmjDiX` |  |
| Stakeholders_Contacts | Contact Type | Config_Stakeholder_SubTyp | `fldkWJacCOWfXt3` |  |
| Stakeholders_Contacts | Focus Countries | Config_Countries | `fldWGNsI6NOwZWL` |  |
| Stakeholders_Contacts | Sector | Config_Sector_And_Activit | `fldadQ1sx8yZRNu` |  |
| Stakeholders_Contacts | Activities | Config_Sector_And_Activit | `fldmUELg0pwAa8i` |  |
| Stakeholders_Contacts | Contact Languages | Config_Languages | `fldCLFVXcaG4OhH` |  |
| Stakeholders_Contacts | Campaign_Targets | Campaign_Targets | `fldGP9ex0wKhGNJ` |  |
| Stakeholders_Contacts | Source_Extractions | Source_Extractions | `fldspSyFrhTopYm` |  |
| Opportunities - Global Ov | Distribution Race | Distribution - Investor S | `fldPkYigQe0Wc4A` |  |
| Opportunities - Global Ov | Distribution Waves | Distribution - Waves | `fldYpZF030W8XrO` |  |
| Opportunities - Global Ov | Q&A | Opportunity - Q&A | `fldKyvOK8Lh3T9Y` |  |
| Opportunities - Global Ov | Distribution Investo | Investor Workstreams | `fldIcMUaCo79nrK` |  |
| Opportunities - Global Ov | Email Activity | Config - Email Activity | `fldetA4KUFYz2Lj` |  |
| Opportunities - Global Ov | Internal - Tasks 2 | Internal - Tasks | `fldVCQTVzmgYqE6` |  |
| Opportunities - Global Ov | Internal - Tasks cop | Internal - Initiatives | `fldSIuFoGqgoHEt` |  |
| Opportunity - Q&A | Company_Type | Config - Variables | `fldUNQ9tTHkat9l` |  |
| Opportunity - Q&A | Opportunity | Opportunities - Global Ov | `fldmg660fyyP1I0` | ✓ |
| Opportunity - Q&A | Used Answer | Opportunity - Q&A | `flddGRDJWqZCeIj` |  |
| Opportunity - Q&A | Hidden field: Used A | Opportunity - Q&A | `fldA7kWqL1Xi5Lu` |  |
| Distribution - Investor S | Opportunities | Opportunities - Global Ov | `fldgmiRIxjgZjSz` |  |
| Distribution - Investor S | Wave Link | Distribution - Waves | `fldL5EoAH6XD40t` | ✓ |
| Distribution - Waves | Opportunity | Opportunities - Global Ov | `fldq1P5js6ul7Jy` | ✓ |
| Distribution - Waves | Email Template - Pre | Config - Email Templates | `fldqa4SEBbIIB5a` |  |
| Distribution - Waves | Assigned Investor Pr | Distribution - Investor S | `flduDSVDW3479JD` |  |
| Distribution - Waves | Generated workstream | Investor Workstreams | `fldiEvj3Ck7FauP` |  |
| Distribution - Waves | Email Activity | Config - Email Activity | `fldjgJiOiz1Oagn` |  |
| Investor Workstreams | Opportunities | Opportunities - Global Ov | `fld9e6tCjtncufJ` |  |
| Investor Workstreams | Next Task Owner | Config - Variables | `fldAvaw7HarNY14` |  |
| Investor Workstreams | Workstream Owner | Config - Variables | `fldAlpeCCZCHYz8` |  |
| Investor Workstreams | Internal - Tasks | Internal - Tasks | `fldiekc6eKEOodz` |  |
| Investor Workstreams | Distribution - Waves | Distribution - Waves | `fldxtx88ToknvPD` |  |
| Internal - Initiatives | Initiative Leader | Config - Users | `fldOfycUeGVjQvX` |  |
| Internal - Initiatives | Parent Initiative | Internal - Initiatives | `fldx4xfjQGgR7Jj` |  |
| Internal - Initiatives | Children Initiatives | Internal - Initiatives | `fldhypZIYc3joen` |  |
| Internal - Initiatives | Opportunity | Opportunities - Global Ov | `fldN8MMTsMpHJpC` |  |
| Internal - Tasks | Owner | Config - Users | `fldR9Uqr7CVTzvA` |  |
| Internal - Tasks | Opportunity | Opportunities - Global Ov | `fldQ280qlIphspf` |  |
| Internal - Tasks | Needs first (Tasks) | Internal - Tasks | `fld2pLlQ3fJPm8t` |  |
| Internal - Tasks | From field: Related  | Internal - Tasks | `fldiDDq4i3N0LR1` |  |
| Internal - Tasks | Investor Workstream | Investor Workstreams | `fldqmgyCJh7Q9gf` |  |
| Help & Feedback - Suggest | Submitted By | Config - Users | `fldkToZ3OK6LJvE` |  |
| Config - Email Templates | Distribution Waves | Distribution - Waves | `fldauKmw8O2kDhk` |  |
| Config - Email Activity | Opportunity | Opportunities - Global Ov | `fldWMwCWTdI6bKa` | ✓ |
| Config - Email Activity | Wave link | Distribution - Waves | `fldAng4EoXPLB7e` | ✓ |
| Config - Email Activity | Campaign_Targets | Campaign_Targets | `fld90h66w4y3BCf` |  |
| Config - Users | Internal - Tasks | Internal - Tasks | `fldd2bQxC7mJc3p` |  |
| Config - Users | Help & Feedback - Su | Help & Feedback - Suggest | `fldh4kX7asV4JR2` |  |
| Config - Users | Internal - Tasks cop | Internal - Initiatives | `flda8PC0Jbm9t3M` |  |
| Config - Users | Origination_Campaign | Origination_Campaigns | `fldrA5YjXct4UFz` |  |
| Config - Users | Source_Extractions | Source_Extractions | `fldAKHAXYbftXzO` |  |
| Config - Users | Source_Extractions | Source_Extractions | `fldkkXWDL8PrRBw` |  |
| Config - Variables | Q&A | Opportunity - Q&A | `fldGjZvPbx6tU8O` |  |
| Config - Variables | Investor Workstreams | Investor Workstreams | `fldTrlvqciZcVYq` |  |
| Config - Variables | Investor Workstreams | Investor Workstreams | `fldtIzexx4kJRoD` |  |
| Config_General_Fields | Contacts | Stakeholders_Contacts | `fld6j4LRqyZdzx8` |  |
| Config_Currencies | Countries | Config_Countries | `` |  |
| Config_Currencies | Stakeholders_Compani | Stakeholders_Companies | `flde6s7SlSY4sR7` |  |
| Config_Currencies | Stakeholders_Busines | Stakeholders_Business_Uni | `fldQC8u63vi1tBI` |  |
| Config_Countries | Related_Currencies | Config_Currencies | `` |  |
| Config_Countries | Stakeholders_Compani | Stakeholders_Companies | `fldUmivMZQDejw7` |  |
| Config_Countries | Stakeholders_Busines | Stakeholders_Business_Uni | `fldhg7U43jc6UDN` |  |
| Config_Countries | Stakeholders_Contact | Stakeholders_Contacts | `fldvII7gcJ1IVMt` |  |
| Config_Countries | Config_Certificates | Config_Certificates | `fldL6bBDHHq5t5g` |  |
| Config_Countries | Config_Certificates  | Config_Certificates | `fld70Q2InixSMvq` |  |
| Config_Countries | Market_Context | Market_Context | `fldiGPvAi2vQFrO` |  |
| Config_Countries | Origination_Campaign | Origination_Campaigns | `fldIwGau3bZwGgI` |  |
| Config_Countries | Config_Sources | Config_Sources | `fldtOZoGUxf2dsj` |  |
| Config_Stakeholder_Types | Sub Types | Config_Stakeholder_SubTyp | `` |  |
| Config_Stakeholder_SubTyp | Dependencies | Config_Stakeholder_Types | `` |  |
| Config_Stakeholder_SubTyp | Stakeholders_Contact | Stakeholders_Contacts | `fldBJ0IGtlqRTZk` |  |
| Config_Stakeholder_SubTyp | Stakeholders_Busines | Stakeholders_Business_Uni | `fldddMbIJ1cyQz6` |  |
| Config_Stakeholder_SubTyp | Origination_Campaign | Origination_Campaigns | `flddGkHXploEHiV` |  |
| Config_Sector_And_Activit | Relationships_Level_ | Stakeholders_Business_Uni | `fldqhylfII6O9tJ` |  |
| Config_Sector_And_Activit | Relationships_Level_ | Stakeholders_Business_Uni | `fld5QXiROXeJw0L` |  |
| Config_Sector_And_Activit | Stakeholders_Contact | Stakeholders_Contacts | `fldSCgzHyhX25NC` |  |
| Config_Sector_And_Activit | Stakeholders_Contact | Stakeholders_Contacts | `fldLXKP9SdLdtT1` |  |
| Config_Sector_And_Activit | Market_Context | Market_Context | `fldbj45oHTaWap8` |  |
| Config_Sector_And_Activit | Origination_Campaign | Origination_Campaigns | `fldv4yljMidf9Gq` |  |
| Config_Sector_And_Activit | Config_Sources | Config_Sources | `fldU51Kvywt2ayK` |  |
| Config_Languages | Related_Countries | Config_Countries | `` |  |
| Config_Languages | Stakeholders_Contact | Stakeholders_Contacts | `fldmUAt8QbFj4G8` |  |
| GICS_Standard | Sector_Code | Config_Activities | `fldWdshLWcL91Br` |  |
| Config_Certificates | Eligible_Countries | Config_Countries | `fldztjIKadoE97M` |  |
| Config_Certificates | Valid_Countries | Config_Countries | `fldgVYP88kTvAB3` |  |
| Config_Certificates | Companies | Stakeholders_Companies | `fldbNeEImVsEkV2` |  |
| Config_Certificates | Company_Certificates | Company_Certificates | `fldsHf8izpzoA3e` |  |
| Config_Activities | GICS_Sub_Industry | GICS_Standard | `fldFGNTZXWPE3Gi` |  |
| Config_Activities | Business_Units | Stakeholders_Business_Uni | `flddnKI79EcwFAH` |  |
| Market_Context | Affected_Sectors | Config_Sector_And_Activit | `fldY7yPsHWq9IE5` |  |
| Market_Context | Affected_Countries | Config_Countries | `fldieOAeVKNHIsr` |  |
| Market_Context | Origination_Campaign | Origination_Campaigns | `fldB7BZaXkvO4w0` |  |
| Market_Context | Source_Extractions | Source_Extractions | `fldX3e8RGBrFUwI` |  |
| Origination_Campaigns | Market_Context | Market_Context | `fldnM2RSuR6yRDD` |  |
| Origination_Campaigns | Target_Stakeholder_T | Config_Stakeholder_SubTyp | `fldOFK7kCwnZE4C` |  |
| Origination_Campaigns | Target_Sectors | Config_Sector_And_Activit | `fldOCRmyepVTSOu` |  |
| Origination_Campaigns | Target_Countries | Config_Countries | `fldwJ6oOpwxpXHN` |  |
| Origination_Campaigns | Owner | Config - Users | `fldBNeusAjEUc7H` |  |
| Origination_Campaigns | Campaign_Targets | Campaign_Targets | `fldhSdahm4INjtO` |  |
| Campaign_Targets | Campaign | Origination_Campaigns | `fldH2x2gIFQrVo3` |  |
| Campaign_Targets | Business_Unit | Stakeholders_Business_Uni | `fldKdevQzGADcGl` |  |
| Campaign_Targets | Contact | Stakeholders_Contacts | `flda1jv9LpoCCBf` |  |
| Campaign_Targets | Email_Activity | Config - Email Activity | `fldEpOhisC8aA0r` |  |
| Campaign_Targets | Source_Extractions | Source_Extractions | `fldDXvfRtUc9IxE` |  |
| Config_Sources | Countries_Covered | Config_Countries | `fld1WskmkT9L2Dv` |  |
| Config_Sources | Sectors_Covered | Config_Sector_And_Activit | `fldvcW2m5yCQyS3` |  |
| Config_Sources | Source_Extractions | Source_Extractions | `fldX4yyOdGBVfd9` |  |
| Source_Extractions | Source | Config_Sources | `fld9OBhWUJLkCQ0` |  |
| Source_Extractions | Extracted_By | Config - Users | `fldDUUzhzNFdOcw` |  |
| Source_Extractions | Target_Company | Stakeholders_Companies | `fldorLYZxfipbMc` |  |
| Source_Extractions | Target_Business_Unit | Stakeholders_Business_Uni | `fldeZmDmf1ju2yc` |  |
| Source_Extractions | Target_Contact | Stakeholders_Contacts | `fldcEaWE66xggw5` |  |
| Source_Extractions | Target_Market_Contex | Market_Context | `fldFDk0VlvfmTZY` |  |
| Source_Extractions | Validated_By | Config - Users | `fldCIdLL87t1Qji` |  |
| Source_Extractions | Campaign_Target | Campaign_Targets | `fld6Crde3ts0u2d` |  |
| Company_Certificates | Company | Stakeholders_Companies | `fldqpfAdKxmxTD1` |  |
| Company_Certificates | Certificate_Type | Config_Certificates | `fldidWXxiBuaAbQ` |  |

---

## DISTRIBUCIÓN DE TIPOS DE CAMPO

| Tipo | Cantidad | % |
|------|----------|---|
| `multipleRecordLinks` | 139 | 24.7% |
| `singleLineText` | 99 | 17.6% |
| `singleSelect` | 51 | 9.1% |
| `multipleLookupValues` | 44 | 7.8% |
| `multilineText` | 27 | 4.8% |
| `richText` | 26 | 4.6% |
| `checkbox` | 26 | 4.6% |
| `number` | 18 | 3.2% |
| `multipleSelects` | 18 | 3.2% |
| `aiText` | 16 | 2.8% |
| `date` | 16 | 2.8% |
| `dateTime` | 15 | 2.7% |
| `rollup` | 13 | 2.3% |
| `formula` | 11 | 2.0% |
| `createdTime` | 9 | 1.6% |
| `url` | 8 | 1.4% |
| `lastModifiedTime` | 8 | 1.4% |
| `multipleAttachments` | 5 | 0.9% |
| `percent` | 6 | 1.1% |
| `rating` | 3 | 0.5% |
| `email` | 2 | 0.4% |
| `phoneNumber` | 1 | 0.2% |
| `singleCollaborator` | 1 | 0.2% |
| `manualSort` | 1 | 0.2% |

---

## REFERENCIA COMPLETA DE FÓRMULAS

### Stakeholders_Companies_Financials

**Yearly Results - Company** (`fldGciO4h9XmpPyqk`)
- Estado: ✓ Válida
- Resultado: `singleLineText`
```
{fldtFQK6pnOGg8NiT} & " - " & {fld6cJ1oSRiDzDTH6}
```

**Debt / EBITDA** (`fldjfnA6iVZdwwY4Z`)
- Estado: ✓ Válida
- Resultado: `percent`
```
IF({fldyKupWEWhoBSP1I} != 0, {fldAbKTlEtTlMW2SA} / {fldyKupWEWhoBSP1I}, BLANK())
```

**Interest Coverage** (`fldcQVUZ0tC8CmASj`)
- Estado: ✓ Válida
- Resultado: `percent`
```
IF({fldAbKTlEtTlMW2SA} != 0, {fld0vQKBrPU37AFe5} / {fldAbKTlEtTlMW2SA}, BLANK())
```

### Stakeholders_Business_Units

**Sector_Formula** (`fldGTP0Ok69Wokvsy`)
- Estado: ✓ Válida
- Resultado: `singleLineText`
```
{fldqhylfII6O9tJnd}
```

### Stakeholders_Contacts

**Full Name** (`fldsvzjNGXEWybta7`)
- Estado: ✓ Válida
- Resultado: `singleLineText`
```
{fldB8pziOzHr497Qv} & " " & {fldf9d2QGtovb61rd}
```

**Sector_Formula** (`fld9zQzt1u0YNaYbD`)
- Estado: ✓ Válida
- Resultado: `singleLineText`
```
{fldSCgzHyhX25NC5C}
```

### Distribution - Waves

**% Opened** (`fldhHsKrijLecl1TK`)
- Estado: ✓ Válida
- Resultado: `percent`
```
IF({fldLGfCtE3l1F9FJz}, {fldRfVSggd6Xv9ObT} / {fldLGfCtE3l1F9FJz}, BLANK())
```

**% Answered** (`fldrZVq1wYG9cfFHr`)
- Estado: ✓ Válida
- Resultado: `percent`
```
IF({fldRfVSggd6Xv9ObT}, {fldytF2n1MwHF8Xwg} / {fldRfVSggd6Xv9ObT}, BLANK())
```

**% Interested** (`fldaMMIPKTGiPQyWC`)
- Estado: ✓ Válida
- Resultado: `percent`
```
IF({fldytF2n1MwHF8Xwg}, {fldKXCOGhRqYBhqd0} / {fldytF2n1MwHF8Xwg}, BLANK())
```

### Investor Workstreams

**Status Duration (days)** (`fldQ9uyAjAXj9lgAb`)
- Estado: ✓ Válida
- Resultado: `number`
```
DATETIME_DIFF(NOW(), {fldPPXEf5Ap7hJVz2}, 'minutes')
```

### Internal - Tasks

**Days Since Creation (If Active)** (`fldUKpql2RDqysKXn`)
- Estado: ✓ Válida
- Resultado: `number`
```
IF(
  AND({fldtMIKtcmBhudikB} != "Done", {fldtMIKtcmBhudikB} != "Discarded"),
  DATETIME_DIFF(TODAY(), {fld0Eo4nDB19F0mAB}, "days"),
  BLANK()
)
```

---

## REFERENCIA COMPLETA DE CAMPOS AI

### Stakeholders_Companies

**GICS Sectors AI** (`fldUYmcWYfZxpYGHj`)
- Campos referenciados: `fldgOU0xOhYBCvrYB`

**Prompt:**
```
*** TASK ***
Extract, deduplicate, and sort all unique values from the input.

*** RULES ***
- Extract all individual values from the input
- Input may be: an array, a comma-separated string, or a nested array with comma-separated strings
- Split any comma-separated strings into individual values
- Trim whitespace from each value
- Remove duplicates (case-sensitive)
- Sort alphabetically A → Z
- Output values joined by commas
- If input is empty or blank, return nothing
- Only return values found in the original input

*** INPUT FORMAT ***
Any of:
- String: `"A, B, A"`
- Array: `["A", "B"]`
- Nested: `["A, B", "C", "A"]`

*** OUTPUT FORMAT ***
Sorted, unique values separated by commas. Nothing else.

*** EXAMPLES ***
**Input 1:**
Apple, Banana, Cherry, Apple

**Output 1:**
Apple, Banana, Cherry

---

**Input 2:**
["Red", "Blue", "Red", "Green"]

**Output 2:**
Blue, Green, Red

---

**Input 3:**
["Red, Blue", "Green", "Yellow", "Red"]

**Output 3:**
Blue, Green, Red, Yellow

---

**Input 4:**
Single

**Output 4:**
Single

---

**Input 5:**
(empty)

**Output 5:**
(nothing)

*** END OF EXAMPLES ***

*** INPUT ***
{{FIELD:fldgOU0xOhYBCvrYB}}

```

**GICS Industries AI** (`fldZfawXl9lndkhse`)
- Campos referenciados: `fldj6NRvuRO9qDkKq`

**Prompt:**
```
*** TASK ***
Extract, deduplicate, and sort all unique values from the input.

*** RULES ***
- Extract all individual values from the input
- Input may be: an array, a comma-separated string, or a nested array with comma-separated strings
- Split any comma-separated strings into individual values
- Trim whitespace from each value
- Remove duplicates (case-sensitive)
- Sort alphabetically A → Z
- Output values joined by commas
- If input is empty or blank, return nothing
- Only return values found in the original input

*** INPUT FORMAT ***
Any of:
- String: `"A, B, A"`
- Array: `["A", "B"]`
- Nested: `["A, B", "C", "A"]`

*** OUTPUT FORMAT ***
Sorted, unique values separated by commas. Nothing else.

*** EXAMPLES ***
**Input 1:**
Apple, Banana, Cherry, Apple

**Output 1:**
Apple, Banana, Cherry

---

**Input 2:**
["Red", "Blue", "Red", "Green"]

**Output 2:**
Blue, Green, Red

---

**Input 3:**
["Red, Blue", "Green", "Yellow", "Red"]

**Output 3:**
Blue, Green, Red, Yellow

---

**Input 4:**
Single

**Output 4:**
Single

---

**Input 5:**
(empty)

**Output 5:**
(nothing)

*** END OF EXAMPLES ***

*** INPUT ***
{{FIELD:fldj6NRvuRO9qDkKq}}

```

**GICS Subindustries AI** (`fld6PxsHtI5vN2pBr`)
- Campos referenciados: `fldKRaAOqGF2uVzVN`

**Prompt:**
```
*** TASK ***
Extract, deduplicate, and sort all unique values from the input.

*** RULES ***
- Extract all individual values from the input
- Input may be: an array, a comma-separated string, or a nested array with comma-separated strings
- Split any comma-separated strings into individual values
- Trim whitespace from each value
- Remove duplicates (case-sensitive)
- Sort alphabetically A → Z
- Output values joined by commas
- If input is empty or blank, return nothing
- Only return values found in the original input

*** INPUT FORMAT ***
Any of:
- String: `"A, B, A"`
- Array: `["A", "B"]`
- Nested: `["A, B", "C", "A"]`

*** OUTPUT FORMAT ***
Sorted, unique values separated by commas. Nothing else.

*** EXAMPLES ***
**Input 1:**
Apple, Banana, Cherry, Apple

**Output 1:**
Apple, Banana, Cherry

---

**Input 2:**
["Red", "Blue", "Red", "Green"]

**Output 2:**
Blue, Green, Red

---

**Input 3:**
["Red, Blue", "Green", "Yellow", "Red"]

**Output 3:**
Blue, Green, Red, Yellow

---

**Input 4:**
Single

**Output 4:**
Single

---

**Input 5:**
(empty)

**Output 5:**
(nothing)

*** END OF EXAMPLES ***

*** INPUT ***
{{FIELD:fldKRaAOqGF2uVzVN}}

```

### Stakeholders_Business_Units

**GICS AI Summary** (`fld2lG6Q14GiQ9NER`)
- Campos referenciados: `fldrcFl2yl9ZeVbtW, fldwOiPSVOdeRuIIJ, fldqhylfII6O9tJnd, fld5QXiROXeJw0LVx, fldddMbIJ1cyQz6Ut`

**Prompt:**
```
*** ROLE ***
You are a financial analyst specializing in GICS (Global Industry Classification Standard) classification. Your task is to classify business units (BUs) into the correct GICS categories based on their primary business activities.

*** GICS CLASSIFICATION LEVELS ***
You will classify business units using three levels:
1. **Sector** (Level 1): The broadest classification (e.g., Financials, Information Technology, Health Care)
2. **Industry** (Level 3): More specific grouping within the sector
3. **Sub-Industry** (Level 4): The most granular classification

Note: We skip Industry Group (Level 2) as it is redundant for our purposes.

*** CLASSIFICATION PRINCIPLES ***
- Classify based on the business unit's **primary revenue-generating activity**
- Business units are typically focused on a single activity—select the **single best classification** in most cases
- Only assign multiple classifications if the BU genuinely spans different industries with no clear primary activity (this should be rare)

*** RULES FOR MULTIPLE CLASSIFICATIONS ***
- Multiple classifications at BU level should be rare—most BUs have a single focus
- If a BU requires multiple classifications, each must include its **full hierarchical path**
- Never mix Sub-Industries from different Industries under a single parent
- Structure multiple classifications as separate, complete branches

*** OUTPUT FORMAT ***

**Single classification (typical):**
<reasoning>
[2-10 sentences analyzing the business unit
```

**GICS Sector** (`fldhHSTO6MR2GMVva`)
- Campos referenciados: `fld2lG6Q14GiQ9NER`

**Prompt:**
```
*** TASK ***
Extract the Sector value(s) from a GICS classification response.

*** RULES ***
- Extract only the Sector level values from the <classification> block
- Ignore all other content (reasoning, analysis, etc.)
- If multiple branches exist, join all Sector values with commas
- If the same Sector appears in multiple branches, list it only once (deduplicate)
- Output the Sector name(s) only—no labels, prefixes, or additional text
- Maintain official GICS taxonomy naming exactly as written in the source

*** INPUT FORMAT ***
The input will contain a full classification response, which includes:
- A <reasoning> block with analysis (ignore this)
- A <classification> block containing the GICS hierarchy (extract Sector from here)

Extract only from the <classification> block.

*** OUTPUT FORMAT ***
Return only the Sector value(s). Examples:
- Single sector: `Financials`
- Multiple sectors: `Communication Services, Information Technology`

*** EXAMPLES ***

**Input 1:**
<reasoning>
BBVA is a diversified financial institution primarily engaged in retail and commercial banking, including deposits, loans, and payment services. Banking activities constitute its dominant revenue source, placing it clearly in the Banks classification.
</reasoning>

<classification>
Sector: Financials
Industry: Banks
Sub-Industry: Diversified Banks
</classification>

**Output 1:**
Financials

---

**Input 2:**
<reasoning>
Alphabet Inc. generates the majority of revenue from digital advertising (Goog
```

**GICS Industry** (`fldXbSsvRapRrIwOC`)
- Campos referenciados: `fld2lG6Q14GiQ9NER`

**Prompt:**
```
*** TASK ***
Extract the Industry value(s) from a GICS classification response.

*** RULES ***
- Extract only the Industry level values from the <classification> block
- Ignore all other content (reasoning, analysis, etc.)
- If multiple branches exist, join all Industry values with commas
- If the same Industry appears in multiple branches, list it only once (deduplicate)
- Output the Industry name(s) only—no labels, prefixes, or additional text
- Maintain official GICS taxonomy naming exactly as written in the source

*** INPUT FORMAT ***
The input will contain a full classification response, which includes:
- A <reasoning> block with analysis (ignore this)
- A <classification> block containing the GICS hierarchy (extract Industry from here)

Extract only from the <classification> block.

*** OUTPUT FORMAT ***
Return only the Industry value(s). Examples:
- Single industry: `Banks`
- Multiple industries: `Interactive Media & Services, IT Services`

*** EXAMPLES ***

**Input 1:**
<reasoning>
BBVA is a diversified financial institution primarily engaged in retail and commercial banking, including deposits, loans, and payment services. Banking activities constitute its dominant revenue source, placing it clearly in the Banks classification.
</reasoning>

<classification>
Sector: Financials
Industry: Banks
Sub-Industry: Diversified Banks
</classification>

**Output 1:**
Banks

---

**Input 2:**
<reasoning>
Alphabet Inc. generates the majority of revenue from digital advertising (
```

**GICS Subindustry** (`fldGOGeS64n2AJfOk`)
- Campos referenciados: `fld2lG6Q14GiQ9NER`

**Prompt:**
```
*** TASK ***
Extract the Sub-Industry value(s) from a GICS classification response.

*** RULES ***
- Extract only the Sub-Industry level values from the <classification> block
- Ignore all other content (reasoning, analysis, etc.)
- If multiple branches exist, join all Sub-Industry values with commas
- If multiple Sub-Industries are listed in a single branch (comma-separated), include all of them
- If the same Sub-Industry appears multiple times, list it only once (deduplicate)
- Output the Sub-Industry name(s) only—no labels, prefixes, or additional text
- Maintain official GICS taxonomy naming exactly as written in the source

*** INPUT FORMAT ***
The input will contain a full classification response, which includes:
- A <reasoning> block with analysis (ignore this)
- A <classification> block containing the GICS hierarchy (extract Sub-Industry from here)

Extract only from the <classification> block.

*** OUTPUT FORMAT ***
Return only the Sub-Industry value(s). Examples:
- Single sub-industry: `Diversified Banks`
- Multiple sub-industries: `Interactive Media & Services, Internet Services & Infrastructure`

*** EXAMPLES ***

**Input 1:**
<reasoning>
BBVA is a diversified financial institution primarily engaged in retail and commercial banking, including deposits, loans, and payment services. Banking activities constitute its dominant revenue source, placing it clearly in the Banks classification.
</reasoning>

<classification>
Sector: Financials
Industry: Banks
Sub-Industry:
```

### Stakeholders_Contacts

**Validator** (`fldfk5nYeDeOaC5qv`)
- Campos referenciados: `fldB8pziOzHr497Qv`

**Prompt:**
```
sd{{FIELD:fldB8pziOzHr497Qv}}

```

### Opportunity - Adaptation

**Attachment Summary** (`fldYUc6hMVTia7uJ1`)
- Campos referenciados: `fldkXN05ew4tPXtyT`

**Prompt:**
```
You are a professional document analyst specializing in summarizing content from various file types. Your task is to extract key points and provide a concise summary of the content found in the attached files. Ensure that the summary captures the main ideas and any important details without including unnecessary information.

Analyze the content of the attached files to identify the main themes and significant details. Summarize these points clearly and concisely, ensuring that the summary is informative and relevant to the document's purpose.

Format your response as plain text, keeping it concise and to the point. If you cannot summarize the content, output "Unable to summarize the content." Example: "The document discusses the impact of climate change on polar bears, highlighting the loss of habitat and food sources." (Real examples should be longer and more detailed.)

Files:
{{FIELD:fldkXN05ew4tPXtyT}}
```

### Distribution - Investor Selection

**IA Recommendation Reasoning** (`fld4JYUPTN55o1SPF`)
- Campos referenciados: `fldqows77nGCbTKTH, fldPkYigQe0Wc4Ano, fldDf7DoeOrGukN15, fldyYwd0qeXwmWgHw, fldsmMuIVB5rPjKNa, fldOK2vtD5dGn7Lwb, fldJncHYkN82R8nAd, flddFVaJWiHOjmoTH, fld7LhJBkVqIdEiFH, fldENCllli3Bqhmip, fldkILp43j1kEOv5K, fldsr2fB66Qi06kG7`

**Prompt:**
```
*** WHO YOU ARE ***
You are a highly senior financial analyst with high expertise, with experience in both big banks like Goldman Sachs, and smaller boutiques alike. 

Now you are working for Alter5. It is an origination engine, that finds and connects businesses with complex financial and M&A needs, with all types of institutional investors. It originates, underwrites and distributes the deals. 

*** HOW YOU RESPOND ***
- Always answer in English
- You are very brief and to the point. 
- Your language is formal and precise, ideal for an investment banking setting.
- First you think the response, you follow the instructions that we are hereby giving, then you write the final response.

*** TASK ***
You will help a managing director that is deciding to which investors it wants to present every deal. You are therefore given a specific "Opportunity x Investor" decision that needs to be taken.

Your task is to analyze the given input and reason how good the fit is between the opportunity and the investor's targeting criteria.

You will provide an executive recommendation, supported by high-quality explanation as to why it i that. There are three recommendation types: NO FIT | LOW FIT | HIGH FIT.

*** INFORMATION PROVIDED ***
Investor Selection Decision Name: {{FIELD:fldqows77nGCbTKTH}}
Opportunity Name: {{FIELD:fldPkYigQe0Wc4Ano}}
Sponsor Company:{{FIELD:fldDf7DoeOrGukN15}}
Investor Company: {{FIELD:fldyYwd0qeXwmWgHw}}
Investor Country: {{FIELD:fldsmMuIVB5rPjKNa}}
Opportunity Tic
```

### Config - Email Templates

**Subject - EN** (`fldCKOSTn70MNl5Zf`)
- Campos referenciados: `fldOZ0b2tvnt13ZEd`

**Prompt:**
```
You are a professional translator specializing in producing clear and accurate English translations of written business messages. Maintain a neutral, business-appropriate tone suitable for email subject lines.

Task description:
Translate the provided Spanish email subject into natural, fluent English. Ensure the meaning and intent of the original message are retained. Rephrase as necessary to produce a subject line that reads as native English and is concise. If the content is not translatable as a subject line, output the failure message.

Output format:
Output a single English email subject line in plain text without any additional text, formatting, or translation notes. If you are unable to complete the translation, output "Unable to translate the provided subject line to English." Example output: "Request for Meeting Confirmation" (real examples should closely follow actual business subject line length and context).

Context and Data:
Subject line in Spanish: {{FIELD:fldOZ0b2tvnt13ZEd}}

Output:

```

**Subject - IT** (`fldzpB8LLk1LgityG`)
- Campos referenciados: `fldOZ0b2tvnt13ZEd`

**Prompt:**
```
You are a professional translator with expertise in translating business correspondence from Spanish to Italian. Your translations should be accurate, clear, and use appropriate formal Italian suitable for an email subject line.

Task description:
Translate the given Spanish email subject line to Italian, conveying the same intent and professionalism. Adapt the content as needed for natural-sounding and concise Italian. If the content is not suitable for translation as a subject line, output the failure message.

Output format:
Output a single Italian email subject line in plain text without any additional text, formatting, or translation notes. If you cannot perform the translation, output "Impossibile tradurre l'oggetto fornito in italiano." Example output: "Richiesta di conferma dell'incontro" (real examples should closely follow actual business subject line length and context).

Context and Data:
Subject line in Spanish: {{FIELD:fldOZ0b2tvnt13ZEd}}

Output:

```

**Body 1 - EN** (`fldXSi9vY6DQ33cID`)
- Campos referenciados: `fldfuOzZb0p92r2eB`

**Prompt:**
```
You are a professional translator specializing in English and Spanish language email templates. Maintain a formal and clear tone suitable for official business communication.

Task description:
Translate the provided email body from Spanish to English, preserving the meaning, tone, and style. Ensure accurate grammar and vocabulary appropriate for a formal audience. Adapt idiomatic expressions as needed to convey the intended message clearly in English without introducing or omitting information.

Output format:
Output only the translated English email text as plain text. Do not include any introductory text, explanations, translation notes, or headings. If the provided content cannot be translated, output "[Translation unavailable: Insufficient or unclear source text]". Example output: "Dear customers, your monthly statement is attached. Please contact us with any questions." (A real translation will typically contain more text depending on the source.)

Context and Data:
Source (Spanish): {{FIELD:fldfuOzZb0p92r2eB}}

Output:

```

**Body 1 - IT** (`fldobmkup53xgrvLl`)
- Campos referenciados: `fldfuOzZb0p92r2eB`

**Prompt:**
```
You are a professional translator specializing in translating business email templates from Spanish to Italian. Maintain a formal and clear tone, ensuring that the message and intent are preserved accurately.

Task description:
Read the provided Spanish email body and translate it precisely into Italian, keeping consistent formatting, structure, and level of formality. Pay close attention to idiomatic language and ensure any business-specific phrases are rendered appropriately in Italian.

Output format:
Return only the Italian translation of the email body as plain text. Do not include explanations, headings, or additional content. If you are unable to provide an accurate translation based on the input, output "Unable to provide translation." For example, if the Spanish input is "Gracias por su atención.", output: "Grazie per la sua attenzione." (Full translations will typically be longer and correspond to complete email bodies.)

Context and Data:
Cuerpo del correo electrónico en español: {{FIELD:fldfuOzZb0p92r2eB}}

Output:

```

**Body 2 - EN** (`fld0pEtmdEwCFT1MM`)
- Campos referenciados: `fld5ZNMUSxQAegt2T`

**Prompt:**
```
You are a professional translator specializing in English and Spanish language email templates. Maintain a formal and clear tone suitable for official business communication.

Task description:
Translate the provided email body from Spanish to English, preserving the meaning, tone, and style. Ensure accurate grammar and vocabulary appropriate for a formal audience. Adapt idiomatic expressions as needed to convey the intended message clearly in English without introducing or omitting information.

Output format:
Output only the translated English email text as plain text. Do not include any introductory text, explanations, translation notes, or headings. If the provided content cannot be translated, output "[Translation unavailable: Insufficient or unclear source text]". Example output: "Dear customers, your monthly statement is attached. Please contact us with any questions." (A real translation will typically contain more text depending on the source.)

Context and Data:
Source (Spanish): {{FIELD:fld5ZNMUSxQAegt2T}}

Output:

```

**Body 2 - IT** (`fld4CJukyF9Vo98oM`)
- Campos referenciados: `fldobmkup53xgrvLl`

**Prompt:**
```
You are a professional translator specializing in translating business email templates from Spanish to Italian. Maintain a formal and clear tone, ensuring that the message and intent are preserved accurately.

Task description:
Read the provided Spanish email body and translate it precisely into Italian, keeping consistent formatting, structure, and level of formality. Pay close attention to idiomatic language and ensure any business-specific phrases are rendered appropriately in Italian.

Output format:
Return only the Italian translation of the email body as plain text. Do not include explanations, headings, or additional content. If you are unable to provide an accurate translation based on the input, output "Unable to provide translation." For example, if the Spanish input is "Gracias por su atención.", output: "Grazie per la sua attenzione." (Full translations will typically be longer and correspond to complete email bodies.)

Context and Data:
Cuerpo del correo electrónico en español: {{FIELD:fldobmkup53xgrvLl}}

Output:

```

---

## REFERENCIA RÁPIDA DE IDs

### Tablas

| # | Tabla | ID | Campos |
|--:|-------|-----|--------|
| 1 | Stakeholders_Companies | `tbl47AWmhYAXerbWz` | 59 |
| 2 | Stakeholders_Companies_Financials | `tblYiuZOi2VGRXqgA` | 13 |
| 3 | Stakeholders_Business_Units | `tblbBsypFvEnooHlr` | 37 |
| 4 | Stakeholders_Contacts | `tblfErIdCjpMkXK17` | 33 |
| 5 | Opportunities - Global Overview | `tblMA730dbXi0Qgqf` | 21 |
| 6 | Opportunity - Adaptation | `tbl6LzYm86cOmOZp9` | 6 |
| 7 | Opportunity - Q&A | `tblUJJNmQweYnYJC7` | 11 |
| 8 | Distribution - Investor Selection | `tblilY0MuymFNdUGA` | 28 |
| 9 | Distribution - Waves | `tblQlEQn1vBmN2MKQ` | 23 |
| 10 | Investor Workstreams | `tblbdMCGgItSYA4tD` | 19 |
| 11 | Internal - Initiatives | `tbl20Bnxshef5bgCe` | 17 |
| 12 | Internal - Tasks | `tbl5UXB4ldePObTlM` | 24 |
| 13 | Help & Feedback - Suggestions | `tblh42ZHkAoptEXlZ` | 9 |
| 14 | Config - Email Templates | `tblywzQ8HedD1nHKF` | 16 |
| 15 | Config - Email Activity | `tblFY14T1zGnPpitb` | 17 |
| 16 | Config - Users | `tblb3kyXSnXS0GPjy` | 12 |
| 17 | Config - Variables | `tblVWtmUZSjitPmOS` | 7 |
| 18 | Config_General_Fields | `tblMrM2E16GXu1VGi` | 3 |
| 19 | Config_Currencies | `tblTYGiICGBehlRZg` | 6 |
| 20 | Config_Countries | `tblC4FxquuxAbf43R` | 21 |
| 21 | Config_Stakeholder_Types | `tbl7R8gjn6KcBYGQj` | 5 |
| 22 | Config_Stakeholder_SubTypes | `tblV2bTQNIYcVULi3` | 9 |
| 23 | Config_Sector_And_Activities | `tblo8dIgdxNMJmcx7` | 14 |
| 24 | Config_Languages | `tblXrAdnl3O16AAyE` | 6 |
| 25 | GICS_Standard | `tblNjc8JHcC6jT9H9` | 8 |
| 26 | Config_Certificates | `tblQ5HZtmVe2ft9xH` | 11 |
| 27 | Config_Activities | `tblcOpprnVmtsMbH4` | 10 |
| 28 | Market_Context | `tblkE6YhMlxn9XXX5` | 19 |
| 29 | Origination_Campaigns | `tbl0B5YGXveYzyADI` | 23 |
| 30 | Campaign_Targets | `tblblROgAVEcWQ7WQ` | 20 |
| 31 | Config_Credit_Strategies | `tbla0eiBSmhIg4lU7` | 3 |
| 32 | Config_Sources | `tbl4MEJa6mh1w3EG4` | 19 |
| 33 | Source_Extractions | `tblXX2Uqa0xQCtHSD` | 22 |
| 34 | Company_Certificates | `tbl6PZVZasLc0zr9S` | 11 |

---

## INFORMACIÓN DE VERSIÓN

| Campo | Valor |
|-------|-------|
| Fecha generación | 2025-12-30 11:46:55 UTC |
| Base ID | `appEgNSP0tOLJ9YJ9` |
| Total tablas | 34 |
| Total campos | 562 |
| Total relaciones | 139 |

---

*Fin del documento*