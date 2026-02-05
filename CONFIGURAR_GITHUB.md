# 🔗 Configurar GitHub Actions para GCP

## Paso 1: Configurar Secrets en GitHub

1. Ve a tu repositorio en GitHub
2. Ve a: `Settings` > `Secrets and variables` > `Actions`
3. Click en `New repository secret`

### Secret 1: GCP_SA_KEY
- **Name**: `GCP_SA_KEY`
- **Value**: Copia TODO el contenido del archivo `github-actions-key.json`
  ```bash
  cat github-actions-key.json
  ```
  Copia todo el JSON y pégalo en el secret.

### Secret 2: GCP_PROJECT_ID
- **Name**: `GCP_PROJECT_ID`
- **Value**: `chicago-taxi-48702`

### Secret 3: DEVELOPER_EMAIL
- **Name**: `DEVELOPER_EMAIL`
- **Value**: Tu email (ej: `tu-email@gmail.com`)

### Secret 4 (Opcional): OPENWEATHER_API_KEY
- **Name**: `OPENWEATHER_API_KEY`
- **Value**: Tu API key de clima (opcional)

## Paso 2: Ejecutar el Workflow

### Opción A: Automático (Push)
```bash
git add .
git commit -m "Trigger GitHub Actions"
git push origin main
```

### Opción B: Manual
1. Ve a la pestaña `Actions` en GitHub
2. Selecciona "CD Pipeline - Deploy Infrastructure"
3. Click en "Run workflow" > "Run workflow"

## Paso 3: Verificar

El workflow creará automáticamente:
- ✅ Infraestructura en GCP (BigQuery, Cloud Functions, etc.)
- ✅ Ingesta histórica de datos de clima
- ✅ Tablas silver y gold
- ✅ Todo listo para Looker Studio

Verifica en: `Actions` > Ver los logs del workflow
