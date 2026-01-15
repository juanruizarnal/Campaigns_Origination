#!/usr/bin/env python3
"""
Ejecuta todos los tests de APIs
===============================
Este script verifica que todas las APIs necesarias funcionan correctamente.

USO:
    python test_apis/run_all_tests.py
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " VERIFICACIÓN DE APIs - Motor de Originación Alter-5 ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = {}
    
    # Test Anthropic
    print("─" * 60)
    try:
        from test_apis.test_anthropic import test_anthropic_connection
        results["Anthropic"] = test_anthropic_connection()
    except Exception as e:
        print(f"❌ Error importando test de Anthropic: {e}")
        results["Anthropic"] = False
    
    print()
    
    # Test Gemini
    print("─" * 60)
    try:
        from test_apis.test_gemini import test_gemini_connection
        results["Gemini"] = test_gemini_connection()
    except Exception as e:
        print(f"❌ Error importando test de Gemini: {e}")
        results["Gemini"] = False
    
    # Resumen final
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " RESUMEN DE TESTS ".center(58) + "║")
    print("╠" + "═" * 58 + "╣")
    
    all_passed = True
    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        line = f"  {api}: {status}"
        print("║" + line.ljust(58) + "║")
        if not passed:
            all_passed = False
    
    print("╠" + "═" * 58 + "╣")
    
    if all_passed:
        print("║" + " 🎉 TODAS LAS APIs FUNCIONAN CORRECTAMENTE ".center(58) + "║")
        print("║" + " Puedes continuar con el desarrollo ".center(58) + "║")
    else:
        print("║" + " ⚠️  ALGUNAS APIs FALLARON ".center(58) + "║")
        print("║" + " Revisa las instrucciones en INSTRUCCIONES_TEST_APIS.md ".center(58) + "║")
    
    print("╚" + "═" * 58 + "╝")
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

