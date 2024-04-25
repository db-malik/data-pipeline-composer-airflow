resource "google_bigquery_dataset" "datawarehouse_dataset" {
  dataset_id = "DATAWERHOUSE_TERRAFRM"
  location   = "europe-west3"
}

resource "google_bigquery_table" "transformed_table" {
  dataset_id = google_bigquery_dataset.datawarehouse_dataset.dataset_id
  table_id   = "transformed_Table"
  schema = jsonencode([
    { "name" : "SaleID", "type" : "INTEGER", "mode" : "NULLABLE" },
    { "name" : "ProductID", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "Quantity", "type" : "INTEGER", "mode" : "NULLABLE" },
    { "name" : "Price", "type" : "FLOAT", "mode" : "NULLABLE" },
    { "name" : "SaleDate", "type" : "DATE", "mode" : "NULLABLE" }
  ])
}
