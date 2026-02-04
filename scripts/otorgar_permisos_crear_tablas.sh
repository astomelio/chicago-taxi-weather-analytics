#!/bin/bash
# Script rápido para otorgar permisos de creación de tablas en BigQuery

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)

if [ -z "$USER_EMAIL" ]; then
    echo "❌ ERROR: No hay usuario autenticado"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

echo "🔐 Otorgando permisos para crear tablas en BigQuery..."
echo "Usuario: $USER_EMAIL"
echo "Proyecto: $PROJECT_ID"
echo ""

# Otorgar BigQuery Data Editor (permite crear tablas)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="user:$USER_EMAIL" \
    --role="roles/bigquery.dataEditor" \
    --condition=None 2>&1 | grep -v "Updated IAM policy" || echo "✅ Permisos otorgados (o ya existían)"

echo ""
echo "⏳ Esperando propagación de permisos (10 segundos)..."
sleep 10

echo ""
echo "✅ Permisos configurados. Ahora puedes crear tablas en BigQuery."
echo ""
echo "Intenta ejecutar la query CREATE TABLE de nuevo en BigQuery Console."
