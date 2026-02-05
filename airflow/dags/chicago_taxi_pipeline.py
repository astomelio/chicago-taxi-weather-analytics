"""
DAG principal para el pipeline de análisis de taxis de Chicago.
Orquesta la ingesta de datos, transformaciones dbt y actualizaciones diarias.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import BigQueryToGCSOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.python import PythonOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import os

# Configuración - usar variables de Airflow si están disponibles
from airflow.models import Variable

try:
    PROJECT_ID = Variable.get('GCP_PROJECT_ID', default_var='chicago-taxi-48702')
    REGION = Variable.get('GCP_REGION', default_var='us-central1')
except:
    # Fallback si las variables no están disponibles
    PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'chicago-taxi-48702')
    REGION = os.environ.get('GCP_REGION', 'us-central1')
RAW_DATASET = 'chicago_taxi_raw'
SILVER_DATASET = 'chicago_taxi_silver'
GOLD_DATASET = 'chicago_taxi_gold'

default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
    'pool': None,  # No usar pool por defecto
}

# DAG para ingesta histórica (ejecutar una vez)
historical_dag = DAG(
    'chicago_taxi_historical_ingestion',
    default_args=default_args,
    description='Ingesta histórica de datos de taxis y clima',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['historical', 'one-time'],
)

# DAG para pipeline diario
daily_dag = DAG(
    'chicago_taxi_daily_pipeline',
    default_args=default_args,
    description='Pipeline diario: ingesta de clima y transformaciones dbt',
    schedule_interval='0 2 * * *',  # Diario a las 2 AM UTC
    catchup=False,
    tags=['daily', 'production'],
)

def check_historical_data_exists(**context):
    """Verifica si ya existen datos históricos para evitar re-procesamiento."""
    print(f"🔍 Verificando datos históricos en {PROJECT_ID}.{RAW_DATASET}.weather_data")
    hook = BigQueryHook(project_id=PROJECT_ID, location=REGION)
    # Usar formato correcto sin backticks alrededor del project_id
    query = f"""
    SELECT COUNT(DISTINCT date) as days_count
    FROM `{PROJECT_ID}.{RAW_DATASET}.weather_data`
    WHERE date >= '2023-06-01' AND date <= '2023-12-31'
    """
    try:
        result = hook.get_first(query, project_id=PROJECT_ID, location=REGION)
        days_count = result[0] if result else 0
        print(f"📊 Días encontrados: {days_count}")
    except Exception as e:
        # Si la tabla no existe, asumimos que no hay datos históricos
        print(f"⚠️  Error verificando datos históricos: {e}")
        print("   Asumiendo que no hay datos históricos y procediendo con la ingesta.")
        print("   Continuando con la ingesta histórica...")
        return
    
    if days_count >= 180:
        print(f"✅ Ya existen {days_count} días de datos históricos (>= 180).")
        print("   Continuando con el pipeline (dbt puede actualizar datos existentes).")
    else:
        print(f"⚠️  Solo hay {days_count} días. Necesitamos ingesta histórica.")
        print("   Continuando con la ingesta histórica...")

def trigger_weather_function(historical=True, **context):
    """Trigger la Cloud Function de ingesta de clima usando ID token."""
    import requests
    import json
    
    function_url = Variable.get(
        "WEATHER_FUNCTION_URL",
        default_var=f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/weather-ingestion",
    )
    
    # Obtener ID token para autenticación con Cloud Functions
    # Cloud Functions requiere un ID token, no un access token
    try:
        from google.auth import default
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        
        # Obtener credenciales por defecto
        credentials, project = default()
        request_obj = Request()
        
        # Obtener ID token para la URL de la función
        token = id_token.fetch_id_token(request_obj, function_url)
        print(f"✅ ID token obtenido para autenticación")
    except Exception as e:
        print(f"⚠️  Error obteniendo ID token: {e}")
        print("   Intentando con access token como fallback...")
        try:
            credentials.refresh(request_obj)
            token = credentials.token
            print(f"✅ Access token obtenido (puede no funcionar para funciones privadas)")
        except Exception as e2:
            print(f"❌ Error obteniendo cualquier token: {e2}")
            token = None
    
    # Trigger con parámetro histórico
    payload = {"historical": historical}
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print(f"🔄 Invocando Cloud Function: {function_url}")
        print(f"   Payload: {json.dumps(payload)}")
        response = requests.post(function_url, json=payload, headers=headers, timeout=900)
        if response.status_code == 404:
            print("❌ Cloud Function no encontrada (404).")
            print(f"   URL actual: {function_url}")
            print("   Configura la variable Airflow WEATHER_FUNCTION_URL")
            print("   con la URL real de la función desplegada.")
        response.raise_for_status()
        print(f"✅ Cloud Function triggered successfully: {response.status_code}")
        if response.text:
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering function: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status code: {e.response.status_code}")
            print(f"   Response: {e.response.text[:200]}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise

EXPORT_BUCKET = f"{PROJECT_ID}-taxi-export"
EXPORT_URI = f"gs://{EXPORT_BUCKET}/taxi_trips_*.parquet"
RAW_TABLE_ID = f"{PROJECT_ID}.{RAW_DATASET}.taxi_trips_raw_table"
EXTERNAL_TABLE_ID = f"{PROJECT_ID}.{RAW_DATASET}.taxi_trips_ext"


def taxi_data_missing(**context) -> bool:
    """Evita re-procesar si la tabla ya tiene datos."""
    hook = BigQueryHook(project_id=PROJECT_ID, location=REGION)
    query = f"SELECT COUNT(*) as cnt FROM `{RAW_TABLE_ID}`"
    try:
        result = hook.get_first(query, project_id=PROJECT_ID, location=REGION)
        row_count = result[0] if result else 0
        if row_count > 0:
            print(f"✅ taxi_trips_raw_table ya tiene {row_count:,} registros. Saltando carga.")
            return False
        print("⚠️  Tabla existe pero está vacía. Procediendo con la carga.")
        return True
    except Exception as e:
        print(f"⚠️  No se pudo verificar la tabla: {e}")
        print("   Asumiendo que no hay datos. Procediendo con la carga.")
        return True


def ensure_export_bucket(**context):
    """Crea el bucket de export si no existe."""
    hook = GCSHook()
    try:
        hook.get_bucket(EXPORT_BUCKET)
        print(f"✅ Bucket ya existe: gs://{EXPORT_BUCKET}")
        return
    except Exception:
        print(f"🪣 Creando bucket: gs://{EXPORT_BUCKET}")
        hook.create_bucket(EXPORT_BUCKET, location=REGION)


check_taxi_data = ShortCircuitOperator(
    task_id='check_taxi_data_missing',
    python_callable=taxi_data_missing,
    dag=historical_dag,
)

create_export_bucket = PythonOperator(
    task_id='create_export_bucket',
    python_callable=ensure_export_bucket,
    dag=historical_dag,
)

export_public_taxi_to_gcs = BigQueryToGCSOperator(
    task_id='export_public_taxi_to_gcs',
    source_project_dataset_table='bigquery-public-data:chicago_taxi_trips.taxi_trips',
    destination_cloud_storage_uris=[EXPORT_URI],
    export_format='PARQUET',
    compression='GZIP',
    project_id=PROJECT_ID,
    location="US",
    gcp_conn_id='google_cloud_default',
    dag=historical_dag,
)

create_external_table = BigQueryInsertJobOperator(
    task_id='create_external_taxi_table',
    configuration={
        "query": {
            "query": f"""
            CREATE EXTERNAL TABLE IF NOT EXISTS `{EXTERNAL_TABLE_ID}`
            OPTIONS (
              format = 'PARQUET',
              uris = ['{EXPORT_URI}']
            )
            """,
            "useLegacySql": False,
        }
    },
    location=REGION,
    dag=historical_dag,
)

create_raw_table = BigQueryInsertJobOperator(
    task_id='create_raw_taxi_table',
    configuration={
        "query": {
            "query": f"""
            CREATE TABLE IF NOT EXISTS `{RAW_TABLE_ID}` (
              unique_key STRING,
              taxi_id STRING,
              trip_start_timestamp TIMESTAMP,
              trip_end_timestamp TIMESTAMP,
              trip_seconds INT64,
              trip_miles FLOAT64,
              pickup_census_tract STRING,
              dropoff_census_tract STRING,
              pickup_community_area INT64,
              dropoff_community_area INT64,
              fare FLOAT64,
              tips FLOAT64,
              tolls FLOAT64,
              extras FLOAT64,
              trip_total FLOAT64,
              payment_type STRING,
              company STRING,
              pickup_latitude FLOAT64,
              pickup_longitude FLOAT64,
              dropoff_latitude FLOAT64,
              dropoff_longitude FLOAT64
            )
            PARTITION BY DATE(trip_start_timestamp)
            """,
            "useLegacySql": False,
        }
    },
    location=REGION,
    dag=historical_dag,
)

load_historical_taxi = BigQueryInsertJobOperator(
    task_id='load_historical_taxi_data',
    configuration={
        "query": {
            "query": f"""
            INSERT INTO `{RAW_TABLE_ID}`
            SELECT
              unique_key,
              taxi_id,
              trip_start_timestamp,
              trip_end_timestamp,
              trip_seconds,
              trip_miles,
              CAST(pickup_census_tract AS STRING),
              CAST(dropoff_census_tract AS STRING),
              pickup_community_area,
              dropoff_community_area,
              fare,
              tips,
              tolls,
              extras,
              trip_total,
              payment_type,
              company,
              pickup_latitude,
              pickup_longitude,
              dropoff_latitude,
              dropoff_longitude
            FROM `{EXTERNAL_TABLE_ID}`
            WHERE DATE(trip_start_timestamp) >= '2023-06-01'
              AND DATE(trip_start_timestamp) <= '2023-12-31'
              AND trip_start_timestamp IS NOT NULL
              AND trip_seconds IS NOT NULL
              AND trip_seconds > 0
              AND trip_miles >= 0
            """,
            "useLegacySql": False,
            "priority": "BATCH",
        }
    },
    location=REGION,
    dag=historical_dag,
)

# Tareas para DAG histórico
check_historical = PythonOperator(
    task_id='check_historical_data',
    python_callable=check_historical_data_exists,
    pool=None,  # No usar pool para evitar problemas de recursos
    dag=historical_dag,
)

trigger_weather_historical = PythonOperator(
    task_id='trigger_weather_historical',
    python_callable=trigger_weather_function,
    op_kwargs={'historical': True},
    pool=None,  # No usar pool
    dag=historical_dag,
)

run_dbt_silver = BashOperator(
    task_id='run_dbt_silver',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID='{{ params.project_id }}' && \
    export DBT_DATASET=chicago_taxi_silver && \
    # NO usar GOOGLE_APPLICATION_CREDENTIALS - usar ADC de Airflow (oauth)
    # Esto permite acceder a datasets públicos de BigQuery
    unset GOOGLE_APPLICATION_CREDENTIALS || true && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Ejecutar dbt para crear taxi_trips_silver y weather_silver
    # Usa oauth (Application Default Credentials) para acceder a datasets públicos
    dbt run --select silver --profiles-dir /home/airflow/gcs/data/dbt
    """,
    params={
        'project_id': PROJECT_ID,
    },
    pool=None,  # No usar pool
    dag=historical_dag,
)

run_dbt_gold = BashOperator(
    task_id='run_dbt_gold',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID='{{ params.project_id }}' && \
    export DBT_DATASET=chicago_taxi_silver && \
    # NO usar GOOGLE_APPLICATION_CREDENTIALS - usar ADC de Airflow (oauth)
    unset GOOGLE_APPLICATION_CREDENTIALS || true && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Ejecutar dbt
    dbt run --select gold --profiles-dir /home/airflow/gcs/data/dbt
    """,
    params={
        'project_id': PROJECT_ID,
    },
    pool=None,  # No usar pool
    dag=historical_dag,
)

run_dbt_tests = BashOperator(
    task_id='run_dbt_tests',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID='{{ params.project_id }}' && \
    export DBT_DATASET=chicago_taxi_silver && \
    unset GOOGLE_APPLICATION_CREDENTIALS || true && \
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    dbt test --profiles-dir /home/airflow/gcs/data/dbt
    """,
    params={
        'project_id': PROJECT_ID,
    },
    pool=None,
    dag=historical_dag,
)

# Tareas para DAG diario
trigger_weather_daily = PythonOperator(
    task_id='trigger_weather_daily',
    python_callable=trigger_weather_function,
    op_kwargs={'historical': False},
    dag=daily_dag,
)

run_dbt_daily = BashOperator(
    task_id='run_dbt_daily',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID='{{ params.project_id }}' && \
    export DBT_DATASET=chicago_taxi_silver && \
    # NO usar GOOGLE_APPLICATION_CREDENTIALS - usar ADC de Airflow (oauth)
    unset GOOGLE_APPLICATION_CREDENTIALS || true && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Ejecutar dbt
    dbt run --profiles-dir /home/airflow/gcs/data/dbt
    """,
    params={
        'project_id': PROJECT_ID,
    },
    dag=daily_dag,
)

run_dbt_daily_tests = BashOperator(
    task_id='run_dbt_daily_tests',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID='{{ params.project_id }}' && \
    export DBT_DATASET=chicago_taxi_silver && \
    unset GOOGLE_APPLICATION_CREDENTIALS || true && \
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    dbt test --profiles-dir /home/airflow/gcs/data/dbt
    """,
    params={
        'project_id': PROJECT_ID,
    },
    dag=daily_dag,
)

# Dependencias para DAG histórico
# 1. Activar acceso al dataset público (intenta activar si no está activado)
# 2. Cargar datos históricos de taxis a tabla propia (lee del dataset público)
# 3. Verificar datos históricos de clima
# 4. Cargar datos históricos de clima
# 1. Verificar si ya existen datos históricos de taxis
# 2. Exportar dataset público a GCS
# 3. Crear tabla externa
# 4. Crear tabla raw (si no existe) e insertar datos filtrados
# 5. Verificar y cargar datos históricos de clima
# 6. Ejecutar dbt silver y gold
check_taxi_data >> create_export_bucket >> export_public_taxi_to_gcs >> create_external_table >> create_raw_table >> load_historical_taxi >> check_historical >> trigger_weather_historical >> run_dbt_silver >> run_dbt_gold >> run_dbt_tests

# Dependencias para DAG diario
trigger_weather_daily >> run_dbt_daily >> run_dbt_daily_tests
