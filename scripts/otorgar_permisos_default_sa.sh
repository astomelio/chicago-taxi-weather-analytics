#!/bin/bash
# Script para otorgar permisos BigQuery al Compute Engine default service account
# Este es el que aparece como "default" en los logs de Airflow

set -e

PROJECT_ID="brave-computer-454217-q4"
PROJECT_NUMBER="802982033562"

echo "🔐 Otorgando permisos BigQuery al Compute Engine default service account..."
echo "   Proyecto: $PROJECT_ID"
echo ""

# Compute Engine default service account (el que aparece como "default")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "📋 Service Account: $COMPUTE_SA"
echo ""

# Roles necesarios
ROLES=(
  "roles/bigquery.user"
  "roles/bigquery.dataViewer"
  "roles/bigquery.dataEditor"
  "roles/bigquery.jobUser"
)

echo "🔐 Otorgando permisos..."
for ROLE in "${ROLES[@]}"; do
  echo "   Otorgando $ROLE..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="$ROLE" \
    --condition=None 2>&1 | grep -v "Updated IAM policy" || echo "     ✅ Rol otorgado (o ya existía)"
done

echo ""
echo "✅ Permisos otorgados"
echo ""
echo "⏳ Espera 2-5 minutos para propagación de permisos"
echo "   Luego ejecuta el DAG de nuevo en Airflow"
