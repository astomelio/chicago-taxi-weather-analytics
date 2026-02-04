-- Test simple para verificar que puedes crear tablas
-- Ejecuta esto en BigQuery Console

-- Test 1: Verificar que puedes acceder al dataset
SELECT COUNT(*) as test
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
LIMIT 1;

-- Test 2: Crear una tabla de prueba pequeña
CREATE TABLE IF NOT EXISTS `brave-computer-454217-q4.chicago_taxi_raw.test_table`
(
  test_id STRING,
  test_value INT64
)
PARTITION BY test_value;

-- Test 3: Insertar datos de prueba
INSERT INTO `brave-computer-454217-q4.chicago_taxi_raw.test_table`
VALUES ('test1', 1), ('test2', 2);

-- Test 4: Verificar que funcionó
SELECT * FROM `brave-computer-454217-q4.chicago_taxi_raw.test_table`;

-- Si todos estos tests funcionan, entonces puedes crear la tabla real
