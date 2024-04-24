provider "google" {
  credentials = file(var.credentials_file)
  project     = var.project_id
  region      = "europe-west3"
}

variable "credentials_file" {
  description = "Path to the service account credentials file"
  default     = "credentials/credential.json"
}

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

resource "google_composer_environment" "composer_env" {
  name   = "composer-environment"
  region = "europe-west3"

  config {
    # Updated configuration for node settings using workloads config
    workloads_config {
      scheduler {
        cpu        = 1
        memory_gb  = 2.5
        storage_gb = 10
      }
      web_server {
        cpu        = 0.5
        memory_gb  = 1.5
        storage_gb = 10
      }
      worker {
        cpu        = 1
        memory_gb  = 2.5
        storage_gb = 10
        min_count  = 3
        max_count  = 6
      }
    }

    software_config {
      image_version = "composer-2.7.0-airflow-2.7.3"
    }

    # If using private IP or need specific network settings, configure the environment network here
    # environment_size = "ENVIRONMENT_SIZE_SMALL" # Optional: Define if different size is needed
  }
}



resource "google_storage_bucket" "composer_bucket" {
  name     = "gcs-viseo-data-academy-22024-terraform"
  location = "europe-west3"
}

resource "google_storage_bucket_object" "data_in_folder" {
  name         = "data/in/"
  bucket       = google_storage_bucket.composer_bucket.name
  content_type = "application/x-www-form-urlencoded"
  content      = "docs/SALES.csv"
}

resource "google_storage_bucket_object" "data_archive_folder" {
  name         = "data/archive/.placeholder"
  bucket       = google_storage_bucket.composer_bucket.name
  content_type = "text/plain"
  content      = "This is a placeholder file to maintain directory structure."
}

resource "google_storage_bucket_object" "data_error_folder" {
  name         = "data/error/.placeholder"
  bucket       = google_storage_bucket.composer_bucket.name
  content_type = "text/plain"
  content      = "This is a placeholder file to maintain directory structure."
}


# dataset for raw data
resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = "RAW_DATASET_TERRAFORM"
  location   = "europe-west3"
}

# Table within the raw dataset
resource "google_bigquery_table" "raw_sales_table" {
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  table_id   = "RAW_SALES_TABLE"
  schema = jsonencode([
    {
      "name" : "SaleID",
      "type" : "STRING",
      "mode" : "NULLABLE"
    },
    {
      "name" : "ProductID",
      "type" : "STRING",
      "mode" : "NULLABLE"
    },
    {
      "name" : "Quantity",
      "type" : "STRING",
      "mode" : "NULLABLE"
    },
    {
      "name" : "Price",
      "type" : "STRING",
      "mode" : "NULLABLE"
    },
    {
      "name" : "SaleDate",
      "type" : "STRING",
      "mode" : "NULLABLE"
    }
  ])
  depends_on = [google_bigquery_dataset.raw_dataset]
}




# Dataset for transformed data
resource "google_bigquery_dataset" "datawarehouse_dataset" {
  dataset_id = "DATAWERHOUSE_TERRAFRM"
  location   = "europe-west3"
}

# Table within the datawarehouse dataset
resource "google_bigquery_table" "transformed_table" {
  dataset_id = google_bigquery_dataset.datawarehouse_dataset.dataset_id
  table_id   = "transformed_Table"
  schema = jsonencode([
    {
      "name" : "SaleID",
      "type" : "INTEGER",
      "mode" : "NULLABLE"
    },
    {
      "name" : "ProductID",
      "type" : "STRING",
      "mode" : "NULLABLE"
    },
    {
      "name" : "Quantity",
      "type" : "INTEGER",
      "mode" : "NULLABLE"
    },
    {
      "name" : "Price",
      "type" : "FLOAT",
      "mode" : "NULLABLE"
    },
    {
      "name" : "SaleDate",
      "type" : "DATE",
      "mode" : "NULLABLE"
    }
  ])
}
