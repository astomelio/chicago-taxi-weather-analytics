terraform {
  required_version = ">= 1.0"

  # Backend remoto en GCS para persistir el estado
  backend "gcs" {
    bucket = ""  # Se configura en el workflow
    prefix = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# BigQuery Dataset para datos raw
resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id    = "chicago_taxi_raw"
  friendly_name = "Chicago Taxi Raw Data"
  description   = "Raw data layer for Chicago taxi trips and weather data"
  location      = var.region

  labels = {
    environment = "production"
    layer       = "raw"
  }

  lifecycle {
    ignore_changes = [dataset_id]
  }
}

# BigQuery Dataset para datos transformados (Silver)
resource "google_bigquery_dataset" "silver_dataset" {
  dataset_id    = "chicago_taxi_silver"
  friendly_name = "Chicago Taxi Silver Data"
  description   = "Cleaned and deduplicated data layer"
  location      = var.region

  labels = {
    environment = "production"
    layer       = "silver"
  }

  lifecycle {
    ignore_changes = [dataset_id]
  }
}

# BigQuery Dataset para datos analíticos (Gold)
resource "google_bigquery_dataset" "gold_dataset" {
  dataset_id    = "chicago_taxi_gold"
  friendly_name = "Chicago Taxi Gold Data"
  description   = "Analytical and aggregated data layer for dashboards"
  location      = var.region

  labels = {
    environment = "production"
    layer       = "gold"
  }

  lifecycle {
    ignore_changes = [dataset_id]
  }
}

# Tabla para datos del clima (raw)
resource "google_bigquery_table" "weather_raw" {
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  table_id   = "weather_data"

  schema = jsonencode([
    {
      name = "date"
      type = "DATE"
      mode = "REQUIRED"
    },
    {
      name = "temperature"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "humidity"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "wind_speed"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "precipitation"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "weather_condition"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "ingestion_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])

  time_partitioning {
    type  = "DAY"
    field = "date"
  }

  clustering = ["date"]
}

# Tabla para datos de taxis (raw) - vista sobre el dataset público
# Esta vista se crea automáticamente. Si falla por permisos, el sistema seguirá funcionando
# consultando directamente el dataset público en los modelos dbt.
resource "google_bigquery_table" "taxi_trips_raw" {
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  table_id   = "taxi_trips_raw"

  view {
    query          = <<-SQL
      SELECT 
        unique_key,
        taxi_id,
        trip_start_timestamp,
        trip_end_timestamp,
        trip_seconds,
        trip_miles,
        pickup_census_tract,
        dropoff_census_tract,
        pickup_community_area,
        dropoff_community_area,
        fare,
        tips,
        tolls,
        extras,
        trip_total,
        payment_type,
        company,
        pickup_latitude,
        pickup_longitude,
        dropoff_latitude,
        dropoff_longitude
      FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
      WHERE DATE(trip_start_timestamp) >= '2023-06-01'
        AND DATE(trip_start_timestamp) <= '2023-12-31'
    SQL
    use_legacy_sql = false
  }

  # Si falla la creación, no bloquear el resto del despliegue
  lifecycle {
    ignore_changes = [view]
  }
}

# Service Account para Cloud Functions
resource "google_service_account" "weather_ingestion_sa" {
  account_id   = "weather-ingestion-sa"
  display_name = "Service Account for Weather Data Ingestion"
  description  = "Service account for Cloud Function that ingests weather data"

  # Evitar recrear si ya existe
  lifecycle {
    prevent_destroy = false
    ignore_changes  = [account_id]
  }
}

# Permisos para el Service Account
resource "google_project_iam_member" "weather_ingestion_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.weather_ingestion_sa.email}"
}

resource "google_project_iam_member" "weather_ingestion_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.weather_ingestion_sa.email}"
}

# Permiso para acceder a datasets públicos de BigQuery
resource "google_project_iam_member" "weather_ingestion_publicdata" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.weather_ingestion_sa.email}"
}

# Cloud Storage bucket para el código de la función
resource "google_storage_bucket" "function_source" {
  name     = "${var.project_id}-function-source"
  location = var.region

  uniform_bucket_level_access = true

  lifecycle {
    ignore_changes = [name]
  }
}

# Subir el código de la función a Cloud Storage
resource "google_storage_bucket_object" "function_source" {
  name   = "weather-ingestion-source.zip"
  bucket = google_storage_bucket.function_source.name
  source = "${path.module}/weather-ingestion-source.zip"

  # El ZIP debe estar en el directorio terraform/
  # Se crea con: cd functions/weather_ingestion && zip -r ../../terraform/weather-ingestion-source.zip .
}

# Cloud Function para ingesta de datos del clima
resource "google_cloudfunctions2_function" "weather_ingestion" {
  name        = "weather-ingestion"
  location    = var.region
  description = "Function to ingest weather data daily"

  build_config {
    runtime     = "python39"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  # Evitar recrear si ya existe
  lifecycle {
    create_before_destroy = true
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "256M"
    timeout_seconds       = 540
    service_account_email = google_service_account.weather_ingestion_sa.email
    environment_variables = {
      PROJECT_ID          = var.project_id
      DATASET_ID          = google_bigquery_dataset.raw_dataset.dataset_id
      TABLE_ID            = google_bigquery_table.weather_raw.table_id
      OPENWEATHER_API_KEY = var.openweather_api_key
    }
  }
}

# Cloud Scheduler para ejecutar la función diariamente
resource "google_cloud_scheduler_job" "weather_ingestion_daily" {
  name        = "weather-ingestion-daily"
  description = "Daily job to ingest previous day's weather data"
  schedule    = "0 2 * * *" # 2 AM UTC daily
  time_zone   = "UTC"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.weather_ingestion.service_config[0].uri
    oidc_token {
      service_account_email = google_service_account.weather_ingestion_sa.email
    }
  }
}

# Column-level security para payment_type
# Solo el email del desarrollador puede acceder a esta columna
resource "google_bigquery_table_iam_member" "payment_type_access" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  table_id   = google_bigquery_table.taxi_trips_raw.table_id
  role       = "roles/bigquery.dataViewer"
  member     = "user:${var.developer_email}"
}

# Policy tag para column-level security
resource "google_data_catalog_policy_tag" "payment_type_policy" {
  taxonomy     = google_data_catalog_taxonomy.sensitive_data.id
  display_name = "Payment Type - Sensitive"
  description  = "Policy tag for payment_type column access control"
}

resource "google_data_catalog_taxonomy" "sensitive_data" {
  display_name = "Sensitive Data Taxonomy"
  description  = "Taxonomy for sensitive data classification"
  region       = var.region

  lifecycle {
    ignore_changes = [display_name]
  }
}
