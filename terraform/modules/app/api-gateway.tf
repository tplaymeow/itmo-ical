resource "yandex_api_gateway" "itmo-ical-api-gateway" {
  name = "itmo-ical-api-gateway"

  custom_domains {
    certificate_id = yandex_cm_certificate.itmo-ical-certificate.id
    fqdn           = var.domain
  }

  spec = templatefile("../../openapi/api.yaml", {
    ADD_NEW_CALENDAR_FUNCTION_ID = yandex_function.add-new-calendar-function.id
    ADD_NEW_CALENDAR_FUNCTION_SA = yandex_iam_service_account.itmo-ical-service-account.id
    GET_CALENDAR_FUNCTION_ID     = yandex_function.get-calendar-function.id
    GET_CALENDAR_FUNCTION_SA     = yandex_iam_service_account.itmo-ical-service-account.id
    WEB_CALENDAR_BUCKET          = yandex_storage_bucket.itmo-ical-web.bucket
    WEB_CALENDAR_SA              = yandex_iam_service_account.itmo-ical-service-account.id
  })
}
