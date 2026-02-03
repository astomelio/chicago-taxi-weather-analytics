#!/bin/bash
# Script para preparar el despliegue (crear ZIP, etc.)

set -e

echo "📦 Preparando archivos para despliegue..."

# Crear ZIP de la función
cd functions/weather_ingestion
zip -r ../../terraform/weather-ingestion-source.zip . -x "*.pyc" "__pycache__/*" "*.git*" "*.zip" > /dev/null 2>&1
cd ../..

echo "✅ ZIP creado: terraform/weather-ingestion-source.zip"
echo ""
echo "Ahora puedes ejecutar:"
echo "  cd terraform"
echo "  terraform init"
echo "  terraform plan    # Ver qué se va a crear"
echo "  terraform apply   # Crear todo"
