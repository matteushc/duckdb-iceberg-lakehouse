# DuckDB + Iceberg + MinIO Lakehouse

Small open source lakehouse demo using:

- DuckDB as the SQL engine from Python
- Apache Iceberg tables through an Iceberg REST catalog
- MinIO as S3-compatible object storage
- Docker Compose for the whole stack

## Services

| Service | Purpose | URL |
| --- | --- | --- |
| `minio` | S3-compatible object storage | <http://localhost:9001> |
| `iceberg-rest` | Apache Iceberg REST catalog | <http://localhost:8181> |
| `jupyter` | JupyterLab with DuckDB, MinIO, and notebooks | <http://localhost:8888> |
| `app` | Python + DuckDB demo runner | n/a |

Default MinIO credentials are `admin` / `password123`.
Default Jupyter token is `lakehouse`.

## Run

```bash
cp .env.example .env
docker compose up --build
```

The `app` service creates a bucket, attaches DuckDB to the Iceberg REST catalog, creates `lakehouse_db.demo.orders`, inserts sample rows, and prints an aggregate query plus Iceberg snapshot metadata.

Open JupyterLab:

```bash
docker compose up --build jupyter
```

Then visit <http://localhost:8888/lab?token=lakehouse> and open `notebooks/duckdb_minio_iceberg.ipynb`.

Run the demo again after services are already up:

```bash
docker compose run --rm app
```

Stop and remove containers:

```bash
docker compose down
```

Remove object storage data as well:

```bash
docker compose down -v
```

## Useful Commands

Open a DuckDB shell inside the app container:

```bash
docker compose run --rm app python
```

Then:

```python
import duckdb
con = duckdb.connect()
con.sql("LOAD httpfs; LOAD iceberg;")
```

The main executable example lives in `app/main.py`.
The shared DuckDB + Iceberg + MinIO connection helper lives in `app/lakehouse.py`.
