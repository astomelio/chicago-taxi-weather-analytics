#!/usr/bin/env python3
"""
Script para crear automáticamente las tablas silver y gold en BigQuery.
Este script se puede ejecutar desde la Cloud Function o como job separado.
"""

from google.cloud import bigquery
import os
import sys
import time

PROJECT_ID = os.environ.get("GCP_PROJECT_ID") or os.environ.get("PROJECT_ID", "brave-computer-454217-q4")

def create_taxi_trips_silver(client: bigquery.Client, project_id: str) -> bool:
    """Crea la tabla taxi_trips_silver."""
    print("🔄 Creando taxi_trips_silver...")
    print("   (Esto puede tardar 5-10 minutos)")
    
    query = f"""
    CREATE OR REPLACE TABLE `{project_id}.chicago_taxi_silver.taxi_trips_silver`
    PARTITION BY trip_date
    CLUSTER BY trip_date AS
    WITH raw_trips AS (
      SELECT *
      FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
      WHERE trip_start_timestamp IS NOT NULL
        AND trip_seconds IS NOT NULL
        AND trip_seconds > 0
        AND trip_miles >= 0
        AND DATE(trip_start_timestamp) >= '2023-06-01'
        AND DATE(trip_start_timestamp) <= '2023-12-31'
    ),
    deduplicated_trips AS (
      SELECT *
      FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                 PARTITION BY unique_key 
                 ORDER BY trip_start_timestamp DESC
               ) AS rn
        FROM raw_trips
      )
      WHERE rn = 1
    )
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
      company,
      pickup_latitude,
      pickup_longitude,
      dropoff_latitude,
      dropoff_longitude,
      DATE(trip_start_timestamp) AS trip_date,
      EXTRACT(HOUR FROM trip_start_timestamp) AS trip_hour,
      EXTRACT(DAYOFWEEK FROM trip_start_timestamp) AS trip_day_of_week,
      CASE 
        WHEN trip_seconds > 0 THEN trip_miles / (trip_seconds / 3600.0)
        ELSE NULL
      END AS avg_speed_mph
    FROM deduplicated_trips
    """
    
    try:
        job = client.query(query)
        print("   ⏳ Ejecutando query...")
        job.result()
        print("   ✅ taxi_trips_silver creada")
        
        # Verificar
        query_count = f"SELECT COUNT(*) as count FROM `{project_id}.chicago_taxi_silver.taxi_trips_silver`"
        result = client.query(query_count).result()
        count = next(result).count
        print(f"   ✅ Registros: {count:,}")
        return True
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "permission" in error_msg.lower():
            print(f"   ❌ Error de permisos: {error_msg[:200]}")
            return False
        else:
            print(f"   ❌ Error: {error_msg[:200]}")
            return False

def create_daily_summary(client: bigquery.Client, project_id: str) -> bool:
    """Crea la tabla daily_summary."""
    print("\n🔄 Creando daily_summary...")
    print("   (Esto puede tardar 2-5 minutos)")
    
    query = f"""
    CREATE OR REPLACE TABLE `{project_id}.chicago_taxi_gold.daily_summary`
    PARTITION BY date
    CLUSTER BY date AS
    WITH taxi_trips AS (
      SELECT *
      FROM `{project_id}.chicago_taxi_silver.taxi_trips_silver`
    ),
    weather_data AS (
      SELECT *
      FROM `{project_id}.chicago_taxi_silver.weather_silver`
    )
    SELECT
      t.trip_date as date,
      w.weather_category,
      w.temperature_category,
      w.temperature,
      w.precipitation,
      w.wind_speed,
      w.humidity,
      w.weather_condition,
      COUNT(*) AS total_trips,
      COUNT(DISTINCT t.taxi_id) AS unique_taxis,
      AVG(t.trip_seconds) AS avg_trip_duration_seconds,
      APPROX_QUANTILES(t.trip_seconds, 100)[OFFSET(50)] AS median_trip_duration_seconds,
      SUM(t.trip_miles) AS total_miles,
      AVG(t.trip_miles) AS avg_trip_miles,
      AVG(t.avg_speed_mph) AS avg_speed_mph,
      AVG(t.fare) AS avg_fare,
      AVG(t.tips) AS avg_tips,
      AVG(t.trip_total) AS avg_trip_total,
      SUM(t.trip_total) AS total_revenue
    FROM taxi_trips t
    LEFT JOIN weather_data w
      ON t.trip_date = w.date
    GROUP BY 
      t.trip_date,
      w.weather_category,
      w.temperature_category,
      w.temperature,
      w.precipitation,
      w.wind_speed,
      w.humidity,
      w.weather_condition
    ORDER BY t.trip_date
    """
    
    try:
        job = client.query(query)
        print("   ⏳ Ejecutando query...")
        job.result()
        print("   ✅ daily_summary creada")
        
        # Verificar
        query_count = f"SELECT COUNT(*) as count FROM `{project_id}.chicago_taxi_gold.daily_summary`"
        result = client.query(query_count).result()
        count = next(result).count
        print(f"   ✅ Registros: {count:,}")
        
        # Mostrar muestra
        query_sample = f"""
        SELECT 
          date,
          total_trips,
          temperature,
          weather_category,
          avg_trip_duration_seconds / 60 as avg_duration_minutes,
          total_revenue
        FROM `{project_id}.chicago_taxi_gold.daily_summary`
        ORDER BY date
        LIMIT 5
        """
        result = client.query(query_sample).result()
        print("\n📊 Muestra de datos:")
        print("   Fecha       | Viajes    | Temp | Clima      | Duración | Ingresos")
        print("   " + "-" * 70)
        for row in result:
            print(f"   {row.date} | {row.total_trips:>8,} | {row.temperature:>4.1f}°C | {row.weather_category[:10]:>10} | {row.avg_duration_minutes:>7.1f}m | ${row.total_revenue:>10,.2f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:200]}")
        return False

def main():
    """Función principal."""
    print("=" * 70)
    print("🔄 CREANDO TABLAS SILVER Y GOLD AUTOMÁTICAMENTE")
    print("=" * 70)
    print(f"Proyecto: {PROJECT_ID}\n")
    
    client = bigquery.Client(project=PROJECT_ID)
    
    # Crear taxi_trips_silver
    if not create_taxi_trips_silver(client, PROJECT_ID):
        print("\n❌ No se pudo crear taxi_trips_silver")
        print("   Verifica los permisos del service account")
        sys.exit(1)
    
    # Crear daily_summary
    if not create_daily_summary(client, PROJECT_ID):
        print("\n❌ No se pudo crear daily_summary")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("✅ ¡TODAS LAS TABLAS CREADAS EXITOSAMENTE!")
    print("=" * 70)
    print(f"\n📊 Tabla daily_summary lista en:")
    print(f"   {PROJECT_ID}.chicago_taxi_gold.daily_summary")
    print("\n🎯 Puedes conectarla a Looker Studio ahora")

if __name__ == "__main__":
    main()
