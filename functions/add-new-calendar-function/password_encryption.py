import base64
import os
from dataclasses import dataclass

import requests

KMS_KEY_ID = os.getenv("KMS_KEY_ID")


@dataclass
class PasswordEncryptionResult:
    password: str
    key_id: str
    version_id: str


def base64_encode(string: str) -> str:
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


def encrypt_password(login: str, password: str, token: str) -> PasswordEncryptionResult:
    response = requests.post(
        f"https://kms.yandex/kms/v1/keys/{KMS_KEY_ID}:encrypt",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "aadContext": base64_encode(login),
            "plaintext": base64_encode(password)
        },
    )

    response.raise_for_status()

    json_result = response.json()
    return PasswordEncryptionResult(
        password=json_result["ciphertext"],
        key_id=json_result["keyId"],
        version_id=json_result["versionId"]
    )
