# Guía de Setup Completo

Esta guía te permitirá clonar el repositorio y desplegar TODO automáticamente en tu cuenta de Google Cloud.

## Requisitos Previos

1. **Cuenta de Google Cloud Platform** con facturación habilitada
2. **Cuenta de GitHub** (para GitHub Actions)
3. **Proyecto de GCP** creado

## Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repo>
cd prueba_orbidi
```

## Paso 2: Crear Service Account en GCP

Este Service Account será usado por GitHub Actions para desplegar la infraestructura.

```bash
# Configurar proyecto
export GCP_PROJECT_ID="tu-proyecto-gcp"
gcloud config set project $GCP_PROJECT_ID

# Crear Service Account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account" \
  --project=$GCP_PROJECT_ID

# Dar permisos necesarios
# Owner para crear recursos de infraestructura
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/owner"

# Permiso específico para acceder a datasets públicos de BigQuery
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# Crear key JSON
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# Mostrar el contenido del JSON (copiar todo)
cat github-actions-key.json
```

## Paso 3: Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Ve a: `Settings > Secrets and variables > Actions`
3. Agrega los siguientes secrets:

### Secrets Requeridos:

- **`GCP_SA_KEY`**: Contenido completo del archivo `github-actions-key.json` (todo el JSON)
- **`GCP_PROJECT_ID`**: Tu proyecto de GCP (ej: `mi-proyecto-gcp`)
- **`DEVELOPER_EMAIL`**: Tu email (ej: `tu-email@gmail.com`)

### Secrets Opcionales:

- **`OPENWEATHER_API_KEY`**: API key de clima (opcional, solo si quieres fallback)
- **`GCP_REGION`**: Región de GCP (default: `us-central1`)

## Paso 4: Hacer Push a Main

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

## Paso 5: Verificar Despliegue

GitHub Actions automáticamente:

1. ✅ Crea ZIP de la Cloud Function
2. ✅ Habilita APIs necesarias
3. ✅ Ejecuta `terraform apply`
4. ✅ Crea toda la infraestructura
5. ✅ Ejecuta modelos dbt

### Ver el Progreso:

Ve a: `Actions` en tu repositorio de GitHub para ver el progreso del despliegue.

### Verificar Recursos Creados:

Una vez completado, verifica en GCP:

- **BigQuery**: https://console.cloud.google.com/bigquery?project=TU-PROYECTO
- **Cloud Functions**: https://console.cloud.google.com/functions?project=TU-PROYECTO
- **Cloud Scheduler**: https://console.cloud.google.com/cloudscheduler?project=TU-PROYECTO

## ¿Qué se Crea Automáticamente?

✅ **BigQuery Datasets**:
   - `chicago_taxi_raw`
   - `chicago_taxi_silver`
   - `chicago_taxi_gold`

✅ **Tablas**:
   - `weather_data` (en raw)
   - `taxi_trips_raw` (vista, si hay permisos)

✅ **Cloud Function**:
   - `weather-ingestion`
   - Configurada para ingerir datos del clima

✅ **Cloud Scheduler**:
   - `weather-ingestion-daily`
   - Ejecuta diariamente a las 2 AM UTC

✅ **Service Account**:
   - `weather-ingestion-sa`
   - Con permisos necesarios

✅ **Cloud Storage**:
   - Bucket para código de función

## Solución de Problemas

### Error: "Billing not enabled"
- Habilita facturación en: https://console.cloud.google.com/billing

### Error: "API not enabled"
- El workflow habilita las APIs automáticamente
- Si falla, habilita manualmente desde la consola

### Error: "Permission denied"
- Verifica que el Service Account tenga rol `roles/owner`
- Verifica que el JSON key esté correcto en GitHub Secrets

### Vista taxi_trips_raw no se crea
- No es crítico, el sistema funciona sin ella
- Los modelos dbt consultan directamente el dataset público
- Puedes crearla manualmente desde BigQuery console si lo deseas

## Verificar que Todo Funciona

```bash
# Ver recursos en Terraform
cd terraform
terraform state list

# Ver outputs
terraform output

# Probar Cloud Function (desde GCP console o gcloud)
gcloud functions call weather-ingestion \
  --region=us-central1 \
  --gen2 \
  --data '{"mode":"test"}'
```

## Próximos Pasos

1. **Ingesta Histórica de Datos del Clima**:
   - Ejecuta la función manualmente con modo histórico
   - O espera a que Cloud Scheduler ejecute la ingesta diaria

2. **Ejecutar Modelos dbt**:
   ```bash
   cd dbt
   dbt run --models silver gold
   ```

3. **Crear Dashboard en Looker Studio**:
   - Sigue las instrucciones en `DASHBOARD_SETUP.md`
