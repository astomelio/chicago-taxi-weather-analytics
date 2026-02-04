# Instrucciones Paso a Paso: Cargar Datos Históricos

## Paso 1: Abrir BigQuery Console

1. Ve a: https://console.cloud.google.com/bigquery?project=brave-computer-454217-q4
2. **IMPORTANTE**: Verifica en la esquina superior derecha que estés usando tu email personal (NO un service account)

## Paso 2: Crear la Tabla Vacía

1. En BigQuery Console, click en "Compose new query" (o el botón "+" para nueva query)
2. Abre el archivo `scripts/query_crear_tabla_vacia.sql` en tu editor
3. **Copia TODO el contenido** del archivo
4. **Pega** en BigQuery Console
5. Click en "Run"
6. Espera a que termine (debería ser rápido, ~10 segundos)
7. Verifica que diga "This statement created a new table"

## Paso 3: Insertar Datos de Junio (Prueba)

1. En BigQuery Console, click en "Compose new query" de nuevo
2. Abre el archivo `scripts/query_insert_junio.sql`
3. **Copia TODO el contenido**
4. **Pega** en BigQuery Console
5. En "More" → "Query settings":
   - Cambia "Job priority" a "Batch" (más barato)
6. Click en "Run"
7. Espera a que termine (puede tardar 3-5 minutos para junio)

## Paso 4: Verificar que Funcionó

Ejecuta esta query para verificar:

```sql
SELECT COUNT(*) as total_registros
FROM `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`;
```

Deberías ver un número (ej: ~1,000,000 para junio)

## Paso 5: Si Funcionó, Continuar con los Demás Meses

1. Abre `scripts/query_insert_julio_diciembre.sql`
2. **Ejecuta cada INSERT por separado** (uno a la vez)
3. Empieza con el primer INSERT (Julio)
4. Espera a que termine
5. Luego ejecuta el siguiente (Agosto)
6. Y así sucesivamente...

**O puedes copiar y ejecutar cada INSERT individualmente:**

### Julio:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-07-01'
  AND DATE(trip_start_timestamp) < '2023-08-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

### Agosto:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-08-01'
  AND DATE(trip_start_timestamp) < '2023-09-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

### Septiembre:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-09-01'
  AND DATE(trip_start_timestamp) < '2023-10-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

### Octubre:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-10-01'
  AND DATE(trip_start_timestamp) < '2023-11-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

### Noviembre:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-11-01'
  AND DATE(trip_start_timestamp) < '2023-12-01'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

### Diciembre:
```sql
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
WHERE DATE(trip_start_timestamp) >= '2023-12-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
  AND trip_start_timestamp IS NOT NULL
  AND trip_seconds IS NOT NULL
  AND trip_seconds > 0
  AND trip_miles >= 0;
```

## Paso 6: Verificar Total Final

Después de cargar todos los meses, ejecuta:

```sql
SELECT COUNT(*) as total_registros
FROM `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`;
```

Deberías ver aproximadamente **6,931,127 registros**

## Paso 7: Continuar con el Pipeline

Una vez que la tabla tenga datos:

1. Ve a Airflow UI
2. Trigger el DAG `chicago_taxi_historical_ingestion`
3. El DAG detectará que la tabla ya tiene datos y saltará la carga
4. Continuará con el resto del pipeline (clima, dbt, etc.)

---

## Resumen Visual

```
1. Abrir BigQuery Console
   ↓
2. Ejecutar query_crear_tabla_vacia.sql
   ↓
3. Ejecutar query_insert_junio.sql (prueba)
   ↓
4. Si funciona, ejecutar los demás meses uno por uno
   ↓
5. Verificar total: ~6.9 millones de registros
   ↓
6. Trigger DAG en Airflow
```
