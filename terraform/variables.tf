variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "openweather_api_key" {
  description = "API Key de clima (OPCIONAL) - Solo se usa como fallback si BigQuery público no tiene datos"
  type        = string
  sensitive   = true
  default     = ""
}

variable "developer_email" {
  description = "Email of the developer (for column-level security)"
  type        = string
}

variable "chicago_latitude" {
  description = "Latitude for Chicago weather data"
  type        = number
  default     = 41.8781
}

variable "chicago_longitude" {
  description = "Longitude for Chicago weather data"
  type        = number
  default     = -87.6298
}
