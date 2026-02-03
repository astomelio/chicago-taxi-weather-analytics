-- Script para crear las tablas silver y gold en BigQuery
-- Ejecuta este script en BigQuery Console: https://console.cloud.google.com/bigquery

-- ============================================================================
-- 1. Crear tabla taxi_trips_silver
-- ============================================================================
-- Esta tabla filtra y limpia los datos de taxis del rango 2023-06-01 a 2023-12-31
-- Tiempo estimado: 5-10 minutos

CREATE OR REPLACE TABLE `brave-computer-454217-q4.chicago_taxi_silver.taxi_trips_silver`
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
FROM deduplicated_trips;

-- ============================================================================
-- 2. Crear tabla daily_summary (ejecutar DESPUÉS de que taxi_trips_silver esté lista)
-- ============================================================================
-- Esta tabla agrega los datos por día y condiciones climáticas
-- Tiempo estimado: 2-5 minutos

CREATE OR REPLACE TABLE `brave-computer-454217-q4.chicago_taxi_gold.daily_summary`
PARTITION BY date
CLUSTER BY date AS
WITH taxi_trips AS (
  SELECT *
  FROM `brave-computer-454217-q4.chicago_taxi_silver.taxi_trips_silver`
),
weather_data AS (
  SELECT *
  FROM `brave-computer-454217-q4.chicago_taxi_silver.weather_silver`
)
SELECT
  t.trip_date as date,
  w.weather_category,
  w.temperature_category,
  w.temperature,
  w.precipitation,
  w.wind_speed,
  w.humidity,
  w.weather_condition,
  COUNT(*) AS total_trips,
  COUNT(DISTINCT t.taxi_id) AS unique_taxis,
  AVG(t.trip_seconds) AS avg_trip_duration_seconds,
  APPROX_QUANTILES(t.trip_seconds, 100)[OFFSET(50)] AS median_trip_duration_seconds,
  SUM(t.trip_miles) AS total_miles,
  AVG(t.trip_miles) AS avg_trip_miles,
  AVG(t.avg_speed_mph) AS avg_speed_mph,
  AVG(t.fare) AS avg_fare,
  AVG(t.tips) AS avg_tips,
  AVG(t.trip_total) AS avg_trip_total,
  SUM(t.trip_total) AS total_revenue
FROM taxi_trips t
LEFT JOIN weather_data w
  ON t.trip_date = w.date
GROUP BY 
  t.trip_date,
  w.weather_category,
  w.temperature_category,
  w.temperature,
  w.precipitation,
  w.wind_speed,
  w.humidity,
  w.weather_condition
ORDER BY t.trip_date;
