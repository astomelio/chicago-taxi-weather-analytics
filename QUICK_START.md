# Quick Start Guide

Esta guía te ayudará a poner en marcha el proyecto rápidamente.

## Pasos Rápidos

### 1. Prerequisitos

Asegúrate de tener instalado:
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- [dbt](https://docs.getdbt.com/docs/get-started/installation) >= 1.0
- [Python](https://www.python.org/downloads/) >= 3.9
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- Cuenta de GCP con proyecto activo
- API key de [OpenWeatherMap](https://openweathermap.org/api)

### 2. Configurar Variables

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores
export GCP_PROJECT_ID="tu-proyecto-gcp"
export OPENWEATHER_API_KEY="tu-api-key"
export DEVELOPER_EMAIL="tu-email@example.com"
```

### 3. Configurar GCP

```bash
# Autenticarse en GCP
gcloud auth login
gcloud config set project $GCP_PROJECT_ID

# Habilitar APIs necesarias
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable storage.googleapis.com
```

### 4. Crear Service Account

```bash
# Crear service account
gcloud iam service-accounts create dbt-service-account \
    --display-name="dbt Service Account"

# Asignar roles
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:dbt-service-account@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:dbt-service-account@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Crear y descargar key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=dbt-service-account@$GCP_PROJECT_ID.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
```

### 5. Desplegar Infraestructura

```bash
cd terraform

# Copiar y editar variables
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores

# Inicializar Terraform
terraform init

# Revisar plan
terraform plan

# Aplicar
terraform apply
```

### 6. Desplegar Cloud Function

```bash
# Ejecutar script de deployment
./scripts/deploy_function.sh

# Aplicar Terraform nuevamente para actualizar la función
cd terraform
terraform apply
```

### 7. Ingestar Datos Históricos del Clima

```bash
# Opción 1: Ejecutar localmente
python functions/weather_ingestion/main.py --historical

# Opción 2: Ejecutar Cloud Function manualmente
gcloud functions call weather-ingestion \
    --data '{"historical": true}' \
    --region us-central1
```

### 8. Ejecutar Transformaciones dbt

```bash
cd dbt

# Instalar dependencias
dbt deps

# Ejecutar modelos Silver
dbt run --models silver

# Ejecutar modelos Gold
dbt run --models gold

# Ejecutar tests
dbt test
```

### 9. Crear Dashboard

Sigue las instrucciones en [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) para crear el dashboard en Looker Studio.

### 10. Compartir Dashboard

1. Abrir el dashboard en Looker Studio
2. Clic en "Compartir"
3. Agregar:
   - alejandro@astrafy.io
   - felipe.bereilh@orbidi.com
4. Copiar el link y agregarlo al README.md

## Verificación

Para verificar que todo funciona:

```bash
# Verificar datos en BigQuery
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`$GCP_PROJECT_ID.chicago_taxi_raw.weather_data\`"

# Verificar modelos dbt
cd dbt
dbt test
```

## Troubleshooting

### Error: "Permission denied"
- Verifica que el service account tenga los permisos correctos
- Verifica que las APIs estén habilitadas

### Error: "API key invalid"
- Verifica que tu API key de OpenWeatherMap sea válida
- Asegúrate de tener un plan que permita acceso histórico

### Error: "Dataset not found"
- Ejecuta `terraform apply` para crear los datasets
- Verifica que el proyecto de GCP sea correcto

## Siguiente Paso

Una vez que todo esté funcionando, puedes:
1. Revisar los datos en BigQuery
2. Crear visualizaciones adicionales
3. Agregar más análisis o métricas
4. Configurar alertas para el pipeline
