# Intentar crear conexión de Looker Studio a BigQuery
# Nota: Looker Studio no tiene provider oficial de Terraform,
# pero podemos preparar todo lo necesario para facilitar la conexión

# Crear una vista específica para Looker Studio con formato optimizado
resource "google_bigquery_table" "looker_studio_view" {
  dataset_id = google_bigquery_dataset.gold_dataset.dataset_id
  table_id   = "looker_studio_dashboard_data"

  view {
    query = <<-SQL
      SELECT 
        date,
        total_trips,
        avg_trip_duration_seconds / 60.0 as avg_duration_minutes,
        avg_trip_miles,
        temperature,
        weather_condition,
        weather_category,
        temperature_category,
        precipitation,
        wind_speed,
        humidity,
        total_revenue,
        -- Campos calculados para facilitar visualización
        CASE 
          WHEN precipitation = 0 THEN 'Sin lluvia'
          WHEN precipitation < 5 THEN 'Lluvia ligera'
          WHEN precipitation < 15 THEN 'Lluvia moderada'
          ELSE 'Lluvia intensa'
        END as rain_category,
        EXTRACT(DAYOFWEEK FROM date) as day_of_week,
        CASE EXTRACT(DAYOFWEEK FROM date)
          WHEN 1 THEN 'Domingo'
          WHEN 2 THEN 'Lunes'
          WHEN 3 THEN 'Martes'
          WHEN 4 THEN 'Miércoles'
          WHEN 5 THEN 'Jueves'
          WHEN 6 THEN 'Viernes'
          WHEN 7 THEN 'Sábado'
        END as day_name
      FROM `${var.project_id}.${google_bigquery_dataset.gold_dataset.dataset_id}.daily_summary`
      ORDER BY date
    SQL
    use_legacy_sql = false
  }

  description = "Vista optimizada para Looker Studio dashboard"
  
  labels = {
    purpose = "looker-studio"
    layer   = "gold"
  }
}

# Nota: Looker Studio no tiene provider de Terraform oficial
# Esta vista facilita la conexión manual pero no crea el dashboard automáticamente
# La información de conexión está en outputs.tf
# Para crear el dashboard, usar:
# 1. Ejecutar: terraform output looker_studio_connection_info
# 2. Click en connection_url del output
# 3. O ir a: https://lookerstudio.google.com/ y conectar manualmente
