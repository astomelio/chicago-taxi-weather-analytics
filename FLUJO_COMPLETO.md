# Flujo Completo de la Prueba - Explicación Detallada

## 🎯 Objetivo
Analizar si las condiciones climáticas afectan la duración de los viajes en taxis de Chicago.

## 📊 Flujo de Datos Completo

### PASO 1: Datos de Taxis (NO se cargan, se leen directamente)

**¿De dónde vienen?**
- Del dataset **público** de BigQuery: `bigquery-public-data.chicago_taxi_trips.taxi_trips`
- **NO necesitas cargarlos manualmente** - ya están en BigQuery

**¿Qué hace Terraform?**
- Crea una **VISTA** en tu proyecto que filtra los datos:
  ```sql
  SELECT * FROM bigquery-public-data.chicago_taxi_trips.taxi_trips
  WHERE DATE(trip_start_timestamp) >= '2023-06-01'
    AND DATE(trip_start_timestamp) <= '2023-12-31'
  ```
- Esta vista se llama `chicago_taxi_raw.taxi_trips_raw`
- Es solo una "ventana" a los datos públicos, no copia nada

**Resultado:** Tienes acceso a los datos de taxis filtrados por fecha

---

### PASO 2: Datos del Clima (SÍ se cargan desde API)

**¿De dónde vienen?**
- De una API externa de clima (se implementó Visual Crossing como ejemplo)
- **SÍ necesitas cargarlos** porque no están en BigQuery

**¿Qué hace la Cloud Function?**
- Llama a la API para obtener datos del clima
- Los guarda en BigQuery en la tabla `chicago_taxi_raw.weather_data`

**Modos:**
1. **Histórico**: Carga desde 2023-06-01 hasta HOY
2. **Diario**: Carga solo el día anterior (automático cada día)

**Resultado:** Tienes datos del clima en BigQuery

---

### PASO 3: Transformaciones con dbt (UNE AMBOS DATASETS)

**Capa Silver (Limpieza):**

1. **`taxi_trips_silver`**:
   - Lee de `chicago_taxi_raw.taxi_trips_raw` (la vista)
   - Limpia y deduplica los datos de taxis
   - Agrega campos calculados (velocidad promedio, etc.)

2. **`weather_silver`**:
   - Lee de `chicago_taxi_raw.weather_data` (los datos que cargaste)
   - Limpia y categoriza los datos del clima
   - Crea categorías: Rainy, Snowy, Clear, Cloudy, etc.

**Capa Gold (Análisis - AQUÍ SE UNEN):**

1. **`daily_summary`**:
   ```sql
   SELECT 
     t.trip_date,
     w.weather_category,  -- Del clima
     AVG(t.trip_seconds) as avg_trip_duration,  -- De los taxis
     COUNT(*) as total_trips  -- De los taxis
   FROM taxi_trips_silver t
   LEFT JOIN weather_silver w
     ON t.trip_date = w.date  -- AQUÍ SE UNEN POR FECHA
   ```
   - **UNE** datos de taxis con datos del clima por fecha
   - Calcula métricas: duración promedio, total de viajes, etc.
   - **ESTE ES EL DATASET QUE USA EL DASHBOARD**

2. **`taxi_weather_analysis`**:
   - Similar pero más detallado (por hora, por condición climática)

**Resultado:** Datos unidos listos para el dashboard

---

### PASO 4: Dashboard en Looker Studio

**¿Qué muestra?**
- Gráficos que comparan:
  - Duración de viajes vs. condición climática
  - Número de viajes vs. temperatura
  - Correlaciones entre clima y comportamiento de taxis

**¿De dónde lee?**
- De las tablas **Gold** (`daily_summary`, `taxi_weather_analysis`)
- Que ya tienen los datos de taxis Y clima unidos

---

## 🔄 Resumen del Flujo

```
┌─────────────────────────────────────────────────────────┐
│ 1. DATOS DE TAXIS                                       │
│    BigQuery Público → Vista (filtrada por fecha)       │
│    ✅ NO se cargan, solo se leen                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. DATOS DEL CLIMA                                      │
│    API Externa → Cloud Function → BigQuery              │
│    ✅ SÍ se cargan (histórico + diario)                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. TRANSFORMACIONES (dbt)                               │
│    Silver: Limpia ambos datasets                        │
│    Gold: UNE taxis + clima por fecha                    │
│    ✅ Aquí se combinan los datos                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. DASHBOARD (Looker Studio)                            │
│    Lee de Gold → Muestra análisis                       │
│    ✅ Muestra la relación clima vs duración de viajes   │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Puntos Clave

1. **Datos de taxis**: NO se cargan, se leen del dataset público
2. **Datos del clima**: SÍ se cargan desde API externa
3. **dbt une ambos**: En la capa Gold se combinan por fecha
4. **Dashboard**: Muestra el análisis de la relación clima-viajes

## 📝 Lo que SÍ necesitas hacer

1. ✅ Ejecutar Terraform → Crea la vista de taxis y la tabla de clima
2. ✅ Ejecutar Cloud Function (histórico) → Carga datos del clima
3. ✅ Ejecutar dbt → Transforma y une ambos datasets
4. ✅ Crear dashboard → Visualiza el análisis

## ❌ Lo que NO necesitas hacer

- ❌ Cargar datos de taxis manualmente (ya están en BigQuery público)
- ❌ Descargar nada de los taxis (solo se leen)
