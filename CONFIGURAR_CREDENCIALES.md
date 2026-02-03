# Configurar Credenciales de Google Cloud

Esta guía te ayudará a configurar las credenciales necesarias para probar el sistema con BigQuery público.

## Paso 1: Instalar Google Cloud SDK (gcloud CLI)

### macOS (con Homebrew - Recomendado)

```bash
brew install google-cloud-sdk
```

### macOS (Instalación Manual)

1. Descarga el instalador desde: https://cloud.google.com/sdk/docs/install
2. Ejecuta el instalador
3. Sigue las instrucciones en pantalla

### Verificar Instalación

```bash
gcloud --version
```

Deberías ver algo como:
```
Google Cloud SDK 450.0.0
```

## Paso 2: Autenticación en Google Cloud

### Opción A: Usar el Script Automático (Más Fácil)

```bash
./scripts/setup_credentials.sh
```

Este script:
- Te autenticará en GCP
- Configurará Application Default Credentials (necesario para Python)
- Configurará el proyecto

### Opción B: Configuración Manual

#### 2.1. Autenticación Básica

```bash
gcloud auth login
```

Esto abrirá tu navegador para que inicies sesión con tu cuenta de Google.

#### 2.2. Application Default Credentials (Para Python)

```bash
gcloud auth application-default login
```

**Importante**: Esto es necesario para que las aplicaciones Python puedan acceder a BigQuery sin necesidad de un archivo de credenciales.

#### 2.3. Configurar Proyecto

```bash
# Listar proyectos disponibles
gcloud projects list

# Configurar proyecto
gcloud config set project TU-PROYECTO-ID
```

**Nota**: Puedes usar cualquier proyecto de GCP para acceder a datasets públicos de BigQuery. Si no tienes un proyecto, puedes crear uno en: https://console.cloud.google.com/

## Paso 3: Verificar Configuración

```bash
# Ver cuenta autenticada
gcloud auth list

# Ver proyecto configurado
gcloud config get-value project

# Verificar credenciales de aplicación
gcloud auth application-default print-access-token
```

## Paso 4: Configurar Variables de Entorno

```bash
# Configurar PROJECT_ID
export GCP_PROJECT_ID="tu-proyecto-gcp"
export PROJECT_ID="tu-proyecto-gcp"

# Para hacerlo permanente, agrégalo a ~/.zshrc o ~/.bashrc
echo 'export GCP_PROJECT_ID="tu-proyecto-gcp"' >> ~/.zshrc
echo 'export PROJECT_ID="tu-proyecto-gcp"' >> ~/.zshrc
```

## Paso 5: Probar que Funciona

```bash
# Activar entorno virtual (si lo creaste)
source venv_test/bin/activate

# Probar acceso a BigQuery
python3 scripts/test_bigquery_direct.py
```

## Solución de Problemas

### Error: "Your default credentials were not found"

**Solución**: Ejecuta:
```bash
gcloud auth application-default login
```

### Error: "Project not found"

**Solución**: Verifica que el proyecto existe:
```bash
gcloud projects list
gcloud config set project TU-PROYECTO-ID
```

### Error: "Permission denied"

**Solución**: Asegúrate de que tu cuenta tenga permisos en el proyecto. Para datasets públicos, solo necesitas estar autenticado.

### No tengo un proyecto de GCP

**Solución**: 
1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto (es gratis)
3. Usa ese PROJECT_ID en la configuración

**Nota**: Para acceder a datasets públicos de BigQuery, no necesitas habilitar facturación, solo estar autenticado.

## Alternativa: Probar sin Credenciales

Si prefieres no configurar credenciales ahora, puedes probar la query directamente en BigQuery Console:

1. Ve a: https://console.cloud.google.com/bigquery
2. Copia la query de `scripts/test_bigquery_weather.sql`
3. Pégala y ejecútala

Esto te permitirá verificar que los datos existen sin necesidad de configurar credenciales localmente.
