resource "yandex_cm_certificate" "itmo-ical-certificate" {
  name    = "itmo-ical-certificate"
  domains = [var.domain]

  managed {
    challenge_type = "DNS_CNAME"
  }
}