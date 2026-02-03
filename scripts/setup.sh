#!/bin/bash

# Script de setup para el proyecto Chicago Taxi Analysis
# Este script ayuda a configurar el entorno local

set -e

echo "🚀 Configurando el proyecto Chicago Taxi Analysis..."

# Verificar que las variables de entorno estén configuradas
if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID no está configurado"
    exit 1
fi

if [ -z "$OPENWEATHER_API_KEY" ]; then
    echo "⚠️  Advertencia: OPENWEATHER_API_KEY no está configurado"
    echo "   Necesitarás configurarlo antes de ejecutar la ingesta de datos del clima"
fi

# Crear archivo de variables de Terraform si no existe
if [ ! -f "terraform/terraform.tfvars" ]; then
    echo "📝 Creando terraform.tfvars desde el ejemplo..."
    cp terraform/terraform.tfvars.example terraform/terraform.tfvars
    echo "⚠️  Por favor, edita terraform/terraform.tfvars con tus valores"
fi

# Instalar dependencias de Python
echo "📦 Instalando dependencias de Python..."
if [ -d "functions/weather_ingestion" ]; then
    cd functions/weather_ingestion
    pip install -r requirements.txt
    cd ../..
fi

# Verificar que Terraform esté instalado
if ! command -v terraform &> /dev/null; then
    echo "❌ Error: Terraform no está instalado"
    echo "   Instala Terraform desde https://www.terraform.io/downloads"
    exit 1
fi

# Verificar que dbt esté instalado
if ! command -v dbt &> /dev/null; then
    echo "⚠️  Advertencia: dbt no está instalado"
    echo "   Instala dbt con: pip install dbt-bigquery"
fi

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  Advertencia: gcloud CLI no está instalado"
    echo "   Instala desde https://cloud.google.com/sdk/docs/install"
fi

echo "✅ Setup completado!"
echo ""
echo "Próximos pasos:"
echo "1. Edita terraform/terraform.tfvars con tus valores"
echo "2. Ejecuta 'terraform init' en el directorio terraform/"
echo "3. Ejecuta 'terraform plan' para revisar los cambios"
echo "4. Ejecuta 'terraform apply' para crear la infraestructura"
echo "5. Ejecuta la ingesta histórica de datos del clima"
echo "6. Ejecuta 'dbt run' para crear los modelos de datos"
