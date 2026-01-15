# 📘 Guía de Usuario - Motor de Originación Alter-5

Esta guía está dirigida al **equipo comercial** para utilizar el sistema de originación de campañas.

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Cómo Crear Campañas](#cómo-crear-campañas)
3. [Cómo Revisar Targets](#cómo-revisar-targets)
4. [Cómo Aprobar Envíos](#cómo-aprobar-envíos)
5. [Vistas en Airtable](#vistas-en-airtable)
6. [FAQ](#faq)

---

## 🎯 Introducción

El Motor de Originación automatiza el proceso de:

1. **Encontrar empresas** que necesitan financiación
2. **Evaluar** si son elegibles para garantías FEI
3. **Crear campañas** personalizadas de outreach
4. **Generar emails** hiper-personalizados

### Flujo de Trabajo

```
Trigger de Mercado → Análisis AI → Selección Targets → Emails Personalizados → Envío (Mailchimp)
         ↓                 ↓                ↓                     ↓
    "BCE baja        Sectores         30 empresas          150 palabras
    tipos 0.25%"     afectados        priorizadas          por email
```

---

## 📝 Cómo Crear Campañas

### Paso 1: Identificar un Trigger de Mercado

Un **trigger** es un evento de mercado que genera oportunidades de financiación:

- 📉 **Bajada de tipos de interés** → Empresas buscan refinanciar
- 📋 **Nueva regulación** → Empresas necesitan adaptarse
- 🏭 **Crisis sectorial** → Empresas necesitan liquidez
- 🌱 **Subvenciones verdes** → Empresas quieren invertir

### Paso 2: Crear la Campaña desde CLI

```bash
python -m cli.main campaign create "BCE baja tipos 0.25%" \
    --sectors Industrials,Renewables \
    --countries ES,PT \
    --max 25
```

### Paso 3: Revisar en Airtable

La campaña aparecerá en la tabla **Origination_Campaigns** con:
- Status: `Proposal`
- Lista de targets preseleccionados
- Borradores de emails generados

---

## 🔍 Cómo Revisar Targets

### En la Vista "Targets Pendientes"

Cada target muestra:

| Campo | Descripción |
|-------|-------------|
| **Company Name** | Nombre de la empresa |
| **Fit Score** | Puntuación 0-100% de relevancia |
| **FEI Status** | Elegibilidad para garantía FEI |
| **Selection Reason** | Por qué fue seleccionada |
| **Email Draft** | Borrador del email |

### Criterios de Revisión

✅ **Aprobar si:**
- Fit Score ≥ 60%
- FEI Status = "Eligible" o "Partially_Eligible"
- La empresa es real y relevante

❌ **Rechazar si:**
- Empresa ya es cliente
- Información incorrecta
- No encaja con el trigger

### Acciones Disponibles

- **Aprobar**: Marcar `Outreach_Status = "Approved"`
- **Rechazar**: Marcar `Outreach_Status = "Rejected"` + nota
- **Editar Email**: Modificar el borrador si es necesario

---

## ✉️ Cómo Aprobar Envíos

### Paso 1: Verificar Targets Aprobados

En la vista "Targets Aprobados", confirmar:
- Todos los emails han sido revisados
- La información de contacto es correcta
- No hay duplicados

### Paso 2: Aprobar la Campaña

Cambiar el status de la campaña:
```
Status: Proposal → Approved
```

### Paso 3: Iniciar Envío (si Mailchimp está configurado)

```bash
python -m cli.main campaign send recCampaignXXX
```

### Paso 4: Monitorear Resultados

En la vista "Métricas de Campaña":
- **Sent**: Emails enviados
- **Opened**: Emails abiertos
- **Clicked**: Clicks en enlaces
- **Replied**: Respuestas recibidas

---

## 📊 Vistas en Airtable

### Vista: Pipeline FEI (Companies)

Muestra empresas agrupadas por elegibilidad FEI:
- 🟢 **Eligible**: Listas para campañas FEI
- 🟡 **Partially_Eligible**: Requieren verificación
- 🔴 **Not_Eligible**: No cumplen criterios
- ⚪ **Unknown**: Pendientes de evaluación

### Vista: Campañas Activas

Muestra campañas en curso con métricas:
- Nombre y trigger
- Número de targets
- Tasas de apertura/click
- Estado actual

### Vista: Targets Pendientes

Muestra targets esperando aprobación:
- Ordenados por Fit Score
- Filtrados por campaña
- Con borrador de email

---

## ❓ FAQ

### ¿Cuántos targets máximo por campaña?
Por defecto, **30 targets** por campaña. Este límite garantiza personalización de calidad.

### ¿Cuánto tiempo tarda en crear una campaña?
El proceso automatizado tarda **5-15 minutos** dependiendo del número de targets.

### ¿Puedo editar los emails generados?
**Sí**, todos los borradores son editables. Se recomienda revisar antes de aprobar.

### ¿Qué es el "cooling-off period"?
Una empresa no puede ser contactada nuevamente hasta **90 días** después del último contacto. El sistema lo filtra automáticamente.

### ¿Qué significa FEI Status?
| Status | Significado |
|--------|-------------|
| **Eligible** | Cumple criterios FEI, puede solicitar garantía |
| **Partially_Eligible** | Cumple parcialmente, requiere verificación |
| **Not_Eligible** | No cumple criterios actuales |
| **Unknown** | No evaluada aún |
| **Expired** | Certificados/premios caducados |

### ¿Cómo se calcula el Fit Score?
Basado en:
- 30% - Relevancia sectorial
- 25% - Match con trigger
- 20% - Elegibilidad FEI
- 15% - Tamaño de empresa
- 10% - Datos de contacto

### ¿Qué hago si un target es incorrecto?
1. Marcar como "Rejected" en Airtable
2. Añadir nota explicando el motivo
3. El sistema aprende para futuras selecciones

### ¿Puedo crear campañas sin trigger?
Sí, usando el comando de selección directa:
```bash
python -m cli.main campaign select recCampaignXXX --sectors "Renewables" --countries "ES"
```

---

## 📞 Soporte

Para problemas técnicos o dudas:
- **Email**: soporte-tech@alter5.com
- **Documentación técnica**: Ver `README.md`

---

*Última actualización: Enero 2026*

