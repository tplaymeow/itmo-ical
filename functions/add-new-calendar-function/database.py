import os

import ydb

driver = ydb.Driver(
    endpoint=os.getenv("YDB_ENDPOINT"),
    database=os.getenv("YDB_DATABASE"),
    credentials=ydb.iam.MetadataUrlCredentials(),
)
driver.wait(fail_fast=True, timeout=5)

pool = ydb.QuerySessionPool(driver)


def insert_to_database(login: str, password: str, key_id: str, version_id: str, user_id: str) -> None:
    pool.execute_with_retries(
        """
        DECLARE $login AS Utf8;
        DECLARE $password AS Utf8;
        DECLARE $keyId AS Utf8;
        DECLARE $versionId AS Utf8;
        DECLARE $userId AS Utf8;
        UPSERT INTO users (login, password, keyId, versionId, userId)
        VALUES ($login, $password, $keyId, $versionId, $userId);
        """,
        {
            "$login": login,
            "$password": password,
            "$keyId": key_id,
            "$versionId": version_id,
            "$userId": user_id,
        }
    )
