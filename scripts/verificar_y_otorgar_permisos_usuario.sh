#!/bin/bash
# Script para verificar y otorgar permisos BigQuery al usuario actual

set -e

PROJECT_ID="brave-computer-454217-q4"

echo "🔍 Verificando usuario actual..."
USER_EMAIL=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)

if [ -z "$USER_EMAIL" ]; then
  echo "❌ No se encontró usuario autenticado"
  echo "   Ejecuta: gcloud auth login"
  exit 1
fi

echo "✅ Usuario: $USER_EMAIL"
echo ""

echo "🔍 Verificando permisos actuales..."
CURRENT_ROLES=$(gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$USER_EMAIL" \
  --format="value(bindings.role)" 2>/dev/null || echo "")

if [ -n "$CURRENT_ROLES" ]; then
  echo "   Roles actuales:"
  echo "$CURRENT_ROLES" | while read role; do
    echo "     - $role"
  done
else
  echo "   ⚠️  No se encontraron roles asignados"
fi

echo ""
echo "🔐 Otorgando permisos BigQuery necesarios..."

ROLES=(
  "roles/bigquery.user"
  "roles/bigquery.dataEditor"
  "roles/bigquery.dataViewer"
  "roles/bigquery.jobUser"
)

for ROLE in "${ROLES[@]}"; do
  echo "   Otorgando $ROLE..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="user:$USER_EMAIL" \
    --role="$ROLE" \
    --condition=None 2>&1 | grep -v "Updated IAM policy" || echo "     ✅ Rol otorgado (o ya existía)"
done

echo ""
echo "✅ Permisos otorgados"
echo ""
echo "🧪 Verificando acceso a BigQuery..."
echo "   Intentando crear un dataset de prueba..."

# Verificar que el dataset raw existe
bq show "$PROJECT_ID:chicago_taxi_raw" 2>&1 | head -3 || {
  echo "   ⚠️  Dataset chicago_taxi_raw no existe"
  echo "   Creándolo..."
  bq mk --dataset --location=us-central1 "$PROJECT_ID:chicago_taxi_raw" || echo "   ⚠️  Error creando dataset"
}

echo ""
echo "✅ Verificación completada"
echo ""
echo "📋 Ahora deberías poder:"
echo "   1. Crear tablas en BigQuery Console"
echo "   2. Ejecutar queries contra datasets públicos"
echo "   3. Cargar datos manualmente"
echo ""
echo "💡 Prueba ejecutando el CREATE TABLE desde BigQuery Console ahora"
