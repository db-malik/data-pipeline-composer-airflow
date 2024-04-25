variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "credentials_file_path" {
  description = "The path to the JSON file that contains your service account key."
  type        = string
}

variable "region" {
  description = "The region of the Composer environment"
  type        = string
}

variable "zone" {
  description = "The zone within the region"
  type        = string
}

variable "network" {
  description = "The name of the VPC network"
  type        = string
}

variable "subnetwork" {
  description = "The name of the subnetwork"
  type        = string
}

variable "environment_name" {
  description = "Name of the Cloud Composer environment"
  type        = string
}

variable "image_version" {
  description = "The Cloud Composer image version"
  type        = string
}

variable "scheduler_cpu" {
  description = "CPU for the scheduler"
  default     = 0.5
}

variable "scheduler_memory_gb" {
  description = "Memory in GB for the scheduler"
  default     = 2
}

variable "scheduler_storage_gb" {
  description = "Storage in GB for the scheduler"
  default     = 1
}

variable "worker_min_count" {
  description = "Minimum number of worker nodes"
  default     = 1
}

variable "worker_max_count" {
  description = "Maximum number of worker nodes"
  default     = 3
}

variable "worker_cpu" {
  description = "CPU for each worker node"
  default     = 0.5
}

variable "worker_memory_gb" {
  description = "Memory in GB for each worker node"
  default     = 2
}

variable "worker_storage_gb" {
  description = "Storage in GB for each worker node"
  default     = 1
}
