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
)

SELECT
  t.trip_date,
  w.weather_category,
  w.temperature_category,
  w.temperature,
  w.precipitation,
  w.wind_speed,
  w.humidity,
  
  -- Resumen diario de viajes
  COUNT(*) AS total_trips,
  COUNT(DISTINCT t.taxi_id) AS unique_taxis,
  
  -- Duración promedio de viajes
  AVG(t.trip_seconds) AS avg_trip_duration_seconds,
  APPROX_QUANTILES(t.trip_seconds, 100)[OFFSET(50)] AS median_trip_duration_seconds,
  
  -- Distancia total y promedio
  SUM(t.trip_miles) AS total_miles,
  AVG(t.trip_miles) AS avg_trip_miles,
  
  -- Ingresos
  SUM(t.trip_total) AS total_revenue,
  AVG(t.trip_total) AS avg_trip_total,
  
  -- Velocidad promedio
  AVG(t.avg_speed_mph) AS avg_speed_mph
  
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
  w.humidity
ORDER BY t.trip_date
