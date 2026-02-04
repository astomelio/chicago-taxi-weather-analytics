"""
DAG principal para el pipeline de análisis de taxis de Chicago.
Orquesta la ingesta de datos, transformaciones dbt y actualizaciones diarias.
"""
from datetime import datetime, timedelta
from airflow import DAG
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

# Crear vista taxi_trips_raw si no existe (para acceso a dataset público)
def create_taxi_trips_raw_view(**context):
    """Crea la vista taxi_trips_raw si no existe para acceder al dataset público."""
    from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    
    hook = BigQueryHook(project_id=PROJECT_ID, location=REGION)
    client = hook.get_client()
    
    # Primero verificar si la vista ya existe
    dataset_ref = client.dataset('chicago_taxi_raw', project=PROJECT_ID)
    table_ref = dataset_ref.table('taxi_trips_raw')
    
    try:
        client.get_table(table_ref)
        print(f"✅ Vista taxi_trips_raw ya existe. Saltando creación.")
        return
    except NotFound:
        print(f"📋 Vista taxi_trips_raw no existe. Creándola...")
    except Exception as e:
        print(f"⚠️  Error verificando si la vista existe: {e}")
        print("   Intentando crear de todas formas...")
    
    # Si no existe, crearla
    view_query = f"""
    CREATE VIEW `{PROJECT_ID}.chicago_taxi_raw.taxi_trips_raw` AS
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
      payment_type,
      company,
      pickup_latitude,
      pickup_longitude,
      dropoff_latitude,
      dropoff_longitude
    FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
    WHERE DATE(trip_start_timestamp) >= '2023-06-01'
      AND DATE(trip_start_timestamp) <= '2023-12-31'
    """
    
    try:
        # Usar insert_job para ejecutar la query
        job_config = bigquery.QueryJobConfig(use_legacy_sql=False)
        query_job = client.query(view_query, job_config=job_config, location=REGION)
        query_job.result()  # Esperar a que termine
        
        # Verificar que se creó correctamente
        try:
            client.get_table(table_ref)
            print(f"✅ Vista taxi_trips_raw creada y verificada exitosamente")
        except NotFound:
            print(f"❌ ERROR: La vista no se creó aunque la query no falló")
            raise Exception("La vista no se pudo crear. Revisa los permisos y logs de BigQuery.")
            
    except Exception as e:
        error_msg = str(e)
        # Si la vista ya existe, no es un error crítico
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            print(f"✅ Vista taxi_trips_raw ya existe (creada entre la verificación y ahora)")
            # Verificar que existe
            try:
                client.get_table(table_ref)
                print(f"✅ Vista verificada y existe")
            except NotFound:
                print(f"⚠️  Advertencia: La vista dice que existe pero no se puede acceder")
        else:
            print(f"❌ Error creando vista: {e}")
            print(f"   Query: {view_query[:200]}...")
            print("   Esto causará que dbt falle. Revisa los permisos.")
            raise  # Hacer raise para que el DAG falle si no se puede crear

create_view = PythonOperator(
    task_id='create_taxi_trips_raw_view',
    python_callable=create_taxi_trips_raw_view,
    pool=None,
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

# Dependencias para DAG histórico
# Crear vista primero, luego verificar datos históricos, luego el resto
create_view >> check_historical >> trigger_weather_historical >> run_dbt_silver >> run_dbt_gold

# Dependencias para DAG diario
trigger_weather_daily >> run_dbt_daily
