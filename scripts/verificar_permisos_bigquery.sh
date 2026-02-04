#!/bin/bash
# Script para verificar y otorgar permisos necesarios para acceder a datasets públicos

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)

echo "======================================================================"
echo "  VERIFICACIÓN Y CONFIGURACIÓN DE PERMISOS BIGQUERY"
echo "======================================================================"
echo "Proyecto: $PROJECT_ID"
echo "Usuario: $USER_EMAIL"
echo ""

if [ -z "$USER_EMAIL" ]; then
    echo "❌ ERROR: No hay usuario autenticado en gcloud"
    echo ""
    echo "Autentícate con:"
    echo "  gcloud auth login"
    exit 1
fi

echo "🔍 Verificando permisos del usuario en el proyecto..."
echo ""

# Verificar si el usuario tiene roles de BigQuery
echo "📋 Roles actuales del usuario:"
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:$USER_EMAIL" \
    --format="table(bindings.role)" 2>/dev/null | grep -i bigquery || echo "   No se encontraron roles de BigQuery"

echo ""
echo "🔐 Otorgando roles necesarios de BigQuery..."

# Otorgar roles necesarios
for ROLE in "roles/bigquery.user" "roles/bigquery.jobUser" "roles/bigquery.dataViewer" "roles/bigquery.dataEditor"; do
    echo "   Otorgando: $ROLE"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="user:$USER_EMAIL" \
        --role="$ROLE" \
        --condition=None 2>&1 | grep -v "Updated IAM policy" || echo "   ✅ $ROLE otorgado (o ya existía)"
done

echo ""
echo "⏳ Esperando propagación de permisos (5 segundos)..."
sleep 5

echo ""
echo "✅ Permisos configurados"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "   PRÓXIMOS PASOS:"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "1. Ve a BigQuery Console:"
echo "   https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo ""
echo "2. Ejecuta esta query de activación:"
echo "   SELECT COUNT(*) as test"
echo "   FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\`"
echo "   WHERE DATE(trip_start_timestamp) >= '2023-06-01'"
echo "     AND DATE(trip_start_timestamp) <= '2023-12-31'"
echo ""
echo "3. Si funciona, ejecuta la query completa para cargar los datos"
echo ""
