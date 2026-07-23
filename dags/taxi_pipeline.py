"""Week 12 assignment starter.

Turn this into a scheduled, parameterized, retryable pipeline. The task
list, the file-by-file map, and the point breakdown are in README.md; the
full brief is in the Week 12 "Assignment: Orchestrated Pipeline" chapter.

This starter parses, so `astro dev start` shows the DAG in the UI, but every
task body raises NotImplementedError and the decorator is not configured yet.
Replace the stubs, wire the tasks together, and fill in the decorator. The
autograder fails while any NotImplementedError remains.
"""

import io

import os
from datetime import datetime
from pathlib import Path
from pydoc import text
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.standard.operators.bash import BashOperator


import requests

from airflow.sdk import dag, get_current_context, task

# Your per-student schema. AIRFLOW_STUDENT is set in .env for local Astro dev;
# on the shared VM it falls back to the dags/<name>/ directory name.
STUDENT = os.environ.get("AIRFLOW_STUDENT") or Path(__file__).parent.name
SCHEMA = f"airflow_{STUDENT}"
TLC_BASE = "https://d37ci6vzurychx.cloudfront.net/trip-data"
DBT_ENV = {
    "PG_HOST": "{{ conn.azure_pg.host }}",
    "PG_USER": "{{ conn.azure_pg.login }}",
    "PG_PASSWORD": "{{ conn.azure_pg.password }}",
    "PG_DBNAME": "{{ conn.azure_pg.schema }}",
    "PG_SCHEMA": SCHEMA,
}


def find_dbt_dir() -> str:
    """Return the mounted dbt project path (Astro vs shared-VM install root)."""
    for candidate in (
        "/usr/local/airflow/include/dbt_project",  # Astro CLI
        "/opt/airflow/include/dbt_project",  # shared VM docker-compose
    ):
        if Path(candidate).is_dir():
            return candidate
    return "/usr/local/airflow/include/dbt_project"


DBT_DIR = find_dbt_dir()


def parquet_url_for(ds: str) -> str:
    """Return the TLC green-taxi parquet URL for a logical date.

    Pure function, extracted from ``download_taxi_month`` so it can be
    unit-tested without an Airflow runtime (see Chapter 6).

    >>> parquet_url_for("2024-01-01")
    'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-01.parquet'
    """
    year_month = ds[:7]  # "2024-01-01" -> "2024-01"
    return f"{TLC_BASE}/green_tripdata_{year_month}.parquet"


def _ds_from_context() -> str:
    """Return the logical-date string for the current task run.

    TaskFlow's ``ds: str`` auto-injection works for *scheduled* runs
    (``logical_date`` is set to the interval boundary) but breaks for
    *manual* triggers in Airflow 3, where ``logical_date`` defaults to
    ``None``. Reading through ``get_current_context()`` with a
    ``run_after`` fallback is the form that works in both modes.
    """
    ctx = get_current_context()
    dr = ctx["dag_run"]
    dt = dr.logical_date or dr.run_after
    return dt.strftime("%Y-%m-%d")


@dag(
    dag_id="bader_taxi_pipeline",
    schedule="@monthly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,  # serialize: concurrent dbt runs collide on __dbt_backup relations
    default_args={
        "retries": 2
    },  # retry transient failures twice before marking the task failed
    tags=["week12", "taxi", "student:bader"],
)
def taxi_pipeline():
    @task
    def ingest_taxi_month() -> int:
        ds = _ds_from_context()
        year_month = ds[:7]
        resp = requests.get(parquet_url_for(ds), timeout=60)
        resp.raise_for_status()
        df = pd.read_parquet(io.BytesIO(resp.content))

        hook = PostgresHook(postgres_conn_id="azure_pg")
        engine = hook.get_sqlalchemy_engine()
        with hook.get_conn() as conn, conn.cursor() as cur:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"')
        df.head(0).to_sql(
            "raw_trips",
            engine,
            schema=SCHEMA,
            if_exists="append",
            index=False,
        )
        with hook.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                f'DELETE FROM "{SCHEMA}".raw_trips '
                "WHERE to_char(lpep_pickup_datetime, 'YYYY-MM') = %s",
                (year_month,),
            )
        df.to_sql(
            "raw_trips",
            engine,
            schema=SCHEMA,
            if_exists="append",
            index=False,
        )
        return len(df)

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"uvx --python 3.11 --from 'dbt-core==1.10.*' --with 'dbt-postgres==1.10.*' dbt deps --project-dir {DBT_DIR} --profiles-dir {DBT_DIR} && uvx --python 3.11 --from 'dbt-core==1.10.*' --with 'dbt-postgres==1.10.*' dbt run --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}",
        env=DBT_ENV,
        append_env=True,
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"uvx --python 3.11 --from 'dbt-core==1.10.*' --with 'dbt-postgres==1.10.*' dbt test --project-dir {DBT_DIR} --profiles-dir {DBT_DIR}",
        env=DBT_ENV,
        append_env=True,
    )

    ingest_taxi_month() >> dbt_run >> dbt_test


taxi_pipeline()
