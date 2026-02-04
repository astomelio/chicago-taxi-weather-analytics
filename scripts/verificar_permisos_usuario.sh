#!/bin/bash
# Script para verificar los permisos actuales del usuario en el proyecto

PROJECT_ID="${GCP_PROJECT_ID:-brave-computer-454217-q4}"

echo "======================================================================"
echo "  VERIFICAR PERMISOS DEL USUARIO"
echo "======================================================================"
echo "Proyecto: $PROJECT_ID"
echo ""

# Intentar obtener el email del usuario desde gcloud
USER_EMAIL=$(gcloud config get-value account 2>/dev/null)

if [ -z "$USER_EMAIL" ]; then
    echo "⚠️  No se pudo obtener el email automáticamente"
    echo ""
    echo "Por favor, proporciona tu email:"
    read -p "Email: " USER_EMAIL
fi

if [ -z "$USER_EMAIL" ]; then
    echo "❌ No se proporcionó email"
    exit 1
fi

echo "Usuario: $USER_EMAIL"
echo ""
echo "🔍 Verificando permisos..."
echo ""

# Verificar permisos usando gcloud
gcloud projects get-iam-policy "$PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.members:user:$USER_EMAIL" \
    --format="table(bindings.role)" 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "   VERIFICACIÓN:"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Busca en la lista arriba:"
echo "  ✅ roles/bigquery.dataEditor  → Tienes permisos para crear tablas"
echo "  ✅ roles/bigquery.user         → Tienes permisos básicos"
echo "  ✅ roles/bigquery.jobUser     → Puedes ejecutar jobs"
echo ""
echo "Si NO ves 'roles/bigquery.dataEditor', el cambio no se aplicó."
echo ""
