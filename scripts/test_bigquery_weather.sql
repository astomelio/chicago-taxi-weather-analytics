-- Query para probar que los datos de clima existen en BigQuery público (NOAA)
-- Ejecuta esta query en la consola de BigQuery: https://console.cloud.google.com/bigquery

-- Probar con una fecha específica (2023-06-01)
SELECT 
    date,
    AVG(CAST(temp AS FLOAT64)) as avg_temp_f,
    AVG(CAST(max AS FLOAT64)) as max_temp_f,
    AVG(CAST(min AS FLOAT64)) as min_temp_f,
    AVG(CAST(wdsp AS FLOAT64)) as avg_wind_speed_knots,
    SUM(CAST(prcp AS FLOAT64)) as total_precipitation_inches,
    AVG(CAST(dewp AS FLOAT64)) as avg_dewpoint_f
FROM `bigquery-public-data.noaa_gsod.gsod2023`
WHERE wban = '94846'  -- Chicago O'Hare International Airport
  AND date = DATE('2023-06-01')
  AND temp != '9999.9'  -- Filtrar valores inválidos
  AND temp IS NOT NULL
GROUP BY date;

-- Probar con varias fechas del período de análisis
SELECT 
    date,
    AVG(CAST(temp AS FLOAT64)) as avg_temp_f,
    AVG(CAST(max AS FLOAT64)) as max_temp_f,
    AVG(CAST(min AS FLOAT64)) as min_temp_f,
    AVG(CAST(wdsp AS FLOAT64)) as avg_wind_speed_knots,
    SUM(CAST(prcp AS FLOAT64)) as total_precipitation_inches
FROM `bigquery-public-data.noaa_gsod.gsod2023`
WHERE wban = '94846'  -- Chicago O'Hare International Airport
  AND date >= DATE('2023-06-01')
  AND date <= DATE('2023-12-31')
  AND temp != '9999.9'  -- Filtrar valores inválidos
  AND temp IS NOT NULL
GROUP BY date
ORDER BY date
LIMIT 10;

-- Verificar que la estación existe
SELECT DISTINCT
    stn,
    wban,
    name
FROM `bigquery-public-data.noaa_gsod.gsod2023`
WHERE wban = '94846'
LIMIT 1;
