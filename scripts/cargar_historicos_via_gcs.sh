#!/bin/bash
set -euo pipefail

PROJECT_ID="${1:-chicago-taxi-48702}"
REGION="${2:-us-central1}"
BUCKET="gs://${PROJECT_ID}-taxi-export"
EXT_TABLE="${PROJECT_ID}:chicago_taxi_raw.taxi_trips_ext"
TARGET_TABLE="${PROJECT_ID}:chicago_taxi_raw.taxi_trips_raw_table"

export PATH="/Users/joaquincano/google-cloud-sdk/bin:$PATH"

echo "🪣 Creando bucket de export (si no existe): $BUCKET"
gsutil mb -p "$PROJECT_ID" -l "$REGION" "$BUCKET" 2>/dev/null || echo "   (bucket ya existe)"

echo "🔄 Exportando tabla pública a GCS (PARQUET)..."
PYTHONPATH="" /Users/joaquincano/google-cloud-sdk/bin/bq extract \
  --project_id="$PROJECT_ID" \
  --compression=GZIP \
  --destination_format=PARQUET \
  --location=US \
  "bigquery-public-data:chicago_taxi_trips.taxi_trips" \
  "$BUCKET/taxi_trips_*.parquet"

echo "🔧 Creando tabla externa sobre GCS..."
PYTHONPATH="" /Users/joaquincano/google-cloud-sdk/bin/bq mk \
  --location="$REGION" \
  --external_table_definition="PARQUET=$BUCKET/taxi_trips_*.parquet" \
  "$EXT_TABLE" || echo "   (tabla externa ya existe)"

echo "🔄 Cargando datos 2023 desde la tabla externa..."
PYTHONPATH="" /Users/joaquincano/google-cloud-sdk/bin/bq query \
  --use_legacy_sql=false \
  --project_id="$PROJECT_ID" \
  --location="$REGION" \
  --priority=BATCH \
  "INSERT INTO \`${PROJECT_ID}.chicago_taxi_raw.taxi_trips_raw_table\`
   SELECT unique_key, taxi_id, trip_start_timestamp, trip_end_timestamp, trip_seconds, trip_miles,
          CAST(pickup_census_tract AS STRING), CAST(dropoff_census_tract AS STRING),
          pickup_community_area, dropoff_community_area, fare, tips, tolls, extras, trip_total,
          payment_type, company, pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude
   FROM \`${PROJECT_ID}.chicago_taxi_raw.taxi_trips_ext\`
   WHERE DATE(trip_start_timestamp) >= '2023-06-01'
     AND DATE(trip_start_timestamp) <= '2023-12-31'
     AND trip_start_timestamp IS NOT NULL
     AND trip_seconds IS NOT NULL
     AND trip_seconds > 0
     AND trip_miles >= 0"

echo "✅ Verificando carga..."
PYTHONPATH="" /Users/joaquincano/google-cloud-sdk/bin/bq query \
  --use_legacy_sql=false \
  --project_id="$PROJECT_ID" \
  --location="$REGION" \
  "SELECT COUNT(*) as total, MIN(DATE(trip_start_timestamp)) as min_date, MAX(DATE(trip_start_timestamp)) as max_date
   FROM \`${PROJECT_ID}.chicago_taxi_raw.taxi_trips_raw_table\`"
