{{
  config(
    materialized='table',
    schema='silver',
    cluster_by=['trip_date'],
    partition_by={
      "field": "trip_date",
      "data_type": "date",
      "granularity": "day"
    }
  )
}}

WITH raw_trips AS (
  SELECT *
  FROM `{{ env_var('GCP_PROJECT_ID') }}.chicago_taxi_raw.taxi_trips_raw`
  WHERE trip_start_timestamp IS NOT NULL
    AND trip_seconds IS NOT NULL
    AND trip_seconds > 0
    AND trip_miles >= 0
    AND DATE(trip_start_timestamp) >= '2023-06-01'
    AND DATE(trip_start_timestamp) <= '2023-12-31'
),

-- Eliminar duplicados basándose en unique_key
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
  -- payment_type se excluye aquí para seguridad, se manejará en una vista separada
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
