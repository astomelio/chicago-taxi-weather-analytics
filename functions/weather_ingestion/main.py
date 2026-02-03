"""
Cloud Function para ingerir datos del clima.

Esta función obtiene datos del clima desde:
- PRIMERO: Dataset público de NOAA en BigQuery (bigquery-public-data.noaa_gsod)
- FALLBACK: API externa si BigQuery no tiene datos (opcional, requiere API key)

Esta función tiene dos modos:

1. MODO HISTÓRICO (primera ejecución):
   - Ingesta todos los datos del período de análisis: 01/06/2023 - 31/12/2023
   - Solo 6 meses para mantener queries dentro del tier gratuito de GCP
   - Se ejecuta una vez para llenar la base de datos histórica
   - Luego Cloud Scheduler ejecuta el modo diario automáticamente

2. MODO DIARIO (ejecución automática):
   - Ingesta solo los datos del día anterior
   - Se ejecuta automáticamente cada día
   - NOTA: Los datos nuevos (2024+) NO se usan en el dashboard (taxis terminan en 2023)
   - Pero se ingieren de todas formas según el requerimiento del desafío
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# requests solo se usa para fallback con API externa
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
PROJECT_ID = os.environ.get("PROJECT_ID")
DATASET_ID = os.environ.get("DATASET_ID")
TABLE_ID = os.environ.get("TABLE_ID")
# API Key - OPCIONAL - Solo se usa como fallback si BigQuery público no tiene datos
# Implementación: Visual Crossing Weather API (gratuita)
# Obtener en: https://www.visualcrossing.com/weather-api
# Nota: Primero intenta usar dataset público de NOAA en BigQuery
WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY") or os.environ.get("WEATHER_API_KEY")
CHICAGO_LAT = float(os.environ.get("CHICAGO_LAT", "41.8781"))
CHICAGO_LON = float(os.environ.get("CHICAGO_LON", "-87.6298"))

# Fechas del período de análisis
START_DATE = datetime(2023, 6, 1)
END_DATE = datetime(2023, 12, 31)


def get_weather_data(date: datetime) -> Dict[str, Any]:
    """
    Obtiene datos del clima para una fecha específica desde BigQuery público (NOAA).
    Usa el dataset público de Google Cloud: bigquery-public-data.noaa_gsod
    
    Args:
        date: Fecha para la cual obtener los datos del clima
        
    Returns:
        Diccionario con los datos del clima
        
    Raises:
        Exception: Si hay error al obtener datos de BigQuery
    """
    # Usar dataset público de NOAA en BigQuery
    # Estación: Chicago O'Hare International Airport (USW00094846)
    # Código WBAN: 94846, Código STN: 725300
    query = f"""
    SELECT 
        date,
        AVG(SAFE_CAST(temp AS FLOAT64)) as avg_temp,
        AVG(SAFE_CAST(dewp AS FLOAT64)) as avg_dewpoint,
        AVG(SAFE_CAST(slp AS FLOAT64)) as avg_pressure,
        AVG(SAFE_CAST(wdsp AS FLOAT64)) as avg_wind_speed,
        SUM(SAFE_CAST(prcp AS FLOAT64)) as total_precipitation,
        AVG(SAFE_CAST(max AS FLOAT64)) as max_temp,
        AVG(SAFE_CAST(min AS FLOAT64)) as min_temp
    FROM `bigquery-public-data.noaa_gsod.gsod{date.year}`
    WHERE wban = '94846'  -- Chicago O'Hare International Airport
      AND date = DATE('{date.date().isoformat()}')
      AND temp IS NOT NULL
    GROUP BY date
    """
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query_job = client.query(query)
        results = query_job.result()
        
        row = next(results, None)
        
        if row:
            # Convertir temperatura de Fahrenheit a Celsius (NOAA usa Fahrenheit)
            temp_c = (row.avg_temp - 32) * 5/9 if row.avg_temp else None
            max_temp_c = (row.max_temp - 32) * 5/9 if row.max_temp else None
            min_temp_c = (row.min_temp - 32) * 5/9 if row.min_temp else None
            
            # Convertir precipitación de pulgadas a mm (1 inch = 25.4 mm)
            precip_mm = row.total_precipitation * 25.4 if row.total_precipitation else 0.0
            
            # Convertir velocidad del viento de nudos a m/s (1 knot = 0.514 m/s)
            wind_speed_ms = row.avg_wind_speed * 0.514 if row.avg_wind_speed else None
            
            # Determinar condición climática basada en temperatura y precipitación
            weather_condition = "Clear"
            if precip_mm > 5:
                weather_condition = "Rain"
            elif precip_mm > 0:
                weather_condition = "Drizzle"
            elif temp_c and temp_c < 0:
                weather_condition = "Cold"
            
            weather_data = {
                "date": date.date().isoformat(),
                "temperature": round(temp_c, 1) if temp_c else None,
                "humidity": None,  # NOAA GSOD no tiene humedad directa, se puede calcular de dewpoint
                "wind_speed": round(wind_speed_ms, 1) if wind_speed_ms else None,
                "precipitation": round(precip_mm, 1),
                "weather_condition": weather_condition,
                "ingestion_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Datos del clima obtenidos exitosamente desde BigQuery para {date.date()}")
            return weather_data
        else:
            # Si no hay datos en NOAA, intentar con API externa como fallback
            logger.warning(f"No se encontraron datos en NOAA para {date.date()}, usando API externa como fallback")
            return get_weather_data_from_api(date)
        
    except Exception as e:
        logger.warning(f"Error obteniendo datos de BigQuery para {date.date()}: {e}. Intentando con API externa...")
        return get_weather_data_from_api(date)


def get_weather_data_from_api(date: datetime) -> Dict[str, Any]:
    """
    Obtiene datos del clima desde API externa (fallback si BigQuery no tiene datos).
    
    Args:
        date: Fecha para la cual obtener los datos del clima
        
    Returns:
        Diccionario con los datos del clima
    """
    if not HAS_REQUESTS:
        raise ValueError("No hay datos en BigQuery público y el módulo 'requests' no está instalado para usar API externa.")
    
    if not WEATHER_API_KEY:
        raise ValueError("No hay datos en BigQuery público y WEATHER_API_KEY no está configurada.")
    
    # Usar Visual Crossing como fallback
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
    params = {
        "location": f"{CHICAGO_LAT},{CHICAGO_LON}",
        "date": date.strftime("%Y-%m-%d"),
        "key": WEATHER_API_KEY,
        "unitGroup": "metric",
        "include": "days"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "days" in data and len(data["days"]) > 0:
            day_data = data["days"][0]
            
            weather_data = {
                "date": date.date().isoformat(),
                "temperature": day_data.get("tempmax", None),
                "humidity": day_data.get("humidity", None),
                "wind_speed": day_data.get("windspeed", None),
                "precipitation": day_data.get("precip", 0.0),
                "weather_condition": day_data.get("conditions", None),
                "ingestion_timestamp": datetime.utcnow().isoformat()
            }
            logger.info(f"Datos del clima obtenidos desde API externa para {date.date()}")
            return weather_data
        else:
            raise Exception(f"No se encontraron datos del día en la respuesta de la API para {date.date()}")
        
    except Exception as e:
        error_msg = f"Error obteniendo datos de API externa para {date.date()}: {e}"
        logger.error(error_msg)
        raise Exception(error_msg)


def check_date_exists(client: bigquery.Client, date: datetime) -> bool:
    """
    Verifica si ya existen datos para una fecha específica.
    
    Args:
        client: Cliente de BigQuery
        date: Fecha a verificar
        
    Returns:
        True si la fecha ya existe, False en caso contrario
    """
    query = f"""
    SELECT COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    WHERE date = DATE('{date.date().isoformat()}')
    """
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        row = next(results)
        return row.count > 0
    except NotFound:
        # La tabla no existe aún
        return False
    except Exception as e:
        logger.error(f"Error verificando fecha: {e}")
        return False


def insert_weather_data(client: bigquery.Client, weather_data: Dict[str, Any]) -> None:
    """
    Inserta datos del clima en BigQuery.
    
    Args:
        client: Cliente de BigQuery
        weather_data: Datos del clima a insertar
    """
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
    
    rows_to_insert = [weather_data]
    
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        logger.error(f"Error insertando datos: {errors}")
        raise Exception(f"Error insertando datos: {errors}")
    else:
        logger.info(f"Datos insertados correctamente para {weather_data['date']}")


def ingest_date_range(client: bigquery.Client, start_date: datetime, end_date: datetime) -> None:
    """
    Ingesta datos del clima para un rango de fechas.
    
    Args:
        client: Cliente de BigQuery
        start_date: Fecha de inicio (inclusive)
        end_date: Fecha de fin (inclusive)
    """
    logger.info(f"Iniciando ingesta desde {start_date.date()} hasta {end_date.date()}")
    
    current_date = start_date
    total_days = 0
    inserted_days = 0
    skipped_days = 0
    
    while current_date <= end_date:
        if not check_date_exists(client, current_date):
            try:
                weather_data = get_weather_data(current_date)
                insert_weather_data(client, weather_data)
                inserted_days += 1
            except Exception as e:
                logger.error(f"Error procesando {current_date.date()}: {e}")
        else:
            logger.debug(f"Datos ya existen para {current_date.date()}")
            skipped_days += 1
        
        current_date += timedelta(days=1)
        total_days += 1
        
        # Log de progreso cada 30 días
        if total_days % 30 == 0:
            logger.info(f"Progreso: {total_days} días procesados, {inserted_days} insertados, {skipped_days} ya existían")
    
    logger.info("=" * 60)
    logger.info(f"INGESTA COMPLETADA")
    logger.info(f"Total de días procesados: {total_days}")
    logger.info(f"Días nuevos insertados: {inserted_days}")
    logger.info(f"Días que ya existían: {skipped_days}")
    logger.info("=" * 60)


def ingest_historical_data(client: bigquery.Client) -> None:
    """
    Ingesta todos los datos históricos del período de análisis (01/06/2023 - 31/12/2023).
    Este es el modo de ingesta histórica que se ejecuta en la primera corrida.
    
    IMPORTANTE: Solo carga hasta 31/12/2023 para mantener las consultas dentro del tier gratuito
    de Google Cloud (6 meses de datos).
    
    Args:
        client: Cliente de BigQuery
    """
    logger.info("=" * 60)
    logger.info("MODO: INGESTA HISTÓRICA")
    logger.info(f"Período: {START_DATE.date()} a {END_DATE.date()} (6 meses)")
    logger.info("NOTA: Solo hasta 31/12/2023 para mantener queries en tier gratuito")
    logger.info("=" * 60)
    
    ingest_date_range(client, START_DATE, END_DATE)


def ingest_single_date(client: bigquery.Client, target_date: datetime) -> None:
    """
    Ingesta datos del clima para una fecha específica.
    
    Args:
        client: Cliente de BigQuery
        target_date: Fecha a ingerir
    """
    target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    logger.info(f"Procesando fecha: {target_date.date()}")
    
    # Verificar si ya existen datos
    if check_date_exists(client, target_date):
        logger.info(f"Los datos para {target_date.date()} ya existen. No se insertarán duplicados.")
        return
    
    # Ingerir datos
    try:
        weather_data = get_weather_data(target_date)
        insert_weather_data(client, weather_data)
        logger.info(f"✅ Datos para {target_date.date()} ingeridos correctamente")
    except Exception as e:
        logger.error(f"❌ Error al ingerir datos para {target_date.date()}: {e}")
        raise


def ingest_daily_data(client: bigquery.Client) -> None:
    """
    Ingesta datos del clima del día anterior.
    Este es el modo diario que se ejecuta automáticamente cada día.
    
    Args:
        client: Cliente de BigQuery
    """
    logger.info("=" * 60)
    logger.info("MODO: INGESTA DIARIA (día anterior)")
    logger.info("=" * 60)
    
    # Obtener datos del día anterior
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    ingest_single_date(client, yesterday)


def main(request):
    """
    Función principal de Cloud Function.
    
    Puede recibir parámetros para especificar el modo:
    - {"historical": true} -> Modo histórico (desde 2023-06-01 hasta hoy)
    - {"date": "2024-01-15"} -> Ingesta fecha específica
    - Sin parámetros -> Modo diario (día anterior)
    
    Args:
        request: Request de Cloud Function (puede contener parámetros)
    """
    try:
        # Inicializar cliente de BigQuery
        client = bigquery.Client(project=PROJECT_ID)
        
        # Parsear request
        request_json = {}
        if hasattr(request, 'get_json'):
            request_json = request.get_json(silent=True) or {}
        elif isinstance(request, dict):
            request_json = request
        
        # Determinar modo de ejecución
        if request_json.get("historical", False):
            # Modo histórico: desde START_DATE hasta hoy
            ingest_historical_data(client)
            mode = "historical"
        elif "date" in request_json:
            # Modo fecha específica
            target_date = datetime.strptime(request_json["date"], "%Y-%m-%d")
            ingest_single_date(client, target_date)
            mode = f"single_date_{request_json['date']}"
        else:
            # Modo diario: día anterior
            ingest_daily_data(client)
            mode = "daily"
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Weather data ingestion completed successfully",
                "mode": mode
            })
        }
        
    except Exception as e:
        logger.error(f"Error en la función: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }


# Para ejecución local
if __name__ == "__main__":
    import sys
    
    # Simular request
    class MockRequest:
        def get_json(self, silent=False):
            if "--historical" in sys.argv:
                return {"historical": True}
            elif "--date" in sys.argv:
                idx = sys.argv.index("--date")
                if idx + 1 < len(sys.argv):
                    return {"date": sys.argv[idx + 1]}
            return {}
    
    request = MockRequest()
    main(request)
