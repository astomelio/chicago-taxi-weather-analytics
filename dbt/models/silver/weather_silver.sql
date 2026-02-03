{{
  config(
    materialized='table',
    schema='silver'
  )
}}

WITH raw_weather AS (
  SELECT *
  FROM `{{ env_var('GCP_PROJECT_ID') }}.chicago_taxi_raw.weather_data`
  WHERE date >= '2023-06-01'
    AND date <= '2023-12-31'
),

-- Eliminar duplicados por fecha, manteniendo el registro más reciente
deduplicated_weather AS (
  SELECT *
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (
             PARTITION BY date 
             ORDER BY ingestion_timestamp DESC
           ) AS rn
    FROM raw_weather
  )
  WHERE rn = 1
)

SELECT
  date,
  temperature,
  humidity,
  wind_speed,
  precipitation,
  weather_condition,
  -- Categorizar condiciones climáticas
  CASE 
    WHEN weather_condition IN ('Rain', 'Drizzle', 'Thunderstorm') THEN 'Rainy'
    WHEN weather_condition IN ('Snow', 'Sleet') THEN 'Snowy'
    WHEN weather_condition IN ('Clear', 'Sun') THEN 'Clear'
    WHEN weather_condition IN ('Clouds', 'Mist', 'Fog') THEN 'Cloudy'
    ELSE 'Other'
  END AS weather_category,
  -- Categorizar temperatura
  CASE 
    WHEN temperature < 0 THEN 'Freezing'
    WHEN temperature < 10 THEN 'Cold'
    WHEN temperature < 20 THEN 'Cool'
    WHEN temperature < 30 THEN 'Warm'
    ELSE 'Hot'
  END AS temperature_category
FROM deduplicated_weather
