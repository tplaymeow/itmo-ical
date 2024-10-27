data "archive_file" "get-calendar-function-archive" {
  source_dir  = "../../functions/get-calendar-function"
  output_path = "../../functions_archives/get-calendar-function.zip"
  type        = "zip"
}

resource "yandex_function" "get-calendar-function" {
  name               = "get-calendar-function"
  user_hash          = data.archive_file.get-calendar-function-archive.output_base64sha256
  runtime            = "python312"
  entrypoint         = "main.handler"
  memory             = "128"
  execution_timeout  = "10"
  service_account_id = yandex_iam_service_account.itmo-ical-service-account.id

  environment = {
    KMS_KEY_ID : yandex_kms_symmetric_key.itmo-password-encryption-key.id,
    YDB_ENDPOINT : "grpcs://${yandex_ydb_database_serverless.itmo-ical-database.ydb_api_endpoint}",
    YDB_DATABASE : yandex_ydb_database_serverless.itmo-ical-database.database_path,
  }

  content {
    zip_filename = data.archive_file.get-calendar-function-archive.output_path
  }
}