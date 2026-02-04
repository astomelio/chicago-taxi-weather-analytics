#!/bin/bash
# Script para cargar datos históricos de taxis directamente en BigQuery
# Usa gcloud/bq en lugar de Python para evitar dependencias

set -e

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"
REGION="us-central1"
DATASET="chicago_taxi_raw"
TABLE="taxi_trips_raw_table"
TABLE_ID="${PROJECT_ID}.${DATASET}.${TABLE}"

echo "======================================================================"
echo "  CARGA DE DATOS HISTÓRICOS - CHICAGO TAXI TRIPS"
echo "======================================================================"
echo "Proyecto: $PROJECT_ID"
echo "Dataset: $DATASET"
echo "Tabla: $TABLE"
echo ""

# Verificar si bq está disponible
if ! command -v bq &> /dev/null; then
    echo "❌ ERROR: bq (BigQuery CLI) no está instalado."
    echo ""
    echo "Instálalo con:"
    echo "  gcloud components install bq"
    echo ""
    exit 1
fi

# Verificar si la tabla ya existe y tiene datos
echo "🔍 Verificando si la tabla ya existe..."
EXISTS=$(bq query --use_legacy_sql=false --project_id="$PROJECT_ID" --location="$REGION" \
    --format=csv --max_rows=1 \
    "SELECT COUNT(*) as cnt FROM \`${TABLE_ID}\`" 2>&1 || echo "NOT_FOUND")

if echo "$EXISTS" | grep -q "NOT_FOUND\|not found\|does not exist"; then
    echo "📋 Tabla no existe. Creándola y cargando datos..."
    SKIP_LOAD=false
elif echo "$EXISTS" | grep -q "^cnt$"; then
    # La query funcionó, obtener el count
    COUNT=$(echo "$EXISTS" | tail -n 1)
    if [ "$COUNT" -gt 0 ]; then
        echo "✅ Tabla ya existe con $COUNT registros. Saltando carga."
        exit 0
    else
        echo "⚠️  Tabla existe pero está vacía. Cargando datos..."
        SKIP_LOAD=false
    fi
else
    # Intentar obtener el count de otra forma
    COUNT_QUERY="SELECT COUNT(*) as cnt FROM \`${TABLE_ID}\`"
    COUNT_RESULT=$(bq query --use_legacy_sql=false --project_id="$PROJECT_ID" --location="$REGION" \
        --format=csv --max_rows=1 "$COUNT_QUERY" 2>&1)
    
    if echo "$COUNT_RESULT" | grep -q "^cnt"; then
        COUNT=$(echo "$COUNT_RESULT" | tail -n 1)
        if [ "$COUNT" -gt 0 ]; then
            echo "✅ Tabla ya existe con $COUNT registros. Saltando carga."
            exit 0
        fi
    fi
    SKIP_LOAD=false
fi

if [ "$SKIP_LOAD" = false ]; then
    echo ""
    echo "🔄 Cargando datos históricos de taxis..."
    echo "   Esto puede tardar 10-20 minutos..."
    echo ""
    
    # Query para cargar datos históricos
    LOAD_QUERY="
    CREATE OR REPLACE TABLE \`${TABLE_ID}\`
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
    FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\`
    WHERE DATE(trip_start_timestamp) >= '2023-06-01'
      AND DATE(trip_start_timestamp) <= '2023-12-31'
      AND trip_start_timestamp IS NOT NULL
      AND trip_seconds IS NOT NULL
      AND trip_seconds > 0
      AND trip_miles >= 0
    "
    
    # Ejecutar la query con prioridad BATCH para reducir costos
    echo "Ejecutando query (prioridad BATCH)..."
    bq query \
        --use_legacy_sql=false \
        --project_id="$PROJECT_ID" \
        --location="$REGION" \
        --priority=BATCH \
        --max_rows=0 \
        "$LOAD_QUERY"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Query ejecutada exitosamente"
        echo ""
        echo "🔍 Verificando datos cargados..."
        
        # Verificar el count final
        COUNT_RESULT=$(bq query --use_legacy_sql=false --project_id="$PROJECT_ID" --location="$REGION" \
            --format=csv --max_rows=1 \
            "SELECT COUNT(*) as cnt FROM \`${TABLE_ID}\`" 2>&1)
        
        if echo "$COUNT_RESULT" | grep -q "^cnt"; then
            COUNT=$(echo "$COUNT_RESULT" | tail -n 1)
            echo "✅ Datos históricos cargados exitosamente: $COUNT registros"
        else
            echo "⚠️  Query completada pero no se pudo verificar el count"
            echo "   Resultado: $COUNT_RESULT"
        fi
    else
        echo ""
        echo "❌ ERROR: La query falló"
        echo ""
        echo "═══════════════════════════════════════════════════════════════════════"
        echo "   POSIBLE SOLUCIÓN:"
        echo "═══════════════════════════════════════════════════════════════════════"
        echo ""
        echo "Si el error es de permisos, ejecuta esta query en BigQuery Console:"
        echo "  https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
        echo ""
        echo "  SELECT COUNT(*) as test"
        echo "  FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\`"
        echo "  WHERE DATE(trip_start_timestamp) >= '2023-06-01'"
        echo "    AND DATE(trip_start_timestamp) <= '2023-12-31'"
        echo ""
        exit 1
    fi
fi

echo ""
echo "✅ Proceso completado exitosamente"
echo ""
echo "Próximos pasos:"
echo "  1. Ejecuta el DAG histórico en Airflow para cargar datos de clima"
echo "  2. Ejecuta dbt para crear las capas silver y gold"
