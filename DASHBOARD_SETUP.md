# Guía para Crear el Dashboard en Looker Studio

## Prerequisitos

1. Datos ya procesados en BigQuery (tablas Gold)
2. Acceso a Looker Studio (gratis con cuenta de Google)
3. Permisos de BigQuery para leer los datasets

## Pasos para Crear el Dashboard

### 1. Conectar a BigQuery

1. Ir a [Looker Studio](https://lookerstudio.google.com/)
2. Crear un nuevo reporte
3. Seleccionar **BigQuery** como fuente de datos
4. Seleccionar el proyecto de GCP
5. Seleccionar el dataset `chicago_taxi_gold`
6. Seleccionar la tabla `daily_summary` o `taxi_weather_analysis`

### 2. Crear Visualizaciones Clave

#### Gráfico 1: Duración Promedio de Viajes por Condición Climática

- **Tipo**: Gráfico de barras
- **Dimensión**: `weather_category`
- **Métrica**: `avg_trip_duration_seconds` (promedio)
- **Título**: "Duración Promedio de Viajes por Condición Climática"

#### Gráfico 2: Número de Viajes por Día y Clima

- **Tipo**: Gráfico de líneas temporales
- **Dimensión**: `trip_date`
- **Métricas**: 
  - `total_trips` (suma)
  - Serie separada por `weather_category`
- **Título**: "Evolución de Viajes por Condición Climática"

#### Gráfico 3: Comparación de Métricas por Clima

- **Tipo**: Tabla de resumen
- **Dimensiones**: `weather_category`
- **Métricas**:
  - `avg_trip_duration_seconds` (promedio)
  - `total_trips` (suma)
  - `avg_trip_miles` (promedio)
  - `total_revenue` (suma)
- **Título**: "Resumen por Condición Climática"

#### Gráfico 4: Distribución de Duración por Temperatura

- **Tipo**: Gráfico de dispersión o barras agrupadas
- **Dimensión**: `temperature_category`
- **Métrica**: `avg_trip_duration_seconds` (promedio)
- **Título**: "Duración de Viajes por Categoría de Temperatura"

#### Gráfico 5: Heatmap de Viajes por Hora y Clima

- **Tipo**: Heatmap
- **Dimensiones**: 
  - `trip_hour` (filas)
  - `weather_category` (columnas)
- **Métrica**: `trips_by_hour` (suma)
- **Título**: "Patrón de Viajes por Hora y Clima"

### 3. Agregar Filtros

- **Filtro de Fecha**: Rango de fechas para `trip_date`
- **Filtro de Clima**: Selector múltiple para `weather_category`
- **Filtro de Temperatura**: Selector para `temperature_category`

### 4. Métricas Clave (KPIs)

Agregar tarjetas con:
- Total de viajes en el período
- Duración promedio de viajes
- Ingresos totales
- Diferencia de duración entre días lluviosos y soleados

### 5. Análisis e Insights

Agregar sección de texto con:
- Conclusiones sobre el impacto del clima
- Correlaciones identificadas
- Recomendaciones basadas en datos

## Consultas SQL Útiles para Análisis

### Comparación de Duración por Clima

```sql
SELECT 
  weather_category,
  AVG(avg_trip_duration_seconds) as avg_duration,
  COUNT(*) as days_count
FROM `project.chicago_taxi_gold.daily_summary`
GROUP BY weather_category
ORDER BY avg_duration DESC
```

### Correlación entre Precipitación y Duración

```sql
SELECT 
  CASE 
    WHEN precipitation = 0 THEN 'Sin lluvia'
    WHEN precipitation < 5 THEN 'Lluvia ligera'
    WHEN precipitation < 15 THEN 'Lluvia moderada'
    ELSE 'Lluvia intensa'
  END as rain_category,
  AVG(avg_trip_duration_seconds) as avg_duration,
  AVG(total_trips) as avg_trips
FROM `project.chicago_taxi_gold.daily_summary`
GROUP BY rain_category
```

## Compartir el Dashboard

1. Hacer clic en **Compartir** (botón superior derecho)
2. Agregar los siguientes emails:
   - alejandro@astrafy.io
   - felipe.bereilh@orbidi.com
3. Dar permisos de **Verer** (Viewer)
4. Copiar el link del dashboard y agregarlo al README.md

## Notas Importantes

- El dashboard debe ser público o compartido con los emails especificados
- Asegurarse de que los datos estén actualizados antes de compartir
- Documentar cualquier filtro o transformación aplicada en el dashboard
