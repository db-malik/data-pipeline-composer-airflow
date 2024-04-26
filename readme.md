# Setting Up Google Cloud Storage, BigQuery, and Cloud Composer with Terraform

This guide provides step-by-step instructions for provisioning Google Cloud Storage (GCS), BigQuery, and Cloud Composer using Terraform.

# Workflow Overview

- The Terraform deployment process orchestrates the creation of project services architecture in Google Cloud Platform. It begins with defining infrastructure requirements in Terraform configuration files. After initializing Terraform and planning changes, the deployment plan is reviewed before applying changes. Upon applying changes, Terraform creates, modifies, or deletes resources as specified.

- Whenever changes are pushed to the specified branch of your GitHub repository, the Cloud Build trigger automatically initiates a build. The build process is defined in the cloudbuild.yaml file located in your repository. This file contains instructions for copying the DAG files from the repository to the Google Cloud Storage bucket used by Composer. Once the build is triggered, Cloud Build executes the steps defined in the cloudbuild.yaml file, ensuring that the latest DAG configurations are available for execution within Composer.

graph TD; A(GitHub) -->|Push Changes| B(Cloud Build Trigger); B --> C[Build Process]; C --> D[Copy DAG Files to GCS Bucket for airflow ]; D --> E[Execute Steps in cloudbuild.yaml]; E --> F[Update DAG Configurations in Composer];

## Prerequisites

Ensure you have Terraform installed on your local machine. Authenticate with Google Cloud using the gcloud CLI and ensure you have the necessary permissions to create resources. Have a Google Cloud project set up and ready for deployment.

## architecture

- composer.tf: This file contains Terraform configuration to deploy a Cloud Composer environment.
- storage.tf: This file contains Terraform configuration to create a Cloud Storage bucket.
- bigquery_datawarehouse.tf and bigquery_raw.tf This file contains Terraform configuration to create a BigQuery datasets and tables.
- cloudbuild.yaml : Copy the DAG files to the Google Cloud Storage bucket used by Composer

## Steps

### **1. Create a Service Account** :

- Go to the [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) page in the Google Cloud Console.
- Create Service Account
- **Generate the Key File** and download

### 2. Authenticate Terraform with GCP

Ensure Terraform can authenticate with your GCP account by setting up Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

### \*\*3. Set Up Terraform

Clone the repository containing the Terraform configuration files.

```
git clone <repository_url>
cd <repository_directory>
```

### \*\*3. Configure Terraform Variables

Create a terraform.tfvars.json file in the root directory of the repository and specify the required variables such as project ID, credentials file path, region, etc. Refer to the provided example for guidance.

```
  {
  "project_id": "your project id",
  "credentials_file_path": "/path to your credential file",
  "region": "specify region",
  "zone": "specify zone",
  "network": "default",
  "subnetwork": "default",
  "environment_name": "composer environement name",
  "image_version": "composer-2.7.0-airflow-2.7.3",
  "scheduler_cpu": 0.5,
  "scheduler_memory_gb": 2,
  "scheduler_storage_gb": 1,
  "web_server_cpu": 0.5,
  "web_server_memory_gb": 2,
  "web_server_storage_gb": 1,
  "worker_cpu": 0.5,
  "worker_memory_gb": 2,
  "worker_storage_gb": 1,
  "worker_min_count": 1,
  "worker_max_count": 3
  }
```

### 3. Initialize Terraform Configuration

Run the following command to initialize Terraform and download the required providers and modules:

```
terraform init
```

### 3. Plan Terraform Deployment

Generate an execution plan to preview the changes Terraform will make:

```
 terraform plan -var-file="terraform.tfvars.json"
```

### 3. Apply Terraform Configuration

```
 terraform apply -var-file="terraform.tfvars.json"
```

Confirm the changes when prompted.

check your gcp and verify services was created

### 3. Create Cloud Build Trigger

### Step 7: Automating Deployment with Cloud Build Trigger

Create Cloud Build Trigger:

Navigate to the Google Cloud Console and select your project. Go to Cloud Build > Triggers. Configure Trigger Details: Provide a name and optional description for the trigger. Select the event that should trigger the build, such as Push to a branch. Choose your GitHub repository and specify the branch to monitor. Specify Build Configuration: Select Cloud Build configuration file (yaml) as the configuration type. Choose Repository as the location. Specify the path to the cloudbuild.yaml file in your GitHub repository. Review and Create Trigger.
