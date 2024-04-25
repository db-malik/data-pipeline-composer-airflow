resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = "RAW_DATASET_TERRAFORM"
  location   = "europe-west3"
}

resource "google_bigquery_table" "raw_sales_table" {
  dataset_id = google_bigquery_dataset.raw_dataset.dataset_id
  table_id   = "RAW_SALES_TABLE"
  schema = jsonencode([
    { "name" : "SaleID", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "ProductID", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "Quantity", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "Price", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "SaleDate", "type" : "STRING", "mode" : "NULLABLE" }
  ])
  depends_on = [google_bigquery_dataset.raw_dataset]
}
