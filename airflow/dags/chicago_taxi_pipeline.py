"""
DAG principal para el pipeline de análisis de taxis de Chicago.
Orquesta la ingesta de datos, transformaciones dbt y actualizaciones diarias.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import os

# Configuración - usar variables de Airflow si están disponibles
from airflow.models import Variable

try:
    PROJECT_ID = Variable.get('GCP_PROJECT_ID', default_var='brave-computer-454217-q4')
    REGION = Variable.get('GCP_REGION', default_var='us-central1')
except:
    # Fallback si las variables no están disponibles
    PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'brave-computer-454217-q4')
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
    hook = BigQueryHook(project_id=PROJECT_ID, location=REGION)
    query = f"""
    SELECT COUNT(DISTINCT date) as days_count
    FROM `{PROJECT_ID}.{RAW_DATASET}.weather_data`
    WHERE date >= '2023-06-01' AND date <= '2023-12-31'
    """
    try:
        result = hook.get_first(query)
        days_count = result[0] if result else 0
    except Exception as e:
        # Si la tabla no existe, asumimos que no hay datos históricos
        print(f"⚠️  Error verificando datos históricos: {e}")
        print("   Asumiendo que no hay datos históricos y procediendo con la ingesta.")
        return 'run_historical_ingestion'
    
    if days_count >= 180:
        print(f"✅ Ya existen {days_count} días de datos históricos. Saltando ingesta histórica.")
        return 'skip_historical_ingestion'
    else:
        print(f"⚠️  Solo hay {days_count} días. Necesitamos ingesta histórica.")
        return 'run_historical_ingestion'

def trigger_weather_function(historical=True, **context):
    """Trigger la Cloud Function de ingesta de clima usando ID token."""
    import requests
    import json
    
    function_url = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net/weather-ingestion"
    
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

# Tareas para DAG histórico
check_historical = PythonOperator(
    task_id='check_historical_data',
    python_callable=check_historical_data_exists,
    dag=historical_dag,
)

trigger_weather_historical = PythonOperator(
    task_id='trigger_weather_historical',
    python_callable=trigger_weather_function,
    op_kwargs={'historical': True},
    dag=historical_dag,
)

create_taxi_trips_silver = BigQueryInsertJobOperator(
    task_id='create_taxi_trips_silver',
    configuration={
        "query": {
            "query": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.{SILVER_DATASET}.taxi_trips_silver`
            PARTITION BY trip_date
            CLUSTER BY trip_date AS
            WITH raw_trips AS (
              SELECT *
              FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
              WHERE trip_start_timestamp IS NOT NULL
                AND trip_seconds IS NOT NULL
                AND trip_seconds > 0
                AND trip_miles >= 0
                AND DATE(trip_start_timestamp) >= '2023-06-01'
                AND DATE(trip_start_timestamp) <= '2023-12-31'
            ),
            deduplicated_trips AS (
              SELECT *
              FROM (
                SELECT *,
                       ROW_NUMBER() OVER (
                         PARTITION BY unique_key 
                         ORDER BY trip_start_timestamp DESC
                       ) AS rn
                FROM raw_trips
              )
              WHERE rn = 1
            )
            SELECT
              unique_key,
              taxi_id,
              trip_start_timestamp,
              trip_end_timestamp,
              trip_seconds,
              trip_miles,
              pickup_census_tract,
              dropoff_census_tract,
              pickup_community_area,
              dropoff_community_area,
              fare,
              tips,
              tolls,
              extras,
              trip_total,
              company,
              pickup_latitude,
              pickup_longitude,
              dropoff_latitude,
              dropoff_longitude,
              DATE(trip_start_timestamp) AS trip_date,
              EXTRACT(HOUR FROM trip_start_timestamp) AS trip_hour,
              EXTRACT(DAYOFWEEK FROM trip_start_timestamp) AS trip_day_of_week,
              CASE 
                WHEN trip_seconds > 0 THEN trip_miles / (trip_seconds / 3600.0)
                ELSE NULL
              END AS avg_speed_mph
            FROM deduplicated_trips
            """,
            "useLegacySql": False,
        }
    },
    location=REGION,
    project_id=PROJECT_ID,
    dag=historical_dag,
)

run_dbt_silver = BashOperator(
    task_id='run_dbt_silver',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID={{ var.value.GCP_PROJECT_ID }} && \
    export DBT_DATASET=chicago_taxi_silver && \
    export GOOGLE_APPLICATION_CREDENTIALS={{ var.value.GCP_SA_KEY_PATH }} && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Verificar credenciales
    echo "🔍 Verificando credenciales..." && \
    ls -la $GOOGLE_APPLICATION_CREDENTIALS || echo "⚠️  Service account key no encontrado" && \
    # Ejecutar dbt
    dbt run --models weather_silver --profiles-dir /home/airflow/gcs/data/dbt
    """,
    dag=historical_dag,
)

run_dbt_gold = BashOperator(
    task_id='run_dbt_gold',
    bash_command="""
    cd /home/airflow/gcs/data/dbt && \
    export GCP_PROJECT_ID={{ var.value.GCP_PROJECT_ID }} && \
    export DBT_DATASET=chicago_taxi_silver && \
    export GOOGLE_APPLICATION_CREDENTIALS={{ var.value.GCP_SA_KEY_PATH }} && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Ejecutar dbt
    dbt run --models gold --profiles-dir /home/airflow/gcs/data/dbt
    """,
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
    export GCP_PROJECT_ID={{ var.value.GCP_PROJECT_ID }} && \
    export DBT_DATASET=chicago_taxi_silver && \
    export GOOGLE_APPLICATION_CREDENTIALS={{ var.value.GCP_SA_KEY_PATH }} && \
    # Verificar que dbt esté instalado, si no, instalarlo
    python3 -m pip install --user dbt-bigquery 2>/dev/null || echo "dbt ya instalado o error en instalación" && \
    # Ejecutar dbt
    dbt run --profiles-dir /home/airflow/gcs/data/dbt
    """,
    dag=daily_dag,
)

# Dependencias para DAG histórico
check_historical >> trigger_weather_historical >> create_taxi_trips_silver >> run_dbt_silver >> run_dbt_gold

# Dependencias para DAG diario
trigger_weather_daily >> run_dbt_daily
