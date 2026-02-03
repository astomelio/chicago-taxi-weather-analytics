#!/bin/bash

# Script para ejecutar la ingesta histórica de datos del clima
# Esto puede ejecutarse localmente o como Cloud Function

set -e

echo "🌤️  Iniciando ingesta histórica de datos del clima..."

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

# Ejecutar la función localmente
cd functions/weather_ingestion

python main.py --historical

echo "✅ Ingesta histórica completada!"
