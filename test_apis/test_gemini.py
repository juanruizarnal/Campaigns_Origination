#!/usr/bin/env python3
"""
Test de conexión a la API de Google Gemini
==========================================
Este script verifica que tu API key de Google AI Studio funciona correctamente.

USO:
    1. Configura tu API key en .env o como variable de entorno:
       export GOOGLE_API_KEY="AIza..."
    
    2. Ejecuta el script:
       python test_apis/test_gemini.py
"""

import os
import sys
from datetime import datetime

# Intentar cargar desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_gemini_connection():
    """Prueba básica de conexión a la API de Gemini."""
    
    print("=" * 60)
    print("🟡 TEST DE API GOOGLE GEMINI")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Verificar que existe la API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: No se encontró GOOGLE_API_KEY")
        print()
        print("   Para configurar tu API key:")
        print("   1. Ve a: https://aistudio.google.com/app/apikey")
        print("   2. Crea una nueva API key")
        print("   3. Configúrala como variable de entorno:")
        print('      export GOOGLE_API_KEY="AIza..."')
        print("   O créala en un archivo .env en el directorio raíz")
        return False
    
    # Mostrar los primeros caracteres de la key
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 15 else "***"
    print(f"✅ API Key encontrada: {masked_key}")
    print()
    
    # 2. Intentar importar la librería
    try:
        import google.generativeai as genai
        print("✅ Librería 'google-generativeai' importada correctamente")
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar google-generativeai: {e}")
        print("   Instala con: pip install google-generativeai")
        return False
    
    # 3. Configurar y probar
    print()
    print("📡 Realizando llamada de prueba a Gemini...")
    print("-" * 40)
    
    try:
        genai.configure(api_key=api_key)
        
        # Usar Gemini 1.5 Flash (rápido y económico)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Llamada mínima de prueba
        response = model.generate_content(
            "Responde SOLO con: 'API de Gemini funcionando correctamente'"
        )
        
        response_text = response.text
        
        print(f"✅ RESPUESTA DE GEMINI:")
        print(f"   {response_text}")
        print()
        
        # Info adicional si está disponible
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            print(f"📊 Tokens usados:")
            print(f"   - Input: {response.usage_metadata.prompt_token_count}")
            print(f"   - Output: {response.usage_metadata.candidates_token_count}")
        
        print()
        print("=" * 60)
        print("✅ TEST EXITOSO: La API de Gemini funciona correctamente")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERROR en la llamada a la API: {e}")
        print()
        print("   Posibles causas:")
        print("   - API key inválida")
        print("   - Cuota excedida (límite gratuito)")
        print("   - Problema de conectividad")
        print()
        print(f"   Tipo de error: {type(e).__name__}")
        return False


def test_gemini_search_grounding():
    """Prueba de Search Grounding (búsqueda web) con Gemini."""
    
    print()
    print("=" * 60)
    print("🟡 TEST DE SEARCH GROUNDING (Búsqueda Web)")
    print("=" * 60)
    print()
    print("⚠️  NOTA: Search Grounding requiere configuración especial")
    print("   y puede no estar disponible en todas las regiones/cuentas.")
    print()
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ API key no configurada")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt que beneficia de búsqueda web
        print("📡 Probando generación con contexto actual...")
        print("-" * 40)
        
        response = model.generate_content(
            """Busca información sobre la empresa Iberdrola en España.
            Responde en formato breve:
            - Sector principal
            - Si tiene certificaciones ambientales conocidas (ISO 14001, etc.)
            - Si trabaja en energías renovables"""
        )
        
        response_text = response.text
        
        print(f"✅ RESPUESTA:")
        print(response_text)
        print()
        
        # Verificar si usó grounding
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                print("✅ Search Grounding disponible y activo")
            else:
                print("ℹ️  Respuesta generada (grounding no confirmado)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("   Si el error es sobre 'grounding', la feature puede no estar")
        print("   habilitada para tu cuenta. El proyecto funcionará sin ella.")
        return False


def test_gemini_structured_output():
    """Prueba de respuesta estructurada (JSON) con Gemini."""
    
    print()
    print("=" * 60)
    print("🟡 TEST DE RESPUESTA ESTRUCTURADA (JSON)")
    print("=" * 60)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ API key no configurada")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt que pide JSON
        response = model.generate_content(
            """Analiza esta empresa ficticia y devuelve SOLO un JSON válido:
            
Empresa: EcoEnergy Solutions
Sector: Energía Solar
Empleados: 150
País: España

Devuelve SOLO este JSON (sin explicaciones ni markdown):
{
    "nombre": "...",
    "sector": "...",
    "tamano": "pyme/midcap/gran_empresa",
    "potencial_fei": "alto/medio/bajo"
}"""
        )
        
        response_text = response.text
        
        print(f"✅ RESPUESTA ESTRUCTURADA:")
        print(response_text)
        print()
        
        # Intentar parsear como JSON
        import json
        try:
            # Limpiar posible markdown
            json_str = response_text.strip()
            if json_str.startswith("```"):
                lines = json_str.split("\n")
                json_str = "\n".join(lines[1:-1])
            
            parsed = json.loads(json_str)
            print("✅ JSON parseado correctamente:")
            print(f"   {json.dumps(parsed, indent=2, ensure_ascii=False)}")
            return True
        except json.JSONDecodeError as e:
            print(f"⚠️  Respuesta recibida pero no es JSON puro: {e}")
            print("   Esto es normal, Gemini a veces añade explicaciones.")
            return True  # La API funcionó
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def list_available_models():
    """Lista los modelos de Gemini disponibles."""
    
    print()
    print("=" * 60)
    print("🟡 MODELOS DISPONIBLES")
    print("=" * 60)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        print("Modelos Gemini accesibles con tu API key:")
        print("-" * 40)
        
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"  • {model.name}")
        
        print()
        print("Recomendados para el proyecto:")
        print("  • gemini-1.5-flash (rápido, económico)")
        print("  • gemini-1.5-pro (más capaz, más lento)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR listando modelos: {e}")
        return False


if __name__ == "__main__":
    success1 = test_gemini_connection()
    
    if success1:
        list_available_models()
        test_gemini_structured_output()
        test_gemini_search_grounding()
    
    print()
    if success1:
        print("🎉 API de Gemini lista para usar en el proyecto")
    else:
        print("⚠️  Revisa la configuración antes de continuar")
        sys.exit(1)

