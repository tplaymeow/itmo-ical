module "app" {
  source = "../modules/app"

  domain       = "itmo-calendar.tplaymeow.online"
  yc-token     = var.yc-token
  yc-cloud-id  = var.yc-cloud-id
  yc-folder-id = var.yc-folder-id
}

terraform {
  backend "s3" {
    endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }

    bucket = "itmo-ical-terraform-state"
    region = "ru-central1"
    key    = "state/terraform.tfstate"

    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
  }
}