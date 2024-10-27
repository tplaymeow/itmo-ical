import os
from datetime import datetime, timezone

import ydb

from models import User

driver = ydb.Driver(
    endpoint=os.getenv("YDB_ENDPOINT"),
    database=os.getenv("YDB_DATABASE"),
    credentials=ydb.iam.MetadataUrlCredentials(),
)
driver.wait(fail_fast=True, timeout=15)

pool = ydb.QuerySessionPool(driver)


def get_user_from_database(user_id: str) -> User:
    result_sets = pool.execute_with_retries(
        """
        DECLARE $userId AS Utf8;
        SELECT login, password, keyId, versionId
        FROM users
        WHERE userId = $userId;
        """,
        {
            "$userId": user_id,
        }
    )
    return User(
        result_sets[0].rows[0].login,
        result_sets[0].rows[0].password,
        result_sets[0].rows[0].keyId,
        result_sets[0].rows[0].versionId
    )

def get_access_token_from_database(user_id: str) -> str | None:
    result_sets = pool.execute_with_retries(
        """
        DECLARE $userId AS Utf8;
        SELECT accessToken
        FROM `authorization-tokens`
        WHERE userId = $userId;
        """,
        {
            "$userId": user_id,
        }
    )

    rows = result_sets[0].rows
    if len(rows) == 0:
        return None

    return rows[0].accessToken


def insert_access_token_to_database(user_id: str, access_token: str) -> None:
    pool.execute_with_retries(
        """
        DECLARE $userId AS Utf8;
        DECLARE $accessToken AS Utf8;
        DECLARE $createdAt AS Timestamp;
        UPSERT INTO `authorization-tokens` (userId, accessToken, createdAt)
        VALUES ($userId, $accessToken, $createdAt);
        """,
        {
            "$userId": user_id,
            "$accessToken": access_token,
            "$createdAt": (datetime.now(timezone.utc), ydb.PrimitiveType.Timestamp)
        }
    )
