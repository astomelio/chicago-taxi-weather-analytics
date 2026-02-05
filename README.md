# Orbidi Data Engineer - Chicago Taxi Trips Analysis

**Esta prueba tiene 2 puntos:**
- **Punto 1**: Documentación y diseño → ver `Part1_Architecture_Design.md`
- **Punto 2**: Implementación técnica → se explica en este README

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
│   └── cargar_historicos_via_gcs.sh
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

4. **Cargar datos históricos (una vez)**:
   - Ve a Airflow UI (el link aparece en los logs de GitHub Actions)
   - Trigger el DAG `chicago_taxi_historical_ingestion`
   - Espera a que complete (puede tardar 20-30 minutos)
   
   El pipeline diario se ejecutará automáticamente después de cargar los históricos

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

1. **Crear Service Account en GCP** (ver `CONFIGURAR_GITHUB.md`)

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

### Dashboard en Looker Studio

**Link del dashboard**: https://lookerstudio.google.com/s/qfSVoIMVddw  
En este link se encuentra el dashboard del proyecto que muestra el análisis de la relación entre clima y duración de viajes.

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

## Estructura de la prueba

### Punto 1
- Documento y diseño en `Part1_Architecture_Design.md`
- Guía del diagrama en `Part1_Diagram_Guide.txt`

### Punto 2 (este README)
- Código en GitHub + Dashboard en Looker Studio
- Análisis de relación entre clima y duración de viajes en taxis de Chicago
- Estado: ✅ Implementado y funcionando

#### Tablas y resultados (resumen)

**Tablas principales**
- **Raw**:
  - `chicago_taxi_raw.taxi_trips_raw_table` (taxis 2023-06 a 2023-12)
  - `chicago_taxi_raw.weather_data` (NOAA 2023-06 a 2023-12)
- **Silver**:
  - `chicago_taxi_silver.taxi_trips_silver`
  - `chicago_taxi_silver.weather_silver`
- **Gold**:
  - `chicago_taxi_gold.daily_summary`
  - `chicago_taxi_gold.taxi_weather_analysis`

**Conteos (aprox.)**
- `taxi_trips_silver`: **3,808,846**
- `weather_silver`: **214**
- `daily_summary`: **214**
- `taxi_weather_analysis`: **5,136**

**dbt tests**
- **Total**: 7 tests
- **Resultado**: ✅ Todos pasan
- **Cobertura**: `not_null` y `unique` en claves y fechas principales

## Autor

Desarrollado para la prueba técnica de Data Engineer de Orbidi.
