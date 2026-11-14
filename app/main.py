from datetime import datetime, timezone

import duckdb

from app.lakehouse import connect_lakehouse


def print_result(result: duckdb.DuckDBPyRelation) -> None:
    rows = result.fetchall()
    columns = [column[0] for column in result.description]
    widths = [
        max(len(str(value)) for value in [column, *[row[index] for row in rows]])
        for index, column in enumerate(columns)
    ]

    print(" | ".join(column.ljust(widths[index]) for index, column in enumerate(columns)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(str(value).ljust(widths[index]) for index, value in enumerate(row)))


def run_demo() -> None:
    con = connect_lakehouse()

    con.sql("CREATE SCHEMA IF NOT EXISTS lakehouse_db.demo;")
    con.sql("DROP TABLE IF EXISTS lakehouse_db.demo.orders;")
    con.sql(
        """
        CREATE TABLE lakehouse_db.demo.orders (
            order_id INTEGER,
            customer VARCHAR,
            order_ts TIMESTAMP,
            amount DOUBLE,
            status VARCHAR
        )
        WITH (
            'format-version' = '2'
        );
        """
    )

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    con.sql(
        f"""
        INSERT INTO lakehouse_db.demo.orders VALUES
            (1, 'Ada', TIMESTAMP '{now}', 125.50, 'paid'),
            (2, 'Linus', TIMESTAMP '{now}', 89.90, 'paid'),
            (3, 'Grace', TIMESTAMP '{now}', 42.00, 'pending'),
            (4, 'Marta', TIMESTAMP '{now}', 240.10, 'paid');
        """
    )

    print("\nDuckDB reading an Apache Iceberg table stored in MinIO:\n")
    print_result(
        con.sql(
            """
            SELECT
                status,
                count(*) AS orders,
                round(sum(amount), 2) AS total_amount
            FROM lakehouse_db.demo.orders
            GROUP BY status
            ORDER BY status;
            """
        )
    )

    print("\nIceberg snapshots:\n")
    print_result(
        con.sql(
            """
            SELECT
                snapshot_id,
                sequence_number,
                timestamp_ms
            FROM iceberg_snapshots(lakehouse_db.demo.orders);
            """
        )
    )


if __name__ == "__main__":
    run_demo()
