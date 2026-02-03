"""
Script para crear dashboard de Looker Studio automáticamente.

Looker Studio no tiene una API pública completa para crear dashboards,
pero podemos:
1. Crear la fuente de datos automáticamente
2. Generar un template JSON del dashboard
3. Proporcionar instrucciones para importarlo

Alternativa: Usar Looker Studio Data API para crear la fuente de datos
y luego usar un template pre-configurado.
"""

import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuración
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "brave-computer-454217-q4")
DATASET_ID = "chicago_taxi_gold"
TABLE_ID = "daily_summary"

def create_looker_data_source():
    """
    Crea una fuente de datos en Looker Studio usando la Data API.
    Nota: Requiere permisos específicos y puede no estar disponible en todos los proyectos.
    """
    try:
        # Intentar usar Looker Studio Data API
        # Nota: Esta API puede requerir configuración adicional
        service = build('datastudio', 'v1')
        
        # Crear fuente de datos
        data_source = {
            'name': 'Chicago Taxi Weather Analysis',
            'type': 'BIGQUERY',
            'dataSourceParameters': {
                'projectId': PROJECT_ID,
                'datasetId': DATASET_ID,
                'tableId': TABLE_ID
            }
        }
        
        # Intentar crear (puede fallar si la API no está habilitada)
        result = service.dataSources().create(body=data_source).execute()
        print(f"✅ Fuente de datos creada: {result.get('dataSourceId')}")
        return result.get('dataSourceId')
        
    except HttpError as e:
        print(f"⚠️  No se pudo crear fuente de datos automáticamente: {e}")
        print("   Esto es normal - Looker Studio requiere configuración manual")
        return None
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def generate_dashboard_template():
    """
    Genera un template JSON del dashboard que se puede importar manualmente.
    """
    template = {
        "version": "1.0",
        "dataSources": [
            {
                "name": "Chicago Taxi Weather Analysis",
                "type": "BIGQUERY",
                "projectId": PROJECT_ID,
                "datasetId": DATASET_ID,
                "tableId": TABLE_ID
            }
        ],
        "charts": [
            {
                "type": "SCORE_CARD",
                "title": "Total de Viajes",
                "metric": "total_trips",
                "aggregation": "SUM"
            },
            {
                "type": "SCORE_CARD",
                "title": "Duración Promedio",
                "metric": "avg_trip_duration_seconds",
                "aggregation": "AVG",
                "format": "DURATION"
            },
            {
                "type": "TIME_SERIES",
                "title": "Evolución de Viajes",
                "dimension": "date",
                "metric": "total_trips",
                "aggregation": "SUM"
            },
            {
                "type": "BAR_CHART",
                "title": "Viajes por Condición Climática",
                "dimension": "weather_category",
                "metric": "total_trips",
                "aggregation": "SUM"
            }
        ],
        "filters": [
            {
                "field": "date",
                "type": "DATE_RANGE"
            },
            {
                "field": "weather_category",
                "type": "MULTI_SELECT"
            }
        ]
    }
    
    return template

def create_dashboard_instructions():
    """
    Genera instrucciones para crear el dashboard manualmente.
    """
    instructions = f"""
# Instrucciones para Crear Dashboard en Looker Studio

## Opción 1: Usar Template (Recomendado)

1. Ve a: https://lookerstudio.google.com/
2. Click en "Create" > "Report"
3. Click en "Use template" (si está disponible)
4. Importa el archivo: `looker_dashboard_template.json`

## Opción 2: Crear Manualmente

1. Ve a: https://lookerstudio.google.com/
2. Click en "Create" > "Report"
3. Click en "Add data" > "BigQuery"
4. Selecciona:
   - Proyecto: {PROJECT_ID}
   - Dataset: {DATASET_ID}
   - Tabla: {TABLE_ID}
5. Click en "Add"

## Opción 3: Usar Looker Studio Community Connector

Si tienes acceso a Looker Studio Data API, puedes usar el script:
```bash
python scripts/create_looker_dashboard.py
```

## Nota Importante

Looker Studio no tiene una API pública completa para crear dashboards automáticamente.
La mejor opción es:
1. Crear un template del dashboard
2. Compartirlo como plantilla
3. O usar las instrucciones en CREAR_DASHBOARD.md
"""
    return instructions

def main():
    print("=" * 70)
    print("🎨 CREACIÓN AUTOMÁTICA DE DASHBOARD LOOKER STUDIO")
    print("=" * 70)
    
    # Intentar crear fuente de datos
    print("\n1️⃣  Intentando crear fuente de datos...")
    data_source_id = create_looker_data_source()
    
    # Generar template
    print("\n2️⃣  Generando template del dashboard...")
    template = generate_dashboard_template()
    
    # Guardar template
    template_file = "looker_dashboard_template.json"
    with open(template_file, 'w') as f:
        json.dump(template, f, indent=2)
    print(f"   ✅ Template guardado en: {template_file}")
    
    # Generar instrucciones
    print("\n3️⃣  Generando instrucciones...")
    instructions = create_dashboard_instructions()
    with open("LOOKER_DASHBOARD_INSTRUCTIONS.md", 'w') as f:
        f.write(instructions)
    print("   ✅ Instrucciones guardadas en: LOOKER_DASHBOARD_INSTRUCTIONS.md")
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print("\n📖 Siguiente paso:")
    print("   - Revisa LOOKER_DASHBOARD_INSTRUCTIONS.md")
    print("   - O sigue CREAR_DASHBOARD.md para crear el dashboard manualmente")
    print("\n⚠️  Nota: Looker Studio requiere creación manual del dashboard")
    print("   pero el template y las instrucciones están listos.")

if __name__ == "__main__":
    main()
