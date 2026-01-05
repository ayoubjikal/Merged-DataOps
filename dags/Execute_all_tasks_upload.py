# dags/load_s3_to_snowflake.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import snowflake.connector
import os

default_args = {
    "owner": "ayoub",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

def open_connection():
    conn = BaseHook.get_connection("snowflake_conn")
    sf = snowflake.connector.connect(
        user=conn.login,
        password=conn.password,
        account=conn.extra_dejson.get("account"),
        warehouse=conn.extra_dejson.get("warehouse"),
        database=conn.extra_dejson.get("database"),
        schema=conn.schema,
        role=conn.extra_dejson.get("role")
    )
    return sf

def create_raw():
    sf = open_connection()
    cur = sf.cursor()
    cur.execute("CREATE OR REPLACE SCHEMA ecommerce_db.raw;")
    print(cur.fetchone())
    sf.close()

def create_table():
    sf = open_connection()
    cur = sf.cursor()
    cur.execute("""CREATE OR REPLACE TABLE ecommerce_table (
        InvoiceNo      VARCHAR,
        StockCode      VARCHAR,
        Description    VARCHAR,
        Quantity       NUMBER,
        InvoiceDate    TIMESTAMP,
        UnitPrice      FLOAT,
        CustomerID     VARCHAR,
        Country        VARCHAR
    );""")
    print(cur.fetchone())
    sf.close()

def create_file_format():
    sf = open_connection()
    cur = sf.cursor()
    cur.execute("""CREATE OR REPLACE FILE FORMAT my_csv_format
        TYPE = 'CSV'
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        TIMESTAMP_FORMAT = 'MM/DD/YYYY HH24:MI'
        ENCODING = 'ISO8859-1';""")
    print(cur.fetchone())
    sf.close()

def create_stage():
    sf = open_connection()
    cur = sf.cursor()
    cur.execute(f"""
        CREATE OR REPLACE STAGE ecommerce_stage
        URL = 's3://ecommerce-dataops/raw/data.csv'
        CREDENTIALS = (AWS_KEY_ID='{os.getenv("AWS_ACCESS_KEY_ID")}' 
                       AWS_SECRET_KEY='{os.getenv("AWS_SECRET_ACCESS_KEY")}')
        FILE_FORMAT = (format_name= raw.my_csv_format);
    """)
    print(cur.fetchone())
    sf.close()

def upload_snowflake():
    sf = open_connection()
    cur = sf.cursor()
    cur.execute("COPY INTO ecommerce_table FROM @ecommerce_stage FILE_FORMAT = my_csv_format")
    print(cur.fetchone())
    sf.close()

with DAG(
    dag_id="all_steps_s3_to_snowflake",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    default_args=default_args,
    catchup=False,
    tags=["load", "snowflake", "s3"],
) as dag:

    create_raw_task = PythonOperator(task_id='test_raw', python_callable=create_raw)
    create_table_task = PythonOperator(task_id='test_table', python_callable=create_table)
    create_fileFormat_task = PythonOperator(task_id='test_file_format', python_callable=create_file_format)
    create_stage_task = PythonOperator(task_id='test_stage', python_callable=create_stage)
    upload_snowflake_task = PythonOperator(task_id='test_snowflake', python_callable=upload_snowflake)

    from airflow.providers.standard.operators.bash import BashOperator

    dbt_run = BashOperator(
    task_id='run_dbt_models',
    bash_command="""
    cd /usr/local/airflow/include/dbt && \
    dbt deps && \
    dbt run --profiles-dir /usr/local/airflow/include/dbt/profiles
    """,
)

    create_raw_task >> create_table_task >> create_fileFormat_task >> create_stage_task >> upload_snowflake_task >> dbt_run
