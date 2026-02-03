#!/bin/bash
# Script para configurar credenciales de GCP

set -e

echo "============================================================"
echo "🔐 CONFIGURACIÓN DE CREDENCIALES DE GOOGLE CLOUD"
echo "============================================================"
echo ""

# Verificar si gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI no está instalado"
    echo ""
    echo "📥 Instalación:"
    echo "   1. macOS: brew install google-cloud-sdk"
    echo "   2. O descarga desde: https://cloud.google.com/sdk/docs/install"
    echo ""
    exit 1
fi

echo "✅ gcloud CLI encontrado"
echo ""

# Verificar si ya está autenticado
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "✅ Ya estás autenticado en GCP:"
    gcloud auth list --filter=status:ACTIVE --format="value(account)" | sed 's/^/   - /'
    echo ""
    read -p "¿Quieres usar esta cuenta? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Iniciando nuevo login..."
        gcloud auth login
    fi
else
    echo "🔑 Iniciando autenticación..."
    gcloud auth login
fi

echo ""
echo "📋 Configurando Application Default Credentials (ADC)..."
echo "   (Necesario para que Python pueda acceder a BigQuery)"
echo ""

gcloud auth application-default login

echo ""
echo "✅ Credenciales configuradas"
echo ""

# Verificar proyecto
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$CURRENT_PROJECT" ]; then
    echo "⚠️  No hay proyecto configurado"
    echo ""
    echo "📝 Lista de proyectos disponibles:"
    gcloud projects list --format="table(projectId,name)" 2>/dev/null || echo "   (No se pudieron listar proyectos)"
    echo ""
    read -p "Ingresa el PROJECT_ID a usar (o presiona Enter para saltar): " PROJECT_ID
    if [ ! -z "$PROJECT_ID" ]; then
        gcloud config set project "$PROJECT_ID"
        echo "✅ Proyecto configurado: $PROJECT_ID"
        export GCP_PROJECT_ID="$PROJECT_ID"
        export PROJECT_ID="$PROJECT_ID"
    fi
else
    echo "✅ Proyecto actual: $CURRENT_PROJECT"
    export GCP_PROJECT_ID="$CURRENT_PROJECT"
    export PROJECT_ID="$CURRENT_PROJECT"
fi

echo ""
echo "============================================================"
echo "✅ CONFIGURACIÓN COMPLETA"
echo "============================================================"
echo ""
echo "📝 Variables de entorno configuradas:"
echo "   GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo "   PROJECT_ID=$PROJECT_ID"
echo ""
echo "🧪 Ahora puedes probar el sistema:"
echo "   python3 scripts/test_bigquery_direct.py"
echo ""
echo "💡 Para usar estas variables en otra terminal:"
echo "   export GCP_PROJECT_ID='$GCP_PROJECT_ID'"
echo "   export PROJECT_ID='$GCP_PROJECT_ID'"
echo ""
