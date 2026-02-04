#!/bin/bash
# Diagnóstico completo del problema de permisos BigQuery

set -e

PROJECT_ID="brave-computer-454217-q4"
REGION="us-central1"
COMPOSER_ENV="chicago-taxi-composer"

echo "🔍 DIAGNÓSTICO COMPLETO: Problema de Permisos BigQuery"
echo "═══════════════════════════════════════════════════════"
echo ""

# 1. Obtener service account de Composer
echo "📋 Paso 1: Service Account de Composer"
COMPOSER_SA=$(gcloud composer environments describe "$COMPOSER_ENV" \
  --location "$REGION" \
  --project "$PROJECT_ID" \
  --format="value(config.nodeConfig.serviceAccount)" 2>/dev/null || echo "")

if [ -z "$COMPOSER_SA" ]; then
  echo "❌ No se pudo obtener el service account de Composer"
  exit 1
fi

echo "   Service Account: $COMPOSER_SA"
echo ""

# 2. Verificar permisos actuales
echo "📋 Paso 2: Permisos Actuales del Service Account"
echo "   Verificando roles BigQuery..."
BQ_ROLES=$(gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$COMPOSER_SA" \
  --format="value(bindings.role)" | grep -i bigquery || echo "NINGUNO")

if [ "$BQ_ROLES" == "NINGUNO" ]; then
  echo "   ❌ NO tiene roles BigQuery asignados"
else
  echo "   ✅ Roles encontrados:"
  echo "$BQ_ROLES" | while read role; do
    echo "      - $role"
  done
fi
echo ""

# 3. Verificar billing
echo "📋 Paso 3: Billing del Proyecto"
BILLING=$(gcloud billing projects describe "$PROJECT_ID" \
  --format="value(billingAccountName)" 2>/dev/null || echo "")

if [ -z "$BILLING" ]; then
  echo "   ❌ NO tiene billing habilitado"
  echo "   🔧 Solución: https://console.cloud.google.com/billing?project=$PROJECT_ID"
else
  echo "   ✅ Billing habilitado: $BILLING"
fi
echo ""

# 4. Intentar query con el service account
echo "📋 Paso 4: Test de Acceso al Dataset Público"
echo "   Intentando query con el service account de Composer..."
bq query --use_legacy_sql=false \
  --project_id="$PROJECT_ID" \
  --location="$REGION" \
  --impersonate-service-account="$COMPOSER_SA" \
  "SELECT COUNT(*) as test FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\` LIMIT 1" \
  2>&1 && {
    echo "   ✅ El service account PUEDE acceder al dataset público"
  } || {
    echo "   ❌ El service account NO puede acceder al dataset público"
    echo ""
    echo "   🔧 Posibles causas:"
    echo "      1. Permisos no otorgados (ver Paso 2)"
    echo "      2. Billing no habilitado (ver Paso 3)"
    echo "      3. Acceso al dataset público no activado (requiere usuario ejecutar query)"
    echo ""
    echo "   💡 SOLUCIÓN RÁPIDA:"
    echo "      Ejecuta este script para otorgar permisos:"
    echo "      ./scripts/verificar_y_otorgar_permisos.sh"
  }
echo ""

# 5. Resumen y recomendaciones
echo "📋 RESUMEN Y RECOMENDACIONES"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Service Account: $COMPOSER_SA"
echo ""

if [ "$BQ_ROLES" == "NINGUNO" ]; then
  echo "❌ PROBLEMA: No tiene roles BigQuery"
  echo "   → Ejecuta: ./scripts/verificar_y_otorgar_permisos.sh"
  echo ""
fi

if [ -z "$BILLING" ]; then
  echo "❌ PROBLEMA: No tiene billing"
  echo "   → Habilita billing: https://console.cloud.google.com/billing?project=$PROJECT_ID"
  echo ""
fi

echo "💡 IMPORTANTE:"
echo "   BigQuery requiere que un USUARIO (no service account) ejecute"
echo "   una query contra el dataset público para activar el acceso."
echo ""
echo "   Para activar acceso:"
echo "   1. Ve a: https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo "   2. Ejecuta: SELECT COUNT(*) FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\` LIMIT 1"
echo "   3. Esto activa el acceso para TODO el proyecto (incluyendo service accounts)"
echo ""
