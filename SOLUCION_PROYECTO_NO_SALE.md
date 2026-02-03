# 🔧 Solución: El Proyecto No Sale en Looker Studio

## Problema

No puedes ver el proyecto `brave-computer-454217-q4` en Looker Studio cuando intentas conectar a BigQuery.

## 🔍 Verificar el Proyecto Correcto

### Paso 1: Ver qué proyectos tienes

Ejecuta en tu terminal:
```bash
gcloud projects list
```

Esto te mostrará todos los proyectos de GCP a los que tienes acceso.

### Paso 2: Verificar el proyecto actual

```bash
gcloud config get-value project
```

Este es el proyecto que estás usando actualmente.

## ✅ Soluciones

### Solución 1: Usar el Proyecto Correcto

Si el proyecto que aparece en la lista es diferente a `brave-computer-454217-q4`:

1. **En Looker Studio**, cuando seleccionas "BigQuery project":
   - Busca en la lista el proyecto que aparece en `gcloud projects list`
   - Selecciona ese proyecto
   - Luego busca el dataset `chicago_taxi_gold`
   - Y la tabla `daily_summary`

### Solución 2: Verificar Permisos

Si el proyecto no aparece en Looker Studio:

1. **Verifica que tengas acceso al proyecto**:
   ```bash
   gcloud projects get-iam-policy brave-computer-454217-q4
   ```

2. **Verifica que puedas acceder a BigQuery**:
   - Ve a: https://console.cloud.google.com/bigquery?project=brave-computer-454217-q4
   - Si puedes ver los datasets, tienes acceso

3. **En Looker Studio**:
   - Asegúrate de estar logueado con la misma cuenta de Google
   - Si no aparece, puede que necesites permisos adicionales

### Solución 3: Usar el Proyecto que Sí Tienes

Si tienes otro proyecto donde desplegaste todo:

1. **Identifica el proyecto correcto**:
   ```bash
   cd terraform
   terraform output
   ```
   
   Esto te mostrará el proyecto que está configurado en Terraform.

2. **En Looker Studio**, usa ese proyecto en lugar de `brave-computer-454217-q4`

### Solución 4: Verificar que los Datasets Existan

Aunque el proyecto no aparezca, puedes intentar:

1. **En Looker Studio**, cuando seleccionas BigQuery:
   - Si no ves el proyecto en la lista, puede que necesites:
     - Esperar unos minutos (a veces tarda en aparecer)
     - Refrescar la página
     - Cerrar y volver a abrir Looker Studio

2. **Alternativa**: Conectar directamente usando el path completo:
   - En Looker Studio, busca la opción "Custom Query" o "SQL"
   - Usa: `brave-computer-454217-q4.chicago_taxi_gold.daily_summary`

## 🎯 Pasos Recomendados

1. **Ejecuta**:
   ```bash
   gcloud projects list
   ```

2. **Copia el Project ID** que aparece (puede ser diferente a `brave-computer-454217-q4`)

3. **En Looker Studio**:
   - Busca ese Project ID en la lista
   - Selecciona ese proyecto
   - Luego busca: `chicago_taxi_gold` > `daily_summary`

## ❓ Si Nada Funciona

1. **Verifica en BigQuery Console**:
   - Ve a: https://console.cloud.google.com/bigquery
   - ¿Puedes ver el proyecto y los datasets?
   - Si no, el problema es de permisos

2. **Verifica la cuenta de Google**:
   - En Looker Studio, asegúrate de estar logueado con la misma cuenta
   - La misma que usaste para crear el proyecto en GCP

3. **Contacta al administrador del proyecto**:
   - Si el proyecto es de otra persona/organización
   - Necesitas que te den acceso explícito

## 📋 Información Útil

Para obtener información del proyecto configurado:
```bash
cd terraform
terraform output
```

Esto te mostrará el `project_id` que está usando Terraform.
