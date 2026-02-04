# Part 1: Design Challenge - Arquitectura de Solución Analítica

## Resumen Ejecutivo

Solución de arquitectura de datos basada en **Data Mesh** para un cliente con múltiples fuentes de datos, diseñada para servir dashboards de BI y modelos ML, utilizando Google Cloud Platform y tecnologías open-source con enfoque en GitOps y DataOps.

## Principios de Diseño

- **Data Mesh**: Arquitectura descentralizada con dominios de datos autónomos
- **GitOps/DataOps**: Automatización completa mediante CI/CD
- **Open Source First**: Priorizar tecnologías open-source
- **Escalabilidad**: Diseño extensible para nuevos dominios y fuentes
- **Gobernanza Federada**: Control descentralizado con estándares centralizados

---

## Componentes de la Arquitectura

### 1. Capa de Ingesta de Datos (Data Ingestion Layer)

#### 1.1 Fuentes de Datos

**Bases de Datos Transaccionales:**
- **PostgreSQL** → CDC (Change Data Capture) con Debezium
- **MySQL** → CDC con Debezium
- **MongoDB** → Change Streams API

**Aplicaciones:**
- **SAP** → SAP Data Services / SAP BW Extractors
- **Salesforce** → Salesforce API / MuleSoft
- **SurveyMonkey** → REST API

#### 1.2 Componentes de Ingesta

**Para Batch (Datos históricos y diarios):**
- **Airbyte** (open-source) - ETL moderno, fácil de usar
- **Cloud Data Fusion** (Google Cloud, basado en CDAP open-source)
- **Cloud Storage** - Almacenamiento temporal de datos extraídos

**Para Streaming (Cambios en tiempo real):**
- **Cloud Pub/Sub** - Cola de mensajes para eventos
- **Dataflow** (Apache Beam) - Procesamiento de streams
- **Debezium** (open-source) - Change Data Capture (CDC) para bases de datos
  - **¿Qué es Debezium?** Es una herramienta que detecta cambios en bases de datos (INSERT, UPDATE, DELETE) y los convierte en eventos de streaming. Útil para mantener datos sincronizados en tiempo real.
  - **Alternativa más simple:** Usar Airbyte también para streaming o hacer extracciones incrementales diarias

**Para APIs REST:**
- **Cloud Functions** - Funciones serverless para llamar APIs
- **Cloud Scheduler** - Programar llamadas periódicas

**Flujo:**
```
Fuentes → [CDC/API/Extractors] → Pub/Sub/Storage → Data Lake
```

**Nota:** Para el diseño del desafío, puedes simplificar usando principalmente **Airbyte** para todo tipo de ingesta (batch y streaming), que es más fácil de entender y mantener.

---

### 2. Data Lake (Bronze Layer)

**Componente:** Google Cloud Storage (GCS)

**Estructura:**
```
gs://data-lake/
├── bronze/
│   ├── customers/
│   │   ├── postgresql/
│   │   ├── salesforce/
│   │   └── sap/
│   ├── products/
│   │   ├── mysql/
│   │   └── sap/
│   └── maisons/
│       ├── mongodb/
│       └── surveymonkey/
└── raw/
    └── [formato original: JSON, CSV, Parquet]
```

**Características:**
- Formato: Parquet (optimizado)
- Particionamiento: Por dominio y fecha
- Retención: Configurable por dominio
- Versionado: Git-like con DVC (Data Version Control)

---

### 3. Data Warehouse (Silver/Gold Layers)

**Componente:** BigQuery

**Estructura por Dominio (Data Mesh):**

```
Proyecto GCP: analytics-platform
├── customers_domain/
│   ├── silver/          # Datos limpios y validados
│   └── gold/            # Datos agregados y listos para consumo
├── products_domain/
│   ├── silver/
│   └── gold/
├── maisons_domain/
│   ├── silver/
│   └── gold/
└── shared/              # Datos compartidos entre dominios
    └── gold/
```

**Características:**
- Cada dominio es autónomo (equipo de datos responsable)
- Datos compartidos en `shared/` para joins cross-domain
- Particionamiento y clustering por fecha/ID
- Column-level security por dominio

---

### 4. Capa de Transformación (Transformation Layer)

#### 4.1 dbt (Data Build Tool) - Open Source

**Uso:** Transformaciones SQL en BigQuery

**Estructura:**
```
dbt/
├── models/
│   ├── customers_domain/
│   │   ├── silver/
│   │   └── gold/
│   ├── products_domain/
│   │   ├── silver/
│   │   └── gold/
│   └── maisons_domain/
│       ├── silver/
│       └── gold/
├── macros/
├── tests/
└── dbt_project.yml
```

**Ejecución:**
- Cloud Composer (Airflow) orquesta ejecuciones
- CI/CD con GitHub Actions valida y ejecuta
- Tests automatizados en cada PR

#### 4.2 Apache Spark (Open Source)

**Uso:** Transformaciones complejas, procesamiento de datos no estructurados

**Componente:** Dataproc (managed Spark)

**Casos de uso:**
- Procesamiento de logs
- Transformaciones complejas de MongoDB
- Feature engineering para ML

---

### 5. Data Mesh - Dominios de Datos

#### 5.1 Dominio: Customers

**Responsable:** Equipo de Customer Analytics

**Fuentes:**
- PostgreSQL (CRM interno)
- Salesforce (CRM externo)
- SAP (sistema ERP)

**Productos de Datos:**
- `customers_silver`: Clientes unificados y deduplicados
- `customers_gold`: Métricas de clientes, segmentación
- `customer_360`: Vista 360° del cliente

#### 5.2 Dominio: Products

**Responsable:** Equipo de Product Analytics

**Fuentes:**
- MySQL (catálogo de productos)
- SAP (inventario, compras)

**Productos de Datos:**
- `products_silver`: Catálogo unificado
- `products_gold`: Métricas de productos, recomendaciones base

#### 5.3 Dominio: Maisons

**Responsable:** Equipo de Brand Analytics

**Fuentes:**
- MongoDB (datos de marcas/maisons)
- SurveyMonkey (encuestas de marca)

**Productos de Datos:**
- `maisons_silver`: Datos de marcas normalizados
- `maisons_gold`: Métricas de marca, NPS

#### 5.4 Extensibilidad

**Nuevos dominios:** Agregar siguiendo el mismo patrón:
1. Crear dataset en BigQuery: `{domain}_domain`
2. Configurar ingesta desde nuevas fuentes
3. Crear modelos dbt en `dbt/models/{domain}_domain/`
4. Documentar en Data Catalog

---

### 6. Capa de Machine Learning

#### 6.1 Vertex AI (Google Cloud)

**Componentes:**
- **Vertex AI Workbench**: Jupyter notebooks para experimentación
- **Vertex AI Training**: Entrenamiento de modelos
- **Vertex AI Prediction**: Servicio de predicciones
- **Vertex AI Feature Store**: Almacén de features

#### 6.2 MLflow (Open Source)

**Uso:** Tracking de experimentos, versionado de modelos

**Integración:**
- Vertex AI Workbench ejecuta MLflow
- Modelos versionados en Artifact Registry
- Metadata en BigQuery

#### 6.3 Modelos ML

**Recomendaciones:**
- Collaborative Filtering (customers × products)
- Content-based (productos similares)

**Predicciones:**
- Churn prediction (customers)
- Demand forecasting (products)
- Brand sentiment (maisons)

**Pipeline:**
```
Features (Feature Store) → Training (Vertex AI) → Model Registry → Serving (Vertex AI Endpoints)
```

---

### 7. Capa de Visualización y BI

#### 7.1 Looker Studio (Google)

**Uso:** Dashboards para departamentos

**Estructura:**
- Dashboard por dominio (Customers, Products, Maisons)
- Dashboard ejecutivo (cross-domain)
- Dashboards operacionales (tiempo real)

#### 7.2 Looker (Opcional - Open Source: Lightdash)

**Uso:** BI self-service para analistas

**Características:**
- Modelos de datos desde dbt
- Exploración ad-hoc
- Embedded analytics

#### 7.3 Dataplex (Google Cloud)

**Uso:** Data Catalog y descubrimiento de datos

---

### 8. Gobernanza Federada

#### 8.1 Data Catalog (Dataplex)

**Funcionalidades:**
- Catálogo de datos por dominio
- Lineage (rastreo de origen)
- Metadata management
- Búsqueda de datos

#### 8.2 Access Control

**BigQuery Column-Level Security:**
- Políticas por dominio
- Roles: `data_analyst_{domain}`, `data_engineer_{domain}`, `data_scientist_{domain}`

**IAM Roles:**
```
roles/
├── customers_domain.admin
├── customers_domain.viewer
├── products_domain.admin
└── maisons_domain.admin
```

#### 8.3 Data Observability

**Componentes:**
- **Monte Carlo Data** (open-source: Great Expectations)
- **dbt tests**: Validaciones en cada transformación
- **Cloud Monitoring**: Alertas de calidad de datos
- **Cloud Logging**: Auditoría de acceso

**Métricas monitoreadas:**
- Freshness (actualización de datos)
- Volume (volumen esperado)
- Schema changes
- Data quality (nulls, duplicados, outliers)

---

### 9. GitOps y DataOps

#### 9.1 Repositorios Git

**Estructura:**
```
repos/
├── data-platform-infra/     # Terraform (infraestructura)
├── data-pipelines/          # Airflow DAGs, dbt
├── ml-models/              # Código de ML, MLflow
└── data-catalog/           # Metadata, documentación
```

#### 9.2 CI/CD Pipelines (GitHub Actions)

**Pipeline de Infraestructura:**
```
PR → Terraform Plan → Review → Merge → Terraform Apply
```

**Pipeline de Datos:**
```
PR → dbt compile → dbt test → Review → Merge → dbt run (staging) → dbt run (prod)
```

**Pipeline de ML:**
```
PR → Unit tests → Review → Merge → Train model → Validate → Deploy
```

#### 9.3 Airflow (Cloud Composer)

**Orquestación:**
- Ingesta diaria/incremental
- Transformaciones dbt
- Entrenamiento de modelos ML
- Monitoreo y alertas

**DAGs por dominio:**
```
airflow/dags/
├── customers/
│   ├── ingest_customers_dag.py
│   └── transform_customers_dag.py
├── products/
│   └── ...
└── maisons/
    └── ...
```

---

## Flujo de Datos Completo

### Flujo Batch (Diario)

```
1. Fuentes → [CDC/Extractors] → Cloud Storage (Bronze)
2. Cloud Storage → BigQuery (Silver) [via Airflow]
3. BigQuery Silver → dbt Transform → BigQuery Gold
4. BigQuery Gold → Looker Studio / Looker
5. BigQuery Gold → Feature Store → ML Models
```

### Flujo Streaming (Tiempo Real)

```
1. Fuentes → Debezium CDC → Pub/Sub
2. Pub/Sub → Dataflow (Apache Beam) → BigQuery
3. BigQuery → Looker Studio (real-time dashboards)
```

### Flujo ML

```
1. Feature Store → Vertex AI Training
2. Model Training → MLflow Tracking
3. Model Validation → Artifact Registry
4. Model Deployment → Vertex AI Endpoints
5. Predictions → BigQuery / API
```

---

## Tecnologías Open-Source Utilizadas

| Componente | Tecnología Open-Source |
|------------|------------------------|
| Ingesta | Airbyte, Debezium |
| Transformación | dbt, Apache Spark |
| Orquestación | Apache Airflow |
| ML | MLflow, scikit-learn, TensorFlow |
| Versionado de Datos | DVC (Data Version Control) |
| Observabilidad | Great Expectations |
| BI | Lightdash (alternativa a Looker) |

---

## Seguridad y Compliance

- **Encriptación:** En tránsito (TLS) y en reposo (AES-256)
- **VPC:** Red privada para recursos sensibles
- **Private IP:** BigQuery, Dataproc sin IPs públicas
- **Auditoría:** Cloud Audit Logs para todos los accesos
- **PII:** Dataplex Data Lineage para rastreo de datos sensibles
- **Retención:** Políticas de lifecycle en Cloud Storage

---

## Escalabilidad y Extensibilidad

### Agregar Nuevo Dominio

1. **Infraestructura:**
   ```terraform
   # Crear dataset BigQuery
   resource "google_bigquery_dataset" "new_domain" {
     dataset_id = "new_domain_domain"
   }
   ```

2. **Ingesta:**
   - Configurar fuente en Airbyte/Data Fusion
   - Crear DAG en Airflow

3. **Transformación:**
   - Crear `dbt/models/new_domain_domain/`
   - Configurar tests

4. **Documentación:**
   - Agregar a Data Catalog
   - Documentar en README del dominio

### Agregar Nueva Fuente

1. Configurar conector en Airbyte/Data Fusion
2. Mapear a dominio existente o crear nuevo
3. Actualizar lineage en Data Catalog

---

## Costos y Optimización

- **BigQuery:** Particionamiento y clustering para reducir costos
- **Cloud Storage:** Lifecycle policies (mover a Nearline/Coldline)
- **Dataproc:** Auto-scaling, preemptible VMs
- **Vertex AI:** Usar preemptible para entrenamiento
- **Reservations:** Para workloads predecibles

---

## Monitoreo y Alertas

- **Cloud Monitoring:** Métricas de pipelines, calidad de datos
- **Cloud Logging:** Logs centralizados
- **Alertas:**
  - Pipeline failures
  - Data quality issues
  - Model drift (ML)
  - Cost overruns

---

## Diagrama de Arquitectura - Componentes Clave

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                          │
│  PostgreSQL  MySQL  MongoDB  SAP  Salesforce  SurveyMonkey  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE INGESTA (Data Ingestion)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Debezium │  │ Airbyte  │  │  APIs    │                  │
│  │  (CDC)   │  │ (Batch)  │  │  REST    │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐            ┌──────────────────┐
│ Cloud Storage│            │   Cloud Pub/Sub  │
│   (Bronze)   │            │    (Streaming)  │
└──────┬───────┘            └────────┬─────────┘
       │                              │
       └──────────────┬───────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA WAREHOUSE (BigQuery)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Customers   │  │   Products   │  │   Maisons     │     │
│  │   Domain    │  │    Domain    │  │    Domain    │     │
│  │ Silver/Gold │  │ Silver/Gold  │  │ Silver/Gold  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Shared (Cross-Domain)                   │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐            ┌──────────────────┐
│   dbt        │            │  Apache Spark     │
│ (SQL Transf) │            │  (Complex Transf) │
└──────┬───────┘            └────────┬─────────┘
       │                              │
       └──────────────┬───────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────┐          ┌──────────────────┐
│   BI Layer   │          │   ML Layer       │
│ Looker Studio│          │  Vertex AI       │
│   Looker     │          │  MLflow           │
└──────────────┘          └──────────────────┘
```

### Vista de Data Mesh

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA MESH ARCHITECTURE                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Customers  │  │   Products   │  │   Maisons    │     │
│  │    Domain    │  │    Domain    │  │    Domain    │     │
│  │              │  │              │  │              │     │
│  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │     │
│  │  │ Ingest │  │  │  │ Ingest │  │  │  │ Ingest │  │     │
│  │  └───┬────┘  │  │  └───┬────┘  │  │  └───┬────┘  │     │
│  │      │       │  │      │       │  │      │       │     │
│  │  ┌───▼────┐  │  │  ┌───▼────┐  │  │  ┌───▼────┐  │     │
│  │  │Silver  │  │  │  │Silver  │  │  │  │Silver  │  │     │
│  │  └───┬────┘  │  │  └───┬────┘  │  │  └───┬────┘  │     │
│  │      │       │  │      │       │  │      │       │     │
│  │  ┌───▼────┐  │  │  ┌───▼────┐  │  │  ┌───▼────┐  │     │
│  │  │  Gold  │  │  │  │  Gold  │  │  │  │  Gold  │  │     │
│  │  └────────┘  │  │  └────────┘  │  │  └────────┘  │     │
│  │              │  │              │  │              │     │
│  │  Team:       │  │  Team:       │  │  Team:       │     │
│  │  Customer    │  │  Product     │  │  Brand       │     │
│  │  Analytics   │  │  Analytics   │  │  Analytics   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│         └─────────────────┴─────────────────┘              │
│                            │                               │
│                   ┌────────▼────────┐                      │
│                   │   Shared Data   │                      │
│                   │  (Cross-Domain) │                      │
│                   └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### Vista de GitOps/DataOps

```
┌─────────────────────────────────────────────────────────────┐
│                    GITOPS PIPELINE                           │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │   Git    │───▶│   CI/CD  │───▶│  Deploy  │               │
│  │ (GitHub) │    │(GitHub   │    │(Terraform│               │
│  │          │    │ Actions) │    │ Airflow) │               │
│  └──────────┘    └──────────┘    └──────────┘               │
│                                                              │
│  Repos:                                                      │
│  • data-platform-infra (Terraform)                          │
│  • data-pipelines (dbt, Airflow)                             │
│  • ml-models (ML code)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Checklist para Draw.io

### Elementos a Incluir:

1. **Fuentes de Datos:**
   - PostgreSQL, MySQL, MongoDB (iconos de BD)
   - SAP, Salesforce, SurveyMonkey (iconos de apps)

2. **Capa de Ingesta:**
   - Debezium (CDC)
   - Airbyte (batch)
   - Cloud Functions (APIs)
   - Pub/Sub (streaming)

3. **Storage:**
   - Cloud Storage (Bronze/Data Lake)
   - BigQuery (Silver/Gold por dominio)

4. **Transformación:**
   - dbt
   - Apache Spark (Dataproc)

5. **Orquestación:**
   - Cloud Composer (Airflow)

6. **ML:**
   - Vertex AI
   - MLflow
   - Feature Store

7. **BI:**
   - Looker Studio
   - Looker

8. **Gobernanza:**
   - Dataplex (Data Catalog)
   - IAM/Column Security

9. **GitOps:**
   - GitHub
   - GitHub Actions
   - Terraform

10. **Monitoreo:**
    - Cloud Monitoring
    - Cloud Logging

### Colores Sugeridos:

- **Fuentes:** Azul claro
- **Ingesta:** Naranja
- **Storage:** Verde
- **Transformación:** Amarillo
- **ML:** Morado
- **BI:** Rojo
- **Gobernanza:** Gris
- **GitOps:** Negro

### Flujos (Flechas):

- **Batch:** Flechas sólidas negras
- **Streaming:** Flechas punteadas azules
- **ML Pipeline:** Flechas moradas
- **Metadata/Lineage:** Flechas grises finas

---

## Notas Finales

Este diseño cumple con todos los requisitos del desafío:
- ✅ Google Cloud Platform
- ✅ Tecnologías open-source
- ✅ GitOps y DataOps
- ✅ Data Mesh paradigm
- ✅ Dominios: customers, products, maisons (extensible)
- ✅ Gobernanza federada (acceso, observabilidad, catálogo)
- ✅ BI dashboards
- ✅ ML models

El diseño es **extensible** y **escalable**, permitiendo agregar nuevos dominios y fuentes de datos siguiendo el mismo patrón.
