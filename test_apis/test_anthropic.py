#!/usr/bin/env python3
"""
Test de conexión a la API de Anthropic (Claude)
===============================================
Este script verifica que tu API key de Anthropic funciona correctamente.

USO:
    1. Configura tu API key en .env o como variable de entorno:
       export ANTHROPIC_API_KEY="sk-ant-..."
    
    2. Ejecuta el script:
       python test_apis/test_anthropic.py
"""

import os
import sys
from datetime import datetime

# Intentar cargar desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Si no está instalado, asumimos que la API key está en el entorno

def test_anthropic_connection():
    """Prueba básica de conexión a la API de Anthropic."""
    
    print("=" * 60)
    print("🔵 TEST DE API ANTHROPIC (Claude)")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar que existe la API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ERROR: No se encontró ANTHROPIC_API_KEY")
        print()
        print("   Para configurar tu API key:")
        print("   1. Obtén tu key en: https://console.anthropic.com/settings/keys")
        print("   2. Configúrala como variable de entorno:")
        print('      export ANTHROPIC_API_KEY="sk-ant-..."')
        print("   O créala en un archivo .env en el directorio raíz")
        return False
    
    # Mostrar los primeros caracteres de la key (para verificación)
    masked_key = api_key[:12] + "..." + api_key[-4:] if len(api_key) > 20 else "***"
    print(f"✅ API Key encontrada: {masked_key}")
    print()
    
    # 2. Intentar importar la librería
    try:
        from anthropic import Anthropic
        print("✅ Librería 'anthropic' importada correctamente")
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar la librería anthropic: {e}")
        print("   Instala con: pip install anthropic")
        return False
    
    # 3. Crear cliente e intentar llamada
    print()
    print("📡 Realizando llamada de prueba a Claude...")
    print("-" * 40)
    
    try:
        client = Anthropic(api_key=api_key)
        
        # Llamada mínima de prueba
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Responde SOLO con: 'API funcionando correctamente'"
                }
            ]
        )
        
        # Extraer respuesta
        response_text = response.content[0].text
        
        print(f"✅ RESPUESTA DE CLAUDE:")
        print(f"   {response_text}")
        print()
        print(f"📊 Tokens usados:")
        print(f"   - Input: {response.usage.input_tokens}")
        print(f"   - Output: {response.usage.output_tokens}")
        print(f"   - Modelo: {response.model}")
        print()
        print("=" * 60)
        print("✅ TEST EXITOSO: La API de Anthropic funciona correctamente")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR en la llamada a la API: {e}")
        print()
        print("   Posibles causas:")
        print("   - API key inválida o expirada")
        print("   - Sin créditos en la cuenta")
        print("   - Problema de conectividad")
        print()
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def test_anthropic_structured_output():
    """Prueba de respuesta estructurada (JSON) con Claude."""
    
    print()
    print("=" * 60)
    print("🔵 TEST DE RESPUESTA ESTRUCTURADA (JSON)")
    print("=" * 60)
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ API key no configurada")
        return False
    
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Prompt que pide JSON
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": """Analiza esta empresa ficticia y devuelve JSON:
                    
Empresa: SolarTech España
Sector: Energía Renovable
Certificaciones: ISO 14001

Devuelve SOLO un JSON con este formato:
{
    "nombre": "...",
    "sector": "...",
    "fei_eligible": true/false,
    "razon": "..."
}"""
                }
            ]
        )
        
        response_text = response.content[0].text
        
        print(f"✅ RESPUESTA ESTRUCTURADA:")
        print(response_text)
        print()
        
        # Intentar parsear como JSON
        import json
        try:
            # Extraer JSON si viene con markdown
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text
                
            parsed = json.loads(json_str.strip())
            print("✅ JSON parseado correctamente:")
            print(f"   {json.dumps(parsed, indent=2, ensure_ascii=False)}")
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️  No se pudo parsear como JSON: {e}")
            return True  # La API funcionó, solo falló el parsing
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success1 = test_anthropic_connection()
    
    if success1:
        success2 = test_anthropic_structured_output()
    
    print()
    if success1:
        print("🎉 API de Anthropic lista para usar en el proyecto")
    else:
        print("⚠️  Revisa la configuración antes de continuar")
        sys.exit(1)

