# 🎯 Tour Completo del Sistema Desplegado

Este documento te guía paso a paso para verificar que TODO está funcionando después del despliegue automático.

## 📊 Paso 1: Verificar Infraestructura en GCP

### 1.1 BigQuery - Datasets y Tablas

**URL**: https://console.cloud.google.com/bigquery?project=TU-PROYECTO

**Debes ver:**

#### Dataset: `chicago_taxi_raw`
- ✅ Tabla `weather_data` (con datos del clima)
  - Verifica: `SELECT COUNT(*) FROM chicago_taxi_raw.weather_data`
  - Debe tener ~214 registros (días de junio-diciembre 2023)

#### Dataset: `chicago_taxi_silver`
- ✅ Tabla `taxi_trips_silver` (viajes limpios y deduplicados)
  - Verifica: `SELECT COUNT(*) FROM chicago_taxi_silver.taxi_trips_silver`
  - Debe tener millones de registros
  
- ✅ Tabla `weather_silver` (clima procesado)
  - Verifica: `SELECT COUNT(*) FROM chicago_taxi_silver.weather_silver`
  - Debe tener ~214 registros

#### Dataset: `chicago_taxi_gold`
- ✅ Tabla `taxi_weather_analysis` (análisis detallado)
  - Verifica: `SELECT COUNT(*) FROM chicago_taxi_gold.taxi_weather_analysis`
  - Debe tener millones de registros (uno por viaje)
  
- ✅ Tabla `daily_summary` (resumen diario)
  - Verifica: `SELECT COUNT(*) FROM chicago_taxi_gold.daily_summary`
  - Debe tener ~214 registros (uno por día)

**Query de verificación rápida:**
```sql
SELECT 
  'Raw Weather' as layer, COUNT(*) as records 
FROM `TU-PROYECTO.chicago_taxi_raw.weather_data`
UNION ALL
SELECT 
  'Silver Trips', COUNT(*) 
FROM `TU-PROYECTO.chicago_taxi_silver.taxi_trips_silver`
UNION ALL
SELECT 
  'Silver Weather', COUNT(*) 
FROM `TU-PROYECTO.chicago_taxi_silver.weather_silver`
UNION ALL
SELECT 
  'Gold Analysis', COUNT(*) 
FROM `TU-PROYECTO.chicago_taxi_gold.taxi_weather_analysis`
UNION ALL
SELECT 
  'Gold Summary', COUNT(*) 
FROM `TU-PROYECTO.chicago_taxi_gold.daily_summary`
ORDER BY layer
```

### 1.2 Cloud Functions

**URL**: https://console.cloud.google.com/functions?project=TU-PROYECTO

**Debes ver:**
- ✅ Función `weather-ingestion`
- ✅ Estado: **ACTIVA**
- ✅ URL: `https://weather-ingestion-XXXXX-uc.a.run.app`

**Probar la función:**
1. Click en la función
2. Ve a la pestaña **"Testing"**
3. En "Triggering event", pega:
   ```json
   {"mode": "test"}
   ```
4. Click **"Test the function"**
5. Debe responder con un mensaje de éxito

### 1.3 Cloud Scheduler

**URL**: https://console.cloud.google.com/cloudscheduler?project=TU-PROYECTO

**Debes ver:**
- ✅ Job `weather-ingestion-daily`
- ✅ Estado: **ENABLED**
- ✅ Horario: `0 2 * * *` (2 AM UTC diario)
- ✅ Target: URL de la Cloud Function

**Probar manualmente:**
1. Click en el job
2. Click en **"RUN NOW"**
3. Espera unos segundos
4. Ve a Cloud Functions > Logs para ver la ejecución

### 1.4 Cloud Storage

**URL**: https://console.cloud.google.com/storage/browser?project=TU-PROYECTO

**Debes ver:**
- ✅ Bucket: `TU-PROYECTO-function-source`
- ✅ Archivo: `weather-ingestion-source.zip`

## 📈 Paso 2: Verificar Datos en BigQuery

### 2.1 Verificar Datos de Clima

```sql
-- Verificar que hay datos del clima
SELECT 
  date,
  temperature,
  humidity,
  wind_speed,
  precipitation,
  weather_condition
FROM `TU-PROYECTO.chicago_taxi_raw.weather_data`
ORDER BY date
LIMIT 10
```

**Resultado esperado:** Debe mostrar datos de junio-diciembre 2023.

### 2.2 Verificar Datos de Taxis

```sql
-- Verificar viajes en silver
SELECT 
  trip_date,
  COUNT(*) as trips,
  AVG(trip_seconds) as avg_duration_seconds,
  AVG(trip_miles) as avg_miles
FROM `TU-PROYECTO.chicago_taxi_silver.taxi_trips_silver`
GROUP BY trip_date
ORDER BY trip_date
LIMIT 10
```

**Resultado esperado:** Debe mostrar viajes agrupados por día.

### 2.3 Verificar Análisis Gold

```sql
-- Ver análisis combinado de taxis y clima
SELECT 
  trip_date,
  weather_condition,
  temperature_category,
  COUNT(*) as trips,
  AVG(trip_seconds) as avg_duration,
  AVG(trip_miles) as avg_miles
FROM `TU-PROYECTO.chicago_taxi_gold.taxi_weather_analysis`
GROUP BY trip_date, weather_condition, temperature_category
ORDER BY trip_date
LIMIT 20
```

**Resultado esperado:** Debe mostrar viajes agrupados por día y condición climática.

### 2.4 Verificar Resumen Diario

```sql
-- Ver resumen diario
SELECT 
  date,
  total_trips,
  avg_trip_duration_seconds,
  avg_trip_miles,
  temperature,
  weather_condition,
  precipitation
FROM `TU-PROYECTO.chicago_taxi_gold.daily_summary`
ORDER BY date
LIMIT 10
```

**Resultado esperado:** Debe mostrar un resumen por día con métricas agregadas.

## 🎨 Paso 3: Configurar Dashboard en Looker Studio

### 3.1 Conectar a BigQuery

1. Ve a: https://datastudio.google.com
2. Click en **"Create"** > **"Data Source"**
3. Busca **"BigQuery"**
4. Selecciona tu proyecto
5. Selecciona dataset: `chicago_taxi_gold`
6. Selecciona tabla: `daily_summary` o `taxi_weather_analysis`

### 3.2 Crear Dashboard

**Métricas recomendadas:**

1. **Gráfico de Línea: Viajes por Día**
   - Dimensión: `date`
   - Métrica: `total_trips`
   - Título: "Total de Viajes por Día"

2. **Gráfico de Barras: Viajes por Condición Climática**
   - Dimensión: `weather_condition`
   - Métrica: `total_trips`
   - Título: "Viajes por Condición Climática"

3. **Gráfico de Dispersión: Duración vs Temperatura**
   - Dimensión X: `temperature`
   - Dimensión Y: `avg_trip_duration_seconds`
   - Título: "Duración de Viajes vs Temperatura"

4. **Tabla: Resumen Diario**
   - Columnas: `date`, `total_trips`, `avg_trip_duration_seconds`, `temperature`, `weather_condition`
   - Título: "Resumen Diario"

**Ver instrucciones completas en:** `DASHBOARD_SETUP.md`

## 🔍 Paso 4: Verificar Procesos Automáticos

### 4.1 Verificar Cloud Scheduler

1. Ve a Cloud Scheduler
2. Verifica que el job está **ENABLED**
3. Verifica el horario: `0 2 * * *` (2 AM UTC)
4. Opcional: Click en **"RUN NOW"** para probar

### 4.2 Verificar Logs de Cloud Function

1. Ve a Cloud Functions
2. Click en `weather-ingestion`
3. Ve a la pestaña **"Logs"**
4. Debe mostrar ejecuciones del scheduler (si ya pasó la hora programada)

### 4.3 Verificar que los Datos se Actualizan

```sql
-- Verificar la fecha más reciente de datos del clima
SELECT MAX(date) as latest_weather_date
FROM `TU-PROYECTO.chicago_taxi_raw.weather_data`
```

**Resultado esperado:** Debe ser el día anterior (si el scheduler ya ejecutó).

## ✅ Checklist de Verificación Completa

### Infraestructura
- [ ] BigQuery: 3 datasets creados
- [ ] BigQuery: Tablas con datos
- [ ] Cloud Function: Activa y funcionando
- [ ] Cloud Scheduler: ENABLED y programado
- [ ] Cloud Storage: Bucket con código

### Datos
- [ ] `weather_data`: ~214 registros (jun-dic 2023)
- [ ] `taxi_trips_silver`: Millones de registros
- [ ] `weather_silver`: ~214 registros
- [ ] `taxi_weather_analysis`: Millones de registros
- [ ] `daily_summary`: ~214 registros

### Procesos
- [ ] Cloud Scheduler ejecutando diariamente
- [ ] Cloud Function respondiendo correctamente
- [ ] dbt models ejecutados exitosamente

### Dashboard
- [ ] Conectado a BigQuery
- [ ] Visualizaciones creadas
- [ ] Datos mostrándose correctamente

## 🚨 Solución de Problemas

### No hay datos en las tablas

1. **Verificar ingesta histórica:**
   ```bash
   # Desde gcloud CLI
   gcloud functions call weather-ingestion \
     --region=us-central1 \
     --gen2 \
     --data '{"mode":"historical"}'
   ```

2. **Verificar logs de Cloud Function:**
   - Ve a Cloud Functions > Logs
   - Busca errores

3. **Ejecutar dbt manualmente:**
   ```bash
   cd dbt
   dbt run --models silver gold
   ```

### Cloud Scheduler no ejecuta

1. Verifica que está **ENABLED**
2. Verifica el horario (2 AM UTC)
3. Prueba con **"RUN NOW"**
4. Revisa logs de Cloud Function

### Dashboard no muestra datos

1. Verifica la conexión a BigQuery
2. Verifica que las tablas tienen datos
3. Verifica los permisos del usuario
4. Revisa la configuración de las métricas

## 📊 Queries Útiles para el Dashboard

### Viajes por Hora del Día y Clima

```sql
SELECT 
  EXTRACT(HOUR FROM trip_start_timestamp) as hour,
  weather_condition,
  COUNT(*) as trips,
  AVG(trip_seconds) as avg_duration
FROM `TU-PROYECTO.chicago_taxi_gold.taxi_weather_analysis`
GROUP BY hour, weather_condition
ORDER BY hour, weather_condition
```

### Top 10 Días con Más Viajes

```sql
SELECT 
  date,
  total_trips,
  temperature,
  weather_condition,
  avg_trip_duration_seconds
FROM `TU-PROYECTO.chicago_taxi_gold.daily_summary`
ORDER BY total_trips DESC
LIMIT 10
```

### Análisis de Precipitación

```sql
SELECT 
  CASE 
    WHEN precipitation = 0 THEN 'Sin lluvia'
    WHEN precipitation < 5 THEN 'Lluvia ligera'
    WHEN precipitation < 15 THEN 'Lluvia moderada'
    ELSE 'Lluvia intensa'
  END as rain_category,
  COUNT(*) as days,
  AVG(total_trips) as avg_trips_per_day,
  AVG(avg_trip_duration_seconds) as avg_duration
FROM `TU-PROYECTO.chicago_taxi_gold.daily_summary`
GROUP BY rain_category
ORDER BY avg_trips_per_day DESC
```

## 🎉 ¡Todo Listo!

Si todos los elementos del checklist están marcados, el sistema está completamente funcional:

- ✅ Infraestructura desplegada
- ✅ Datos ingeridos y procesados
- ✅ Procesos automáticos funcionando
- ✅ Dashboard configurado

El sistema ejecutará automáticamente la ingesta diaria de datos del clima y los datos estarán disponibles para análisis en el dashboard.
