-- Estrategia alternativa: Cargar datos mes por mes
-- Esto evita problemas con queries muy grandes

-- PRIMERO: Crear la tabla vacía con el esquema correcto
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

-- LUEGO: Insertar datos mes por mes (ejecuta cada query por separado)

-- Junio 2023
INSERT INTO `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
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
  AND DATE(trip_start_timestamp) < '2023-07-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;

-- Repite para cada mes cambiando las fechas:
-- Julio: '2023-07-01' a '2023-08-01'
-- Agosto: '2023-08-01' a '2023-09-01'
-- Septiembre: '2023-09-01' a '2023-10-01'
-- Octubre: '2023-10-01' a '2023-11-01'
-- Noviembre: '2023-11-01' a '2023-12-01'
-- Diciembre: '2023-12-01' a '2024-01-01'
