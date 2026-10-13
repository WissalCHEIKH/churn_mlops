from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'churn_mlops_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    ingest_task = BashOperator(
        task_id='ingest_data',
        bash_command='python /opt/airflow/include/ingest.py'
    )

    validate_task = BashOperator(
        task_id='validate_data',
        bash_command='python /opt/airflow/include/validate.py'
    )

    train_task = BashOperator(
        task_id='train_model',
        bash_command='python /opt/airflow/include/train.py'
    )

    ingest_task >> validate_task >> train_task