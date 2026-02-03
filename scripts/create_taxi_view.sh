#!/bin/bash
# Script para crear la vista de taxi_trips_raw manualmente
# Se ejecuta si Terraform falla por permisos

set -e

PROJECT_ID=${GCP_PROJECT_ID:-$PROJECT_ID}
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID no está configurado"
    exit 1
fi

echo "📊 Creando vista taxi_trips_raw en BigQuery..."

python3 << PYEOF
from google.cloud import bigquery
client = bigquery.Client(project='$PROJECT_ID')
query = '''
CREATE OR REPLACE VIEW \`$PROJECT_ID.chicago_taxi_raw.taxi_trips_raw\` AS
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
FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\`
WHERE DATE(trip_start_timestamp) >= '2023-06-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
'''
try:
    job = client.query(query)
    job.result()
    print('✅ Vista taxi_trips_raw creada exitosamente')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
PYEOF

echo ""
echo "✅ Vista creada. Ahora puedes ejecutar:"
echo "   cd terraform"
echo "   terraform import google_bigquery_table.taxi_trips_raw projects/$PROJECT_ID/datasets/chicago_taxi_raw/tables/taxi_trips_raw"
