resource "yandex_ydb_database_serverless" "itmo-ical-database" {
  name                = "itmo-ical-database"
  deletion_protection = true
}

resource "yandex_ydb_table" "users-table" {
  path              = "users"
  connection_string = yandex_ydb_database_serverless.itmo-ical-database.ydb_full_endpoint

  column {
    name     = "login"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "password"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "keyId"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "versionId"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "userId"
    type     = "Utf8"
    not_null = true
  }

  primary_key = ["login"]
}

resource "yandex_ydb_table" "authorization-tokens-table" {
  path              = "authorization-tokens"
  connection_string = yandex_ydb_database_serverless.itmo-ical-database.ydb_full_endpoint

  column {
    name     = "userId"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "accessToken"
    type     = "Utf8"
    not_null = true
  }

  column {
    name     = "createdAt"
    type     = "Timestamp"
    not_null = true
  }

  ttl {
    column_name     = "createdAt"
    expire_interval = "PT55M"
  }

  primary_key = ["userId"]
}