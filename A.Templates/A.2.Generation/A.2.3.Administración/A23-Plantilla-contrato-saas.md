# Plantilla de Generación de Contratos SaaS - OGA

## OBJETIVO DE LA PLANTILLA
Esta plantilla está diseñada para que un LLM genere contratos completos y legalmente sólidos para aplicaciones SaaS B2B y B2B2C de OGA, aplicables en el marco legal Español/Europeo, con máxima protección para OGA y flexibilidad para todos los modelos de negocio.

## INSTRUCCIONES FUNDAMENTALES PARA EL LLM

### PRINCIPIOS BÁSICOS
1. **PROTECCIÓN MÁXIMA DE OGA**: Todas las cláusulas deben favorecer y proteger los intereses de OGA
2. **CUMPLIMIENTO NORMATIVO**: Estricto cumplimiento del marco legal Español/Europeo (RGPD, LSSI, Código Civil, etc.)
3. **FLEXIBILIDAD COMERCIAL**: Adaptable a cualquier modelo de negocio SaaS
4. **CLARIDAD JURÍDICA**: Lenguaje preciso que evite ambigüedades
5. **EJECUTABILIDAD**: Cláusulas ejecutables y defendibles legalmente

### MODELOS DE NEGOCIO A CUBRIR
- **Freemium**: Versión gratuita con limitaciones + versión premium
- **Trial**: Período de prueba gratuito con conversión a pago
- **Pago único**: Licencia perpetua o por proyecto
- **Suscripción recurrente**: Mensual, trimestral, anual
- **Por uso/créditos**: Facturación según consumo de API, procesamiento, etc.
- **Por seats/usuarios**: Facturación por número de usuarios activos
- **Híbrido**: Combinación de modelos anteriores

### MARCO LEGAL APLICABLE
- **RGPD** (Reglamento General de Protección de Datos)
- **LSSI** (Ley de Servicios de la Sociedad de la Información)
- **Código Civil Español**
- **Ley de Condiciones Generales de la Contratación**
- **Directiva de Servicios Digitales (DSA)**
- **Ley de Defensa de Consumidores y Usuarios** (cuando aplique B2C)

## ESTRUCTURA DEL CONTRATO

### 1. ENCABEZADO Y PARTES CONTRATANTES
```
CONTRATO DE PRESTACIÓN DE SERVICIOS SaaS
Entre [NOMBRE_CLIENTE] y OGA SOLUCIONES TECNOLÓGICAS, S.L.
```

**Instrucciones para el LLM:**
- Incluir datos completos de identificación de ambas partes
- Especificar representantes legales y poderes
- Incluir domicilios fiscales y de notificación
- Añadir número de identificación fiscal

### 2. ANTECEDENTES Y OBJETO DEL CONTRATO

**Instrucciones para el LLM:**
- Describir claramente el servicio SaaS específico
- Establecer el propósito comercial del contrato
- Definir el alcance técnico y funcional
- Especificar el modelo de negocio aplicable

### 3. DEFINICIONES Y GLOSARIO

**Términos obligatorios a definir:**
- Servicio/Aplicación
- Usuario Final
- Datos del Cliente
- Datos Personales
- Incidente de Seguridad
- Tiempo de Inactividad
- SLA (Service Level Agreement)
- API
- Créditos/Tokens (si aplica)
- Seats/Licencias (si aplica)

### 4. DESCRIPCIÓN DEL SERVICIO

**Instrucciones para el LLM:**
- Detallar funcionalidades principales
- Especificar limitaciones técnicas
- Definir niveles de servicio (SLA)
- Establecer métricas de rendimiento
- Incluir condiciones de disponibilidad

### 5. MODALIDADES DE CONTRATACIÓN Y FACTURACIÓN

**Para cada modelo de negocio, incluir:**

#### 5.1 FREEMIUM
- Limitaciones de la versión gratuita
- Condiciones de upgrade a premium
- Restricciones de uso comercial en versión gratuita
- Derechos de OGA sobre datos en versión gratuita

#### 5.2 TRIAL/PRUEBA
- Duración específica del período de prueba
- Limitaciones durante el trial
- Condiciones de conversión automática
- Política de cancelación durante el trial

#### 5.3 SUSCRIPCIÓN RECURRENTE
- Períodos de facturación (mensual, anual)
- Condiciones de renovación automática
- Política de cancelación y reembolsos
- Cambios de plan durante la suscripción

#### 5.4 PAGO POR USO/CRÉDITOS
- Definición de unidades de consumo
- Tarifas por tramo de uso
- Sistema de prepago vs. postpago
- Política de créditos no utilizados

#### 5.5 LICENCIAS POR USUARIO (SEATS)
- Definición de usuario activo
- Política de adición/eliminación de usuarios
- Facturación prorrateada
- Transferencia de licencias

### 6. OBLIGACIONES DE LAS PARTES

#### 6.1 OBLIGACIONES DE OGA
- Provisión del servicio según SLA
- Mantenimiento y actualizaciones
- Soporte técnico (niveles y horarios)
- Seguridad y protección de datos
- Notificación de incidentes

#### 6.2 OBLIGACIONES DEL CLIENTE
- Pago puntual de facturas
- Uso conforme a los términos
- Protección de credenciales de acceso
- Cumplimiento de normativas aplicables
- Colaboración en resolución de incidentes

### 7. PROPIEDAD INTELECTUAL E INDUSTRIAL

**Cláusulas de protección para OGA:**
- Propiedad exclusiva de OGA sobre el software
- Licencia limitada y revocable al cliente
- Prohibición de ingeniería inversa
- Protección de algoritmos y metodologías
- Derechos sobre mejoras y desarrollos

### 8. PROTECCIÓN DE DATOS Y PRIVACIDAD

**Cumplimiento RGPD obligatorio:**
- Roles de Responsable vs. Encargado del tratamiento
- Finalidades específicas del tratamiento
- Base legal para cada tratamiento
- Derechos de los interesados
- Medidas de seguridad técnicas y organizativas
- Procedimiento de notificación de brechas
- Transferencias internacionales (si aplica)

### 9. CONFIDENCIALIDAD

**Protección máxima para OGA:**
- Definición amplia de información confidencial
- Obligaciones de no divulgación
- Excepciones limitadas y específicas
- Duración indefinida de la confidencialidad
- Medidas de protección requeridas

### 10. NIVELES DE SERVICIO (SLA)

**Métricas específicas:**
- Disponibilidad del servicio (ej: 99.9%)
- Tiempo de respuesta (ej: <2 segundos)
- Tiempo de resolución de incidentes
- Penalizaciones por incumplimiento
- Exclusiones del SLA (mantenimiento, fuerza mayor)

### 11. LIMITACIÓN DE RESPONSABILIDAD

**Protección máxima para OGA:**
- Exclusión de daños indirectos y lucro cesante
- Limitación cuantitativa (ej: importe pagado en 12 meses)
- Exclusiones específicas por mal uso
- Responsabilidad del cliente por sus usuarios
- Indemnización a OGA por reclamaciones de terceros

### 12. FACTURACIÓN Y CONDICIONES DE PAGO

**Instrucciones para el LLM:**
- Especificar periodicidad de facturación
- Condiciones de pago (plazos, métodos)
- Intereses de demora
- Suspensión por impago
- Política de reembolsos (restrictiva)

### 13. DURACIÓN Y TERMINACIÓN

**Protección para OGA:**
- Duración mínima del contrato
- Condiciones de renovación
- Causas de terminación por OGA
- Efectos de la terminación
- Obligaciones post-terminación

### 14. MODIFICACIONES DEL SERVICIO

**Flexibilidad para OGA:**
- Derecho unilateral de modificación
- Procedimiento de notificación
- Período de adaptación para el cliente
- Derecho de terminación del cliente por cambios sustanciales

### 15. FUERZA MAYOR Y CIRCUNSTANCIAS EXCEPCIONALES

**Protección amplia:**
- Definición extensa de fuerza mayor
- Inclusión de ciberataques y pandemias
- Suspensión de obligaciones
- Procedimiento de notificación

### 16. RESOLUCIÓN DE CONFLICTOS

**Instrucciones para el LLM:**
- Jurisdicción española obligatoria
- Tribunales de Madrid (domicilio OGA)
- Mediación previa obligatoria
- Ley aplicable española

### 17. DISPOSICIONES GENERALES

**Cláusulas estándar:**
- Integridad del contrato
- Modificaciones por escrito
- Nulidad parcial
- Notificaciones válidas
- Cesión de derechos (prohibida para el cliente)

## ANEXOS OBLIGATORIOS

### ANEXO I: ESPECIFICACIONES TÉCNICAS
- Arquitectura del sistema
- Integraciones disponibles
- Formatos de datos soportados
- Requisitos técnicos del cliente

### ANEXO II: NIVELES DE SERVICIO (SLA) DETALLADOS
- Métricas específicas por funcionalidad
- Procedimientos de medición
- Reportes de cumplimiento
- Penalizaciones y compensaciones

### ANEXO III: POLÍTICA DE SEGURIDAD
- Medidas de seguridad implementadas
- Certificaciones de seguridad
- Procedimientos de backup
- Plan de continuidad de negocio

### ANEXO IV: TRATAMIENTO DE DATOS PERSONALES
- Addendum de procesamiento de datos (DPA)
- Categorías de datos tratados
- Finalidades específicas
- Medidas de seguridad RGPD

### ANEXO V: TARIFAS Y CONDICIONES COMERCIALES
- Estructura de precios detallada
- Descuentos por volumen
- Condiciones especiales
- Política de cambios de precio

## INSTRUCCIONES ESPECÍFICAS DE REDACCIÓN

### LENGUAJE Y ESTILO
1. **Precisión jurídica**: Usar terminología legal exacta
2. **Claridad**: Evitar ambigüedades que puedan perjudicar a OGA
3. **Completitud**: No dejar lagunas legales
4. **Coherencia**: Mantener consistencia terminológica

### CLÁUSULAS DE PROTECCIÓN OBLIGATORIAS
1. **Limitación de responsabilidad** máxima permitida por ley
2. **Exclusión de garantías** implícitas
3. **Indemnización** del cliente a OGA
4. **Jurisdicción** favorable a OGA
5. **Modificación unilateral** de términos

### ADAPTACIÓN POR MODELO DE NEGOCIO
- **Freemium**: Enfatizar limitaciones y derechos de OGA
- **Trial**: Conversión automática y limitaciones temporales
- **Suscripción**: Renovación automática y política de cancelación restrictiva
- **Por uso**: Medición precisa y facturación automática
- **Seats**: Control estricto de usuarios y transferencias

## CHECKLIST DE COMPLETITUD

### ✅ VERIFICACIONES OBLIGATORIAS
- [ ] Todas las cláusulas protegen los intereses de OGA
- [ ] Cumplimiento completo del marco legal Español/Europeo
- [ ] Adaptación específica al modelo de negocio
- [ ] Limitación máxima de responsabilidad de OGA
- [ ] Protección completa de propiedad intelectual
- [ ] Cumplimiento RGPD detallado
- [ ] SLA específicos y medibles
- [ ] Procedimientos de terminación favorables a OGA
- [ ] Jurisdicción y ley aplicable española
- [ ] Anexos técnicos y comerciales completos

### ✅ VALIDACIONES FINALES
- [ ] Coherencia entre cláusulas principales y anexos
- [ ] Ausencia de contradicciones internas
- [ ] Terminología consistente en todo el documento
- [ ] Numeración y referencias correctas
- [ ] Formato profesional y legible

## NOTAS IMPORTANTES PARA EL LLM

1. **SIEMPRE** favorecer los intereses de OGA en caso de ambigüedad
2. **NUNCA** incluir cláusulas que puedan perjudicar a OGA
3. **ADAPTAR** específicamente al modelo de negocio solicitado
4. **INCLUIR** todos los anexos relevantes
5. **VERIFICAR** cumplimiento normativo completo
6. **MANTENER** coherencia con términos y condiciones complementarios

---

**IMPORTANTE**: Este contrato debe ser revisado por el departamento legal de OGA antes de su uso. Esta plantilla proporciona una base sólida pero puede requerir adaptaciones específicas según el caso particular.