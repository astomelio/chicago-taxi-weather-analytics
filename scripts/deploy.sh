#!/bin/bash
# Script completo para desplegar toda la infraestructura con Terraform

set -e

echo "============================================================"
echo "🚀 DESPLIEGUE COMPLETO DE INFRAESTRUCTURA"
echo "============================================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "terraform/main.tf" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Verificar variables de entorno
if [ -z "$GCP_PROJECT_ID" ] && [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID o PROJECT_ID no está configurado"
    echo "   export GCP_PROJECT_ID='tu-proyecto-gcp'"
    exit 1
fi

PROJECT_ID=${GCP_PROJECT_ID:-$PROJECT_ID}
echo "✅ Proyecto: $PROJECT_ID"
echo ""

# 1. Crear ZIP de la función
echo "📦 Paso 1/4: Creando ZIP de la Cloud Function..."
cd functions/weather_ingestion
zip -r ../../terraform/weather-ingestion-source.zip . -x "*.pyc" "__pycache__/*" "*.git*" "*.zip" > /dev/null 2>&1
cd ../..
echo "   ✅ ZIP creado: terraform/weather-ingestion-source.zip"
echo ""

# 2. Inicializar Terraform
echo "🔧 Paso 2/4: Inicializando Terraform..."
cd terraform
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
terraform init -upgrade > /dev/null 2>&1
echo "   ✅ Terraform inicializado"
echo ""

# 3. Mostrar plan
echo "📋 Paso 3/4: Generando plan de despliegue..."
echo ""
terraform plan
echo ""

# 4. Aplicar cambios
echo "🚀 Paso 4/4: ¿Aplicar cambios? (s/n)"
read -r response
if [[ "$response" =~ ^[Ss]$ ]]; then
    echo ""
    echo "Aplicando cambios..."
    terraform apply -auto-approve
    echo ""
    echo "============================================================"
    echo "✅ DESPLIEGUE COMPLETADO"
    echo "============================================================"
    echo ""
    terraform output
else
    echo ""
    echo "Despliegue cancelado. Ejecuta 'terraform apply' cuando estés listo."
fi

cd ..
