# 🔓 Activar Acceso al Dataset Público de BigQuery

## Problema

El service account de Composer no puede acceder al dataset público `bigquery-public-data.chicago_taxi_trips.taxi_trips` porque BigQuery requiere que un **usuario** (no un service account) ejecute una query primero para activar el acceso.

## Solución Rápida (2 minutos)

### Paso 1: Abrir BigQuery Console

1. Ve a: https://console.cloud.google.com/bigquery?project=brave-computer-454217-q4
2. **IMPORTANTE**: Verifica en la esquina superior derecha que estés usando tu **email personal** (NO un service account)

### Paso 2: Ejecutar Query de Activación

Copia y pega esta query en BigQuery Console:

```sql
SELECT COUNT(*) as test
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE DATE(trip_start_timestamp) >= '2023-06-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
```

3. Click en **"Run"**
4. Espera a que termine (debería ser rápido, ~10-30 segundos)

### Paso 3: Verificar que Funcionó

Deberías ver un número como resultado (ej: `6931127`). Esto significa que el acceso está activado.

### Paso 4: Volver a Ejecutar el DAG

1. Ve a Airflow UI: https://console.cloud.google.com/composer/environments/chicago-taxi-composer/locations/us-central1/monitoring/airflow?project=brave-computer-454217-q4
2. Encuentra el DAG `chicago_taxi_historical_ingestion`
3. Click en el botón de "play" para ejecutarlo de nuevo

## ¿Por qué es Necesario?

BigQuery requiere que un **usuario con permisos de facturación** ejecute una query contra un dataset público para "activar" el acceso para todo el proyecto. Esto es una medida de seguridad para evitar que proyectos sin billing accedan a datasets públicos.

Una vez activado, **todos** los service accounts del proyecto pueden acceder al dataset público.

## Verificación

Después de ejecutar la query de activación, puedes verificar que funciona ejecutando esta query desde BigQuery Console:

```sql
SELECT COUNT(*) as total
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE DATE(trip_start_timestamp) >= '2023-06-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
```

Deberías ver: **6,931,127 registros**

## Nota Importante

- ✅ Debe ejecutarse con tu **usuario personal** (no service account)
- ✅ Solo necesitas hacerlo **una vez** por proyecto
- ✅ Después de esto, el DAG debería funcionar correctamente
