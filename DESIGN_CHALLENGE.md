# Design Challenge - Arquitectura de Datos

## Resumen Ejecutivo

Este documento describe la arquitectura propuesta para un cliente que busca modernizar su enfoque analítico, migrando desde sistemas legacy hacia una arquitectura moderna basada en Google Cloud Platform, siguiendo principios de Data Mesh y DataOps.

## Requisitos del Cliente

- **Plataforma**: Google Cloud Platform
- **Tecnologías**: Open-source preferentemente
- **Enfoque**: GitOps y DataOps
- **Paradigma**: Data Mesh
- **Dominios de datos**: customers, products, maisons (extensible)
- **Gobernanza**: Federada para acceso, observabilidad y catálogo

## Arquitectura Propuesta

### Componentes Principales

#### 1. Capa de Ingesta (Ingestion Layer)

**Herramientas**:
- **Airbyte** (open-source): Para integración de datos desde múltiples fuentes
  - PostgreSQL, MySQL, MongoDB
  - SAP (via API/ODBC)
  - Salesforce (via API)
  - SurveyMonkey (via API)
- **Cloud Storage**: Landing zone para datos en formato raw

**Patrón**: ELT (Extract, Load, Transform)
- Los datos se extraen y cargan en su formato original
- Las transformaciones se realizan en la capa de procesamiento

#### 2. Capa de Almacenamiento (Storage Layer)

**Arquitectura de Capas (Medallion Architecture)**:

- **Bronze (Raw)**: Datos sin procesar, tal como se ingieren
  - BigQuery para datos estructurados
  - Cloud Storage para datos no estructurados (logs, documentos)
  
- **Silver (Cleaned)**: Datos limpios y deduplicados
  - BigQuery con esquemas validados
  - Eliminación de duplicados
  - Enriquecimiento básico
  
- **Gold (Curated)**: Datos listos para consumo analítico
  - Agregaciones y métricas pre-calculadas
  - Modelos de datos optimizados para BI y ML

#### 3. Capa de Procesamiento (Processing Layer)

**Herramientas**:
- **dbt (data build tool)**: Transformaciones SQL
  - Modelos versionados en Git
  - Tests automatizados
  - Documentación generada automáticamente
  
- **Apache Spark (Dataproc)**: Para procesamiento de grandes volúmenes
  - ETL complejos
  - Procesamiento de datos no estructurados
  
- **Cloud Dataflow**: Para pipelines de streaming (si aplica)

#### 4. Capa de Servicio (Service Layer) - Data Mesh

**Data Products por Dominio**:

1. **Customer Data Product**
   - Dataset: `customer_domain.gold`
   - Owner: Equipo de Customer Analytics
   - Contratos de datos definidos
   
2. **Product Data Product**
   - Dataset: `product_domain.gold`
   - Owner: Equipo de Product Management
   
3. **Maison Data Product**
   - Dataset: `maison_domain.gold`
   - Owner: Equipo de Brand Management

**Características**:
- Cada data product es independiente y versionado
- APIs de datos para consumo programático
- Documentación automática

#### 5. Capa de Consumo (Consumption Layer)

**BI Dashboards**:
- **Looker**: Para dashboards empresariales
- **Looker Studio**: Para análisis ad-hoc y self-service
- **Metabase**: Alternativa open-source

**ML/AI**:
- **Vertex AI**: Plataforma unificada para ML
  - AutoML para modelos rápidos
  - Custom training para modelos específicos
  - Feature Store para features reutilizables
- **BigQuery ML**: Para modelos SQL-based

#### 6. Gobernanza de Datos (Data Governance)

**Catálogo de Datos**:
- **Data Catalog**: Catálogo centralizado de Google Cloud
  - Metadata automática
  - Lineage de datos
  - Tags y políticas

**Acceso y Seguridad**:
- **IAM**: Control de acceso a nivel de proyecto/dataset/tabla
- **Column-level security**: Para datos sensibles
- **Data Loss Prevention (DLP)**: Para detección y protección de PII
- **VPC Service Controls**: Para aislamiento de red

**Observabilidad**:
- **Cloud Monitoring**: Métricas de pipelines
- **Cloud Logging**: Logs centralizados
- **Dataform**: Para monitoreo de calidad de datos
- **Great Expectations**: Para validación de datos (open-source)

#### 7. Orquestación y Automatización

**Orquestación**:
- **Cloud Scheduler**: Para pipelines simples (implementado en la prueba)
- **Cloud Composer (Apache Airflow)**: Para orquestación compleja (escalabilidad futura)
  - DAGs versionados en Git
  - Retries y alertas automáticas
  - Manejo de dependencias entre múltiples tareas
  - Se implementará cuando haya múltiples ingestas diarias o procesos batch complejos
  
**CI/CD**:
- **Cloud Build**: Para automatización
- **GitHub Actions**: Para validación de código
  - Tests de dbt
  - Validación de Terraform
  - Linting y formateo

**Infraestructura como Código**:
- **Terraform**: Para todos los recursos de GCP
  - Módulos reutilizables
  - Variables y outputs documentados

## Flujo de Datos

```
[Fuentes de Datos] 
    ↓
[Airbyte] → [Cloud Storage (Bronze)]
    ↓
[dbt/Spark] → [BigQuery (Silver)]
    ↓
[dbt] → [BigQuery (Gold)]
    ↓
[Data Products por Dominio]
    ↓
[Looker/Looker Studio] + [Vertex AI]
```

## Extensibilidad

Para agregar nuevos data products:

1. Crear nuevo módulo de Terraform para el dominio
2. Configurar Airbyte para nuevas fuentes (si aplica)
3. Crear modelos dbt en el nuevo dominio
4. Publicar data product en Data Catalog
5. Documentar en el catálogo

## Consideraciones de Costos

- **BigQuery**: Uso de slots reservados para workloads predecibles
- **Cloud Storage**: Lifecycle policies para mover datos antiguos a Nearline/Coldline
- **Dataproc**: Clusters efímeros para reducir costos
- **Composer**: Usar el tier más bajo posible según necesidades

## Seguridad y Compliance

- Encriptación en tránsito y en reposo
- Auditoría completa con Cloud Audit Logs
- Backup automático de datos críticos
- Disaster recovery plan documentado

## Próximos Pasos

1. Validar arquitectura con stakeholders
2. Crear POC para un dominio (ej: customers)
3. Establecer métricas de éxito
4. Plan de migración gradual desde sistemas legacy
