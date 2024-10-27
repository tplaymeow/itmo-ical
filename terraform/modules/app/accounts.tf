resource "yandex_iam_service_account" "itmo-ical-service-account" {
  folder_id = var.yc-folder-id
  name      = "itmo-ical-service-account"
}

resource "yandex_resourcemanager_folder_iam_member" "admin" {
  folder_id = var.yc-folder-id
  member    = "serviceAccount:${yandex_iam_service_account.itmo-ical-service-account.id}"
  role      = "admin"
}

resource "yandex_iam_service_account_static_access_key" "itmo-ical-service-account-obj-storage-static-key" {
  service_account_id = yandex_iam_service_account.itmo-ical-service-account.id
  description        = "static access key for object storage"
}
