#!/bin/bash

# Script para desplegar la Cloud Function de ingesta de datos del clima

set -e

echo "🚀 Desplegando Cloud Function para ingesta de datos del clima..."

# Verificar variables de entorno
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID no está configurado"
    exit 1
fi

if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "⚠️  Advertencia: OPENWEATHER_API_KEY no está configurada"
    echo "   El sistema usará BigQuery público (NOAA) como fuente principal"
    echo "   La API key solo se necesita como fallback si BigQuery no tiene datos"
fi

# Obtener el bucket de Terraform output o usar uno por defecto
BUCKET_NAME="${GCP_PROJECT_ID}-function-source"
FUNCTION_NAME="weather-ingestion"
REGION="${GCP_REGION:-us-central1}"

# Crear directorio temporal para el código
TEMP_DIR=$(mktemp -d)
echo "📦 Empaquetando código en $TEMP_DIR"

# Copiar código de la función
cp -r functions/weather_ingestion/* "$TEMP_DIR/"

# Instalar dependencias
cd "$TEMP_DIR"
pip install -r requirements.txt -t .

# Crear archivo ZIP
zip -r function-source.zip . -x "*.pyc" "__pycache__/*" "*.git*"

# Subir a Cloud Storage
echo "📤 Subiendo código a Cloud Storage..."
gsutil cp function-source.zip "gs://${BUCKET_NAME}/weather-ingestion-source.zip"

# Limpiar
cd -
rm -rf "$TEMP_DIR"

echo "✅ Código subido exitosamente"
echo ""
echo "Ahora ejecuta 'terraform apply' para actualizar la Cloud Function con el nuevo código"
