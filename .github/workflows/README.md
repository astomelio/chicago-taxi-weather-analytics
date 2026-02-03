# GitHub Actions Workflows

## CI Pipeline (`ci.yml`)

**Cuándo se ejecuta:**
- Push a `main` o `develop`
- Pull Requests a `main` o `develop`

**Qué hace:**
- ✅ Valida código de Terraform
- ✅ Prueba modelos de dbt
- ✅ Lint de código Python

**NO despliega**, solo valida.

---

## CD Pipeline (`cd.yml`)

**Cuándo se ejecuta:**
- Push a `main` (solo cambios en `terraform/`, `functions/`, o el workflow mismo)
- Ejecución manual desde GitHub Actions

**Qué hace:**
1. ✅ Crea ZIP de la Cloud Function
2. ✅ Despliega infraestructura con Terraform
3. ✅ Ejecuta modelos dbt (silver y gold)

**SÍ despliega automáticamente** cuando haces push a main.

---

## Secrets Necesarios en GitHub

Configurar en: `Settings > Secrets and variables > Actions`

1. **`GCP_SA_KEY`** - Service Account JSON key de GCP (para autenticación)
2. **`GCP_PROJECT_ID`** - ID del proyecto de GCP
3. **`DEVELOPER_EMAIL`** - Email para column-level security
4. **`OPENWEATHER_API_KEY`** - (Opcional) API key de clima para fallback

### Crear Service Account para GitHub Actions

```bash
# Crear service account
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account" \
  --project=TU-PROYECTO

# Dar permisos necesarios
gcloud projects add-iam-policy-binding TU-PROYECTO \
  --member="serviceAccount:github-actions-sa@TU-PROYECTO.iam.gserviceaccount.com" \
  --role="roles/owner"

# Crear key JSON
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@TU-PROYECTO.iam.gserviceaccount.com

# Copiar el contenido del JSON y pegarlo en GitHub Secrets como GCP_SA_KEY
```

---

## Flujo de Trabajo

1. **Desarrollo local:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   # Hacer cambios
   git commit -m "Agregar funcionalidad"
   git push origin feature/nueva-funcionalidad
   ```

2. **Crear Pull Request:**
   - CI se ejecuta automáticamente
   - Valida que todo esté correcto

3. **Merge a main:**
   - CI valida el código
   - CD despliega automáticamente a GCP

4. **Resultado:**
   - Infraestructura actualizada
   - Cloud Function desplegada
   - Modelos dbt ejecutados

---

## Ejecución Manual

Puedes ejecutar el CD manualmente desde:
`Actions > CD Pipeline > Run workflow`
