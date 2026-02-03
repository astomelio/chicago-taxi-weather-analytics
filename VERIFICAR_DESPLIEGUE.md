# Cómo Verificar que el Despliegue Automático Funciona

Este documento explica **cómo saber** que el sistema se desplegó correctamente cuando alguien clona el repo y hace push.

## ✅ Verificación Automática en GitHub Actions

### 1. Ver el Workflow en GitHub

1. Ve a tu repositorio en GitHub
2. Click en la pestaña **"Actions"**
3. Busca el workflow **"CD Pipeline - Deploy Infrastructure"**
4. Click en la ejecución más reciente

### 2. Verificar que Todos los Jobs Pasaron

Debes ver 3 jobs, todos con ✅ verde:

1. **✅ prepare-function-zip** - Crea el ZIP de la función
2. **✅ deploy-terraform** - Despliega la infraestructura
3. **✅ deploy-dbt** - Ejecuta los modelos dbt

### 3. Verificar Outputs de Terraform

En el job `deploy-terraform`, al final debe aparecer:

```
Outputs:

gold_dataset_id = "chicago_taxi_gold"
raw_dataset_id = "chicago_taxi_raw"
scheduler_job_name = "weather-ingestion-daily"
silver_dataset_id = "chicago_taxi_silver"
weather_ingestion_function_url = "https://..."
```

## ✅ Verificación Manual en GCP Console

### 1. Verificar BigQuery

**URL**: https://console.cloud.google.com/bigquery?project=TU-PROYECTO

**Debes ver:**
- ✅ Dataset `chicago_taxi_raw`
  - Tabla `weather_data`
- ✅ Dataset `chicago_taxi_silver`
  - Tabla `taxi_trips_silver`
  - Tabla `weather_silver`
- ✅ Dataset `chicago_taxi_gold`
  - Tabla `taxi_weather_analysis`
  - Tabla `daily_summary`

### 2. Verificar Cloud Functions

**URL**: https://console.cloud.google.com/functions?project=TU-PROYECTO

**Debes ver:**
- ✅ Función `weather-ingestion`
- ✅ Estado: **ACTIVA**
- ✅ URL: `https://weather-ingestion-XXXXX-uc.a.run.app`

### 3. Verificar Cloud Scheduler

**URL**: https://console.cloud.google.com/cloudscheduler?project=TU-PROYECTO

**Debes ver:**
- ✅ Job `weather-ingestion-daily`
- ✅ Estado: **ENABLED**
- ✅ Horario: `0 2 * * *` (2 AM UTC diario)
- ✅ Target: URL de la Cloud Function

### 4. Verificar Cloud Storage

**URL**: https://console.cloud.google.com/storage/browser?project=TU-PROYECTO

**Debes ver:**
- ✅ Bucket: `TU-PROYECTO-function-source`
- ✅ Archivo: `weather-ingestion-source.zip`

### 5. Verificar Service Account

**URL**: https://console.cloud.google.com/iam-admin/serviceaccounts?project=TU-PROYECTO

**Debes ver:**
- ✅ `weather-ingestion-sa@TU-PROYECTO.iam.gserviceaccount.com`
- ✅ Con roles: `BigQuery Data Editor`, `BigQuery Job User`, `BigQuery Data Viewer`

## ✅ Verificación con Terraform (Opcional)

Si tienes acceso local con credenciales:

```bash
cd terraform
terraform state list
```

**Debes ver ~14 recursos:**
- `google_bigquery_dataset.*` (3)
- `google_bigquery_table.*` (2)
- `google_cloudfunctions2_function.*` (1)
- `google_cloud_scheduler_job.*` (1)
- `google_service_account.*` (1)
- `google_project_iam_member.*` (3)
- `google_storage_bucket.*` (1)
- `google_storage_bucket_object.*` (1)
- `google_data_catalog_*` (2)

## ✅ Verificación Funcional

### Probar Cloud Function

```bash
# Obtener URL desde Terraform output o GCP console
curl -X POST https://weather-ingestion-XXXXX-uc.a.run.app \
  -H "Content-Type: application/json" \
  -d '{"mode":"test"}'
```

**Respuesta esperada:**
- Si no autenticado: `403 Forbidden` (normal, requiere auth)
- Si autenticado: JSON con resultado

### Verificar que Cloud Scheduler Está Programado

En GCP Console > Cloud Scheduler:
- El job debe estar **ENABLED**
- Puedes hacer click en **"RUN NOW"** para probarlo manualmente

## ❌ Qué Hacer si Algo Falla

### Error: "Billing not enabled"
- Habilita facturación en: https://console.cloud.google.com/bigquery?project=TU-PROYECTO

### Error: "API not enabled"
- El workflow habilita APIs automáticamente
- Si falla, habilita manualmente desde: https://console.cloud.google.com/apis

### Error: "Permission denied"
- Verifica que el Service Account tenga rol `roles/owner`
- Verifica que el JSON key esté correcto en GitHub Secrets

### Vista taxi_trips_raw no se crea
- **No es crítico**, el sistema funciona sin ella
- Los modelos dbt consultan directamente el dataset público
- Puedes crearla manualmente desde BigQuery console si lo deseas

## 📊 Resumen de Verificación

| Componente | Cómo Verificar | Estado Esperado |
|------------|---------------|-----------------|
| GitHub Actions | Actions > CD Pipeline | ✅ Todos los jobs verdes |
| BigQuery | Console > BigQuery | ✅ 3 datasets creados |
| Cloud Functions | Console > Functions | ✅ weather-ingestion activa |
| Cloud Scheduler | Console > Scheduler | ✅ weather-ingestion-daily ENABLED |
| Cloud Storage | Console > Storage | ✅ Bucket con ZIP |
| Service Account | Console > IAM | ✅ weather-ingestion-sa con roles |

## ✅ Confirmación Final

**Si TODOS estos elementos están presentes, el despliegue fue exitoso:**

1. ✅ GitHub Actions completó sin errores
2. ✅ BigQuery tiene los 3 datasets
3. ✅ Cloud Function está activa
4. ✅ Cloud Scheduler está ENABLED
5. ✅ Service Account tiene permisos

**El sistema está funcionando y Cloud Scheduler ejecutará la función diariamente a las 2 AM UTC.**
