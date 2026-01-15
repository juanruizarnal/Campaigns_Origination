# 🔑 Instrucciones para Probar las APIs

Este documento contiene instrucciones detalladas para obtener las API keys y probar las APIs de Anthropic (Claude) y Google (Gemini).

---

## 📋 Resumen Rápido

| API | Obtener Key | Coste | Límite Gratuito |
|-----|-------------|-------|-----------------|
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/settings/keys) | ~$3/1M tokens input | $5 crédito inicial |
| **Gemini** | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Gratis* | 15 RPM, 1M TPM |

*Gemini 1.5 Flash tiene tier gratuito generoso

---

## 1️⃣ Obtener API Key de Anthropic (Claude)

### Paso 1: Crear cuenta
1. Ve a **https://console.anthropic.com/**
2. Haz clic en "Sign Up"
3. Completa el registro con tu email

### Paso 2: Añadir método de pago (opcional pero recomendado)
1. Ve a **Settings > Billing**
2. Añade tarjeta de crédito
3. Establece un límite mensual de gasto (ej: $20)

> ⚠️ Sin método de pago, tendrás un límite muy bajo de tokens

### Paso 3: Crear API Key
1. Ve a **Settings > API Keys**
2. Haz clic en **"Create Key"**
3. Ponle un nombre descriptivo (ej: "Alter5-Origination")
4. **COPIA LA KEY INMEDIATAMENTE** - solo se muestra una vez
5. Debería empezar con: `sk-ant-api03-...`

### Paso 4: Configurar variable de entorno
```bash
# En tu terminal (Mac/Linux):
export ANTHROPIC_API_KEY="sk-ant-api03-tu-key-aqui"

# O añádelo a tu .env:
echo 'ANTHROPIC_API_KEY=sk-ant-api03-tu-key-aqui' >> .env
```

---

## 2️⃣ Obtener API Key de Google (Gemini)

### Paso 1: Acceder a Google AI Studio
1. Ve a **https://aistudio.google.com/**
2. Inicia sesión con tu cuenta de Google
3. Acepta los términos de servicio

### Paso 2: Crear API Key
1. En el menú lateral, haz clic en **"Get API key"**
2. O ve directamente a **https://aistudio.google.com/app/apikey**
3. Haz clic en **"Create API key"**
4. Selecciona un proyecto de Google Cloud (o crea uno nuevo)
5. **COPIA LA KEY** - empieza con: `AIzaSy...`

### Paso 3: Configurar variable de entorno
```bash
# En tu terminal (Mac/Linux):
export GOOGLE_API_KEY="AIzaSy-tu-key-aqui"

# O añádelo a tu .env:
echo 'GOOGLE_API_KEY=AIzaSy-tu-key-aqui' >> .env
```

---

## 3️⃣ Probar las APIs con Python

### Opción A: Usando los scripts de test

```bash
# 1. Ir al directorio del proyecto
cd /Users/juan/Documents/cursor_projects/Origination_Campaigns

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux
# o: venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
mv env.example.txt .env
# Edita .env con tus API keys reales

# 5. Probar Anthropic
python test_apis/test_anthropic.py

# 6. Probar Gemini
python test_apis/test_gemini.py
```

### Opción B: Prueba rápida en Python interactivo

```python
# Probar Anthropic
from anthropic import Anthropic
client = Anthropic(api_key="tu-api-key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=100,
    messages=[{"role": "user", "content": "Di hola"}]
)
print(response.content[0].text)
```

```python
# Probar Gemini
import google.generativeai as genai
genai.configure(api_key="tu-api-key")
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Di hola")
print(response.text)
```

---

## 4️⃣ Probar con Postman

### Test de Anthropic (Claude)

**Request:**
```
POST https://api.anthropic.com/v1/messages
```

**Headers:**
```
x-api-key: sk-ant-api03-tu-key-aqui
anthropic-version: 2023-06-01
content-type: application/json
```

**Body (JSON):**
```json
{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Di hola en español"
        }
    ]
}
```

**Respuesta esperada (200 OK):**
```json
{
    "id": "msg_...",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": "¡Hola! ¿En qué puedo ayudarte hoy?"
        }
    ],
    "model": "claude-sonnet-4-20250514",
    "usage": {
        "input_tokens": 10,
        "output_tokens": 15
    }
}
```

### Test de Gemini

**Request:**
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=TU_API_KEY
```

**Headers:**
```
content-type: application/json
```

**Body (JSON):**
```json
{
    "contents": [
        {
            "parts": [
                {
                    "text": "Di hola en español"
                }
            ]
        }
    ]
}
```

**Respuesta esperada (200 OK):**
```json
{
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": "¡Hola! 👋"
                    }
                ],
                "role": "model"
            }
        }
    ],
    "usageMetadata": {
        "promptTokenCount": 5,
        "candidatesTokenCount": 4
    }
}
```

---

## 5️⃣ Probar con cURL (Terminal)

### Test Anthropic
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [
      {"role": "user", "content": "Di hola"}
    ]
  }'
```

### Test Gemini
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {"parts": [{"text": "Di hola"}]}
    ]
  }'
```

---

## ❌ Errores Comunes y Soluciones

### Anthropic

| Error | Causa | Solución |
|-------|-------|----------|
| `401 Unauthorized` | API key inválida | Verifica que la key empieza con `sk-ant-` |
| `400 invalid_api_key` | Key mal formada | Copia de nuevo desde la consola |
| `429 rate_limit_exceeded` | Límite alcanzado | Espera 1 minuto o añade billing |
| `529 overloaded` | Servidores saturados | Reintentar con backoff |

### Gemini

| Error | Causa | Solución |
|-------|-------|----------|
| `400 API_KEY_INVALID` | Key inválida | Regenera en AI Studio |
| `403 PERMISSION_DENIED` | Cuota excedida o región | Verifica proyecto en Cloud Console |
| `429 RESOURCE_EXHAUSTED` | Rate limit | Espera 60 segundos |

---

## ✅ Checklist de Verificación

Antes de continuar con el desarrollo, verifica:

- [ ] API key de Anthropic creada y copiada
- [ ] API key de Gemini creada y copiada
- [ ] Variables de entorno configuradas en `.env`
- [ ] Test de Anthropic pasado (`python test_apis/test_anthropic.py`)
- [ ] Test de Gemini pasado (`python test_apis/test_gemini.py`)
- [ ] Ambas APIs responden correctamente

---

## 💡 Consejos de Costes

### Anthropic
- Claude Sonnet: ~$3/1M input tokens, ~$15/1M output tokens
- Para desarrollo: limita `max_tokens` a 500
- Activa límite mensual en Billing

### Gemini
- 1.5 Flash: **GRATIS** hasta 15 req/min y 1M tokens/día
- 1.5 Pro: $0.125/1M input tokens
- Usa Flash para desarrollo, Pro solo si necesitas más capacidad

**Estimación mensual MVP**: ~$20-50 (principalmente Anthropic)

---

## 📞 Soporte

- **Anthropic**: [support@anthropic.com](mailto:support@anthropic.com)
- **Google AI**: [AI Studio Discord](https://discord.gg/google-ai)

---

*Documento actualizado: 2 Enero 2026*

