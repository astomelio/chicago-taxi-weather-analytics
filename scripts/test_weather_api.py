#!/usr/bin/env python3
"""
Script simple para probar que la función de ingesta de datos del clima funciona.
No requiere BigQuery ni infraestructura desplegada.
"""

import os
import sys
from datetime import datetime

# Agregar el directorio de la función al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions', 'weather_ingestion'))

def test_weather_api():
    """Prueba que la obtención de datos del clima funciona"""
    
    # Verificar que tenemos PROJECT_ID (necesario para BigQuery)
    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("PROJECT_ID")
    if not project_id:
        print("⚠️  ADVERTENCIA: GCP_PROJECT_ID no está configurada")
        print("   Se necesita para acceder a BigQuery público")
        print("   Configúrala con: export GCP_PROJECT_ID='tu-proyecto'")
        print("   O usa: export PROJECT_ID='tu-proyecto'")
        return False
    
    print(f"✅ GCP Project ID encontrado: {project_id}")
    
    # API key es opcional (solo fallback)
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if api_key:
        print(f"✅ API Key encontrada (fallback): {api_key[:10]}...")
    else:
        print("ℹ️  API Key no configurada (se usará solo BigQuery público)")
    
    # Importar función
    try:
        from main import get_weather_data
    except ImportError as e:
        print(f"❌ Error importando función: {e}")
        return False
    
    # Configurar variables necesarias para BigQuery
    os.environ["PROJECT_ID"] = project_id
    os.environ["DATASET_ID"] = "chicago_taxi_raw"  # No se usa para la prueba, pero la función lo requiere
    os.environ["TABLE_ID"] = "weather_data"  # No se usa para la prueba
    
    # Probar con una fecha específica
    test_date = datetime(2023, 6, 1)
    print(f"\n🌤️  Probando obtención de datos del clima para {test_date.date()}...")
    print("   Fuente: BigQuery público (NOAA)")
    
    try:
        weather_data = get_weather_data(test_date)
        
        print("\n✅ Datos obtenidos exitosamente desde BigQuery:")
        print(f"   Fecha: {weather_data['date']}")
        print(f"   Temperatura: {weather_data.get('temperature', 'N/A')}°C")
        print(f"   Humedad: {weather_data.get('humidity', 'N/A')}%")
        print(f"   Viento: {weather_data.get('wind_speed', 'N/A')} m/s")
        print(f"   Precipitación: {weather_data.get('precipitation', 'N/A')} mm")
        print(f"   Condición: {weather_data.get('weather_condition', 'N/A')}")
        
        return True
        
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        print("\n💡 Posibles causas:")
        print("   - GCP_PROJECT_ID incorrecto")
        print("   - Problema de conexión a BigQuery")
        print("   - Permisos insuficientes en GCP")
        print("   - Datos no disponibles en NOAA para esa fecha")
        if api_key:
            print("   - Intentará usar API externa como fallback")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DE FUNCIÓN DE INGESTA DE DATOS DEL CLIMA")
    print("=" * 60)
    print()
    
    success = test_weather_api()
    
    print()
    print("=" * 60)
    if success:
        print("✅ PRUEBA EXITOSA - La función funciona correctamente")
    else:
        print("❌ PRUEBA FALLIDA - Revisa los errores arriba")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
