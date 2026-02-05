-- Queries SQL listas para usar en Looker Studio Dashboard
-- Proyecto: chicago-taxi-48702

-- ============================================
-- 1. RESUMEN DIARIO (Principal para Dashboard)
-- ============================================
SELECT 
  date,
  total_trips,
  avg_trip_duration_seconds / 60 as avg_duration_minutes,
  avg_trip_miles,
  temperature,
  weather_condition,
  weather_category,
  temperature_category,
  precipitation,
  wind_speed,
  humidity,
  total_revenue
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
ORDER BY date;

-- ============================================
-- 2. ANÁLISIS POR CONDICIÓN CLIMÁTICA
-- ============================================
SELECT 
  weather_category,
  COUNT(DISTINCT trip_date) as days_count,
  SUM(total_trips) as total_trips,
  AVG(total_trips) as avg_trips_per_day,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes,
  AVG(temperature) as avg_temperature,
  AVG(precipitation) as avg_precipitation
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
GROUP BY weather_category
ORDER BY total_trips DESC;

-- ============================================
-- 3. TOP 20 DÍAS CON MÁS VIAJES
-- ============================================
SELECT 
  date,
  total_trips,
  weather_condition,
  temperature,
  precipitation,
  avg_trip_duration_seconds / 60 as avg_duration_minutes,
  total_revenue
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
ORDER BY total_trips DESC
LIMIT 20;

-- ============================================
-- 4. ANÁLISIS POR HORA DEL DÍA Y CLIMA
-- ============================================
SELECT 
  trip_hour,
  weather_category,
  SUM(trips_by_hour) as total_trips,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes
FROM `chicago-taxi-48702.chicago_taxi_gold.taxi_weather_analysis`
GROUP BY trip_hour, weather_category
ORDER BY trip_hour, weather_category;

-- ============================================
-- 5. IMPACTO DE LA PRECIPITACIÓN
-- ============================================
SELECT 
  CASE 
    WHEN precipitation = 0 THEN 'Sin lluvia'
    WHEN precipitation < 5 THEN 'Lluvia ligera (<5mm)'
    WHEN precipitation < 15 THEN 'Lluvia moderada (5-15mm)'
    ELSE 'Lluvia intensa (>15mm)'
  END as rain_category,
  COUNT(*) as days,
  AVG(total_trips) as avg_trips_per_day,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes,
  AVG(total_revenue) as avg_revenue
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
GROUP BY rain_category
ORDER BY avg_trips_per_day DESC;

-- ============================================
-- 6. ANÁLISIS POR TEMPERATURA
-- ============================================
SELECT 
  temperature_category,
  COUNT(DISTINCT trip_date) as days,
  SUM(total_trips) as total_trips,
  AVG(total_trips) as avg_trips_per_day,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes,
  AVG(temperature) as avg_temperature
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
GROUP BY temperature_category
ORDER BY avg_trips_per_day DESC;

-- ============================================
-- 7. EVOLUCIÓN TEMPORAL (Serie de Tiempo)
-- ============================================
SELECT 
  date,
  total_trips,
  avg_trip_duration_seconds / 60 as avg_duration_minutes,
  temperature,
  precipitation,
  weather_condition
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
ORDER BY date;

-- ============================================
-- 8. COMPARACIÓN: DÍAS LLUVIOSOS VS SECOS
-- ============================================
SELECT 
  CASE 
    WHEN precipitation > 0 THEN 'Con lluvia'
    ELSE 'Sin lluvia'
  END as rain_status,
  COUNT(*) as days,
  AVG(total_trips) as avg_trips,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes,
  AVG(total_revenue) as avg_revenue
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
GROUP BY rain_status;

-- ============================================
-- 9. DISTRIBUCIÓN DE VIAJES POR DÍA DE SEMANA
-- ============================================
SELECT 
  EXTRACT(DAYOFWEEK FROM date) as day_of_week,
  CASE EXTRACT(DAYOFWEEK FROM date)
    WHEN 1 THEN 'Domingo'
    WHEN 2 THEN 'Lunes'
    WHEN 3 THEN 'Martes'
    WHEN 4 THEN 'Miércoles'
    WHEN 5 THEN 'Jueves'
    WHEN 6 THEN 'Viernes'
    WHEN 7 THEN 'Sábado'
  END as day_name,
  AVG(total_trips) as avg_trips,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`
GROUP BY day_of_week, day_name
ORDER BY day_of_week;

-- ============================================
-- 10. MÉTRICAS GENERALES (KPIs)
-- ============================================
SELECT 
  COUNT(DISTINCT date) as total_days,
  SUM(total_trips) as total_trips,
  AVG(total_trips) as avg_trips_per_day,
  AVG(avg_trip_duration_seconds) / 60 as avg_duration_minutes,
  AVG(temperature) as avg_temperature,
  SUM(total_revenue) as total_revenue,
  AVG(total_revenue) as avg_revenue_per_day
FROM `chicago-taxi-48702.chicago_taxi_gold.daily_summary`;
