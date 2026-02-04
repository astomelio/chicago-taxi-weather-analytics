-- Paso 1: Crear la tabla vacía con el esquema correcto
-- Ejecuta esto PRIMERO

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
