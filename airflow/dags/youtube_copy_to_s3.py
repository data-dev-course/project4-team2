from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from plugins import s3, youtube_api

DAG_ID = 'youtube_copy_to_S3'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 1),
    catchup=False,
    schedule_interval="@daily",
) as dag:
    
    get_youtube_data_task = PythonOperator(
        task_id = 'get_youtube_data',
        python_callable=youtube_api.get_data
    )
    
    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=s3.upload_to_s3,
        op_args=[get_youtube_data_task.output]
    )
    
    get_youtube_data_task >> upload_to_s3_task