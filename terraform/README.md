# Terraform Infrastructure

Este directorio contiene la infraestructura como código para el proyecto Chicago Taxi Analysis.

## Estructura

- `main.tf`: Recursos principales (BigQuery, Cloud Functions, Cloud Scheduler)
- `variables.tf`: Variables de entrada
- `outputs.tf`: Valores de salida
- `terraform.tfvars.example`: Ejemplo de archivo de variables

## Uso

### 1. Configurar Variables

Copiar el archivo de ejemplo y editar con tus valores:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Editar `terraform.tfvars` con:
- `project_id`: Tu proyecto de GCP
- `region`: Región de GCP (default: us-central1)
- `openweather_api_key`: Tu API key de OpenWeatherMap
- `developer_email`: Tu email para column-level security

### 2. Inicializar Terraform

```bash
terraform init
```

### 3. Revisar Plan

```bash
terraform plan
```

### 4. Aplicar Cambios

```bash
terraform apply
```

### 5. Destruir Recursos (si es necesario)

```bash
terraform destroy
```

## Recursos Creados

- **BigQuery Datasets**: 
  - `chicago_taxi_raw`: Datos sin procesar
  - `chicago_taxi_silver`: Datos limpios
  - `chicago_taxi_gold`: Datos analíticos

- **Cloud Function**: `weather-ingestion`
  - Ejecuta diariamente para ingerir datos del clima
  - Puede ejecutarse manualmente para ingesta histórica

- **Cloud Scheduler**: `weather-ingestion-daily`
  - Ejecuta la función diariamente a las 2 AM UTC

- **Service Account**: `weather-ingestion-sa`
  - Permisos necesarios para escribir en BigQuery

## Notas

- Asegúrate de tener los permisos necesarios en GCP
- El proyecto debe tener las APIs habilitadas:
  - BigQuery API
  - Cloud Functions API
  - Cloud Scheduler API
  - Cloud Storage API
