from airflow import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from datetime import datetime, timedelta
import logging
import os

# Path to dbt project
DBT_PROJECT_PATH = "/usr/local/airflow/include/dbt"

logger = logging.getLogger('dag_logger')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='ecommerce_dag',
    default_args=default_args,
    description='Daily ingestion of ecommerce transactions to S3 and Snowflake',
    schedule='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'ingestion'],
)


def start_job(**context):
    execution_date = context['ds']
    logger.info(f"Starting the pipeline for date: {execution_date}")


def end_job(**context):
    execution_date = context['ds']
    logger.info(f"All processes completed for date: {execution_date}")


# Helper function to generate S3 path based on execution date
def get_s3_key(ds):
    """Generate partitioned S3 key: raw/year=YYYY/month=MM/day=DD/transactions_YYYY-MM-DD.csv"""
    date_obj = datetime.strptime(ds, '%Y-%m-%d')
    return f"raw/year={date_obj.year}/month={date_obj.month:02d}/day={date_obj.day:02d}/transactions_{ds}.csv"


def get_local_filename(ds):
    """Generate local filename based on execution date"""
    return f"/usr/local/airflow/include/data/transactions_{ds}.csv"


def check_file_exists(**context):
    """Branch: if daily file exists -> 'upload_to_s3', else -> 'skip_upload'."""
    ds = context['ds']
    file_path = f"/usr/local/airflow/include/data/transactions_{ds}.csv"
    if os.path.exists(file_path):
        logger.info(f"File found: {file_path}")
        return "upload_to_s3"
    else:
        logger.warning(f"File not found: {file_path}. Skipping upload only.")
        return "skip_upload"


start_task = PythonOperator(
    task_id='start_job',
    python_callable=start_job,
    dag=dag
)

end_task = PythonOperator(
    task_id='end_job',
    python_callable=end_job,
    trigger_rule='none_failed_min_one_success',  # Run even if upstream tasks were skipped
    dag=dag
)

check_file_task = BranchPythonOperator(
    task_id='check_file_exists',
    python_callable=check_file_exists,
    dag=dag
)

# Dummy to represent the branch when upload is skipped
skip_upload = EmptyOperator(task_id='skip_upload', dag=dag)

# Simpler template approach for upload
upload_to_s3_task = LocalFilesystemToS3Operator(    
    task_id='upload_to_s3',
    filename="/usr/local/airflow/include/data/transactions_{{ ds }}.csv",
    # use ds (YYYY-MM-DD) to build partition parts — execution_date isn't available in this template context
    dest_key="raw/year={{ ds.split('-')[0] }}/month={{ ds.split('-')[1] }}/day={{ ds.split('-')[2] }}/transactions_{{ ds }}.csv",
    dest_bucket="ecommerce-dataops",
    aws_conn_id='aws_default',
    replace=True,
    dag=dag
)

# Load data incrementally into Snowflake using COPY INTO with file tracking
# The COPY INTO command with file metadata tracking prevents reloading the same file
load_to_snowflake_task = SnowflakeOperator(
    task_id='load_to_snowflake',
    snowflake_conn_id='snowflake_default',
    sql="""
        USE WAREHOUSE ecommerce_wh;
        USE DATABASE ecommerce_db;
        USE SCHEMA RAW;

        COPY INTO ECOMMERCE_TABLE (
            InvoiceNo,
            StockCode,
            Description,
            Quantity,
            InvoiceDate,
            UnitPrice,
            CustomerID,
            Country
        )
        FROM (
            SELECT
                $1::STRING  AS InvoiceNo,
                $2::STRING  AS StockCode,
                $3::STRING  AS Description,
                $4::INTEGER AS Quantity,
                $5::STRING  AS InvoiceDate,
                $6::FLOAT   AS UnitPrice,
                $7::INTEGER AS CustomerID,
                $8::STRING  AS Country
            FROM @my_s3_stage/raw/year={{ ds.split('-')[0] }}/month={{ ds.split('-')[1] }}/day={{ ds.split('-')[2] }}/transactions_{{ ds }}.csv
        )
        FILE_FORMAT = (FORMAT_NAME = 'CSV_FORMAT')
        ON_ERROR = 'CONTINUE';
    """,
    trigger_rule='one_success',
    dag=dag
)

# DBT TASKS 

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command=f'cd {DBT_PROJECT_PATH} && dbt run --profiles-dir {DBT_PROJECT_PATH}',
    dag=dag
)

dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command=f'cd {DBT_PROJECT_PATH} && dbt test --profiles-dir {DBT_PROJECT_PATH}',
    dag=dag
)
#comment 
start_task >> check_file_task
check_file_task >> upload_to_s3_task >> load_to_snowflake_task
check_file_task >> skip_upload >> load_to_snowflake_task
load_to_snowflake_task >> dbt_run >> dbt_test >> end_task