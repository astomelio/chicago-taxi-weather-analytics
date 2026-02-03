# 🎨 Guía Completa para Crear el Dashboard en Looker Studio

## 📋 Paso 1: Conectar a BigQuery

1. **Ir a Looker Studio**: https://lookerstudio.google.com/
   - Asegúrate de estar logueado con tu cuenta de Google

2. **Crear nuevo reporte**: 
   - Click en el botón **"Create"** (arriba a la izquierda)
   - Selecciona **"Report"**

3. **Agregar fuente de datos**:
   - Te aparecerá una ventana "Add data to report"
   - Busca y click en **"BigQuery"** (está en la lista de conectores)

4. **Seleccionar tu proyecto y tabla**:
   - En "Select a BigQuery project", busca: `brave-computer-454217-q4`
   - **Si no aparece**, busca por: `My Project 33994` (ese es el nombre del proyecto)
   - O busca en la lista todos tus proyectos y selecciona el que tenga los datasets `chicago_taxi_*`
   
   **Para la tabla, tienes 2 opciones:**
   
   **Opción A: Si `daily_summary` está disponible (recomendado)**
   - En "Select a dataset", selecciona: `chicago_taxi_gold`
   - En "Select a table", selecciona: `daily_summary`
   
   **Opción B: Si `daily_summary` está vacía, usa datos de clima**
   - En "Select a dataset", selecciona: `chicago_taxi_silver`
   - En "Select a table", selecciona: `weather_silver`
   - (Tiene 214 días de datos de clima listos para visualizar)
   
   - Click en **"Add"** (o "Connect")
   
   **Nota**: Si `daily_summary` está vacía, las tablas se crearán automáticamente cuando GitHub Actions ejecute el workflow completo. Mientras tanto, puedes usar `weather_silver` para crear visualizaciones de clima.

5. **Verificar conexión**:
   - Deberías ver tus datos con columnas como: `date`, `total_trips`, `temperature`, `weather_category`, etc.
   - Si ves los datos, ¡estás conectado! ✅

## 📊 Paso 2: Crear Visualizaciones Clave

### Visualización 1: KPIs Principales (Tarjetas)

**Crear 4 tarjetas de métricas:**

1. **Total de Viajes**
   - Métrica: `total_trips` (Sum)
   - Formato: Número con separadores de miles

2. **Duración Promedio**
   - Métrica: `avg_trip_duration_seconds / 60` (Average)
   - Formato: Número con 1 decimal
   - Unidad: "minutos"

3. **Temperatura Promedio**
   - Métrica: `temperature` (Average)
   - Formato: Número con 1 decimal
   - Unidad: "°C"

4. **Ingresos Totales**
   - Métrica: `total_revenue` (Sum)
   - Formato: Moneda (USD)

### Visualización 2: Evolución Temporal de Viajes

**Tipo**: Gráfico de líneas temporales

- **Dimensión**: `date`
- **Métrica**: `total_trips` (Sum)
- **Título**: "Evolución de Viajes por Día"
- **Eje Y**: "Número de Viajes"
- **Eje X**: "Fecha"

**Agregar serie adicional:**
- Click en "Add metric"
- Métrica: `temperature` (Average)
- Eje Y secundario: Temperatura (°C)
- Color diferente para distinguir

### Visualización 3: Viajes por Condición Climática

**Tipo**: Gráfico de barras

- **Dimensión**: `weather_category`
- **Métrica**: `total_trips` (Sum)
- **Título**: "Total de Viajes por Condición Climática"
- **Ordenar**: Por métrica (descendente)
- **Colores**: Diferentes colores por categoría

### Visualización 4: Duración Promedio por Clima

**Tipo**: Gráfico de barras

- **Dimensión**: `weather_category`
- **Métrica**: `avg_trip_duration_seconds / 60` (Average)
- **Título**: "Duración Promedio de Viajes por Condición Climática"
- **Unidad**: "minutos"

### Visualización 5: Impacto de la Precipitación

**Tipo**: Gráfico de barras agrupadas

- **Dimensión**: Categoría calculada:
  ```
  CASE 
    WHEN precipitation = 0 THEN 'Sin lluvia'
    WHEN precipitation < 5 THEN 'Lluvia ligera'
    WHEN precipitation < 15 THEN 'Lluvia moderada'
    ELSE 'Lluvia intensa'
  END
  ```
- **Métricas**:
  - `total_trips` (Sum)
  - `avg_trip_duration_seconds / 60` (Average)
- **Título**: "Impacto de la Precipitación"

### Visualización 6: Comparación de Métricas por Clima

**Tipo**: Tabla de resumen

- **Dimensiones**: `weather_category`
- **Métricas**:
  - `total_trips` (Sum)
  - `avg_trip_duration_seconds / 60` (Average)
  - `temperature` (Average)
  - `precipitation` (Average)
  - `total_revenue` (Sum)
- **Título**: "Resumen por Condición Climática"
- **Formato**: Números con separadores

### Visualización 7: Heatmap de Viajes por Hora y Clima

**Tipo**: Tabla pivotada (Heatmap)

1. **Crear nueva fuente de datos**: Conectar a `taxi_weather_analysis`
2. **Dimensiones**:
   - Filas: `trip_hour`
   - Columnas: `weather_category`
3. **Métrica**: `trips_by_hour` (Sum)
4. **Título**: "Patrón de Viajes por Hora y Clima"
5. **Formato de color**: Escala de colores (verde claro a rojo oscuro)

### Visualización 8: Dispersión: Duración vs Temperatura

**Tipo**: Gráfico de dispersión

- **Dimensión X**: `temperature`
- **Dimensión Y**: `avg_trip_duration_seconds / 60`
- **Tamaño de burbuja**: `total_trips`
- **Color**: `weather_category`
- **Título**: "Relación entre Temperatura y Duración de Viajes"

## 🎛️ Paso 3: Agregar Filtros

### Filtro de Fecha
- **Tipo**: Control de rango de fechas
- **Campo**: `date`
- **Posición**: Parte superior del dashboard

### Filtro de Clima
- **Tipo**: Selector múltiple
- **Campo**: `weather_category`
- **Posición**: Parte superior del dashboard

### Filtro de Temperatura
- **Tipo**: Selector de rango
- **Campo**: `temperature`
- **Posición**: Parte superior del dashboard

## 📝 Paso 4: Agregar Insights y Conclusiones

**Crear sección de texto con:**

### Insights Clave:

1. **Impacto del Clima**:
   - "Los días con condiciones climáticas adversas muestran un aumento en la duración promedio de los viajes."

2. **Correlación Temperatura-Duración**:
   - "Existe una correlación entre la temperatura y la duración de los viajes."

3. **Patrones Temporales**:
   - "Los viajes muestran patrones claros según la hora del día y las condiciones climáticas."

4. **Recomendaciones**:
   - "Se recomienda ajustar la flota de taxis según las condiciones climáticas previstas."

## 🎨 Paso 5: Diseño y Formato

### Tema y Colores:
- Usar colores consistentes para cada categoría climática
- Fondo claro para mejor legibilidad
- Títulos claros y descriptivos

### Layout:
- KPIs en la parte superior
- Gráficos principales en el centro
- Tablas de resumen en la parte inferior
- Filtros en la parte superior

## 🔗 Paso 6: Compartir el Dashboard

1. **Click en "Share"** (botón superior derecho)
2. **Agregar emails**:
   - alejandro@astrafy.io
   - felipe.bereilh@orbidi.com
3. **Permisos**: "Viewer"
4. **Copiar link** y agregarlo al README.md

## 📊 Queries SQL de Referencia

Todas las queries están disponibles en: `QUERIES_DASHBOARD.sql`

### Query Principal para el Dashboard:

```sql
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
FROM `brave-computer-454217-q4.chicago_taxi_gold.daily_summary`
ORDER BY date
```

## ✅ Checklist Final

- [ ] Dashboard conectado a BigQuery
- [ ] KPIs principales creados
- [ ] Gráficos de evolución temporal
- [ ] Análisis por condición climática
- [ ] Impacto de precipitación
- [ ] Heatmap de horas y clima
- [ ] Filtros configurados
- [ ] Insights agregados
- [ ] Dashboard compartido con emails requeridos
- [ ] Link agregado al README.md

## 🎯 Resultado Esperado

Un dashboard interactivo que muestre:

1. ✅ Métricas clave (KPIs)
2. ✅ Evolución temporal de viajes
3. ✅ Impacto del clima en los viajes
4. ✅ Análisis de precipitación
5. ✅ Patrones por hora del día
6. ✅ Correlaciones entre variables
7. ✅ Insights y conclusiones

El dashboard debe ser claro, interactivo y permitir explorar los datos desde diferentes perspectivas.
