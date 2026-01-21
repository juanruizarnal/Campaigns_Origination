# Guía de Deployment - Motor de Originación Alter-5 v2.0

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Local](#configuración-local)
3. [Pruebas Pre-Deploy](#pruebas-pre-deploy)
4. [Deploy en Streamlit Cloud](#deploy-en-streamlit-cloud)
5. [Deploy en Railway (Recomendado)](#deploy-en-railway-recomendado)
6. [Deploy en Render](#deploy-en-render)
7. [Deploy en Fly.io](#deploy-en-flyio)
8. [Verificación Post-Deploy](#verificación-post-deploy)
9. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### APIs Necesarias (OBLIGATORIAS)

1. **Anthropic Claude API**
   - Crear cuenta en https://console.anthropic.com/
   - Generar API key
   - Plan recomendado: Build ($5/mes) o superior

2. **Google Gemini API**
   - Crear proyecto en https://console.cloud.google.com/
   - Habilitar Generative Language API
   - Generar API key en https://aistudio.google.com/app/apikey
   - Tier gratuito: 60 RPM, 1500 RPD

3. **Airtable**
   - Crear cuenta en https://airtable.com/
   - Crear base de datos con el schema proporcionado
   - Generar Personal Access Token con permisos de read/write

### APIs Opcionales

- **Slack**: Para notificaciones y alertas
- **Mailchimp**: Para envío de emails de campaña
- **Proxycurl**: Para datos de LinkedIn
- **MongoDB Atlas**: Para cache (free tier disponible)

---

## Configuración Local

### 1. Clonar y configurar entorno

```bash
# Clonar repositorio
git clone <repo-url>
cd Origination_Campaigns_V2

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: .\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Playwright para web scraping
playwright install chromium
```

### 2. Configurar variables de entorno

```bash
# Copiar ejemplo
cp .env.production.example .env

# Editar con tus credenciales
nano .env  # o tu editor preferido
```

Variables mínimas requeridas:
```env
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
AIRTABLE_PAT=pat...
AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9
```

### 3. Ejecutar localmente

```bash
# Modo desarrollo - Solo Streamlit
streamlit run frontend/app.py

# Modo completo con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

---

## Pruebas Pre-Deploy

### Ejecutar verificación automática

```bash
# Verificar todo está listo
python scripts/verify_deploy.py

# Con archivo .env específico
python scripts/verify_deploy.py --env .env.production

# Sin tests de conectividad (offline)
python scripts/verify_deploy.py --skip-api-tests
```

### Pruebas manuales recomendadas

```bash
# 1. Probar conexión a Airtable
python -c "
from core.airtable_client import get_airtable_client
client = get_airtable_client()
print('Airtable OK:', client.get_table('companies'))
"

# 2. Probar Claude API
python -c "
from integrations.claude import get_claude_client
client = get_claude_client()
response = client.generate('Say hello in Spanish')
print('Claude OK:', response[:50])
"

# 3. Probar Gemini API
python -c "
from integrations.gemini import get_gemini_client
client = get_gemini_client()
response = client.generate('What is 2+2?')
print('Gemini OK:', response[:50])
"

# 4. Probar flujo completo (dry-run)
python -c "
from agents.evaluador_fei import EvaluadorFEI
import asyncio
agent = EvaluadorFEI()
# Requiere un company_id válido de tu Airtable
# result = asyncio.run(agent.evaluate('recXXX', dry_run=True))
print('EvaluadorFEI OK')
"
```

---

## Deploy en Streamlit Cloud

Streamlit Cloud es la opción más rápida para publicar solo el frontend.

### 1. Preparar el repositorio

- La rama principal debe ser `main`
- El archivo principal es `frontend/app.py`
- La configuración de tema vive en `.streamlit/config.toml`

### 2. Crear la app en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Conecta tu cuenta de GitHub si no lo has hecho
3. Selecciona el repo `juanruizarnal/OriginationEngineV1`
4. En **Branch** selecciona `main`
5. En **Main file path** escribe `frontend/app.py`
6. Pulsa **Deploy**

### 3. Configurar secrets (obligatorio)

En **App settings → Secrets**, pega este bloque y reemplaza valores:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_API_KEY = "AIza..."
AIRTABLE_PAT = "pat..."
AIRTABLE_BASE_ID = "appEgNSP0tOLJ9YJ9"
```

### 4. Validación rápida

1. Abre la URL de la app
2. Verifica que cargue el dashboard sin errores
3. Prueba una consulta simple en "Empresas"

---

## Deploy en Railway (Recomendado)

Railway ofrece la mejor experiencia para este tipo de aplicación con free tier generoso.

### 1. Preparar cuenta

1. Crear cuenta en https://railway.app/
2. Conectar con GitHub
3. Verificar cuenta para obtener $5/mes de créditos

### 2. Deploy con Railway CLI

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Crear proyecto
railway init

# Añadir Redis (requerido para Celery)
railway add --database redis

# Deploy
railway up

# Ver URL
railway open
```

### 3. Configurar variables de entorno

En el dashboard de Railway o por CLI:

```bash
# Configurar variables
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
railway variables set GOOGLE_API_KEY=AIzaxxx
railway variables set AIRTABLE_PAT=patxxx
railway variables set AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9
railway variables set ALTER5_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
railway variables set CORS_ORIGINS=https://your-app.railway.app
railway variables set LOG_LEVEL=INFO

# Redis URL se configura automáticamente
```

### 4. Arquitectura en Railway

Para el sistema completo con automatización 24/7:

```
Proyecto Railway:
├── Service: alter5-app (Streamlit) - $0-5/mes
│   ├── Docker: Dockerfile (target: production)
│   └── Port: 8501
├── Service: alter5-api (FastAPI) - Solo si necesitas webhooks
│   ├── Docker: Dockerfile (target: api)
│   └── Port: 8000
├── Service: redis (Database) - Incluido
└── Service: alter5-worker (Celery) - Solo para automatización
    └── Docker: Dockerfile (target: worker)
```

---

## Deploy en Render

Render ofrece free tier con spin-down después de 15min de inactividad.

### 1. Preparar render.yaml

Crear archivo `render.yaml` en la raíz:

```yaml
services:
  - type: web
    name: alter5-origination
    runtime: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: AIRTABLE_PAT
        sync: false
      - key: AIRTABLE_BASE_ID
        sync: false
      - key: REDIS_URL
        fromService:
          type: redis
          name: alter5-redis
          property: connectionString
    healthCheckPath: /health
    plan: free

  - type: redis
    name: alter5-redis
    plan: free
    maxmemoryPolicy: allkeys-lru
```

### 2. Deploy

1. Ir a https://dashboard.render.com/
2. New > Blueprint
3. Conectar repo GitHub
4. Render detectará `render.yaml`
5. Configurar variables de entorno
6. Deploy

---

## Deploy en Fly.io

Fly.io ofrece 3 VMs gratuitas y es muy rápido.

### 1. Preparar fly.toml

```toml
app = "alter5-origination"
primary_region = "mad"  # Madrid

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8501
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[services]]
  protocol = "tcp"
  internal_port = 8501

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [[services.http_checks]]
    interval = "30s"
    timeout = "5s"
    path = "/_stcore/health"
```

### 2. Deploy

```bash
# Instalar flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Crear app
fly launch

# Configurar secrets
fly secrets set ANTHROPIC_API_KEY=sk-ant-xxx
fly secrets set GOOGLE_API_KEY=AIzaxxx
fly secrets set AIRTABLE_PAT=patxxx
fly secrets set AIRTABLE_BASE_ID=appEgNSP0tOLJ9YJ9

# Deploy
fly deploy

# Ver logs
fly logs
```

---

## Verificación Post-Deploy

### 1. Verificar health endpoint

```bash
# Reemplazar con tu URL
curl https://your-app.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "components": {
    "api": "up",
    "airtable": "configured",
    "gemini": "configured",
    "claude": "configured"
  }
}
```

### 2. Verificar aplicación Streamlit

1. Abrir URL en navegador
2. Verificar que carga la página principal
3. Probar navegación a diferentes páginas
4. Ejecutar una evaluación FEI de prueba

### 3. Verificar API (si está habilitada)

```bash
# Sin autenticación (health)
curl https://your-api.railway.app/health

# Con autenticación
curl -H "X-API-Key: tu-api-key" \
  https://your-api.railway.app/status
```

### 4. Probar flujo completo

1. **Página Originación**: Buscar empresas por sector
2. **Evaluación FEI**: Evaluar una empresa
3. **Dashboard**: Verificar métricas

---

## Troubleshooting

### Error: "REDIS_URL not found"

```bash
# En Railway
railway variables set REDIS_URL=$(railway variables get REDIS_URL --service redis)

# O usar Redis externo (Upstash)
railway variables set REDIS_URL=redis://default:xxx@xxx.upstash.io:6379
```

### Error: "Airtable authentication failed"

1. Verificar que el PAT tiene permisos correctos
2. Verificar que el BASE_ID es correcto
3. Regenerar PAT si es necesario

### Error: "Claude/Gemini rate limit"

El sistema tiene rate limiting integrado, pero si persiste:
1. Verificar tier de API
2. Reducir `concurrent_requests` en `core/rate_limiter.py`

### Logs lentos o timeout

```bash
# Railway
railway logs --tail 100

# Render
render logs --tail

# Fly.io
fly logs
```

### Playwright no funciona

El Dockerfile incluye todas las dependencias, pero si falla:
```dockerfile
# Añadir en Dockerfile si es necesario
RUN playwright install-deps chromium
```

---

## Costes Estimados

### Opción Mínima (Solo Streamlit) - ~$0-5/mes
- Railway free tier o Render free tier
- Airtable free tier (1000 records)
- APIs de LLM: ~$5-20/mes según uso

### Opción Completa (Con automatización) - ~$20-50/mes
- Railway: ~$10/mes (app + worker + redis)
- MongoDB Atlas: Free tier
- APIs de LLM: ~$10-30/mes
- Slack: Free tier
- Total: ~$20-40/mes

### Para Escalar
- Upgrader a tiers pagados según necesidad
- Considerar dedicated Redis
- Monitorizar costes de API con los dashboards

---

## Soporte

- Issues: https://github.com/your-repo/issues
- Documentación: Ver `/docs` en el repositorio
- Logs estructurados: Usar `structlog` para debugging

---

*Motor de Originación Alter-5 v2.0 - 2026*
