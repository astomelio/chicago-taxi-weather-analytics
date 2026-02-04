#!/bin/bash
# Script para subir DAGs manualmente a Cloud Composer

set -e

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"
REGION="${GCP_REGION:-us-central1}"
COMPOSER_ENV="chicago-taxi-composer"

echo "🔍 Obteniendo información del entorno de Composer..."
BUCKET=$(gcloud composer environments describe "$COMPOSER_ENV" \
  --location "$REGION" \
  --project "$PROJECT_ID" \
  --format="value(config.dagGcsPrefix)" 2>/dev/null | sed 's|/dags||' || echo "")

if [ -z "$BUCKET" ]; then
  echo "❌ ERROR: No se pudo obtener el bucket de Composer"
  echo "   Verifica que Composer esté creado y funcionando"
  exit 1
fi

echo "✅ Bucket encontrado: $BUCKET"
echo "   Destino: gs://$BUCKET/dags/"
echo ""

# Verificar que los archivos existen
if [ ! -d "airflow/dags" ]; then
  echo "❌ ERROR: Directorio airflow/dags no existe"
  exit 1
fi

# Listar archivos que se van a subir
echo "📋 Archivos DAG encontrados:"
ls -la airflow/dags/*.py || echo "⚠️  No se encontraron archivos .py"
echo ""

# Subir cada archivo .py individualmente
for dag_file in airflow/dags/*.py; do
  if [ -f "$dag_file" ]; then
    filename=$(basename "$dag_file")
    echo "📤 Subiendo $filename..."
    gsutil cp "$dag_file" "gs://$BUCKET/dags/$filename"
    if [ $? -eq 0 ]; then
      echo "   ✅ $filename subido correctamente"
    else
      echo "   ❌ Error subiendo $filename"
      exit 1
    fi
  fi
done

# Subir requirements.txt si existe
if [ -f "airflow/dags/requirements.txt" ]; then
  echo "📤 Subiendo requirements.txt..."
  gsutil cp airflow/dags/requirements.txt "gs://$BUCKET/data/requirements.txt"
  echo "   ✅ requirements.txt subido"
fi

echo ""
echo "✅ Todos los DAGs subidos correctamente"
echo ""
echo "🔍 Verificando DAGs en el bucket:"
gsutil ls "gs://$BUCKET/dags/*.py" || echo "⚠️  No se encontraron DAGs en el bucket"
echo ""
echo "📋 Próximos pasos:"
echo "1. Espera 1-2 minutos para que Airflow detecte los nuevos DAGs"
echo "2. Ve a la UI de Airflow y verifica que los DAGs aparezcan"
echo "3. Si hay errores, revisa los logs de parsing en Airflow"
