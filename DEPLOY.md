# Guía de Despliegue con Terraform

## Flujo Correcto de Terraform

Terraform funciona así:
1. **`terraform init`** - Inicializa el proyecto (descarga providers)
2. **`terraform plan`** - Muestra qué se va a crear (OPCIONAL pero recomendado)
3. **`terraform apply`** - **Crea TODO automáticamente**

## Pasos para Desplegar

### 1. Preparar archivos

```bash
./scripts/prepare_deploy.sh
```

Esto crea el ZIP de la Cloud Function.

### 2. Configurar variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores
```

### 3. Inicializar Terraform

```bash
terraform init
```

### 4. Ver qué se va a crear (opcional)

```bash
terraform plan
```

### 5. Crear todo

```bash
terraform apply
```

Terraform te preguntará si quieres continuar. Responde `yes` o usa `-auto-approve`:

```bash
terraform apply -auto-approve
```

## ¿Qué crea Terraform?

- ✅ BigQuery Datasets (raw, silver, gold)
- ✅ Tablas y vistas
- ✅ Cloud Storage Bucket
- ✅ Service Account con permisos
- ✅ Cloud Function
- ✅ Cloud Scheduler (ejecuta diariamente a las 2 AM UTC)
- ✅ Permisos IAM

## Notas Importantes

1. **La vista de taxi_trips_raw** se crea usando las credenciales del usuario que ejecuta Terraform (no del service account). Asegúrate de estar autenticado con `gcloud auth application-default login`.

2. **Si la Cloud Function ya existe**, Terraform la actualizará automáticamente.

3. **El Cloud Scheduler** se crea automáticamente y ejecuta la función todos los días a las 2 AM UTC.

4. **Para ingesta histórica**, puedes ejecutar la función manualmente desde la consola de GCP o usando:
   ```bash
   gcloud functions call weather-ingestion --region=us-central1 --data '{"mode":"historical"}'
   ```

## Verificar Despliegue

```bash
# Ver outputs
terraform output

# Ver recursos creados
terraform state list
```
