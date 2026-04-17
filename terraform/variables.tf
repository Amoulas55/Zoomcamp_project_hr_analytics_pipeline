variable "project_id" {
  description = "Your GCP Project ID"
  type        = string
}

variable "credentials_file" {
  description = "Path to GCP service account JSON key"
  type        = string
  default     = "../google_credentials.json"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west4"
}

variable "location" {
  description = "GCP multi-region location"
  type        = string
  default     = "EU"
}

variable "bq_dataset_name" {
  description = "BigQuery Dataset Name"
  type        = string
  default     = "hr_analytics_dataset"
}

variable "gcs_bucket_name" {
  description = "GCS Bucket Name for the data lake"
  type        = string
}
