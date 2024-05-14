# Setting Up Google Cloud Storage, BigQuery, and Cloud Composer with Terraform

- Exercise Documentation Located in the docs folder within the repository.

- Data File: The sales.csv file, which is used in the exercises, can be found

This guide provides comprehensive instructions for provisioning Google Cloud Storage (GCS), BigQuery, and Cloud Composer environments using Terraform.

The setup process integrates with GitHub for source control and Google Cloud Build for continuous integration, automating the deployment of Airflow DAGs through Cloud Composer.

# Workflow Overview

The Terraform deployment orchestrates the creation and configuration of Google Cloud services. Here's a brief overview of the workflow:

- Terraform Configuration: Define infrastructure as code using Terraform to manage resources in Google Cloud Platform (GCP).

![ Architecture](docs/architecture.png ' Architecture')

- Continuous Integration: Set up Cloud Build triggers to automate the deployment process when changes are pushed to a specified branch in a GitHub repository.

- Resource Provisioning: Automatically create instances of GCS, BigQuery, and Cloud Composer based on Terraform configurations.

![ Workflow](docs/architecture.png ' Workflow')

- DAG Deployment: Use Cloud Build to transfer Airflow DAG files from GitHub to GCS, making them available to Cloud Composer for workflow execution.

![ Diagram](docs/diagram.svg ' Diagram')

# Prerequisites

- Terraform Installation: Ensure Terraform is installed on your local machine.
- Google Cloud SDK: Install and authenticate with the Google Cloud SDK.
- Permissions: Confirm you have the necessary permissions to create and manage resources in your GCP project.

# Architecture Components

composer.tf: Configures Cloud Composer. storage.tf: Creates a GCS bucket. bigquery_datawarehouse.tf & bigquery_raw.tf: Set up BigQuery datasets and tables. cloudbuild.yaml: Manages the copying of DAG files to the GCS bucket utilized by Cloud Composer. Setup Steps

# Steps

1. Create a Service Account

   - Navigate to the Service Accounts page in the GCP Console.
   - Click on Create Service Account, provide a name, and click Create.
   - Assign roles necessary for managing GCP resources.
   - Click on Create Key, select JSON, and download the key file.

2. Authenticate Terraform with GCP Set up your environment to authenticate Terraform with GCP:

   ```
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
   ```

3. Clone and Configure Terraform

   Clone the repository and configure Terraform:

   ```
   git clone git@github.com:db-malik/data-pipeline-composer-airflow.git
   cd data-pipeline-composer-airflow
   ```

4. Define Terraform Variables

   Create a terraform.tfvars.json file with all necessary configurations: take the configuration below as a template and update it with your config

   ```

   {
     "project_id": "your project id,
     "credentials_file_path": "./your path to credentials.json",
     "region": "region",
     "zone": "zone",
     "network": "default",
     "subnetwork": "default",
     "environment_name": "your composer environement name",
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

5. Initialize terraform

   Initialize Terraform and plan your deployment:

   ```
   terraform init
   ```

6. Plan Terraform

   ```
   terraform plan -var-file="terraform.tfvars.json"
   ```

7. Apply Terraform Configuration

   Apply the configuration to create the resources:

   ```
   terraform apply -var-file="terraform.tfvars.json"
   ```

8. Set Up Cloud Build Trigger

   Configure a Cloud Build trigger in the GCP Console:

   Go to Cloud Build > Triggers. Create Trigger. Provide the trigger name, event type (e.g., Push to a branch), and source (GitHub repository). Set the build configuration to use cloudbuild.yaml. Save and create the trigger.

   add three subbscriptions to trigger as folow

   \_COMPOSER_BUCKET = 'write composer bucket name' \_COMPOSER_ENV_NAME = 'write your composer environement name' \_LOCATION = 'write composer location (region)'

9. Add Environment Variables in Cloud Composer

   After setting up the necessary infrastructure, it's essential to configure environment variables within your Cloud Composer environment. These variables can be used to control various aspects of your Airflow workflows dynamically.

   - Navigate to the Cloud Composer Environment
   - Add all Environment Variables below keys and complete the correspandant value :

   ```
       PROJECT_NAME : 'your project name'
       BUCKET_NAME : 'your cloud storage bucket name'
       LOCATION  : 'region of your bucket'

       DATA_FOLDER : data
       IN_FOLDER : in
       ARCHIVE_FOLDER  : archive
       ERROR_FOLDER : error
       RAW_DATASET : RAW
       RAW_SALES_TABLE : RAW_SALES_TABLE
       DATAWERHOUSE_DATASET : DATAWERHOUSE
       DWH_TABLE : DWH
   ```

Once the Terraform configurations are applied, and the Cloud Build trigger is set up, validate by checking the specified GCP project to ensure all services are correctly provisioned and operational.

10. Push Changes and Monitor Build Process

    - After configuring the Cloud Build trigger, push your changes to GitHub to initiate the automated deployment:

    - Push Changes to GitHub: Use git push to upload your latest changes to the branch monitored by the Cloud Build trigger.

    - Check Build Progress: Go to Cloud Build > History in the Google Cloud Console to view the progress and status of your build.

    - Ensure the build completes successfully and without errors.

11. Verify DAGs in Composer

    - Ensure that all DAG files are correctly copied and visible in the Cloud Composer environment

    - Check GCS Bucket: Go to the GCS bucket linked with your Composer environment. Verify that all DAG files are present in the specified DAG folder.

    - Open Airflow Web UI: Return to the Cloud Composer details page in the Google Cloud Console. Click on the link to the Airflow web UI found under the Airflow webserver section. In the Airflow UI, check that all DAGs are listed and can be triggered manually.

    - Confirmation Confirm that all components are functional and the DAGs are operational:

    - Ensure that no errors are reported in the Cloud Build history.
    - Confirm that all DAGs are available in the Airflow web UI and appear as expected.
    - Optionally, trigger a DAG manually to confirm that workflows execute correctly.
