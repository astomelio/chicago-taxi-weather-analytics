# Orbidi Data Engineer Challenge - Chicago Taxi Trips Analysis

## Descripción del Proyecto

Este proyecto analiza la relación entre las condiciones climáticas y la duración de los viajes en taxis de Chicago. El alcalde de Chicago sospecha que el clima afecta la duración de los viajes, por lo que se ha desarrollado un dashboard en Looker Studio para explorar esta hipótesis.

## Arquitectura

### Componentes Principales

1. **Ingesta de Datos**
   - **Datos de Taxis**: Extraídos directamente de BigQuery (dataset público de Chicago)
   - **Datos del Clima**: Obtenidos desde dataset público de NOAA en BigQuery (bigquery-public-data.noaa_gsod)
   - Pipeline programado con Cloud Scheduler y Cloud Functions

2. **Almacenamiento**
   - **BigQuery**: Data warehouse para almacenar datos raw y transformados
   - Capas de datos: Raw (Bronze) → Silver → Gold

3. **Transformación**
   - **dbt**: Herramienta para transformaciones y modelado de datos
   - Eliminación de duplicados en capa Silver
   - Agregaciones y joins en capa Gold

4. **Visualización**
   - **Looker Studio**: Dashboard interactivo para análisis

5. **Seguridad**
   - Column-level security para `payment_type` (solo accesible por el email del desarrollador)

## Estructura del Proyecto

```
.
├── terraform/              # Infraestructura como código
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
├── dbt/                    # Transformaciones de datos
│   ├── models/
│   ├── profiles.yml
│   └── dbt_project.yml
├── functions/              # Cloud Functions
│   └── weather_ingestion/
├── scripts/               # Scripts auxiliares
│   └── setup.sh
├── .github/               # CI/CD
│   └── workflows/
└── README.md
```

## 🚀 Inicio Rápido - Despliegue Automático

**Para desplegar TODO automáticamente en tu cuenta de Google Cloud:**

1. **Clonar el repositorio**
2. **Configurar Secrets en GitHub** (ver [SETUP.md](SETUP.md))
3. **Hacer push a main**
4. **GitHub Actions despliega TODO automáticamente**

📖 **Guía completa**: Ver [SETUP.md](SETUP.md)

---

## Requisitos Previos

- Cuenta de Google Cloud Platform con proyecto activo y facturación habilitada
- Cuenta de GitHub (para despliegue automático)
- (Opcional) API key de clima solo si BigQuery público no tiene datos para alguna fecha

## Configuración Inicial

### Opción 1: Despliegue Automático con GitHub Actions (Recomendado)

**Pasos:**

1. **Crear Service Account en GCP** (ver [SETUP.md](SETUP.md#paso-2-crear-service-account-en-gcp))

2. **Configurar Secrets en GitHub**:
   - Ve a: `Settings > Secrets and variables > Actions`
   - Agrega: `GCP_SA_KEY`, `GCP_PROJECT_ID`, `DEVELOPER_EMAIL`
   - (Opcional): `OPENWEATHER_API_KEY`, `GCP_REGION`

3. **Hacer push a main**:
   ```bash
   git push origin main
   ```

**GitHub Actions automáticamente:**
- ✅ Habilita APIs necesarias
- ✅ Crea ZIP de la función
- ✅ Ejecuta `terraform apply`
- ✅ Despliega toda la infraestructura
- ✅ Ejecuta modelos dbt

### Opción 2: Despliegue Manual (Alternativa)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 3. Configurar dbt

```bash
cd dbt
dbt deps
dbt debug
```

### 4. Ejecutar Ingesta de Datos del Clima

**Modo Histórico** (primera ejecución - ingesta todos los datos de junio-diciembre 2023):
```bash
python functions/weather_ingestion/main.py --historical
```

**Modo Diario** (ejecución diaria - ingesta solo el día anterior):
```bash
python functions/weather_ingestion/main.py
```

### 5. Ejecutar Transformaciones dbt

```bash
cd dbt
dbt run --models silver
dbt run --models gold
dbt test
```

### 6. Crear Dashboard en Looker Studio

Sigue las instrucciones en [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) para crear el dashboard.

**Nota**: Una vez creado, compartir el dashboard con:
- alejandro@astrafy.io
- felipe.bereilh@orbidi.com

Y agregar el link en este README.

## Filtros de Datos

- **Período de análisis**: 01/06/2023 - 31/12/2023 (6 meses)
- **Fuente de taxis**: BigQuery Public Dataset `bigquery-public-data.chicago_taxi_trips.taxi_trips`
- **Datos del clima**: 
  - Fuente: Dataset público de NOAA en BigQuery (bigquery-public-data.noaa_gsod)
  - Históricos: 01/06/2023 - 31/12/2023 (6 meses, para mantener queries en tier gratuito)
  - Diarios: Se ingieren automáticamente cada día (aunque no se usen en el dashboard)

## Pipeline de Datos

### Flujo de Datos

1. **Raw Layer (Bronze)**
   - Datos de taxis extraídos de BigQuery público
   - Datos del clima obtenidos desde dataset público de NOAA en BigQuery

2. **Silver Layer**
   - Limpieza y deduplicación de datos
   - Validación de esquemas
   - Enriquecimiento con metadatos

3. **Gold Layer**
   - Agregaciones por día/hora
   - Joins entre taxis y clima
   - Métricas calculadas (duración promedio, etc.)

### Automatización

- **GitHub Actions**: Despliega automáticamente cuando haces push a `main`
  - CI: Valida código en PRs
  - CD: Despliega infraestructura y ejecuta dbt en `main`
- **Cloud Scheduler**: Ejecuta la función de ingesta diaria a las 02:00 AM UTC
- **Cloud Functions**: Procesa la ingesta de datos del clima
- **dbt**: Transformaciones ejecutadas manualmente o vía CI/CD

**Nota sobre escalabilidad**: Para esta prueba, Cloud Scheduler es suficiente. Si en el futuro se requieren múltiples ingestas diarias, procesos en batch complejos, o dependencias entre tareas, se recomienda migrar a Cloud Composer (Apache Airflow) para una orquestación más robusta.

## Seguridad

- Column-level security implementada para `payment_type`
- Solo el email del desarrollador tiene acceso a esta columna
- Implementado mediante políticas de seguridad de BigQuery

## CI/CD

El proyecto incluye pipelines de CI/CD con GitHub Actions para:
- Validación de código Terraform
- Tests de modelos dbt
- Linting y formateo de código

## Costos

Al usar solo 6 meses de datos (junio-diciembre 2023), las consultas permanecen dentro del tier gratuito de Google Cloud para proyectos nuevos.

## Autor

Desarrollado como parte del desafío técnico de Data Engineer de Orbidi.
