# 📊 Plantilla DERCIOM - Investigación Operativa
## Guía Exhaustiva para Análisis de Problemas de Optimización

---

## 🎯 INSTRUCCIONES DE USO PARA AGENTE DE IA

### Propósito del Documento DERCIOM

El documento **DERCIOM** es una metodología estructurada de OGA para el análisis completo de problemas que pueden resolverse mediante **Investigación Operativa**. El acrónimo significa:

- **D**escripción del problema
- **E**ntidades y conjuntos fundamentales  
- **R**estricciones (duras y blandas)
- **C**riterios de optimización
- **I**nputs (datos de entrada)
- **O**utputs (resultados esperados)
- **M**odelo matemático

### Nivel de Rigor Requerido

**CRÍTICO**: Este documento debe mantener el **mismo nivel de detalle técnico y rigor matemático** que el documento de referencia Smartiming-DERCIOM. Esto significa:

- **Profundidad técnica**: Explicaciones detalladas con ejemplos concretos
- **Rigor matemático**: Formulaciones precisas cuando sea aplicable
- **Exhaustividad**: Cobertura completa de todos los aspectos del problema
- **Claridad narrativa**: Explicaciones comprensibles pero técnicamente precisas
- **Ejemplos ilustrativos**: Casos concretos que clarifiquen conceptos abstractos

### Instrucciones Específicas

1. **Reemplaza TODOS los placeholders** `[VARIABLE]` con información específica del problema
2. **Mantén la estructura exacta** de secciones del documento original
3. **Incluye ejemplos concretos** en cada sección, no te limites a descripciones genéricas
4. **Desarrolla la formulación matemática** con el nivel de detalle del anexo original
5. **Asegura coherencia** entre todas las secciones del documento
6. **Valida completitud** usando el checklist al final

---

## 📋 INFORMACIÓN DE CONTEXTO [OBLIGATORIO]

**Proyecto/Sistema**: [NOMBRE_ESPECÍFICO_PROYECTO]  
**Fecha de Análisis**: [DD/MM/AAAA]  
**Analista(s)**: [NOMBRE_ANALISTA] - [ESPECIALIDAD]  
**Experto(s) de Dominio**: [NOMBRE_EXPERTO] - [CARGO] ([AÑOS_EXPERIENCIA] años)  
**Organización**: [NOMBRE_EMPRESA/INSTITUCIÓN]  
**Departamento/Área**: [ÁREA_ESPECÍFICA]  
**Tipo de Problema**: [Programación/Asignación/Ruteo/Scheduling/Inventario/etc.]  
**Complejidad Estimada**: [NP-Difícil/Polinomial/Exponencial]  
**Metodología**: [Entrevistas/Observación/Análisis documental/Transcripciones]

---

## 1. DESCRIPCIÓN GENERAL [OBLIGATORIO]

### Contexto del Problema

[Descripción detallada del problema o situación que requiere optimización. Incluir el entorno organizacional, las limitaciones actuales, y por qué es necesario aplicar Investigación Operativa. Mínimo 200 palabras explicando la situación actual y la motivación para la optimización.]

**Ejemplo de nivel de detalle requerido:**
> "En este instituto, la mayor parte de la actividad lectiva se concentra en el turno de mañana, con clases de 8:15 a 14:45 (cada sesión dura 1 hora) y un recreo de 30 minutos a media mañana (de 11:15 a 11:45). Excepción: existe únicamente un grupo de secundaria para adultos en horario de tarde (18:00 a 22:00), cuyo horario actualmente se elabora manualmente por separado..."

### Situación Actual (As Is)

[Descripción exhaustiva de cómo se resuelve actualmente el problema, incluyendo:]

- **Proceso manual actual**: [Descripción paso a paso del proceso existente]
- **Recursos involucrados**: [Personal, tiempo, herramientas utilizadas]
- **Limitaciones identificadas**: [Problemas específicos del proceso actual]
- **Métricas actuales**: [Indicadores de rendimiento del proceso existente]
- **Costes asociados**: [Tiempo, recursos, ineficiencias cuantificadas]

### Visión Propuesta (To Be)

[Descripción detallada de la solución optimizada propuesta, incluyendo:]

- **Automatización prevista**: [Qué procesos se automatizarán]
- **Mejoras esperadas**: [Beneficios específicos y cuantificados]
- **Integración con sistemas**: [Cómo se conectará con sistemas existentes]
- **Flujo de trabajo optimizado**: [Proceso paso a paso mejorado]
- **Impacto organizacional**: [Cambios en roles, responsabilidades, procesos]

### Clasificación del Problema

- **Tipo de Optimización**: [Lineal/No lineal/Entera/Mixta/Estocástica]
- **Naturaleza**: [Determinística/Estocástica]
- **Horizonte Temporal**: [Estático/Dinámico/Multi-periodo]
- **Objetivos**: [Mono-objetivo/Multi-objetivo]
- **Complejidad Computacional**: [P/NP/NP-Completo/NP-Difícil]

---

## 2. ENTIDADES Y CONJUNTOS FUNDAMENTALES [OBLIGATORIO]

### Entidades Principales

Para cada entidad, proporcionar:
- **Definición precisa**
- **Atributos relevantes**
- **Relaciones con otras entidades**
- **Ejemplos concretos**
- **Cardinalidad estimada**

#### [ENTIDAD_1]: [NOMBRE_ENTIDAD]
- **Definición**: [Descripción técnica precisa de qué representa esta entidad]
- **Atributos**:
  - `[atributo_1]`: [Tipo de dato] - [Descripción y rango de valores]
  - `[atributo_2]`: [Tipo de dato] - [Descripción y rango de valores]
  - `[atributo_n]`: [Tipo de dato] - [Descripción y rango de valores]
- **Ejemplos**: [2-3 ejemplos concretos con valores específicos]
- **Cardinalidad**: [Número estimado de instancias]
- **Relaciones**: [Cómo se relaciona con otras entidades]

#### [ENTIDAD_2]: [NOMBRE_ENTIDAD]
[Repetir estructura anterior]

### Conjuntos y Dominios

#### Conjuntos Básicos
- **[CONJUNTO_1]** = {[elemento_1], [elemento_2], ..., [elemento_n]}
  - *Descripción*: [Qué representa este conjunto]
  - *Cardinalidad*: |[CONJUNTO_1]| = [número]
  - *Propiedades*: [Características especiales del conjunto]

#### Conjuntos Derivados
- **[CONJUNTO_DERIVADO]** = [CONJUNTO_1] × [CONJUNTO_2] × ... 
  - *Descripción*: [Producto cartesiano o combinación específica]
  - *Cardinalidad*: |[CONJUNTO_DERIVADO]| = [cálculo]
  - *Restricciones*: [Limitaciones en las combinaciones válidas]

### Parámetros del Sistema

| Parámetro | Símbolo | Descripción | Tipo | Rango/Valores |
|-----------|---------|-------------|------|---------------|
| [Parámetro_1] | [p₁] | [Descripción detallada] | [Entero/Real/Binario] | [min, max] |
| [Parámetro_2] | [p₂] | [Descripción detallada] | [Entero/Real/Binario] | [min, max] |

---

## 3. RESTRICCIONES [OBLIGATORIO]

### 3.1 Restricciones Duras (Obligatorias)

**IMPORTANTE**: Estas restricciones deben cumplirse al 100%. Su violación hace la solución inválida.

#### RD001: [NOMBRE_RESTRICCIÓN_DURA_1]
- **Descripción**: [Explicación detallada de la restricción]
- **Justificación**: [Por qué es obligatoria - legal, técnica, física]
- **Formulación Matemática**: 
  ```
  [Expresión matemática precisa]
  ∀ [dominio de aplicación]
  ```
- **Ejemplo**: [Caso concreto que ilustre la restricción]
- **Impacto si se viola**: [Consecuencias específicas]

#### RD002: [NOMBRE_RESTRICCIÓN_DURA_2]
[Repetir estructura anterior]

### 3.2 Restricciones Blandas (Preferencias y Criterios Flexibles)

**IMPORTANTE**: Estas restricciones son deseables pero no obligatorias. Se incorporan en la función objetivo como penalizaciones.

#### RB001: [NOMBRE_RESTRICCIÓN_BLANDA_1]
- **Descripción**: [Explicación detallada de la preferencia]
- **Nivel de Importancia**: [Crítica/Alta/Media/Baja]
- **Peso en Función Objetivo**: [W₁] = [valor numérico]
- **Formulación como Penalización**:
  ```
  Penalización = W₁ × [expresión de violación]
  ```
- **Ejemplo**: [Caso concreto que ilustre la preferencia]
- **Justificación**: [Por qué es deseable]

#### RB002: [NOMBRE_RESTRICCIÓN_BLANDA_2]
[Repetir estructura anterior]

### Matriz de Restricciones

| ID | Tipo | Descripción | Criticidad | Complejidad | Impacto |
|----|------|-------------|------------|-------------|---------|
| RD001 | Dura | [Descripción breve] | Obligatoria | [Alta/Media/Baja] | [Descripción] |
| RB001 | Blanda | [Descripción breve] | [Nivel] | [Alta/Media/Baja] | [Descripción] |

---

## 4. CRITERIOS DE OPTIMIZACIÓN (OBJETIVOS) [OBLIGATORIO]

### Función Objetivo Principal

**Tipo**: [Minimización/Maximización]

**Formulación Matemática**:
```
[Función objetivo principal con notación matemática precisa]
Minimizar/Maximizar Z = Σ [términos específicos]
```

**Componentes de la Función Objetivo**:

#### Componente 1: [NOMBRE_COMPONENTE]
- **Descripción**: [Qué mide este componente]
- **Peso**: [W₁] = [valor y justificación]
- **Formulación**: [Expresión matemática específica]
- **Unidades**: [Unidades de medida]

#### Componente 2: [NOMBRE_COMPONENTE]
[Repetir estructura anterior]

### Objetivos Secundarios (si aplica)

En caso de optimización multi-objetivo:

#### Objetivo 2: [NOMBRE_OBJETIVO_SECUNDARIO]
- **Formulación**: [Expresión matemática]
- **Relación con objetivo principal**: [Conflicto/Sinergia/Independiente]
- **Método de manejo**: [Ponderación/Lexicográfico/Pareto]

### Métricas de Calidad de la Solución

| Métrica | Fórmula | Valor Objetivo | Rango Aceptable |
|---------|---------|----------------|-----------------|
| [Métrica_1] | [Fórmula] | [Valor ideal] | [min - max] |
| [Métrica_2] | [Fórmula] | [Valor ideal] | [min - max] |

---

## 5. DATOS DE ENTRADA (INPUTS) NECESARIOS [OBLIGATORIO]

### 5.1 Datos Maestros

#### Categoría 1: [NOMBRE_CATEGORÍA_DATOS]
- **Descripción**: [Qué tipo de información contiene]
- **Fuente**: [De dónde se obtienen los datos]
- **Formato**: [CSV/JSON/Base de datos/API/Manual]
- **Frecuencia de actualización**: [Diaria/Semanal/Mensual/Anual]
- **Volumen estimado**: [Número de registros]

**Estructura de datos**:
```
[NOMBRE_TABLA/ARCHIVO]:
- campo_1: [tipo] - [descripción]
- campo_2: [tipo] - [descripción]
- campo_n: [tipo] - [descripción]
```

**Ejemplo de datos**:
```
Registro 1: {campo_1: valor_1, campo_2: valor_2, ...}
Registro 2: {campo_1: valor_3, campo_2: valor_4, ...}
```

#### Categoría 2: [NOMBRE_CATEGORÍA_DATOS]
[Repetir estructura anterior]

### 5.2 Parámetros de Configuración

| Parámetro | Descripción | Tipo | Valor por Defecto | Rango Válido |
|-----------|-------------|------|-------------------|--------------|
| [param_1] | [Descripción] | [Tipo] | [Valor] | [min, max] |
| [param_2] | [Descripción] | [Tipo] | [Valor] | [min, max] |

### 5.3 Restricciones Dinámicas

- **[RESTRICCIÓN_DINÁMICA_1]**: [Descripción y cómo se especifica]
- **[RESTRICCIÓN_DINÁMICA_2]**: [Descripción y cómo se especifica]

### 5.4 Validaciones de Entrada

#### Validaciones Críticas
- [ ] **[VALIDACIÓN_1]**: [Descripción de la validación]
- [ ] **[VALIDACIÓN_2]**: [Descripción de la validación]

#### Validaciones de Consistencia
- [ ] **[CONSISTENCIA_1]**: [Verificación entre conjuntos de datos]
- [ ] **[CONSISTENCIA_2]**: [Verificación de integridad referencial]

### 5.5 Datos de Ejemplo

**Conjunto de datos mínimo para pruebas**:
- [ENTIDAD_1]: [X] registros
- [ENTIDAD_2]: [Y] registros
- Parámetros: [Lista de valores específicos]

---

## 6. RESULTADOS ESPERADOS (OUTPUTS) [OBLIGATORIO]

### 6.1 Solución Principal

#### Estructura de la Solución
```
SOLUCIÓN_ÓPTIMA:
{
  "objetivo_principal": [valor_numérico],
  "tiempo_ejecución": [segundos],
  "estado_optimización": "[Óptima/Factible/No_factible]",
  "asignaciones": {
    "[entidad_1]": {
      "[atributo_1]": [valor],
      "[atributo_2]": [valor]
    }
  }
}
```

#### Ejemplo de Solución
[Proporcionar un ejemplo concreto de cómo se vería una solución típica]

### 6.2 Métricas de la Solución

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Valor función objetivo | [valor] | [Qué significa este valor] |
| Restricciones violadas | [número] | [Cuáles y por qué] |
| Gap de optimalidad | [porcentaje] | [Distancia al óptimo] |
| Tiempo de cálculo | [segundos] | [Rendimiento computacional] |

### 6.3 Reportes y Visualizaciones

#### Reporte Ejecutivo
- **Resumen de la solución**: [Descripción en lenguaje natural]
- **Beneficios cuantificados**: [Mejoras específicas vs situación actual]
- **Recomendaciones**: [Acciones sugeridas]

#### Reportes Técnicos
- **Detalle de asignaciones**: [Formato específico]
- **Análisis de sensibilidad**: [Cómo cambia la solución con parámetros]
- **Estadísticas de optimización**: [Métricas del proceso de solución]

#### Visualizaciones
- **[TIPO_GRÁFICO_1]**: [Qué muestra y para qué audiencia]
- **[TIPO_GRÁFICO_2]**: [Qué muestra y para qué audiencia]

### 6.4 Formatos de Exportación

| Formato | Propósito | Audiencia | Contenido |
|---------|-----------|-----------|-----------|
| PDF | Reporte ejecutivo | Directivos | Resumen y recomendaciones |
| Excel | Análisis detallado | Analistas | Datos completos y métricas |
| JSON/XML | Integración | Sistemas | Datos estructurados |
| CSV | Importación | Usuarios finales | Asignaciones específicas |

---

## 7. MÉTRICAS [OBLIGATORIO]

### 7.1 Métricas de Calidad de la Solución

#### Métricas Primarias
- **[MÉTRICA_PRIMARIA_1]**: 
  - *Definición*: [Cómo se calcula]
  - *Objetivo*: [Valor ideal]
  - *Rango aceptable*: [min - max]
  - *Frecuencia de medición*: [Cuándo se evalúa]

#### Métricas Secundarias
- **[MÉTRICA_SECUNDARIA_1]**:
  - *Definición*: [Cómo se calcula]
  - *Propósito*: [Para qué se usa]
  - *Umbral de alerta*: [Valor que requiere atención]

### 7.2 Métricas de Rendimiento del Sistema

| Métrica | Fórmula | Objetivo | Medición |
|---------|---------|----------|----------|
| Tiempo de ejecución | [fórmula] | < [X] segundos | Por ejecución |
| Uso de memoria | [fórmula] | < [Y] MB | Durante ejecución |
| Escalabilidad | [fórmula] | Lineal hasta [Z] entidades | Por tamaño de problema |

### 7.3 Métricas de Negocio

#### Beneficios Cuantificables
- **Reducción de costes**: [Cálculo específico]
- **Ahorro de tiempo**: [Horas/días ahorrados]
- **Mejora de eficiencia**: [Porcentaje de mejora]
- **ROI estimado**: [Retorno de inversión]

#### KPIs de Adopción
- **Tasa de uso**: [Porcentaje de casos que usan la optimización]
- **Satisfacción del usuario**: [Escala y método de medición]
- **Reducción de intervención manual**: [Porcentaje]

### 7.4 Dashboard de Monitoreo

**Métricas en tiempo real**:
- [Métrica_1]: Actualización [frecuencia]
- [Métrica_2]: Actualización [frecuencia]

**Alertas automáticas**:
- [Condición_1] → [Acción_1]
- [Condición_2] → [Acción_2]

---

## 8. ANEXO: FORMULACIÓN MATEMÁTICA DEL MODELO [OBLIGATORIO]

### 8.1 Notación Matemática

#### Conjuntos
- **[CONJUNTO_1]**: [Descripción] = {[elementos]}
- **[CONJUNTO_2]**: [Descripción] = {[elementos]}

#### Índices
- **[i]** ∈ [CONJUNTO_1]: [Descripción del índice]
- **[j]** ∈ [CONJUNTO_2]: [Descripción del índice]

#### Parámetros
- **[parámetro_1]**: [Descripción] [unidades]
- **[parámetro_2]**: [Descripción] [unidades]

#### Variables de Decisión
- **[variable_1]**: [Descripción] [tipo: binaria/entera/continua]
- **[variable_2]**: [Descripción] [tipo: binaria/entera/continua]

### 8.2 Formulación del Modelo

#### Función Objetivo
```
Minimizar/Maximizar:
Z = Σ[i∈I] Σ[j∈J] [coeficiente_ij] × [variable_ij] + [términos adicionales]
```

#### Restricciones Duras

**Restricción 1: [NOMBRE_RESTRICCIÓN]**
```
Σ[i∈I] [variable_i] [operador] [valor_derecho]  ∀ [dominio]
```
*Descripción*: [Qué garantiza esta restricción]

**Restricción 2: [NOMBRE_RESTRICCIÓN]**
```
[Formulación matemática específica]
```
*Descripción*: [Qué garantiza esta restricción]

#### Restricciones de Dominio
```
[variable_1] ∈ {0, 1}  ∀ [dominio]
[variable_2] ≥ 0       ∀ [dominio]
[variable_3] ∈ ℤ⁺      ∀ [dominio]
```

### 8.3 Extensiones del Modelo

#### Variantes del Problema
- **Versión estocástica**: [Cómo se modifica el modelo]
- **Versión multi-objetivo**: [Formulación alternativa]
- **Versión dinámica**: [Consideraciones temporales]

#### Técnicas de Solución Recomendadas
- **Método exacto**: [Algoritmo específico y justificación]
- **Heurística**: [Algoritmo aproximado para instancias grandes]
- **Metaheurística**: [Para casos muy complejos]

### 8.4 Análisis de Complejidad

- **Complejidad temporal**: O([expresión])
- **Complejidad espacial**: O([expresión])
- **Tamaño máximo resoluble**: [Estimación basada en recursos]

### 8.5 Validación del Modelo

#### Casos de Prueba
- **Instancia pequeña**: [Descripción y solución conocida]
- **Instancia mediana**: [Características]
- **Instancia grande**: [Límites de escalabilidad]

#### Verificación de Correctitud
- [ ] Todas las restricciones duras se cumplen
- [ ] La función objetivo es coherente con los criterios
- [ ] Las variables tienen dominios apropiados
- [ ] El modelo es matemáticamente consistente

---

## ✅ CHECKLIST DE COMPLETITUD Y CALIDAD

### Completitud del Documento
- [ ] Todos los placeholders [VARIABLE] han sido reemplazados
- [ ] Todas las secciones obligatorias están completas
- [ ] Se incluyen ejemplos concretos en cada sección
- [ ] La formulación matemática es precisa y completa
- [ ] Los datos de entrada están completamente especificados
- [ ] Los outputs esperados están claramente definidos

### Calidad Técnica
- [ ] El nivel de detalle es comparable al documento de referencia
- [ ] Las restricciones están correctamente clasificadas (duras/blandas)
- [ ] La función objetivo refleja los criterios de optimización
- [ ] El modelo matemático es coherente con la descripción narrativa
- [ ] Las métricas son específicas y medibles
- [ ] Se incluyen validaciones y casos de prueba

### Coherencia Interna
- [ ] Las entidades mencionadas en restricciones están definidas
- [ ] Los parámetros del modelo aparecen en los inputs
- [ ] Las variables de decisión se corresponden con los outputs
- [ ] La notación matemática es consistente en todo el documento
- [ ] Los ejemplos son coherentes con las definiciones

### Rigor Metodológico
- [ ] Se justifica por qué es un problema de Investigación Operativa
- [ ] Se identifica correctamente el tipo de optimización
- [ ] Las restricciones tienen justificación técnica o de negocio
- [ ] Se consideran aspectos de escalabilidad y rendimiento
- [ ] Se incluyen métricas de validación de la solución

---

**Analista**: [NOMBRE_ANALISTA] | **Fecha**: [DD/MM/AAAA]  
**Experto de Dominio**: [NOMBRE_EXPERTO] | **Validado**: [SÍ/NO]  
**Versión**: [X.Y] | **Estado**: [Borrador/En Revisión/Aprobado]

---

*Este documento DERCIOM constituye la especificación técnica completa para el desarrollo de una solución de Investigación Operativa para [NOMBRE_PROYECTO], integrando el conocimiento experto del dominio con metodologías de optimización matemática para asegurar el éxito del proyecto.*