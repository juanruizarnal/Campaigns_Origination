# 🎨 Plantilla de Especificaciones de Frontend Completas

## Guía Exhaustiva para Product Manager Expert Agent

---

## 🎯 INSTRUCCIONES DE USO

### Para el Agente de IA Product Manager

Esta plantilla está diseñada para generar especificaciones completas de frontend que integren el análisis funcional del Analista Funcional Expert Agent, el PRD y las especificaciones técnicas del CTO. El objetivo es crear un documento que permita a un Frontend Developer Expert Agent implementar la solución garantizando las mejores prácticas de desarrollo, un estilo profesional, moderno y tecnológico donde la simplicidad y el acompañamiento al usuario sean prioritarios.

**PRINCIPIOS FUNDAMENTALES**:

- **Onboarding Invisible**: La interfaz debe ser tan intuitiva que no requiera explicación
- **Simplicidad Radical**: Cada elemento debe tener un propósito claro y necesario
- **Acompañamiento Continuo**: Guiar al usuario en cada paso sin ser intrusivo
- **Profesionalidad Moderna**: Estética contemporánea que inspire confianza
- **Accesibilidad Universal**: Diseño inclusivo para todos los usuarios

**IMPORTANTE**:

- Completa TODAS las secciones marcadas como [OBLIGATORIO]
- Las secciones marcadas como [OPCIONAL] úsalas según la relevancia del proyecto
- Reemplaza todos los placeholders `[VARIABLE]` con información específica
- Mantén coherencia con el análisis funcional y PRD de referencia
- Incluye especificaciones técnicas precisas y medibles
- Prioriza la experiencia de usuario sobre la complejidad técnica

---

## 📋 INFORMACIÓN DE CONTEXTO [OBLIGATORIO]

**Fecha**: [DD/MM/AAAA]
**Proyecto/Sistema**: [NOMBRE_PROYECTO]
**Versión de Especificaciones**: [X.Y.Z]
**Product Manager**: [NOMBRE] - [EXPERIENCIA]
**Documentos de Referencia**:
- Análisis Funcional: `[RUTA_ANALISIS_FUNCIONAL]`
- PRD: `[RUTA_PRD]`
- Informe CTO: `[RUTA_INFORME_CTO]`
- Esquema OpenAPI: `[RUTA_OPENAPI_SCHEMA]`

**Objetivo de las Especificaciones**: [DESCRIPCIÓN_OBJETIVO_ESPECÍFICO]
**Alcance del Frontend**: [DEFINIR_LÍMITES_FRONTEND]
**Audiencia Objetivo**: [PERFIL_USUARIOS_FINALES]
**Plataformas Target**: [WEB/MÓVIL/DESKTOP/PWA]

---

## 🎯 RESUMEN EJECUTIVO [OBLIGATORIO]

### Visión del Producto

[Descripción de la visión del producto desde la perspectiva del usuario final. Incluir el valor principal que aporta y cómo transforma la experiencia del usuario. Mínimo 150 palabras, máximo 250.]

### Objetivos de UX/UI

[Lista de 3-5 objetivos específicos de experiencia de usuario que debe cumplir el frontend:]

1. **[OBJETIVO_UX_1]**: [Descripción y métrica de éxito]
2. **[OBJETIVO_UX_2]**: [Descripción y métrica de éxito]
3. **[OBJETIVO_UX_3]**: [Descripción y métrica de éxito]

### Principios de Diseño

[Principios específicos que guiarán todas las decisiones de diseño e implementación:]

- **[PRINCIPIO_1]**: [Descripción y aplicación práctica]
- **[PRINCIPIO_2]**: [Descripción y aplicación práctica]
- **[PRINCIPIO_3]**: [Descripción y aplicación práctica]

---

## 👥 ANÁLISIS DE USUARIOS [OBLIGATORIO]

### Personas Principales

#### Persona 1: [NOMBRE_PERSONA]

- **Perfil**: [Edad, profesión, nivel técnico]
- **Objetivos**: [Qué busca lograr con el producto]
- **Frustraciones**: [Pain points específicos]
- **Comportamiento Digital**: [Cómo interactúa con tecnología]
- **Contexto de Uso**: [Cuándo, dónde y cómo usa el producto]
- **Dispositivos Preferidos**: [Desktop, móvil, tablet]
- **Nivel de Experiencia**: [Novato/Intermedio/Experto]

#### Persona 2: [NOMBRE_PERSONA]

[Repetir estructura anterior]

### Journey Map de Usuario

#### Fase 1: Descubrimiento
- **Touchpoints**: [Puntos de contacto con el producto]
- **Emociones**: [Estado emocional del usuario]
- **Acciones**: [Qué hace el usuario]
- **Oportunidades**: [Cómo mejorar la experiencia]

#### Fase 2: Onboarding
[Repetir estructura anterior]

#### Fase 3: Uso Regular
[Repetir estructura anterior]

#### Fase 4: Maestría
[Repetir estructura anterior]

---

## 🔄 FLUJOS DE USUARIO DETALLADOS [OBLIGATORIO]

### Flujo Principal: [NOMBRE_FLUJO_PRINCIPAL]

#### Descripción del Flujo
[Descripción narrativa del flujo completo, explicando el contexto, objetivo y valor para el usuario]

#### Pasos del Flujo

##### Paso 1: [NOMBRE_PASO]

**Contexto**: [Situación del usuario al llegar a este paso]
**Objetivo**: [Qué busca lograr el usuario]
**Acción Principal**: [Acción más importante que debe realizar]

**Elementos de Interfaz**:
- **Título/Encabezado**: "[TEXTO_EXACTO]"
- **Descripción/Subtítulo**: "[TEXTO_EXACTO]"
- **Campos de Entrada**:
  - `[NOMBRE_CAMPO]`: [Tipo, validaciones, placeholder, ayuda]
  - `[NOMBRE_CAMPO_2]`: [Tipo, validaciones, placeholder, ayuda]
- **Botones de Acción**:
  - **Primario**: "[TEXTO_BOTÓN]" - [Acción que ejecuta]
  - **Secundario**: "[TEXTO_BOTÓN]" - [Acción que ejecuta]
- **Enlaces/Navegación**: [Enlaces adicionales disponibles]

**Estados de la Interfaz**:
- **Estado Inicial**: [Cómo se ve cuando carga]
- **Estado de Carga**: [Indicadores de progreso]
- **Estado de Error**: [Mensajes y recuperación]
- **Estado de Éxito**: [Confirmación y siguiente paso]

**Validaciones y Feedback**:
- **Validación en Tiempo Real**: [Qué se valida mientras escribe]
- **Mensajes de Error**: [Textos específicos para cada error]
- **Mensajes de Ayuda**: [Tooltips, hints, ejemplos]
- **Confirmaciones**: [Qué se confirma al usuario]

**Tiempo Estimado**: [X segundos/minutos]
**Tasa de Éxito Objetivo**: [X%]

##### Paso 2: [NOMBRE_PASO]
[Repetir estructura anterior]

#### Flujos Alternativos

##### Flujo de Error: [TIPO_ERROR]
- **Trigger**: [Qué causa este flujo]
- **Comportamiento**: [Cómo se maneja]
- **Recuperación**: [Cómo vuelve al flujo principal]

##### Flujo de Cancelación
- **Puntos de Salida**: [Dónde puede cancelar]
- **Confirmación**: [Si requiere confirmación]
- **Estado Final**: [Dónde termina el usuario]

### Flujo Secundario: [NOMBRE_FLUJO_SECUNDARIO]
[Repetir estructura completa del flujo principal]

---

## 🖼️ WIREFRAMES Y MOCKUPS [OBLIGATORIO]

### Arquitectura de Información

#### Estructura de Navegación
```
[NOMBRE_APP]
├── [SECCIÓN_PRINCIPAL_1]
│   ├── [SUBSECCIÓN_1.1]
│   ├── [SUBSECCIÓN_1.2]
│   └── [SUBSECCIÓN_1.3]
├── [SECCIÓN_PRINCIPAL_2]
│   ├── [SUBSECCIÓN_2.1]
│   └── [SUBSECCIÓN_2.2]
└── [SECCIÓN_PRINCIPAL_3]
    └── [SUBSECCIÓN_3.1]
```

#### Jerarquía de Contenido
- **Nivel 1 - Navegación Principal**: [Elementos más importantes]
- **Nivel 2 - Navegación Secundaria**: [Subsecciones]
- **Nivel 3 - Contenido**: [Información específica]
- **Nivel 4 - Acciones**: [Botones y controles]

### Wireframes por Pantalla

#### Pantalla 1: [NOMBRE_PANTALLA]

**Propósito**: [Objetivo principal de esta pantalla]
**Contexto de Llegada**: [Cómo llega el usuario aquí]

```
┌─────────────────────────────────────────────────────────────┐
│ [HEADER/NAVEGACIÓN]                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [TÍTULO PRINCIPAL]                                          │
│ [Subtítulo o descripción breve]                            │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [SECCIÓN PRINCIPAL]                                     │ │
│ │                                                         │ │
│ │ [Elemento 1]: [Descripción/Función]                    │ │
│ │ [Elemento 2]: [Descripción/Función]                    │ │
│ │ [Elemento 3]: [Descripción/Función]                    │ │
│ │                                                         │ │
│ │ [BOTÓN PRIMARIO]  [BOTÓN SECUNDARIO]                   │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [SECCIÓN SECUNDARIA]                                    │ │
│ │ [Contenido adicional o información de soporte]         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [FOOTER/INFORMACIÓN ADICIONAL]                             │
└─────────────────────────────────────────────────────────────┘
```

**Elementos Específicos**:
- **[ELEMENTO_1]**: [Función, comportamiento, estilo]
- **[ELEMENTO_2]**: [Función, comportamiento, estilo]
- **[ELEMENTO_3]**: [Función, comportamiento, estilo]

**Interacciones**:
- **Click en [ELEMENTO]**: [Qué sucede]
- **Hover en [ELEMENTO]**: [Efecto visual]
- **Scroll**: [Comportamiento del scroll]

**Responsive Behavior**:
- **Desktop (>1200px)**: [Cómo se adapta]
- **Tablet (768-1199px)**: [Cómo se adapta]
- **Mobile (<768px)**: [Cómo se adapta]

#### Pantalla 2: [NOMBRE_PANTALLA]
[Repetir estructura anterior]

### Estados de Componentes

#### Componente: [NOMBRE_COMPONENTE]

**Estados Visuales**:
- **Default**: [Apariencia normal]
- **Hover**: [Al pasar el mouse]
- **Active/Pressed**: [Al hacer click]
- **Focused**: [Al recibir foco]
- **Disabled**: [Cuando está deshabilitado]
- **Loading**: [Durante carga]
- **Error**: [En caso de error]
- **Success**: [En caso de éxito]

**Variantes**:
- **Primario**: [Estilo principal]
- **Secundario**: [Estilo alternativo]
- **Terciario**: [Estilo mínimo]

---

## 🎨 SISTEMA DE DISEÑO [OBLIGATORIO]

### Paleta de Colores

#### Colores Primarios
- **Primary**: `#[HEX_CODE]` - [Uso y significado]
- **Primary Light**: `#[HEX_CODE]` - [Uso y significado]
- **Primary Dark**: `#[HEX_CODE]` - [Uso y significado]

#### Colores Secundarios
- **Secondary**: `#[HEX_CODE]` - [Uso y significado]
- **Accent**: `#[HEX_CODE]` - [Uso y significado]

#### Colores de Sistema
- **Success**: `#[HEX_CODE]` - Estados de éxito
- **Warning**: `#[HEX_CODE]` - Advertencias
- **Error**: `#[HEX_CODE]` - Errores
- **Info**: `#[HEX_CODE]` - Información

#### Colores Neutros
- **Gray 50**: `#[HEX_CODE]` - Fondos muy claros
- **Gray 100**: `#[HEX_CODE]` - Fondos claros
- **Gray 200**: `#[HEX_CODE]` - Bordes suaves
- **Gray 300**: `#[HEX_CODE]` - Bordes normales
- **Gray 400**: `#[HEX_CODE]` - Texto deshabilitado
- **Gray 500**: `#[HEX_CODE]` - Texto secundario
- **Gray 600**: `#[HEX_CODE]` - Texto normal
- **Gray 700**: `#[HEX_CODE]` - Texto principal
- **Gray 800**: `#[HEX_CODE]` - Texto enfatizado
- **Gray 900**: `#[HEX_CODE]` - Texto muy enfatizado

### Tipografía

#### Fuentes
- **Primaria**: [Nombre de fuente] - Para títulos y elementos principales
- **Secundaria**: [Nombre de fuente] - Para texto de cuerpo
- **Monospace**: [Nombre de fuente] - Para código y datos técnicos

#### Escala Tipográfica
- **H1**: [Tamaño]px, [Peso], [Altura de línea] - Títulos principales
- **H2**: [Tamaño]px, [Peso], [Altura de línea] - Títulos de sección
- **H3**: [Tamaño]px, [Peso], [Altura de línea] - Subtítulos
- **H4**: [Tamaño]px, [Peso], [Altura de línea] - Títulos menores
- **Body Large**: [Tamaño]px, [Peso], [Altura de línea] - Texto principal grande
- **Body**: [Tamaño]px, [Peso], [Altura de línea] - Texto normal
- **Body Small**: [Tamaño]px, [Peso], [Altura de línea] - Texto pequeño
- **Caption**: [Tamaño]px, [Peso], [Altura de línea] - Etiquetas y metadatos

### Espaciado y Layout

#### Sistema de Espaciado (8px base)
- **xs**: 4px - Espaciado mínimo
- **sm**: 8px - Espaciado pequeño
- **md**: 16px - Espaciado medio
- **lg**: 24px - Espaciado grande
- **xl**: 32px - Espaciado extra grande
- **2xl**: 48px - Espaciado muy grande
- **3xl**: 64px - Espaciado máximo

#### Grid System
- **Contenedor Máximo**: [X]px
- **Columnas**: 12 columnas
- **Gutter**: [X]px
- **Breakpoints**:
  - **xs**: 0px - 575px
  - **sm**: 576px - 767px
  - **md**: 768px - 991px
  - **lg**: 992px - 1199px
  - **xl**: 1200px+

### Componentes Base

#### Botones

**Especificaciones Técnicas**:
- **Altura Mínima**: 44px (accesibilidad táctil)
- **Padding Horizontal**: 16px (sm), 24px (md), 32px (lg)
- **Border Radius**: [X]px
- **Transiciones**: 200ms ease-in-out

**Variantes**:
```css
/* Botón Primario */
.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  font-weight: 600;
}

/* Botón Secundario */
.btn-secondary {
  background: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  font-weight: 600;
}

/* Botón Terciario */
.btn-tertiary {
  background: transparent;
  color: var(--color-gray-700);
  border: none;
  text-decoration: underline;
}
```

#### Campos de Entrada

**Especificaciones Técnicas**:
- **Altura**: 48px
- **Padding**: 12px 16px
- **Border**: 1px solid var(--color-gray-300)
- **Border Radius**: [X]px
- **Font Size**: 16px (evita zoom en móvil)

**Estados**:
```css
/* Estado Normal */
.input {
  border: 1px solid var(--color-gray-300);
  background: var(--color-white);
}

/* Estado Focus */
.input:focus {
  border: 2px solid var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 3px rgba(primary, 0.1);
}

/* Estado Error */
.input.error {
  border: 2px solid var(--color-error);
}

/* Estado Disabled */
.input:disabled {
  background: var(--color-gray-100);
  color: var(--color-gray-400);
}
```

#### Cards

**Especificaciones**:
- **Padding**: 24px
- **Border Radius**: [X]px
- **Shadow**: 0 2px 8px rgba(0,0,0,0.1)
- **Border**: 1px solid var(--color-gray-200)

---

## 📱 ESPECIFICACIONES RESPONSIVE [OBLIGATORIO]

### Breakpoints y Comportamiento

#### Mobile First Approach
Diseñar primero para móvil y expandir hacia desktop.

#### Breakpoints Específicos
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1439px
- **Large Desktop**: 1440px+

### Adaptaciones por Dispositivo

#### Mobile (320px - 767px)

**Navegación**:
- Menú hamburguesa colapsable
- Navegación inferior (bottom navigation) para acciones principales
- Máximo 5 elementos en navegación principal

**Layout**:
- Una sola columna
- Stack vertical de todos los elementos
- Padding lateral: 16px
- Espaciado vertical reducido

**Interacciones**:
- Botones mínimo 44px de altura
- Áreas táctiles separadas por al menos 8px
- Swipe gestures donde sea apropiado

**Tipografía**:
- Tamaños de fuente optimizados para legibilidad
- Contraste mínimo 4.5:1

#### Tablet (768px - 1023px)

**Layout**:
- 2 columnas donde sea apropiado
- Sidebar colapsable
- Padding lateral: 24px

**Navegación**:
- Combinación de navegación horizontal y vertical
- Posible uso de tabs

#### Desktop (1024px+)

**Layout**:
- Múltiples columnas
- Sidebar fija
- Padding lateral: 32px+
- Uso eficiente del espacio horizontal

**Interacciones**:
- Hover states
- Keyboard navigation
- Tooltips informativos

---

## ⚡ ESPECIFICACIONES DE PERFORMANCE [OBLIGATORIO]

### Métricas Objetivo

#### Core Web Vitals
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

#### Métricas Adicionales
- **FCP (First Contentful Paint)**: < 1.8s
- **TTI (Time to Interactive)**: < 3.5s
- **Speed Index**: < 3.0s

### Optimizaciones Requeridas

#### Imágenes
- Formato WebP con fallback
- Lazy loading para imágenes below-the-fold
- Responsive images con srcset
- Compresión optimizada (calidad 80-85%)

#### Código
- Code splitting por rutas
- Tree shaking para eliminar código no usado
- Minificación de CSS y JavaScript
- Compresión gzip/brotli

#### Carga
- Preload de recursos críticos
- Prefetch de recursos probables
- Service Worker para caching
- CDN para assets estáticos

---

## 🔒 ESPECIFICACIONES DE ACCESIBILIDAD [OBLIGATORIO]

### Estándares de Cumplimiento
- **WCAG 2.1 AA**: Cumplimiento completo
- **Section 508**: Para proyectos gubernamentales
- **EN 301 549**: Para proyectos europeos

### Requisitos Específicos

#### Navegación por Teclado
- Todos los elementos interactivos accesibles por Tab
- Orden lógico de tabulación
- Indicadores visuales de foco claros
- Atajos de teclado para acciones principales

#### Lectores de Pantalla
- Etiquetas ARIA apropiadas
- Texto alternativo para imágenes
- Headings jerárquicos (H1, H2, H3...)
- Landmarks semánticos

#### Contraste y Visibilidad
- Contraste mínimo 4.5:1 para texto normal
- Contraste mínimo 3:1 para texto grande
- No depender solo del color para transmitir información
- Soporte para modo alto contraste

#### Responsive y Zoom
- Funcional hasta 200% de zoom
- Texto redimensionable hasta 200%
- No scroll horizontal en móvil

---

## 🧪 ESPECIFICACIONES DE TESTING [OBLIGATORIO]

### Testing de Usabilidad

#### Métricas de Usabilidad
- **Task Success Rate**: > 90%
- **Time on Task**: [X] segundos por tarea principal
- **Error Rate**: < 5%
- **Satisfaction Score**: > 4.0/5.0

#### Escenarios de Testing
1. **Primer Uso**: Usuario nuevo completa onboarding
2. **Uso Regular**: Usuario experimentado realiza tareas comunes
3. **Recuperación de Errores**: Usuario se recupera de errores comunes
4. **Accesibilidad**: Usuario con discapacidades navega el sistema

### Testing Técnico

#### Testing Cross-Browser
- **Chrome**: Últimas 2 versiones
- **Firefox**: Últimas 2 versiones
- **Safari**: Últimas 2 versiones
- **Edge**: Últimas 2 versiones

#### Testing de Dispositivos
- **iOS**: iPhone 12+, iPad Air+
- **Android**: Samsung Galaxy S20+, Google Pixel 5+
- **Desktop**: 1920x1080, 1366x768, 2560x1440

#### Testing de Performance
- **Lighthouse**: Score > 90 en todas las métricas
- **WebPageTest**: Grade A en todas las categorías
- **GTmetrix**: Grade A en Performance y Structure

---

## 🔄 ESTADOS Y TRANSICIONES [OBLIGATORIO]

### Estados Globales de la Aplicación

#### Estado de Carga Inicial
- **Skeleton screens** para contenido principal
- **Progress indicators** para procesos largos
- **Spinners** para acciones rápidas
- **Shimmer effects** para listas y cards

#### Estado de Error
- **Error boundaries** para errores de JavaScript
- **Fallback UI** para componentes que fallan
- **Retry mechanisms** para errores de red
- **Offline indicators** para pérdida de conexión

#### Estado Vacío
- **Empty states** informativos y accionables
- **Onboarding prompts** para primeros usuarios
- **Call-to-action** claros para siguiente paso

### Transiciones y Animaciones

#### Principios de Animación
- **Duración**: 200-300ms para micro-interacciones
- **Easing**: ease-out para entradas, ease-in para salidas
- **Propósito**: Todas las animaciones deben tener propósito funcional

#### Transiciones Específicas
```css
/* Transición de botones */
.btn {
  transition: all 200ms ease-out;
}

/* Transición de modals */
.modal {
  transition: opacity 300ms ease-out, transform 300ms ease-out;
}

/* Transición de navegación */
.page-transition {
  transition: opacity 250ms ease-in-out;
}
```

---

## 📊 MÉTRICAS Y ANALYTICS [OBLIGATORIO]

### KPIs de Frontend

#### Métricas de Engagement
- **Session Duration**: Tiempo promedio de sesión
- **Page Views per Session**: Páginas vistas por sesión
- **Bounce Rate**: Tasa de rebote por página
- **Return Visitor Rate**: Porcentaje de usuarios recurrentes

#### Métricas de Conversión
- **Conversion Rate**: Tasa de conversión por funnel
- **Drop-off Rate**: Tasa de abandono por paso
- **Feature Adoption**: Adopción de nuevas funcionalidades
- **User Onboarding Completion**: Completación del onboarding

#### Métricas de Performance
- **Page Load Time**: Tiempo de carga por página
- **Error Rate**: Tasa de errores JavaScript
- **API Response Time**: Tiempo de respuesta de APIs
- **Crash Rate**: Tasa de crashes de la aplicación

### Implementación de Analytics

#### Eventos a Trackear
```javascript
// Eventos de navegación
trackEvent('page_view', {
  page: '/dashboard',
  user_type: 'premium',
  session_id: 'xxx'
});

// Eventos de interacción
trackEvent('button_click', {
  button_id: 'cta_primary',
  page: '/landing',
  position: 'hero'
});

// Eventos de conversión
trackEvent('conversion', {
  funnel_step: 'signup_complete',
  user_id: 'xxx',
  conversion_value: 99.99
});
```

#### Herramientas Recomendadas
- **Google Analytics 4**: Analytics general
- **Hotjar/FullStory**: Heatmaps y session recordings
- **Mixpanel/Amplitude**: Event tracking avanzado
- **Sentry**: Error tracking y performance monitoring

---

## 🛠️ ESPECIFICACIONES TÉCNICAS [OBLIGATORIO]

### Stack Tecnológico Recomendado

#### Framework Frontend
- **React 18+**: Con Hooks y Concurrent Features
- **Next.js 13+**: Para SSR/SSG y optimizaciones
- **TypeScript**: Para type safety

#### Styling
- **Tailwind CSS**: Para utility-first styling
- **CSS Modules**: Para componentes específicos
- **Styled Components**: Para componentes dinámicos

#### Estado y Datos
- **Zustand/Redux Toolkit**: Para estado global
- **React Query/SWR**: Para estado del servidor
- **React Hook Form**: Para manejo de formularios

#### Testing
- **Jest**: Unit testing
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **Storybook**: Component documentation

### Arquitectura de Componentes

#### Estructura de Directorios
```
src/
├── components/
│   ├── ui/           # Componentes base del design system
│   ├── forms/        # Componentes de formularios
│   ├── layout/       # Componentes de layout
│   └── features/     # Componentes específicos de features
├── hooks/            # Custom hooks
├── utils/            # Utilidades y helpers
├── types/            # Definiciones de TypeScript
├── styles/           # Estilos globales
└── pages/            # Páginas de la aplicación
```

#### Convenciones de Naming
- **Componentes**: PascalCase (e.g., `UserProfile.tsx`)
- **Hooks**: camelCase con prefijo "use" (e.g., `useUserData.ts`)
- **Utilidades**: camelCase (e.g., `formatDate.ts`)
- **Constantes**: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS.ts`)

### Integración con Backend

#### Especificaciones de API
- **Base URL**: `[API_BASE_URL]`
- **Autenticación**: JWT Bearer tokens
- **Rate Limiting**: [X] requests per minute
- **Error Handling**: Códigos HTTP estándar + error objects

#### Manejo de Estados de Carga
```typescript
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Implementación con React Query
const { data, isLoading, error } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
  staleTime: 5 * 60 * 1000, // 5 minutos
});
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN [OBLIGATORIO]

### Fases de Desarrollo

#### Fase 1: Fundación (Semanas 1-2)
- [ ] **Setup del proyecto y tooling**
  - Configuración de Next.js + TypeScript
  - Setup de Tailwind CSS y design system
  - Configuración de testing suite
  - Setup de CI/CD pipeline

- [ ] **Componentes base del design system**
  - Botones, inputs, cards
  - Layout components (Header, Footer, Sidebar)
  - Sistema de colores y tipografía
  - Documentación en Storybook

#### Fase 2: Páginas Core (Semanas 3-4)
- [ ] **Implementación de páginas principales**
  - Landing page / Dashboard
  - Páginas de autenticación
  - Páginas de perfil de usuario
  - Navegación principal

- [ ] **Integración con APIs**
  - Setup de React Query
  - Implementación de auth flow
  - Manejo de estados de error
  - Loading states y skeleton screens

#### Fase 3: Features Avanzadas (Semanas 5-6)
- [ ] **Funcionalidades específicas del producto**
  - [Feature específica 1]
  - [Feature específica 2]
  - [Feature específica 3]

- [ ] **Optimizaciones de UX**
  - Animaciones y transiciones
  - Responsive design refinement
  - Accesibilidad improvements
  - Performance optimizations

#### Fase 4: Testing y Refinamiento (Semanas 7-8)
- [ ] **Testing comprehensivo**
  - Unit tests para todos los componentes
  - Integration tests para flujos críticos
  - E2E tests para user journeys
  - Accessibility testing

- [ ] **Optimización final**
  - Performance audit y optimizaciones
  - SEO optimizations
  - Analytics implementation
  - Documentation completion

### Criterios de Aceptación por Fase

#### Fase 1 - Fundación
- [ ] Design system documentado en Storybook
- [ ] Todos los componentes base implementados
- [ ] Tests unitarios > 80% coverage
- [ ] CI/CD pipeline funcional

#### Fase 2 - Páginas Core
- [ ] Todas las páginas principales responsive
- [ ] Autenticación completamente funcional
- [ ] Error handling implementado
- [ ] Performance score > 85 en Lighthouse

#### Fase 3 - Features Avanzadas
- [ ] Todas las features del PRD implementadas
- [ ] Animaciones y transiciones pulidas
- [ ] Accesibilidad WCAG 2.1 AA compliant
- [ ] Cross-browser testing completado

#### Fase 4 - Testing y Refinamiento
- [ ] Test coverage > 90%
- [ ] Performance score > 90 en Lighthouse
- [ ] Zero accessibility violations
- [ ] Analytics tracking implementado

---

## ⚠️ RIESGOS Y MITIGACIONES [OBLIGATORIO]

### Riesgos de UX/UI

#### Complejidad de Interfaz
- **Riesgo**: Interfaz demasiado compleja para usuarios novatos
- **Probabilidad**: Media
- **Impacto**: Alto
- **Mitigación**: User testing temprano y iterativo, progressive disclosure
- **Indicador**: Task completion rate < 80%

#### Inconsistencia Visual
- **Riesgo**: Falta de coherencia en el design system
- **Probabilidad**: Media
- **Impacto**: Medio
- **Mitigación**: Design system robusto, code reviews, Storybook
- **Indicador**: Variaciones no documentadas en componentes

### Riesgos Técnicos

#### Performance en Dispositivos Lentos
- **Riesgo**: Aplicación lenta en dispositivos de gama baja
- **Probabilidad**: Alta
- **Impacto**: Alto
- **Mitigación**: Performance budget, testing en dispositivos reales
- **Indicador**: LCP > 3s en dispositivos de prueba

#### Compatibilidad Cross-Browser
- **Riesgo**: Funcionalidad rota en navegadores específicos
- **Probabilidad**: Media
- **Impacto**: Medio
- **Mitigación**: Testing automatizado cross-browser, polyfills
- **Indicador**: Error reports de navegadores específicos

### Riesgos de Negocio

#### Adopción de Usuario
- **Riesgo**: Baja adopción por UX confusa
- **Probabilidad**: Media
- **Impacto**: Crítico
- **Mitigación**: User research, A/B testing, onboarding optimizado
- **Indicador**: Bounce rate > 60%, low engagement

---

## 📋 CHECKLIST DE COMPLETITUD [OBLIGATORIO]

### Antes de Entregar las Especificaciones

#### Documentación
- [ ] Todos los placeholders [VARIABLE] han sido reemplazados
- [ ] Todas las secciones [OBLIGATORIO] están completas
- [ ] Los wireframes están detallados y son comprensibles
- [ ] El design system está completamente especificado
- [ ] Los flujos de usuario están validados con stakeholders

#### Especificaciones Técnicas
- [ ] Stack tecnológico definido y justificado
- [ ] Arquitectura de componentes clara
- [ ] Integración con APIs especificada
- [ ] Plan de testing comprehensivo
- [ ] Métricas de performance definidas

#### UX/UI
- [ ] Personas de usuario validadas
- [ ] Journey maps completos
- [ ] Wireframes responsive para todos los breakpoints
- [ ] Estados de error y carga especificados
- [ ] Accesibilidad WCAG 2.1 AA considerada

#### Implementación
- [ ] Fases de desarrollo realistas
- [ ] Criterios de aceptación específicos
- [ ] Riesgos identificados con mitigaciones
- [ ] Timeline validado con equipo técnico

### Calidad de las Especificaciones

#### Claridad y Detalle
- [ ] Las especificaciones son específicas del proyecto (no genéricas)
- [ ] Incluyen detalles únicos del dominio y usuarios
- [ ] Los requisitos son implementables y verificables
- [ ] El nivel de detalle es apropiado para developers
- [ ] Las decisiones de diseño están justificadas

#### Coherencia
- [ ] Coherente con análisis funcional de referencia
- [ ] Alineado con PRD y objetivos de negocio
- [ ] Consistente con informe técnico del CTO
- [ ] Design system coherente en toda la aplicación
- [ ] Terminología consistente en todo el documento

#### Viabilidad
- [ ] Timeline realista para el scope definido
- [ ] Stack tecnológico apropiado para requisitos
- [ ] Consideraciones de performance factibles
- [ ] Presupuesto de desarrollo realista
- [ ] Riesgos identificados son relevantes y manejables

---

## 📚 ANEXOS Y REFERENCIAS [OPCIONAL]

### Documentación de Soporte
- **Análisis de Competencia**: [Enlaces a análisis de productos similares]
- **User Research**: [Enlaces a estudios de usuarios]
- **Technical Constraints**: [Limitaciones técnicas del backend]
- **Brand Guidelines**: [Guías de marca corporativa]

### Herramientas y Recursos
- **Design Tools**: Figma, Sketch, Adobe XD
- **Prototyping**: Framer, Principle, ProtoPie
- **Testing Tools**: Maze, UserTesting, Hotjar
- **Development Tools**: Storybook, Chromatic, Percy

### Referencias Externas
- [Material Design Guidelines](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Performance Best Practices](https://web.dev/fast/)

---

## ✅ VALIDACIÓN Y APROBACIÓN

### Revisores Requeridos
- [ ] **UX Designer**: [Nombre] - [Fecha revisión]
- [ ] **Frontend Lead**: [Nombre] - [Fecha revisión]
- [ ] **Product Manager**: [Nombre] - [Fecha revisión]
- [ ] **CTO/Tech Lead**: [Nombre] - [Fecha revisión]

### Criterios de Aprobación
- [ ] Coherencia con análisis funcional y PRD
- [ ] Viabilidad técnica validada por equipo de desarrollo
- [ ] UX validada con user research o testing
- [ ] Design system completo y consistente
- [ ] Plan de implementación realista y detallado

### Próximos Pasos Post-Aprobación
1. **Creación de Backlog Técnico**: [Responsable y fecha]
2. **Setup de Proyecto**: [Responsable y fecha]
3. **Kick-off con Equipo de Desarrollo**: [Fecha planificada]
4. **Primera Demo/Review**: [Fecha planificada]

---

**Product Manager**: [NOMBRE_PM] | **Fecha**: [DD/MM/AAAA]
**Basado en**: Análisis Funcional + PRD + Informe CTO + OpenAPI Schema
**Validado por**: [MÉTODO_VALIDACIÓN]
**Versión**: [X.Y] | **Estado**: [Borrador/En Revisión/Aprobado]

---

*Estas especificaciones de frontend constituyen la guía completa para implementar una interfaz de usuario excepcional que priorice la simplicidad, el acompañamiento al usuario y la excelencia técnica, garantizando una experiencia de onboarding invisible y un diseño profesional y moderno.*