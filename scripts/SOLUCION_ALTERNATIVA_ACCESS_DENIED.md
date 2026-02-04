# Solución Alternativa: Access Denied en Query Grande

## Problema

La query pequeña funciona, pero la query grande da "Access Denied". Esto puede ser por:
- Límites de BigQuery para queries grandes desde datasets públicos
- Problemas de contexto/sesión
- Restricciones de organización

## Solución 1: Ejecutar desde el mismo contexto

1. **En BigQuery Console, ejecuta PRIMERO la query pequeña que funcionó:**
   ```sql
   SELECT COUNT(*) as test
   FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
   WHERE DATE(trip_start_timestamp) >= '2023-06-01'
     AND DATE(trip_start_timestamp) <= '2023-12-31'
   ```

2. **INMEDIATAMENTE después (sin cerrar la pestaña), ejecuta la query grande**

3. **Si sigue fallando, prueba la Solución 2**

---

## Solución 2: Usar el DAG de Airflow

El DAG de Airflow debería funcionar porque usa el service account de Composer que ya tiene permisos:

1. **Ve a Airflow UI:**
   - Link en los logs de GitHub Actions
   - O: https://console.cloud.google.com/composer/environments

2. **Trigger el DAG `chicago_taxi_historical_ingestion`**

3. **El DAG ejecutará `load_historical_taxi_data` que carga los datos**

---

## Solución 3: Cargar mes por mes (más lento pero más seguro)

1. **Crea la tabla vacía primero:**
   ```sql
   CREATE TABLE IF NOT EXISTS `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
   (
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
   PARTITION BY DATE(trip_start_timestamp);
   ```

2. **Luego inserta mes por mes** (ejecuta cada query por separado):

   **Junio:**
   ```sql
   INSERT INTO `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
   SELECT * FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
   WHERE DATE(trip_start_timestamp) >= '2023-06-01'
     AND DATE(trip_start_timestamp) < '2023-07-01'
     AND trip_start_timestamp IS NOT NULL
     AND trip_seconds IS NOT NULL
     AND trip_seconds > 0
     AND trip_miles >= 0;
   ```

   **Julio:**
   ```sql
   INSERT INTO `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
   SELECT * FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
   WHERE DATE(trip_start_timestamp) >= '2023-07-01'
     AND DATE(trip_start_timestamp) < '2023-08-01'
     AND trip_start_timestamp IS NOT NULL
     AND trip_seconds IS NOT NULL
     AND trip_seconds > 0
     AND trip_miles >= 0;
   ```

   **Repite para Agosto, Septiembre, Octubre, Noviembre, Diciembre** (cambia las fechas)

---

## Solución 4: Usar BigQuery Data Transfer (más complejo)

Si nada funciona, puedes usar BigQuery Data Transfer Service, pero es más complejo de configurar.

---

## Recomendación

**Usa la Solución 2 (Airflow DAG)** - Es la más confiable porque:
- El service account de Composer ya tiene los permisos correctos
- El código ya está probado
- Se ejecuta automáticamente

Solo necesitas trigger el DAG desde Airflow UI.
