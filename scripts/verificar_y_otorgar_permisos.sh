#!/bin/bash
# Script para verificar y otorgar permisos BigQuery al service account de Composer

set -e

PROJECT_ID="brave-computer-454217-q4"
REGION="us-central1"
COMPOSER_ENV="chicago-taxi-composer"

echo "🔍 Verificando y otorgando permisos BigQuery al service account de Composer..."
echo "   Proyecto: $PROJECT_ID"
echo "   Composer: $COMPOSER_ENV"
echo ""

# Obtener el service account de Composer
echo "📋 Paso 1: Obteniendo service account de Composer..."
COMPOSER_SA=$(gcloud composer environments describe "$COMPOSER_ENV" \
  --location "$REGION" \
  --project "$PROJECT_ID" \
  --format="value(config.nodeConfig.serviceAccount)" 2>/dev/null || echo "")

if [ -z "$COMPOSER_SA" ] || [ "$COMPOSER_SA" == "" ]; then
  echo "❌ Error: No se pudo obtener el service account de Composer"
  echo "   Verifica que Composer esté creado y funcionando"
  exit 1
fi

echo "✅ Service Account de Composer: $COMPOSER_SA"
echo ""

# Verificar permisos actuales
echo "📋 Paso 2: Verificando permisos actuales..."
echo "   Roles actuales del service account:"
gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$COMPOSER_SA" \
  --format="table(bindings.role)" || echo "   No se encontraron roles"
echo ""

# Otorgar roles necesarios
echo "📋 Paso 3: Otorgando roles BigQuery necesarios..."
echo "   Estos roles permiten:"
echo "   - Acceder a datasets públicos"
echo "   - Crear y modificar tablas"
echo "   - Ejecutar queries"
echo ""

ROLES=(
  "roles/bigquery.user"
  "roles/bigquery.dataViewer"
  "roles/bigquery.dataEditor"
  "roles/bigquery.jobUser"
)

for ROLE in "${ROLES[@]}"; do
  echo "   🔐 Otorgando $ROLE..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPOSER_SA" \
    --role="$ROLE" \
    --condition=None 2>&1 | grep -v "Updated IAM policy" || echo "   ✅ Rol otorgado (o ya existía)"
done

echo ""
echo "✅ Permisos otorgados"
echo ""

# Esperar propagación
echo "⏳ Esperando propagación de permisos (30 segundos)..."
sleep 30

# Verificar que funciona
echo "📋 Paso 4: Verificando acceso a dataset público..."
echo "   Ejecutando query de prueba..."

bq query --use_legacy_sql=false \
  --project_id="$PROJECT_ID" \
  --location="$REGION" \
  --impersonate-service-account="$COMPOSER_SA" \
  "SELECT COUNT(*) as test FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\` LIMIT 1" \
  2>&1 && {
    echo "✅ ¡Acceso verificado! El service account puede acceder al dataset público"
  } || {
    echo "⚠️  El test falló, pero esto puede ser normal si:"
    echo "   1. Los permisos aún no han propagado (espera 2-5 minutos)"
    echo "   2. El acceso al dataset público no está activado (ejecuta query manualmente)"
    echo ""
    echo "   Para activar acceso al dataset público:"
    echo "   1. Ve a: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
    echo "   2. Ejecuta: SELECT COUNT(*) FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\` LIMIT 1"
  }

echo ""
echo "📋 Resumen:"
echo "   Service Account: $COMPOSER_SA"
echo "   Roles otorgados:"
for ROLE in "${ROLES[@]}"; do
  echo "     - $ROLE"
done
echo ""
echo "✅ Proceso completado"
echo ""
echo "💡 Si aún falla, espera 2-5 minutos para propagación de permisos"
echo "   y luego vuelve a ejecutar el DAG en Airflow"
