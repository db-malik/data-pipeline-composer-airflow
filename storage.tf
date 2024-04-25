resource "google_storage_bucket" "composer_bucket" {
  name     = "gcs-viseo-data-academy-22024-terraform"
  location = "europe-west3"
}

resource "google_storage_bucket_object" "data_in_folder" {
  name         = "data/in/"
  bucket       = google_storage_bucket.composer_bucket.name
  content_type = "text/plain"
  content      = "This is a placeholder file to maintain directory structure."
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
