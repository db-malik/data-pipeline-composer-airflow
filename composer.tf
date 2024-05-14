
resource "google_composer_environment" "airflow" {
  provider = google
  name     = var.environment_name
  region   = var.region
  project  = var.project_id

  config {
    node_config {
      network    = "projects/${var.project_id}/global/networks/${var.network}"
      subnetwork = "projects/${var.project_id}/regions/${var.region}/subnetworks/${var.subnetwork}"
    }

    workloads_config {
      scheduler {
        cpu        = var.scheduler_cpu
        memory_gb  = var.scheduler_memory_gb
        storage_gb = var.scheduler_storage_gb
      }
      worker {
        cpu        = var.worker_cpu
        memory_gb  = var.worker_memory_gb
        storage_gb = var.worker_storage_gb
        min_count  = var.worker_min_count
        max_count  = var.worker_max_count
      }
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"
    software_config {
      image_version = var.image_version
    }
  }

  labels = {
    environment = "airflow"
    team        = "data-engineering"
  }
}
