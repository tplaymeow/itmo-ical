import base64
import os

import requests

from models import User

KMS_KEY_ID = os.getenv("KMS_KEY_ID")


def base64_decode(string: str) -> str:
    return base64.b64decode(string.encode("utf-8")).decode("utf-8")


def base64_encode(string: str) -> str:
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


def decrypt_password(user: User, token: str) -> str:
    response = requests.post(
        f"https://kms.yandex/kms/v1/keys/{KMS_KEY_ID}:decrypt",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={
            "keyId": user.key_id,
            "versionId": user.version_id,
            "aadContext": base64_encode(user.login),
            "ciphertext": user.password
        },
    )

    response.raise_for_status()

    json_result = response.json()
    return base64_decode(json_result["plaintext"])
