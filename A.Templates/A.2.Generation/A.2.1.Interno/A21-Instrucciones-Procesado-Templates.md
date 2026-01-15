# 🔧 Instrucciones Genéricas de Procesamiento de Plantillas

## Guía Exhaustiva para Procesamiento de Documentos con Plantillas

---

## 🎯 OBJETIVO Y ALCANCE

### Propósito de estas Instrucciones

Estas instrucciones están diseñadas para garantizar que cualquier LLM procese correctamente las plantillas creadas y genere documentos finales de calidad profesional que parezcan elaborados por un experto humano. El documento resultante debe ser un **entregable final** listo para su uso inmediato.

### Aplicabilidad

Estas instrucciones son válidas para TODAS las plantillas del sistema:
- ✅ Product Requirements Document (`create-prd.md`)
- ✅ Generación de Tareas de Desarrollo (`generate-tasks.md`)
- ✅ Análisis de Producto y Mercado (`generate-analisis-producto-mercado.md`)
- ✅ Especificaciones de Frontend (`generate-frontend-specs.md`)
- ✅ Informe Científico-Técnico (`generate-informe-cientifico-tecnico.md`)
- ✅ Análisis Funcional Completo (`Plantilla-Analisis-Funcional-Completo.md`)
- ✅ Propuestas Comerciales (`generate-propuesta-comercial.md`)
- ✅ Contratos SaaS (`generate-contrato-saas.md`)
- ✅ Memorias Técnico-Económicas (`generate-memoria-tecnico-economica.md`)
- ✅ Y cualquier plantilla futura que siga la estructura establecida

---

## 📖 FASE 1: LECTURA Y COMPRENSIÓN DE LA PLANTILLA

### 1.1 Análisis Inicial de la Plantilla

**OBLIGATORIO**: Antes de comenzar a generar contenido, debes:

1. **Leer completamente la plantilla** de principio a fin
2. **Identificar el tipo de documento** y su propósito específico
3. **Localizar las instrucciones específicas** del agente experto
4. **Mapear todas las secciones** obligatorias y opcionales
5. **Identificar todos los placeholders** que requieren reemplazo

### 1.2 Identificación de Elementos Clave

**Busca y cataloga estos elementos**:

- **Secciones [OBLIGATORIO]**: Deben completarse siempre
- **Secciones [OPCIONAL]**: Completar solo si es relevante para el contexto
- **Placeholders `[VARIABLE]`**: Reemplazar con información específica
- **Instrucciones específicas**: Seguir al pie de la letra
- **Nivel de detalle requerido**: Respetar las especificaciones de longitud
- **Audiencia objetivo**: Adaptar el tono y nivel técnico
- **Formato específico**: Mantener estructura, tablas, listas, etc.

### 1.3 Comprensión del Contexto

**Analiza el contexto proporcionado**:
- Información del proyecto/cliente/problema
- Documentos de referencia mencionados
- Restricciones específicas del dominio
- Objetivos del documento final

---

## ⚙️ FASE 2: PROCESAMIENTO Y GENERACIÓN

### 2.1 Reemplazo de Placeholders

**REGLAS CRÍTICAS para placeholders `[VARIABLE]`**:

1. **NUNCA dejes un placeholder sin reemplazar**
2. **Reemplaza con información específica y relevante**
3. **Si no tienes información exacta, genera contenido realista y coherente**
4. **Mantén la coherencia entre placeholders relacionados**
5. **Respeta el formato esperado** (fechas, números, nombres, etc.)

**Ejemplos de reemplazo correcto**:
- `[DD/MM/AAAA]` → `15/01/2024`
- `[NOMBRE_PROYECTO]` → `Sistema de Gestión Inteligente de Inventarios`
- `[SECTOR_ESPECÍFICO]` → `Retail y Comercio Electrónico`
- `[DESCRIPCIÓN_OBJETIVO_ESPECÍFICO]` → `Optimizar la gestión de inventarios mediante IA predictiva para reducir costes operativos en un 25%`

### 2.2 Procesamiento de Secciones

**Para secciones [OBLIGATORIO]**:
- Completar SIEMPRE con contenido sustancial
- Respetar longitudes mínimas y máximas especificadas
- Incluir todos los elementos solicitados
- Mantener el nivel de detalle requerido

**Para secciones [OPCIONAL]**:
- Evaluar relevancia para el contexto específico
- Si es relevante, completar con el mismo rigor que las obligatorias
- Si no es relevante, omitir completamente (no dejar vacía)

### 2.3 Generación de Contenido Profesional

**Principios fundamentales**:

1. **Especificidad sobre generalidad**: Evitar contenido genérico
2. **Datos cuantitativos**: Incluir números, porcentajes, métricas específicas
3. **Coherencia interna**: Mantener consistencia en todo el documento
4. **Nivel técnico apropiado**: Adaptar al expertise de la audiencia
5. **Actionabilidad**: Proporcionar recomendaciones concretas y ejecutables

---

## 👤 FASE 3: HUMANIZACIÓN DEL CONTENIDO

### 3.1 Eliminación de Elementos de Plantilla

**OBLIGATORIO eliminar**:
- Todas las marcas `[OBLIGATORIO]` y `[OPCIONAL]`
- Instrucciones entre paréntesis como `(Mínimo 150 palabras)`
- Comentarios explicativos dirigidos al LLM
- Placeholders no reemplazados
- Referencias a "completar esta sección"

### 3.2 Completar Elementos Interactivos

**Checkboxes y listas de tareas**:
- `- [ ]` → `- ✅` (para tareas completadas)
- `- [ ]` → `- ⏳` (para tareas en progreso)
- `- [ ]` → `- ❌` (para tareas no aplicables)

**Tablas**:
- Completar todas las celdas con datos específicos
- Eliminar filas de ejemplo si no son necesarias
- Mantener formato y alineación

### 3.3 Tono y Estilo Profesional

**Características del contenido final**:

1. **Autoridad y expertise**: Escribir como un experto en la materia
2. **Claridad y precisión**: Evitar ambigüedades
3. **Profesionalismo**: Tono formal pero accesible
4. **Confianza**: Afirmaciones seguras respaldadas por datos
5. **Orientación a resultados**: Enfoque en outcomes y beneficios

---

## ✅ FASE 4: VALIDACIÓN Y CONTROL DE CALIDAD

### 4.1 Checklist de Completitud

**Verificar antes de entregar**:

- [ ] ✅ Todas las secciones obligatorias están completas
- [ ] ✅ Todos los placeholders han sido reemplazados
- [ ] ✅ No quedan elementos de plantilla visibles
- [ ] ✅ El contenido es específico y relevante al contexto
- [ ] ✅ Las longitudes de sección respetan los requisitos
- [ ] ✅ El formato y estructura se mantienen correctamente
- [ ] ✅ El tono es profesional y apropiado para la audiencia
- [ ] ✅ Hay coherencia entre todas las secciones
- [ ] ✅ Se incluyen datos cuantitativos donde es posible
- [ ] ✅ Las recomendaciones son accionables y específicas

### 4.2 Validación de Calidad Técnica

**Criterios de evaluación**:

1. **Rigor técnico**: El contenido demuestra expertise en la materia
2. **Coherencia interna**: No hay contradicciones entre secciones
3. **Completitud**: Todas las preguntas implícitas están respondidas
4. **Utilidad práctica**: El documento sirve para tomar decisiones
5. **Profesionalismo**: El documento refleja estándares empresariales altos

### 4.3 Revisión Final

**Antes de entregar, confirmar**:
- El documento es un entregable final completo
- No requiere edición adicional para su uso
- Cumple con el propósito específico de la plantilla
- Refleja el nivel de expertise esperado del agente especializado

---

## 🚨 REGLAS CRÍTICAS Y PROHIBICIONES

### ❌ NUNCA HAGAS ESTO

1. **NO dejes placeholders sin reemplazar**
2. **NO incluyas instrucciones de la plantilla en el documento final**
3. **NO uses contenido genérico o de relleno**
4. **NO omitas secciones obligatorias**
5. **NO cambies la estructura fundamental de la plantilla**
6. **NO uses un tono informal o poco profesional**
7. **NO hagas afirmaciones sin fundamento**
8. **NO dejes checkboxes sin marcar**
9. **NO incluyas comentarios como "Esta sección debe completarse"**
10. **NO generes contenido que requiera validación externa para ser útil**

### ✅ SIEMPRE HAZ ESTO

1. **SÍ reemplaza todos los elementos variables con contenido específico**
2. **SÍ mantén el nivel de detalle y rigor especificado**
3. **SÍ adapta el contenido al contexto específico proporcionado**
4. **SÍ incluye datos cuantitativos y métricas específicas**
5. **SÍ proporciona recomendaciones accionables**
6. **SÍ mantén coherencia en todo el documento**
7. **SÍ usa un tono profesional y experto**
8. **SÍ completa todos los elementos interactivos**
9. **SÍ genera un documento inmediatamente utilizable**
10. **SÍ respeta las especificaciones técnicas de cada plantilla**

---

## 🎯 INSTRUCCIONES ESPECÍFICAS POR TIPO DE PLANTILLA

### Para Product Requirements Document (PRD)
- Mantén enfoque en valor de negocio y alineación estratégica
- Incluye métricas de éxito específicas y medibles
- Proporciona análisis de riesgos detallado y planes de mitigación
- Especifica criterios de aceptación claros y testeable

### Para Generación de Tareas de Desarrollo
- Descompón épicas en user stories específicas y estimables
- Incluye dependencias técnicas y secuenciación lógica
- Proporciona estimaciones realistas basadas en complejidad
- Especifica criterios de definición de "hecho" (DoD)

### Para Análisis de Producto y Mercado
- Enfócate en datos de mercado reales y tendencias actuales
- Incluye análisis competitivo específico
- Proporciona métricas cuantificables de oportunidad

### Para Especificaciones de Frontend
- Mantén coherencia con principios de UX/UI modernos
- Especifica tecnologías y frameworks concretos
- Incluye wireframes o descripciones visuales detalladas

### Para Informes Científico-Técnicos
- Mantén rigor académico y precisión matemática
- Incluye referencias bibliográficas actualizadas
- Justifica todas las decisiones algorítmicas

### Para Análisis Funcional
- Proporciona insights accionables y específicos
- Incluye recomendaciones priorizadas
- Mantén enfoque en valor de negocio

### Para Propuestas Comerciales
- Incluye pricing específico y justificado
- Proporciona cronogramas detallados
- Enfócate en ROI y beneficios cuantificables

---

## 📋 CHECKLIST FINAL DE ENTREGA

Antes de considerar el documento completado, verifica:

### Estructura y Formato
- [ ] ✅ Mantiene la estructura original de la plantilla
- [ ] ✅ Todos los títulos y subtítulos están presentes
- [ ] ✅ El formato markdown está correcto
- [ ] ✅ Las tablas están completas y bien formateadas
- [ ] ✅ Las listas y numeraciones son consistentes

### Contenido y Calidad
- [ ] ✅ Cada sección tiene contenido sustancial y relevante
- [ ] ✅ No hay contenido genérico o de relleno
- [ ] ✅ Los datos y métricas son específicos y realistas
- [ ] ✅ Las recomendaciones son accionables
- [ ] ✅ El nivel técnico es apropiado para la audiencia

### Profesionalismo
- [ ] ✅ El tono es profesional y experto
- [ ] ✅ No hay errores gramaticales o de formato
- [ ] ✅ El documento inspira confianza y credibilidad
- [ ] ✅ Es inmediatamente utilizable sin edición adicional

### Completitud
- [ ] ✅ Todas las secciones obligatorias están completas
- [ ] ✅ Todos los placeholders han sido reemplazados
- [ ] ✅ No quedan elementos de plantilla visibles
- [ ] ✅ El documento cumple su propósito específico

---

## 🔄 PROCESO DE MEJORA CONTINUA

Si durante el procesamiento encuentras:
- **Información insuficiente**: Genera contenido realista y coherente basado en mejores prácticas del sector
- **Contradicciones en la plantilla**: Prioriza las instrucciones más específicas
- **Ambigüedades**: Interpreta en favor de mayor calidad y especificidad
- **Elementos faltantes**: Completa con contenido apropiado para mantener la coherencia

**Recuerda**: El objetivo final es generar un documento que un experto humano estaría orgulloso de entregar a un cliente o stakeholder importante.