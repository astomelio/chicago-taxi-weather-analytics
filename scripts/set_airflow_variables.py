#!/usr/bin/env python3
"""
Script para configurar variables de Airflow en Cloud Composer.
Se ejecuta dentro del entorno de Composer usando gcloud composer environments run.
"""
import os
import sys
from airflow.models import Variable
from airflow import settings

def set_variables():
    """Configura todas las variables de Airflow necesarias."""
    variables = {
        'GCP_PROJECT_ID': os.environ.get('GCP_PROJECT_ID', ''),
        'GCP_REGION': os.environ.get('GCP_REGION', 'us-central1'),
        'DBT_PROJECT_DIR': '/home/airflow/gcs/data/dbt',
        'DBT_PROFILES_DIR': '/home/airflow/gcs/data/dbt',
        'DBT_PROFILE': 'chicago_taxi_analysis',
        'GCP_SA_KEY_PATH': '/home/airflow/gcs/data/github-actions-key.json',
        'OPENWEATHER_API_KEY': os.environ.get('OPENWEATHER_API_KEY', ''),
    }
    
    print("🔧 Configurando variables de Airflow...")
    
    for key, value in variables.items():
        if value:  # Solo configurar si tiene valor
            try:
                Variable.set(key, value)
                print(f"   ✅ {key} = {value[:50]}..." if len(str(value)) > 50 else f"   ✅ {key} = {value}")
            except Exception as e:
                print(f"   ⚠️  Error configurando {key}: {e}")
        else:
            print(f"   ⏭️  Saltando {key} (sin valor)")
    
    print("✅ Variables configuradas correctamente")
    
    # Verificar que se configuraron
    print("\n📋 Variables configuradas:")
    for key in variables.keys():
        try:
            value = Variable.get(key, default_var=None)
            if value:
                print(f"   {key} = {value[:50]}..." if len(str(value)) > 50 else f"   {key} = {value}")
        except:
            print(f"   {key} = (no configurada)")

if __name__ == '__main__':
    set_variables()
