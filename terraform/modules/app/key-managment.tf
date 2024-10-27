resource "yandex_kms_symmetric_key" "itmo-password-encryption-key" {
  name              = "itmo-password-encryption-key"
  default_algorithm = "AES_128"

  lifecycle {
    prevent_destroy = true
  }
}
