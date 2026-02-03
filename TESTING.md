# Guía de Pruebas

## Prueba de los Modos de Ingesta

El pipeline tiene dos modos de operación claramente diferenciados:

### 1. Modo Histórico (Primera Ejecución)

Ingesta todos los datos históricos del período de análisis (01/06/2023 - 31/12/2023).

**IMPORTANTE**: Solo carga hasta 31/12/2023 (6 meses) para mantener las consultas dentro del tier gratuito de Google Cloud, como especifica el desafío.

**Ejecutar:**
```bash
# Configurar variables de entorno
export GCP_PROJECT_ID="tu-proyecto"
export DATASET_ID="chicago_taxi_raw"
export TABLE_ID="weather_data"
export OPENWEATHER_API_KEY="tu-api-key"

# Ejecutar modo histórico
python functions/weather_ingestion/main.py --historical
```

**Qué esperar:**
- Logs que muestran "MODO: INGESTA HISTÓRICA"
- Procesa 214 días (del 1 de junio al 31 de diciembre de 2023) - **SOLO 6 MESES**
- Inserta datos en BigQuery para cada día
- Al final muestra resumen: total procesados, nuevos insertados, ya existentes
- **NO carga datos de 2024+** (para mantener queries en tier gratuito)

### 2. Modo Diario (Ejecución Automática)

Ingesta solo los datos del día anterior. Este modo se ejecuta automáticamente cada día.

**IMPORTANTE**: Aunque estemos en 2024/2025, este modo sigue ejecutándose. Los datos nuevos (2024+) NO se usarán en el dashboard porque los datos de taxis solo van hasta diciembre 2023, pero el requerimiento del desafío pide que el pipeline siga activo.

**Ejecutar:**
```bash
# Configurar variables de entorno (mismas que arriba)
export GCP_PROJECT_ID="tu-proyecto"
export DATASET_ID="chicago_taxi_raw"
export TABLE_ID="weather_data"
export OPENWEATHER_API_KEY="tu-api-key"

# Ejecutar modo diario (sin flag --historical)
python functions/weather_ingestion/main.py
```

**Qué esperar:**
- Logs que muestran "MODO: INGESTA DIARIA (día anterior)"
- Procesa solo 1 día (el día anterior a hoy - puede ser 2024, 2025, etc.)
- Si la fecha está en 2023: muestra que se usará en el dashboard
- Si la fecha está fuera de 2023: muestra advertencia que NO se usará en el dashboard
- Verifica si ya existen datos antes de insertar
- Incluso si el día está fuera del rango de análisis (2023), lo ingiere igual (según requerimiento)

## Verificar Datos en BigQuery

```sql
-- Verificar datos históricos
SELECT 
  date,
  temperature,
  weather_condition,
  COUNT(*) as count
FROM `tu-proyecto.chicago_taxi_raw.weather_data`
WHERE date >= '2023-06-01' AND date <= '2023-12-31'
GROUP BY date, temperature, weather_condition
ORDER BY date
LIMIT 10;

-- Contar total de días ingeridos
SELECT COUNT(DISTINCT date) as total_days
FROM `tu-proyecto.chicago_taxi_raw.weather_data`
WHERE date >= '2023-06-01' AND date <= '2023-12-31';
```

## Prueba de la API

Para verificar que la API key funciona:

```bash
# Ejemplo con Visual Crossing (API implementada)
curl "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/41.8781,-87.6298/2023-06-01?key=TU_API_KEY&unitGroup=metric&include=days"
```

Deberías recibir un JSON con datos del clima para esa fecha.

## Troubleshooting

### Error: "WEATHER_API_KEY no está configurada"
- Asegúrate de exportar la variable `OPENWEATHER_API_KEY`
- O configúrala en `terraform/terraform.tfvars`

### Error: "API key inválida o expirada"
- Verifica que la API key sea correcta
- Asegúrate de que la API key esté activa en el proveedor de la API

### Error: "Límite de rate excedido"
- El tier gratuito tiene límite de 1000 llamadas/día
- Espera unos minutos o considera hacer la ingesta histórica en batches

### Los datos no aparecen en BigQuery
- Verifica que el dataset y tabla existan
- Revisa los logs para ver si hubo errores de inserción
- Verifica permisos del service account
