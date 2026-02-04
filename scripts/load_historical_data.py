#!/usr/bin/env python3
"""
Script para cargar datos históricos directamente en BigQuery.
Útil cuando el DAG de Airflow no se ha ejecutado o falló.
"""
import os
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Configuración
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'brave-computer-454217-q4')
REGION = 'us-central1'
RAW_DATASET = 'chicago_taxi_raw'

def load_historical_taxi_data():
    """Carga datos históricos de taxis del dataset público a una tabla propia."""
    client = bigquery.Client(project=PROJECT_ID, location=REGION)
    
    table_id = f"{PROJECT_ID}.{RAW_DATASET}.taxi_trips_raw_table"
    
    # Verificar si la tabla ya existe y tiene datos
    try:
        table = client.get_table(table_id)
        count_query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        count_job = client.query(count_query, location=REGION)
        count_result = count_job.result()
        row_count = next(count_result).cnt
        
        if row_count > 0:
            print(f"✅ Tabla {table_id} ya existe con {row_count:,} registros.")
            return True
        else:
            print(f"⚠️  Tabla existe pero está vacía. Cargando datos...")
    except NotFound:
        print(f"📋 Tabla {table_id} no existe. Creándola y cargando datos...")
    except Exception as e:
        print(f"⚠️  Error verificando tabla: {e}")
        print("   Intentando crear de todas formas...")
    
    # Crear tabla y cargar datos históricos
    load_query = f"""
    CREATE OR REPLACE TABLE `{table_id}`
    PARTITION BY DATE(trip_start_timestamp)
    CLUSTER BY trip_start_timestamp AS
    SELECT 
      unique_key,
      taxi_id,
      trip_start_timestamp,
      trip_end_timestamp,
      trip_seconds,
      trip_miles,
      pickup_census_tract,
      dropoff_census_tract,
      pickup_community_area,
      dropoff_community_area,
      fare,
      tips,
      tolls,
      extras,
      trip_total,
      payment_type,
      company,
      pickup_latitude,
      pickup_longitude,
      dropoff_latitude,
      dropoff_longitude
    FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
    WHERE DATE(trip_start_timestamp) >= '2023-06-01'
      AND DATE(trip_start_timestamp) <= '2023-12-31'
      AND trip_start_timestamp IS NOT NULL
      AND trip_seconds IS NOT NULL
      AND trip_seconds > 0
      AND trip_miles >= 0
    """
    
    try:
        print(f"🔄 Cargando datos históricos de taxis (esto puede tardar 10-20 minutos)...")
        job_config = bigquery.QueryJobConfig(use_legacy_sql=False, priority='BATCH')
        query_job = client.query(load_query, job_config=job_config, location=REGION)
        query_job.result()  # Esperar a que termine
        
        # Verificar que se cargó correctamente
        count_query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
        count_job = client.query(count_query, location=REGION)
        count_result = count_job.result()
        row_count = next(count_result).cnt
        print(f"✅ Datos históricos de taxis cargados exitosamente: {row_count:,} registros")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "Access Denied" in error_msg or "permission" in error_msg.lower() or "403" in error_msg:
            print(f"")
            print(f"❌ ERROR DE PERMISOS: No se puede acceder al dataset público de BigQuery")
            print(f"")
            print(f"═══════════════════════════════════════════════════════════════════════")
            print(f"   SOLUCIÓN REQUERIDA:")
            print(f"═══════════════════════════════════════════════════════════════════════")
            print(f"")
            print(f"   1. Ve a BigQuery Console:")
            print(f"      https://console.cloud.google.com/bigquery?project={PROJECT_ID}")
            print(f"")
            print(f"   2. Ejecuta esta query (con tu usuario, NO service account):")
            print(f"      SELECT COUNT(*) as test")
            print(f"      FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`")
            print(f"      WHERE DATE(trip_start_timestamp) >= '2023-06-01'")
            print(f"        AND DATE(trip_start_timestamp) <= '2023-12-31'")
            print(f"")
            print(f"   3. Esto activará el acceso al dataset público para todo el proyecto")
            print(f"")
            print(f"   4. Una vez activado, vuelve a ejecutar este script")
            print(f"")
            print(f"═══════════════════════════════════════════════════════════════════════")
            return False
        else:
            print(f"❌ Error cargando datos históricos: {e}")
            return False

if __name__ == '__main__':
    print("=" * 70)
    print("  CARGA DE DATOS HISTÓRICOS - CHICAGO TAXI TRIPS")
    print("=" * 70)
    print(f"Proyecto: {PROJECT_ID}")
    print(f"Dataset: {RAW_DATASET}")
    print("")
    
    success = load_historical_taxi_data()
    
    if success:
        print("")
        print("✅ Proceso completado exitosamente")
        print("")
        print("Próximos pasos:")
        print("  1. Ejecuta el DAG histórico en Airflow para cargar datos de clima")
        print("  2. Ejecuta dbt para crear las capas silver y gold")
    else:
        print("")
        print("❌ Proceso falló. Revisa los mensajes de error arriba.")
        exit(1)
