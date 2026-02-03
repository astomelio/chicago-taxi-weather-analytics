#!/usr/bin/env python3
"""
Script para probar directamente la query de BigQuery público.
Requiere autenticación de GCP configurada.
"""

import os
from google.cloud import bigquery
from datetime import datetime

def test_bigquery_weather():
    """Prueba que podemos acceder a datos de clima en BigQuery público"""
    
    # Obtener PROJECT_ID
    project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("PROJECT_ID")
    if not project_id:
        print("⚠️  Configura PROJECT_ID:")
        print("   export GCP_PROJECT_ID='tu-proyecto-gcp'")
        print("\n💡 Puedes usar cualquier proyecto de GCP para acceder a datasets públicos")
        return False
    
    print(f"✅ Usando proyecto: {project_id}")
    print()
    
    # Crear cliente de BigQuery
    try:
        client = bigquery.Client(project=project_id)
        print("✅ Cliente de BigQuery creado")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        print("\n💡 Configura las credenciales de GCP:")
        print("   gcloud auth application-default login")
        return False
    
    # Probar query con fecha específica
    test_date = datetime(2023, 6, 1)
    query = f"""
    SELECT 
        date,
        AVG(SAFE_CAST(temp AS FLOAT64)) as avg_temp,
        AVG(SAFE_CAST(max AS FLOAT64)) as max_temp,
        AVG(SAFE_CAST(min AS FLOAT64)) as min_temp,
        AVG(SAFE_CAST(wdsp AS FLOAT64)) as avg_wind_speed,
        SUM(SAFE_CAST(prcp AS FLOAT64)) as total_precipitation
    FROM `bigquery-public-data.noaa_gsod.gsod{test_date.year}`
    WHERE wban = '94846'
      AND date = DATE('{test_date.date().isoformat()}')
      AND temp IS NOT NULL
    GROUP BY date
    """
    
    print(f"🌤️  Probando query para {test_date.date()}...")
    print("   Dataset: bigquery-public-data.noaa_gsod")
    print("   Estación: Chicago O'Hare (WBAN: 94846)")
    print()
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        row = next(results, None)
        
        if row:
            print("✅ Datos encontrados en BigQuery público:")
            print(f"   Fecha: {row.date}")
            print(f"   Temperatura promedio: {row.avg_temp}°F")
            print(f"   Temperatura máxima: {row.max_temp}°F")
            print(f"   Temperatura mínima: {row.min_temp}°F")
            print(f"   Viento promedio: {row.avg_wind_speed} nudos")
            print(f"   Precipitación: {row.total_precipitation} pulgadas")
            print()
            print("✅ La función debería funcionar correctamente con estas credenciales")
            return True
        else:
            print("⚠️  No se encontraron datos para esa fecha")
            print("   Verifica la query en: scripts/test_bigquery_weather.sql")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando query: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Configura credenciales: gcloud auth application-default login")
        print("   2. Verifica que el proyecto existe y tienes permisos")
        print("   3. Prueba la query directamente en BigQuery console")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA DE ACCESO A BIGQUERY PÚBLICO (NOAA)")
    print("=" * 60)
    print()
    
    success = test_bigquery_weather()
    
    print()
    print("=" * 60)
    if success:
        print("✅ PRUEBA EXITOSA")
    else:
        print("❌ PRUEBA FALLIDA")
        print()
        print("📝 Para probar sin credenciales, ejecuta la query SQL directamente:")
        print("   https://console.cloud.google.com/bigquery")
        print("   Ver: scripts/test_bigquery_weather.sql")
    print("=" * 60)
