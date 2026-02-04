#!/bin/bash
# Script para configurar Airflow/Cloud Composer

set -e

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"
REGION="${GCP_REGION:-us-central1}"
COMPOSER_ENV="${COMPOSER_ENV:-chicago-taxi-composer}"

echo "🚀 Configurando Airflow para Chicago Taxi Pipeline"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Composer Env: $COMPOSER_ENV"

# Verificar si Composer está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI no está instalado"
    exit 1
fi

# Obtener bucket de Composer
echo ""
echo "📦 Obteniendo bucket de Composer..."
COMPOSER_BUCKET=$(gcloud composer environments describe $COMPOSER_ENV \
    --location $REGION \
    --project $PROJECT_ID \
    --format="value(config.dagGcsPrefix)" | sed 's|/dags||')

if [ -z "$COMPOSER_BUCKET" ]; then
    echo "❌ No se pudo obtener el bucket de Composer"
    echo "   Asegúrate de que el entorno de Composer existe:"
    echo "   gcloud composer environments create $COMPOSER_ENV --location $REGION"
    exit 1
fi

echo "✅ Bucket encontrado: $COMPOSER_BUCKET"

# Subir DAGs
echo ""
echo "📤 Subiendo DAGs a Composer..."
gsutil -m cp -r airflow/dags/* gs://$COMPOSER_BUCKET/dags/
echo "✅ DAGs subidos"

# Subir dbt
echo ""
echo "📤 Subiendo dbt a Composer..."
gsutil -m cp -r dbt/* gs://$COMPOSER_BUCKET/dags/dbt/
echo "✅ dbt subido"

# Subir service account key (si existe)
if [ -f "github-actions-key.json" ]; then
    echo ""
    echo "📤 Subiendo service account key..."
    gsutil cp github-actions-key.json gs://$COMPOSER_BUCKET/dags/service-account-key.json
    echo "✅ Service account key subido"
else
    echo "⚠️  github-actions-key.json no encontrado. Asegúrate de subirlo manualmente."
fi

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ve a Airflow UI: https://console.cloud.google.com/composer/environments/$COMPOSER_ENV/monitoring?project=$PROJECT_ID"
echo "2. Configura variables en Admin > Variables:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_REGION: $REGION"
echo "3. Trigger el DAG 'chicago_taxi_historical_ingestion' para la primera ejecución"
