output "raw_dataset_id" {
  description = "BigQuery Raw Dataset ID"
  value       = google_bigquery_dataset.raw_dataset.dataset_id
}

output "silver_dataset_id" {
  description = "BigQuery Silver Dataset ID"
  value       = google_bigquery_dataset.silver_dataset.dataset_id
}

output "gold_dataset_id" {
  description = "BigQuery Gold Dataset ID"
  value       = google_bigquery_dataset.gold_dataset.dataset_id
}

output "weather_ingestion_function_url" {
  description = "URL of the weather ingestion Cloud Function"
  value       = google_cloudfunctions2_function.weather_ingestion.service_config[0].uri
}

output "scheduler_job_name" {
  description = "Name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.weather_ingestion_daily.name
}

output "looker_studio_connection_info" {
  description = "Información para conectar Looker Studio a BigQuery automáticamente"
  value = {
    project_id     = var.project_id
    dataset_id     = google_bigquery_dataset.gold_dataset.dataset_id
    table_id       = "daily_summary"
    full_path      = "${var.project_id}.${google_bigquery_dataset.gold_dataset.dataset_id}.daily_summary"
    connection_url = "https://lookerstudio.google.com/datasources/create?connectorId=bigquery&projectId=${var.project_id}&datasetId=${google_bigquery_dataset.gold_dataset.dataset_id}&tableId=daily_summary"
    instructions   = "Click en la URL arriba o ve a Looker Studio > Create > Report > BigQuery > ${var.project_id} > ${google_bigquery_dataset.gold_dataset.dataset_id} > daily_summary"
  }
}
