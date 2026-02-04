# Orbidi Data Engineer Challenge - Chicago Taxi Trips Analysis

> **Nota sobre el Desafío**: Este desafío consta de dos partes:
> - **Part 1: Design Challenge** - Requiere un diagrama de arquitectura en PDF (entregable separado)
> - **Part 2: Coding Challenge** - Este repositorio implementa la solución de código
> 
> Ver `Orbidi Data Engineer Technical Challenge.pdf` para los detalles completos del desafío.

## Descripción del Proyecto

Este proyecto analiza la relación entre las condiciones climáticas y la duración de los viajes en taxis de Chicago. El alcalde de Chicago sospecha que el clima afecta la duración de los viajes, por lo que se ha desarrollado un dashboard en Looker Studio para explorar esta hipótesis.

**Este repositorio implementa el Part 2: Coding Challenge del desafío técnico de Orbidi.**

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
├── airflow/                # Orquestación con Airflow (RECOMENDADO)
│   └── dags/
│       ├── chicago_taxi_pipeline.py
│       └── requirements.txt
├── functions/              # Cloud Functions
│   └── weather_ingestion/
├── scripts/               # Scripts auxiliares
│   ├── setup_airflow.sh
│   └── verify_tables.py
├── .github/               # CI/CD (solo para infraestructura)
│   └── workflows/
└── README.md
```

## 🚀 Inicio Rápido - Todo Automático

**GitHub Actions hace TODO automáticamente:**

1. **Configurar Secrets en GitHub**:
   - Ve a: `Settings > Secrets and variables > Actions`
   - Agrega: `GCP_SA_KEY`, `GCP_PROJECT_ID`, `DEVELOPER_EMAIL`
   - (Opcional): `OPENWEATHER_API_KEY`, `GCP_REGION`

2. **Hacer push a main**:
   ```bash
   git push origin main
   ```

3. **GitHub Actions automáticamente**:
   - ✅ Despliega infraestructura con Terraform (BigQuery, Cloud Functions, etc.)
   - ✅ Crea entorno de Cloud Composer (si no existe)
   - ✅ Sube DAGs de Airflow
   - ✅ Sube código dbt
   - ✅ Configura variables de Airflow
   - ✅ **TODO queda listo para usar**

4. **Último paso manual (una vez)**:
   - Ve a Airflow UI (el link aparece en los logs de GitHub Actions)
   - Trigger el DAG `chicago_taxi_historical_ingestion`
   - El pipeline diario se ejecutará automáticamente después

📖 **Guía completa de Airflow**: Ver [airflow/README.md](airflow/README.md)

### ¿Quién hace qué?

- **Terraform (via GitHub Actions)**: Crea infraestructura (BigQuery, Cloud Functions, Cloud Scheduler)
- **GitHub Actions**: Configura Airflow automáticamente (crea Composer, sube DAGs, configura variables)
- **Airflow**: Ejecuta el pipeline de datos (ingesta, transformaciones dbt)
- **Tú**: Solo necesitas trigger el DAG histórico una vez

---

## Requisitos Previos

- Cuenta de Google Cloud Platform con proyecto activo y facturación habilitada
- Cuenta de GitHub (para despliegue automático)
- (Opcional) API key de clima solo si BigQuery público no tiene datos para alguna fecha

## Configuración Inicial

### Opción 1: Pipeline con Airflow (Recomendado para Datos)

Ver [airflow/README.md](airflow/README.md) para instrucciones completas.

### Opción 2: Despliegue de Infraestructura con GitHub Actions

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

## Estructura del Desafío

Este proyecto corresponde al **Part 2: Coding Challenge** del desafío técnico de Orbidi.

### Part 1: Design Challenge
- **Entregable**: Diagrama de arquitectura en PDF
- **Tema**: Diseño de solución analítica para cliente con múltiples fuentes de datos
  - Fuentes: PostgreSQL, MySQL, MongoDB, SAP, Salesforce, SurveyMonkey
  - Objetivos: BI dashboards y modelos ML
  - Requisitos: Data mesh, GitOps, DataOps, Google Cloud, tecnologías open-source
  - Dominios de datos: customers, products, maisons (extensible)
  - Gobernanza federada: acceso, observabilidad, catálogo
- **Estado**: 📋 **DISEÑO COMPLETADO** - Ver documentación en `Part1_Architecture_Design.md`
- **Guía para diagrama**: Ver `Part1_Diagram_Guide.txt` para crear el diagrama en draw.io
- **Ubicación esperada**: `Part1_Architecture_Diagram.pdf` (crear desde la guía)

### Part 2: Coding Challenge (Este Repositorio)
- **Entregable**: Código en GitHub + Dashboard en Looker Studio
- **Tema**: Análisis de relación entre clima y duración de viajes en taxis de Chicago
- **Requisitos**: Terraform, dbt, automatización, BigQuery, Looker Studio
- **Estado**: ✅ Implementado y funcionando

## Autor

Desarrollado como parte del desafío técnico de Data Engineer de Orbidi.
