#!/bin/bash
# Script para configurar secrets de GitHub usando GitHub CLI

set -e

REPO="astomelio/prueba_orbidi"

echo "🔐 Configurando secrets para: $REPO"
echo ""

# Verificar autenticación
if ! gh auth status &>/dev/null; then
    echo "❌ No estás autenticado en GitHub CLI"
    echo "   Ejecuta: gh auth login"
    exit 1
fi

# Verificar que existe el key file
if [ ! -f "github-actions-key.json" ]; then
    echo "❌ No se encuentra github-actions-key.json"
    exit 1
fi

# Configurar GCP_SA_KEY
echo "📝 Configurando GCP_SA_KEY..."
cat github-actions-key.json | gh secret set GCP_SA_KEY --repo "$REPO"
echo "   ✅ GCP_SA_KEY configurado"

# Configurar GCP_PROJECT_ID
echo "📝 Configurando GCP_PROJECT_ID..."
echo "brave-computer-454217-q4" | gh secret set GCP_PROJECT_ID --repo "$REPO"
echo "   ✅ GCP_PROJECT_ID configurado"

# Configurar DEVELOPER_EMAIL
echo "📝 Configurando DEVELOPER_EMAIL..."
echo "canopolaniajoaquin@gmail.com" | gh secret set DEVELOPER_EMAIL --repo "$REPO"
echo "   ✅ DEVELOPER_EMAIL configurado"

echo ""
echo "✅ TODOS LOS SECRETS CONFIGURADOS"
echo ""

# Verificar secrets
echo "📋 Secrets configurados:"
gh secret list --repo "$REPO"

echo ""
echo "🔄 Ejecutando workflow..."
gh workflow run "CD Pipeline - Deploy Infrastructure.yml" --repo "$REPO" 2>&1 || \
gh workflow run "cd.yml" --repo "$REPO" 2>&1 || {
    echo "⚠️  No se pudo ejecutar automáticamente"
    echo "   Ejecuta manualmente desde: https://github.com/$REPO/actions"
}

echo ""
echo "📊 Ver progreso en:"
echo "   https://github.com/$REPO/actions"
echo ""
echo "⏳ Espera 15-20 minutos para que el workflow cree las tablas gold"
