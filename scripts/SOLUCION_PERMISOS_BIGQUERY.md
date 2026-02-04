# Solución: Permisos BigQuery para Datasets Públicos

## El Problema Real

El error "Access Denied" en BigQuery para datasets públicos **NO es un problema de código**. Es un problema de:

1. **Billing no habilitado** en el proyecto
2. **Service Account sin permisos** correctos
3. **Identidad incorrecta** (usando service account sin permisos en lugar de usuario)

## Checklist de Solución

### 1️⃣ Verificar Billing

**BigQuery requiere billing incluso para datasets públicos.**

#### Verificar en GCP Console:
1. Ve a: https://console.cloud.google.com/billing?project=brave-computer-454217-q4
2. Verifica que el proyecto tenga una cuenta de billing vinculada
3. Si no tiene, link una cuenta de billing

#### Verificar desde CLI:
```bash
gcloud billing projects describe brave-computer-454217-q4 \
  --format="value(billingAccountName)"
```

Si está vacío → **NO tiene billing habilitado**

### 2️⃣ Verificar Service Account de Composer

El service account que usa Composer necesita permisos específicos.

#### Obtener el service account de Composer:
```bash
gcloud composer environments describe chicago-taxi-composer \
  --location us-central1 \
  --project brave-computer-454217-q4 \
  --format="value(config.nodeConfig.serviceAccount)"
```

#### Verificar permisos actuales:
```bash
PROJECT_ID="brave-computer-454217-q4"
COMPOSER_SA="<service-account-email>"

gcloud projects get-iam-policy "$PROJECT_ID" \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$COMPOSER_SA" \
  --format="table(bindings.role)"
```

### 3️⃣ Otorgar Permisos Correctos

El service account de Composer necesita estos roles:

```bash
PROJECT_ID="brave-computer-454217-q4"
COMPOSER_SA="<service-account-email>"

# Roles necesarios para BigQuery
for ROLE in \
  "roles/bigquery.user" \
  "roles/bigquery.dataViewer" \
  "roles/bigquery.dataEditor" \
  "roles/bigquery.jobUser"; do
  
  echo "Otorgando $ROLE a $COMPOSER_SA"
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$COMPOSER_SA" \
    --role="$ROLE"
done
```

**Nota**: `roles/bigquery.user` es el más importante - incluye los otros básicos.

### 4️⃣ Verificar Identidad en Código

Si funciona en BigQuery UI pero no en código → problema de credenciales.

#### En Python:
```python
from google.auth import default
credentials, project = default()
print(f"Autenticando con: {credentials.service_account_email}")
```

#### En Airflow:
El DAG usa `BigQueryHook` que usa Application Default Credentials (ADC).
Verifica que el service account de Composer tenga los permisos.

### 5️⃣ Test Rápido

#### Desde BigQuery UI (debe funcionar):
```sql
SELECT COUNT(*) as test
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE DATE(trip_start_timestamp) >= '2023-06-01'
  AND DATE(trip_start_timestamp) <= '2023-12-31'
LIMIT 10;
```

#### Desde CLI (con service account):
```bash
bq query --use_legacy_sql=false \
  --project_id=brave-computer-454217-q4 \
  --location=us-central1 \
  "SELECT COUNT(*) as test FROM \`bigquery-public-data.chicago_taxi_trips.taxi_trips\` LIMIT 1"
```

Si el primero funciona pero el segundo no → **problema de permisos del service account**

## Solución Automática (Workflow)

El workflow `.github/workflows/cd.yml` ahora:

1. ✅ **Verifica billing** antes de continuar
2. ✅ **Otorga permisos** al service account de GitHub Actions
3. ✅ **Obtiene el service account real de Composer** después de crearse
4. ✅ **Otorga permisos** al service account de Composer
5. ✅ **Hace un test** para verificar acceso

## Regla Mental Importante

**En BigQuery, incluso para datasets públicos, siempre necesitas:**

1. ✅ Proyecto con **billing habilitado**
2. ✅ Identidad (usuario o service account) con **permisos BigQuery**

Si falla uno de los dos → **403 Access Denied**

## Troubleshooting

### Error: "Access Denied: Table bigquery-public-data:..."
**Causa**: Service account sin permisos o billing no habilitado
**Solución**: 
1. Verifica billing: https://console.cloud.google.com/billing?project=brave-computer-454217-q4
2. Otorga `roles/bigquery.user` al service account de Composer
3. Espera 2-5 minutos para propagación de permisos

### Error: Funciona en UI pero no en código
**Causa**: Estás usando credenciales diferentes
**Solución**:
1. Verifica qué service account está usando el código
2. Otorga permisos a ese service account específico

### Error: Permisos otorgados pero sigue fallando
**Causa**: Permisos no han propagado aún
**Solución**:
1. Espera 2-5 minutos
2. Verifica que los permisos estén en IAM: https://console.cloud.google.com/iam-admin/iam?project=brave-computer-454217-q4

## Referencias

- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [BigQuery IAM Roles](https://cloud.google.com/bigquery/docs/access-control)
- [Composer Service Accounts](https://cloud.google.com/composer/docs/composer-2/access-control)
