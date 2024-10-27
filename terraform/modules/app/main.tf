terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  token     = var.yc-token
  cloud_id  = var.yc-cloud-id
  folder_id = var.yc-folder-id
  zone      = "ru-central1-a"
}