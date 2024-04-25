resource "google_bigquery_dataset" "datawarehouse_dataset" {
  dataset_id = "DATAWERHOUSE"
  location   = "europe-west3"
}

resource "google_bigquery_table" "transformed_table" {
  dataset_id = google_bigquery_dataset.datawarehouse_dataset.dataset_id
  table_id   = "DWH"
  schema = jsonencode([
    { "name" : "SaleID", "type" : "INTEGER", "mode" : "NULLABLE" },
    { "name" : "ProductID", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "Quantity", "type" : "INTEGER", "mode" : "NULLABLE" },
    { "name" : "Price", "type" : "NUMERIC", "mode" : "NULLABLE" },
    { "name" : "SaleDate", "type" : "DATE", "mode" : "NULLABLE" },
    { "name" : "TotalPrice", "type" : "NUMERIC", "mode" : "NULLABLE" }
  ])
}
