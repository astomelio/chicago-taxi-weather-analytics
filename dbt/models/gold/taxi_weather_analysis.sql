{{
  config(
    materialized='table',
    schema='gold'
  )
}}

WITH taxi_trips AS (
  SELECT *
  FROM `{{ var('project_id') }}.{{ var('silver_dataset') }}.taxi_trips_silver`
),

weather_data AS (
  SELECT *
  FROM `{{ var('project_id') }}.{{ var('silver_dataset') }}.weather_silver`
),

-- Agregar datos del clima a los viajes por fecha
trips_with_weather AS (
  SELECT 
    t.*,
    w.temperature,
    w.humidity,
    w.wind_speed,
    w.precipitation,
    w.weather_condition,
    w.weather_category,
    w.temperature_category
  FROM taxi_trips t
  LEFT JOIN weather_data w
    ON t.trip_date = w.date
)

SELECT
  trip_date,
  weather_category,
  temperature_category,
  temperature,
  precipitation,
  wind_speed,
  humidity,
  
  -- Métricas de viajes
  COUNT(*) AS total_trips,
  COUNT(DISTINCT taxi_id) AS unique_taxis,
  
  -- Métricas de duración
  AVG(trip_seconds) AS avg_trip_duration_seconds,
  APPROX_QUANTILES(trip_seconds, 100)[OFFSET(50)] AS median_trip_duration_seconds,
  MIN(trip_seconds) AS min_trip_duration_seconds,
  MAX(trip_seconds) AS max_trip_duration_seconds,
  STDDEV(trip_seconds) AS stddev_trip_duration_seconds,
  
  -- Métricas de distancia
  AVG(trip_miles) AS avg_trip_miles,
  SUM(trip_miles) AS total_miles,
  
  -- Métricas de velocidad
  AVG(avg_speed_mph) AS avg_speed_mph,
  
  -- Métricas financieras
  AVG(fare) AS avg_fare,
  AVG(tips) AS avg_tips,
  AVG(trip_total) AS avg_trip_total,
  SUM(trip_total) AS total_revenue,
  
  -- Métricas por hora del día
  trip_hour,
  COUNT(*) AS trips_by_hour
  
FROM trips_with_weather
GROUP BY 
  trip_date,
  weather_category,
  temperature_category,
  temperature,
  precipitation,
  wind_speed,
  humidity,
  trip_hour
ORDER BY trip_date, trip_hour
