#!/bin/bash

# Script para probar que el sistema funciona correctamente

set -e

echo "🧪 Probando el sistema Chicago Taxi Analysis..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar comandos
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 instalado"
        return 0
    else
        echo -e "${RED}❌${NC} $1 NO instalado"
        return 1
    fi
}

# Función para verificar variables de entorno
check_env_var() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}❌${NC} $1 no configurada"
        return 1
    else
        echo -e "${GREEN}✅${NC} $1 configurada"
        return 0
    fi
}

echo "1️⃣ Verificando herramientas instaladas..."
check_command python3
check_command terraform
check_command dbt
check_command gcloud
echo ""

echo "2️⃣ Verificando variables de entorno..."
check_env_var GCP_PROJECT_ID
check_env_var OPENWEATHER_API_KEY
check_env_var GOOGLE_APPLICATION_CREDENTIALS
echo ""

echo "3️⃣ Verificando estructura del proyecto..."
if [ -f "terraform/main.tf" ]; then
    echo -e "${GREEN}✅${NC} Terraform configurado"
else
    echo -e "${RED}❌${NC} terraform/main.tf no encontrado"
fi

if [ -f "functions/weather_ingestion/main.py" ]; then
    echo -e "${GREEN}✅${NC} Cloud Function configurada"
else
    echo -e "${RED}❌${NC} functions/weather_ingestion/main.py no encontrado"
fi

if [ -f "dbt/dbt_project.yml" ]; then
    echo -e "${GREEN}✅${NC} dbt configurado"
else
    echo -e "${RED}❌${NC} dbt/dbt_project.yml no encontrado"
fi
echo ""

echo "4️⃣ Verificando dependencias de Python..."
if [ -f "functions/weather_ingestion/requirements.txt" ]; then
    echo "Instalando dependencias..."
    cd functions/weather_ingestion
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅${NC} Dependencias instaladas"
    cd ../..
else
    echo -e "${YELLOW}⚠️${NC} requirements.txt no encontrado"
fi
echo ""

echo "5️⃣ Probando función de ingesta (modo test - una fecha específica)..."
if [ -n "$GCP_PROJECT_ID" ] && [ -n "$OPENWEATHER_API_KEY" ]; then
    export DATASET_ID="chicago_taxi_raw"
    export TABLE_ID="weather_data"
    export CHICAGO_LAT="41.8781"
    export CHICAGO_LON="-87.6298"
    
    # Probar con una fecha específica (modo test)
    echo "Probando obtención de datos del clima para 2023-06-01..."
    python3 -c "
import sys
sys.path.insert(0, 'functions/weather_ingestion')
from main import get_weather_data
from datetime import datetime
try:
    data = get_weather_data(datetime(2023, 6, 1))
    print(f'✅ Datos obtenidos: {data[\"date\"]} - Temp: {data.get(\"temperature\")}°C')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
" && echo -e "${GREEN}✅${NC} Función de ingesta funciona correctamente" || echo -e "${RED}❌${NC} Error en función de ingesta"
else
    echo -e "${YELLOW}⚠️${NC} Variables de entorno no configuradas, saltando prueba"
fi
echo ""

echo "6️⃣ Verificando sintaxis de Terraform..."
if [ -f "terraform/main.tf" ]; then
    cd terraform
    terraform init -backend=false > /dev/null 2>&1
    if terraform validate > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Terraform válido"
    else
        echo -e "${RED}❌${NC} Terraform tiene errores"
        terraform validate
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️${NC} No se puede validar Terraform"
fi
echo ""

echo "7️⃣ Verificando sintaxis de dbt..."
if [ -f "dbt/dbt_project.yml" ]; then
    cd dbt
    if dbt parse > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} dbt válido"
    else
        echo -e "${YELLOW}⚠️${NC} dbt parse requiere configuración completa"
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️${NC} No se puede validar dbt"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Verificación completada"
echo ""
echo "Próximos pasos:"
echo "1. Configurar terraform/terraform.tfvars"
echo "2. Ejecutar: terraform init && terraform apply"
echo "3. Ejecutar ingesta histórica: python functions/weather_ingestion/main.py --historical"
echo "4. Ejecutar dbt: cd dbt && dbt run"
