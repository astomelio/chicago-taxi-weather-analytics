#!/usr/bin/env python3
"""
Script para verificar que las tablas existen en BigQuery y mostrar datos reales.
Ejecutar: python3 scripts/verify_tables.py
"""

from google.cloud import bigquery
import os
import sys

PROJECT_ID = "brave-computer-454217-q4"

def verify_tables():
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        print(f"🔍 Verificando tablas en proyecto: {PROJECT_ID}\n")
        print("=" * 60)
        
        # Verificar datasets y tablas
        datasets = ["chicago_taxi_raw", "chicago_taxi_silver", "chicago_taxi_gold"]
        
        for dataset_id in datasets:
            print(f"\n📊 Dataset: {dataset_id}")
            try:
                dataset = client.get_dataset(dataset_id)
                print(f"   ✅ Dataset existe")
                
                # Listar tablas
                tables = list(client.list_tables(dataset_id))
                if tables:
                    for table in tables:
                        table_ref = client.get_table(f"{PROJECT_ID}.{dataset_id}.{table.table_id}")
                        row_count = table_ref.num_rows if hasattr(table_ref, 'num_rows') else None
                        size_mb = table_ref.num_bytes / (1024*1024) if hasattr(table_ref, 'num_bytes') and table_ref.num_bytes else 0
                        print(f"   📋 Tabla: {table.table_id}")
                        print(f"      Tipo: {table_ref.table_type}")
                        if row_count:
                            print(f"      Filas: {row_count:,}")
                        print(f"      Tamaño: {size_mb:.2f} MB")
                else:
                    print(f"   ⚠️  No hay tablas en este dataset")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Queries de datos reales
        print("\n\n" + "=" * 60)
        print("🔍 QUERIES DE DATOS REALES:\n")
        
        # 1. Weather data
        print("1️⃣  Weather Data (RAW):")
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_days,
                MIN(date) as min_date,
                MAX(date) as max_date,
                COUNT(DISTINCT date) as unique_days
            FROM `{PROJECT_ID}.chicago_taxi_raw.weather_data`
            """
            result = client.query(query).result()
            row = next(result)
            print(f"   ✅ Total días: {row.total_days}")
            print(f"   ✅ Rango: {row.min_date} a {row.max_date}")
            print(f"   ✅ Días únicos: {row.unique_days}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 2. Taxi trips silver
        print("\n2️⃣  Taxi Trips Silver:")
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_trips,
                MIN(trip_date) as min_date,
                MAX(trip_date) as max_date
            FROM `{PROJECT_ID}.chicago_taxi_silver.taxi_trips_silver`
            """
            result = client.query(query).result()
            row = next(result)
            print(f"   ✅ Total viajes: {row.total_trips:,}")
            print(f"   ✅ Rango: {row.min_date} a {row.max_date}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 3. Weather silver
        print("\n3️⃣  Weather Silver:")
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_days,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM `{PROJECT_ID}.chicago_taxi_silver.weather_silver`
            """
            result = client.query(query).result()
            row = next(result)
            print(f"   ✅ Total días: {row.total_days}")
            print(f"   ✅ Rango: {row.min_date} a {row.max_date}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 4. Daily summary (gold)
        print("\n4️⃣  Daily Summary (Gold):")
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_rows,
                MIN(trip_date) as min_date,
                MAX(trip_date) as max_date,
                SUM(total_trips) as total_trips
            FROM `{PROJECT_ID}.chicago_taxi_gold.daily_summary`
            """
            result = client.query(query).result()
            row = next(result)
            print(f"   ✅ Total filas: {row.total_rows}")
            print(f"   ✅ Rango: {row.min_date} a {row.max_date}")
            if row.total_trips:
                print(f"   ✅ Total viajes agregados: {row.total_trips:,}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Taxi weather analysis (gold)
        print("\n5️⃣  Taxi Weather Analysis (Gold):")
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_rows,
                MIN(trip_date) as min_date,
                MAX(trip_date) as max_date
            FROM `{PROJECT_ID}.chicago_taxi_gold.taxi_weather_analysis`
            """
            result = client.query(query).result()
            row = next(result)
            print(f"   ✅ Total filas: {row.total_rows}")
            print(f"   ✅ Rango: {row.min_date} a {row.max_date}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        print("\n💡 Asegúrate de tener:")
        print("   1. google-cloud-bigquery instalado: pip install google-cloud-bigquery")
        print("   2. Credenciales configuradas: export GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json")
        print("   3. O ejecutar: gcloud auth application-default login")
        sys.exit(1)

if __name__ == "__main__":
    verify_tables()
