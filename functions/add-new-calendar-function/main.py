import json
import logging
import uuid

import database
import password_encryption


def error() -> dict:
    return {"statusCode": 500}


def handler(event, context):
    body = json.loads(event["body"])
    login = body["login"]
    password = body["password"]

    try:
        user_password_encryption = password_encryption.encrypt_password(
            login,
            password,
            context.token["access_token"]
        )
    except Exception as e:
        logging.error(e)
        return error()

    user_id = str(uuid.uuid4())

    try:
        database.insert_to_database(
            login,
            user_password_encryption.password,
            user_password_encryption.key_id,
            user_password_encryption.version_id,
            user_id
        )
    except Exception as e:
        logging.error(e)
        return error()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "isBase64Encoded": False,
        "body": json.dumps({
            "user_id": user_id
        })
    }
