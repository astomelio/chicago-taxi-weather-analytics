# Airflow Pipeline para Chicago Taxi Analysis

Este directorio contiene los DAGs de Airflow para orquestar el pipeline de datos.

## Estructura

```
airflow/
├── dags/
│   ├── chicago_taxi_pipeline.py    # DAG principal
│   └── requirements.txt            # Dependencias Python
└── README.md
```

## DAGs

### 1. `chicago_taxi_historical_ingestion`
**Propósito**: Ingesta histórica de datos (ejecutar una vez)

**Tareas**:
1. Verifica si ya existen datos históricos
2. Trigger Cloud Function para ingesta histórica de clima
3. Crea tabla `taxi_trips_silver` desde dataset público
4. Ejecuta dbt modelos silver
5. Ejecuta dbt modelos gold

**Trigger**: Manual (una sola vez)

### 2. `chicago_taxi_daily_pipeline`
**Propósito**: Pipeline diario de actualización

**Tareas**:
1. Trigger Cloud Function para ingesta diaria de clima
2. Ejecuta dbt para actualizar tablas silver y gold

**Schedule**: Diario a las 2 AM UTC

## Configuración en Cloud Composer

### 1. Subir DAGs a Cloud Composer

```bash
# Copiar DAGs al bucket de Composer
gsutil cp -r airflow/dags/* gs://[COMPOSER_BUCKET]/dags/

# Copiar dbt al bucket
gsutil cp -r dbt/* gs://[COMPOSER_BUCKET]/dags/dbt/
```

### 2. Instalar dependencias Python

En Cloud Composer, ir a:
- Environment > PyPI packages
- Agregar: `apache-airflow-providers-google`, `dbt-bigquery`, `google-cloud-bigquery`

### 3. Configurar Variables de Airflow

En Airflow UI > Admin > Variables:
- `GCP_PROJECT_ID`: Tu proyecto de GCP
- `GCP_REGION`: Región (ej: us-central1)

### 4. Configurar dbt profiles

El archivo `dbt/profiles.yml` debe estar en `/home/airflow/gcs/dags/dbt/` con:

```yaml
chicago_taxi_analysis:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: /home/airflow/gcs/dags/service-account-key.json
      project: "{{ env_var('GCP_PROJECT_ID') }}"
      dataset: chicago_taxi_silver
      location: us-central1
      threads: 4
      timeout_seconds: 300
      priority: interactive
      maximum_bytes_billed: 1000000000
```

## Ejecución

### Primera vez (Ingesta Histórica)

1. En Airflow UI, encontrar DAG `chicago_taxi_historical_ingestion`
2. Hacer click en "Trigger DAG"
3. Monitorear ejecución

### Pipeline Diario

Se ejecuta automáticamente todos los días a las 2 AM UTC.

## Ventajas sobre GitHub Actions

✅ **Orquestación adecuada**: Airflow está diseñado para pipelines de datos
✅ **Retries automáticos**: Manejo robusto de errores
✅ **Monitoreo**: UI completa para visualizar ejecuciones
✅ **Scheduling**: Programación nativa de tareas
✅ **Dependencias**: Gestión clara de dependencias entre tareas
✅ **Escalabilidad**: Puede manejar pipelines complejos
✅ **Acceso a datasets públicos**: Airflow usa credenciales de usuario, no service account
