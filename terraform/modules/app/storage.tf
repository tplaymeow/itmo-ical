resource "yandex_storage_bucket" "itmo-ical-web" {
  access_key = yandex_iam_service_account_static_access_key.itmo-ical-service-account-obj-storage-static-key.access_key
  secret_key = yandex_iam_service_account_static_access_key.itmo-ical-service-account-obj-storage-static-key.secret_key
  bucket     = "itmo-ical-web"
  acl        = "public-read"

  website {
    index_document = "index.html"
  }
}

resource "yandex_storage_object" "itmo-ical-web-index-html" {
  access_key   = yandex_iam_service_account_static_access_key.itmo-ical-service-account-obj-storage-static-key.access_key
  secret_key   = yandex_iam_service_account_static_access_key.itmo-ical-service-account-obj-storage-static-key.secret_key
  bucket       = yandex_storage_bucket.itmo-ical-web.id
  key          = "index.html"
  content_type = "text/html"
  source_hash  = filesha256("../../web-page/index.html")
  source       = "../../web-page/index.html"
}
