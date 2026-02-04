-- Paso 2: Insertar datos de JUNIO 2023
-- Ejecuta esto DESPUÉS de crear la tabla vacía

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
