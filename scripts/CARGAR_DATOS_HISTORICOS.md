# Cargar Datos Históricos - Instrucciones

## ⚠️ IMPORTANTE: Activar Acceso al Dataset Público PRIMERO

**ANTES de cargar los datos, debes activar el acceso al dataset público:**

### Paso 1: Verificar y Otorgar Permisos

**Opción A: Desde Terminal (Recomendado)**
```bash
# Verificar y otorgar permisos automáticamente
./scripts/verificar_permisos_bigquery.sh
```

**Opción B: Manualmente desde Console**
1. Ve a: https://console.cloud.google.com/iam-admin/iam?project=brave-computer-454217-q4
2. Busca tu email en la lista
3. Verifica que tengas estos roles:
   - `BigQuery User` (roles/bigquery.user)
   - `BigQuery Job User` (roles/bigquery.jobUser)
   - `BigQuery Data Viewer` (roles/bigquery.dataViewer)
4. Si no los tienes, click en "Grant Access" y agrégalos

### Paso 2: Activar Acceso al Dataset Público

1. **Ve a BigQuery Console:**
   ```
   https://console.cloud.google.com/bigquery?project=brave-computer-454217-q4
   ```

2. **Asegúrate de estar usando TU USUARIO (no un service account)**
   - Verifica en la esquina superior derecha que estás logueado con tu cuenta personal
   - Si ves un service account, cambia a tu cuenta personal

3. **Ejecuta esta query de ACTIVACIÓN (muy simple):**
   ```sql
   SELECT COUNT(*) as test
   FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
   WHERE DATE(trip_start_timestamp) >= '2023-06-01'
     AND DATE(trip_start_timestamp) <= '2023-12-31'
   ```

4. **Si funciona, verás un resultado (ej: `test: 6931127`)**
   - Esto activa el acceso al dataset público para TODO el proyecto
   - Ahora los service accounts también podrán acceder

5. **Si sigue fallando con "Access Denied":**
   - ✅ Verifica que ejecutaste `./scripts/verificar_permisos_bigquery.sh`
   - ✅ Verifica que estés usando tu cuenta personal (no service account)
   - ✅ Verifica que el proyecto tenga facturación habilitada
   - ✅ Espera 1-2 minutos después de otorgar permisos (puede tardar en propagarse)
   - ⚠️ Si persiste, puede ser una restricción de organización. Contacta al administrador

---

## Opción 1: Desde BigQuery Console (Más Fácil) ⭐

**IMPORTANTE: Primero ejecuta la query de activación arriba**

1. **Ve a BigQuery Console:**
   ```
   https://console.cloud.google.com/bigquery?project=brave-computer-454217-q4
   ```

2. **Ejecuta esta query para CARGAR los datos (versión simplificada):**
   ```sql
   CREATE OR REPLACE TABLE `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
   PARTITION BY DATE(trip_start_timestamp)
   AS
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
   WHERE DATE(trip_start_timestamp) >= '2023-06-01'
     AND DATE(trip_start_timestamp) <= '2023-12-31'
     AND trip_start_timestamp IS NOT NULL
     AND trip_seconds IS NOT NULL
     AND trip_seconds > 0
     AND trip_miles >= 0
   ```

3. **Configura la query:**
   - En "More" → "Query settings"
   - Cambia "Job priority" a "Batch" (para reducir costos)
   - Click en "Run"

4. **Si obtienes error de sintaxis:**
   - Usa la versión SIN clustering (archivo `query_cargar_datos_sin_clustering.sql`)
   - El clustering se puede agregar después si es necesario

5. **Si obtienes "Access Denied":**
   - ⚠️ **NO has activado el acceso aún**
   - Vuelve al paso de "Activar Acceso al Dataset Público" arriba
   - Ejecuta primero la query de activación simple

6. **Espera a que complete** (20-40 minutos para ~7 millones de registros)

5. **Verifica que se cargó:**
   ```sql
   SELECT COUNT(*) as total_registros
   FROM `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`
   ```
   Deberías ver ~6,931,127 registros

---

## Opción 2: Desde Terminal (Si tienes gcloud instalado)

1. **Instala bq (si no lo tienes):**
   ```bash
   gcloud components install bq
   ```

2. **Ejecuta el script:**
   ```bash
   export GCP_PROJECT_ID="brave-computer-454217-q4"
   ./scripts/load_historical_data.sh
   ```

---

## Opción 3: Desde Airflow UI

1. **Ve a Airflow UI:**
   - El link aparece en los logs de GitHub Actions
   - O busca en: https://console.cloud.google.com/composer/environments

2. **Trigger el DAG:**
   - Busca `chicago_taxi_historical_ingestion`
   - Click en el botón "Play" ▶️
   - Espera a que complete (20-30 minutos)

---

## Después de Cargar los Datos

Una vez que `taxi_trips_raw_table` tenga datos:

1. **Ejecuta el DAG histórico en Airflow** para cargar datos de clima
2. **Ejecuta dbt** para crear las capas silver y gold:
   - Desde Airflow: El DAG histórico ejecuta dbt automáticamente
   - O manualmente desde terminal:
     ```bash
     cd dbt
     dbt run --select silver
     dbt run --select gold
     ```

---

## Verificar que Todo Funcionó

Ejecuta estas queries en BigQuery:

```sql
-- Verificar datos raw
SELECT COUNT(*) FROM `brave-computer-454217-q4.chicago_taxi_raw.taxi_trips_raw_table`;
-- Debería ser ~6,931,127

-- Verificar datos silver
SELECT COUNT(*) FROM `brave-computer-454217-q4.chicago_taxi_silver.taxi_trips_silver`;
-- Debería ser similar (después de deduplicación)

-- Verificar datos gold
SELECT COUNT(*) FROM `brave-computer-454217-q4.chicago_taxi_gold.daily_summary`;
-- Debería tener ~214 días (junio-diciembre 2023)
```
