#!/usr/bin/env python3
"""
Script para autorizar el proyecto de GCP para usar el dataset público de BigQuery.
Este script debe ejecutarse UNA VEZ con credenciales de usuario (no service account)
para autorizar el proyecto. Después de esto, el service account podrá acceder.
"""
import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'brave-computer-454217-q4')

if not PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable is required")

print(f"🔐 Autorizando proyecto {PROJECT_ID} para usar dataset público...")
print("   Esto debe ejecutarse con credenciales de USUARIO (no service account)")

client = bigquery.Client(project=PROJECT_ID)

# Query simple para autorizar el proyecto
query = """
SELECT COUNT(*) as total
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE DATE(trip_start_timestamp) >= '2023-06-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
LIMIT 1
"""

try:
    print("🔄 Ejecutando query de autorización...")
    result = client.query(query).result()
    row = next(result)
    print(f"✅ Proyecto autorizado exitosamente!")
    print(f"   Total viajes disponibles: {row.total:,}")
    print("\n📋 Ahora el service account de GitHub Actions podrá acceder al dataset público.")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Asegúrate de estar autenticado con credenciales de USUARIO:")
    print("   gcloud auth application-default login")
    import sys
    sys.exit(1)
