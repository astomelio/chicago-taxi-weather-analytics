#!/usr/bin/env python3
"""
Script para verificar qué identidad está usando realmente Airflow/Composer.
Ejecutar dentro del entorno de Composer para diagnosticar el problema.
"""
import os
import sys

print("🔍 Verificando identidad que usa Airflow/Composer...")
print("")

# Verificar Application Default Credentials
try:
    import google.auth
    from google.auth import default
    
    credentials, project = default()
    
    print("📋 Application Default Credentials (ADC):")
    if hasattr(credentials, 'service_account_email'):
        print(f"   Service Account: {credentials.service_account_email}")
    elif hasattr(credentials, 'client_email'):
        print(f"   Service Account: {credentials.client_email}")
    else:
        print(f"   Tipo: {type(credentials)}")
        print(f"   Info: {str(credentials)[:200]}")
    
    print(f"   Proyecto: {project}")
    print("")
except Exception as e:
    print(f"❌ Error obteniendo ADC: {e}")
    print("")

# Verificar GOOGLE_APPLICATION_CREDENTIALS
print("📋 Variables de entorno:")
print(f"   GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NO CONFIGURADO')}")
print("")

# Verificar si existe el archivo de credenciales
creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
if creds_path and os.path.exists(creds_path):
    print(f"✅ Archivo de credenciales existe: {creds_path}")
    try:
        import json
        with open(creds_path, 'r') as f:
            creds = json.load(f)
            print(f"   Service Account: {creds.get('client_email', 'NO ENCONTRADO')}")
    except Exception as e:
        print(f"   Error leyendo archivo: {e}")
else:
    print("⚠️  GOOGLE_APPLICATION_CREDENTIALS no está configurado o el archivo no existe")
    print("   Airflow usará Application Default Credentials del entorno")

print("")
print("📋 Verificando acceso a BigQuery...")
try:
    from google.cloud import bigquery
    
    client = bigquery.Client()
    
    # Intentar una query simple
    query = "SELECT COUNT(*) as test FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips` LIMIT 1"
    job = client.query(query)
    result = job.result()
    row = next(result)
    print(f"✅ Acceso a BigQuery funciona! Resultado: {row.test}")
    print(f"   La identidad actual PUEDE acceder al dataset público")
except Exception as e:
    error_msg = str(e)
    print(f"❌ Error accediendo a BigQuery: {error_msg[:300]}")
    if "403" in error_msg or "Access Denied" in error_msg or "permission" in error_msg.lower():
        print("")
        print("🔧 SOLUCIÓN:")
        print("   1. Verifica qué service account está usando (arriba)")
        print("   2. Otorga estos roles a ese service account:")
        print("      - roles/bigquery.user")
        print("      - roles/bigquery.dataViewer")
        print("      - roles/bigquery.dataEditor")
        print("      - roles/bigquery.jobUser")
        print("   3. Ejecuta: ./scripts/verificar_y_otorgar_permisos.sh")
        print("   4. O activa acceso al dataset público ejecutando una query desde BigQuery Console")

print("")
