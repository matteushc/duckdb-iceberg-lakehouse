import os
import time

import duckdb
import requests


def env(name: str, default: str) -> str:
    return os.getenv(name, default)


MINIO_ENDPOINT = env("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", "password123")
AWS_REGION = env("AWS_REGION", "us-east-1")
ICEBERG_REST_URI = env("ICEBERG_REST_URI", "http://iceberg-rest:8181")
ICEBERG_WAREHOUSE = env("ICEBERG_WAREHOUSE", "warehouse")


def wait_for_rest_catalog(timeout_seconds: int = 90) -> None:
    deadline = time.monotonic() + timeout_seconds
    url = f"{ICEBERG_REST_URI.rstrip('/')}/v1/config"

    while time.monotonic() < deadline:
        try:
            response = requests.get(url, timeout=3)
            if response.ok:
                return
        except requests.RequestException:
            pass

        time.sleep(2)

    raise TimeoutError(f"Iceberg REST catalog did not become ready at {url}")


def connect_lakehouse(wait: bool = True) -> duckdb.DuckDBPyConnection:
    if wait:
        wait_for_rest_catalog()

    path = "/app/lakehouse/lakehouse.duckdb"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = duckdb.connect(path)
    con.sql("INSTALL httpfs;")
    con.sql("LOAD httpfs;")
    con.sql("INSTALL iceberg;")
    con.sql("LOAD iceberg;")

    con.sql(
        f"""
        CREATE OR REPLACE SECRET minio_secret (
            TYPE s3,
            KEY_ID '{MINIO_ACCESS_KEY}',
            SECRET '{MINIO_SECRET_KEY}',
            REGION '{AWS_REGION}',
            ENDPOINT '{MINIO_ENDPOINT}',
            URL_STYLE 'path',
            USE_SSL false
        );
        """
    )

    con.sql(
        f"""
        ATTACH '{ICEBERG_WAREHOUSE}' AS lakehouse_db (
            TYPE iceberg,
            ENDPOINT '{ICEBERG_REST_URI}',
            AUTHORIZATION_TYPE 'none',
            ACCESS_DELEGATION_MODE 'none'
        );
        """
    )

    return con
