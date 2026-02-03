# Guía para Probar el Sistema

## Paso 1: (Opcional) API Key de Clima

**IMPORTANTE**: El sistema usa **BigQuery público (NOAA)** como fuente principal. **NO necesitas API key** para el período 2023.

La API key solo se necesita como fallback si BigQuery no tiene datos para alguna fecha específica.

Si quieres configurar fallback:
1. Ir a: https://www.visualcrossing.com/weather-api
2. Crear cuenta gratuita
3. Obtener tu API key desde el dashboard

## Paso 2: Configurar Credenciales de Google Cloud

**IMPORTANTE**: Para probar con BigQuery público, necesitas credenciales de GCP.

### Instalar gcloud CLI (si no lo tienes)

```bash
# macOS
brew install google-cloud-sdk

# O descarga desde: https://cloud.google.com/sdk/docs/install
```

### Configurar Credenciales

**Opción A: Script automático (recomendado)**
```bash
./scripts/setup_credentials.sh
```

**Opción B: Manual**
```bash
# Autenticación
gcloud auth login
gcloud auth application-default login

# Configurar proyecto
gcloud config set project TU-PROYECTO-ID
```

**Ver documentación completa**: [CONFIGURAR_CREDENCIALES.md](CONFIGURAR_CREDENCIALES.md)

### Configurar Variables de Entorno

```bash
# GCP Project ID
export GCP_PROJECT_ID="tu-proyecto-gcp"
export PROJECT_ID="tu-proyecto-gcp"

# API Key (OPCIONAL - solo fallback)
export OPENWEATHER_API_KEY="tu-api-key-aqui"  # Solo si quieres fallback
```

## Paso 3: Probar la Función de Ingesta (Sin BigQuery)

```bash
# Probar que la API funciona
python3 scripts/test_weather_api.py
```

Esto prueba que:
- ✅ La API key funciona
- ✅ Puedes obtener datos del clima
- ✅ La función está correcta

## Paso 4: Instalar Dependencias

```bash
cd functions/weather_ingestion
pip install -r requirements.txt
cd ../..
```

## Paso 5: Probar Modo Histórico (Requiere BigQuery configurado)

**Solo si ya tienes BigQuery configurado:**

```bash
export PROJECT_ID="tu-proyecto"
export DATASET_ID="chicago_taxi_raw"
export TABLE_ID="weather_data"

# Probar con una fecha específica primero
python3 -c "
import sys
sys.path.insert(0, 'functions/weather_ingestion')
from main import get_weather_data, insert_weather_data
from google.cloud import bigquery
from datetime import datetime

client = bigquery.Client(project='$PROJECT_ID')
date = datetime(2023, 6, 1)
data = get_weather_data(date)
print(f'Datos obtenidos: {data}')
# insert_weather_data(client, data)  # Descomentar para insertar
"
```

## Paso 6: Desplegar Infraestructura (Terraform)

```bash
# 1. Copiar y editar variables
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores

# 2. Inicializar
terraform init

# 3. Revisar plan
terraform plan

# 4. Aplicar
terraform apply
```

## Paso 7: Ejecutar Ingesta Histórica Completa

```bash
export PROJECT_ID="tu-proyecto"
export DATASET_ID="chicago_taxi_raw"
export TABLE_ID="weather_data"
export OPENWEATHER_API_KEY="tu-api-key"

python3 functions/weather_ingestion/main.py --historical
```

## Paso 8: Ejecutar Transformaciones dbt

```bash
cd dbt
dbt run --models silver
dbt run --models gold
dbt test
```

## Checklist de Pruebas

- [ ] API key configurada y funciona
- [ ] Función de ingesta obtiene datos correctamente
- [ ] Terraform despliega infraestructura
- [ ] Ingesta histórica completa (214 días)
- [ ] Datos aparecen en BigQuery
- [ ] dbt transforma datos correctamente
- [ ] Tablas Gold tienen datos unidos (taxis + clima)

## Troubleshooting

### Error: "API key inválida"
- Verifica que la API key sea correcta
- Asegúrate de que esté activa en Visual Crossing

### Error: "Terraform no encontrado"
- Instalar Terraform: https://www.terraform.io/downloads
- O usar Cloud Shell de GCP (ya tiene Terraform)

### Error: "dbt no encontrado"
- Instalar: `pip install dbt-bigquery`
- O usar Cloud Shell

### Error: "Permission denied" en BigQuery
- Verificar que el service account tenga permisos
- Verificar que las APIs estén habilitadas
