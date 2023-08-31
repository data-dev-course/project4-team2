from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from plugins import s3, youtube_api, youtube_api_v2

DAG_ID = 'youtube_copy_to_S3'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval="@daily",
) as dag:
    
    get_youtube_data_task = PythonOperator(
        task_id = 'get_youtube_data',
        python_callable=youtube_api_v2.get_data

    )
    
    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=s3.upload_to_s3,
        op_args=[get_youtube_data_task.output]
    )
    
    
    trigger_youtube_copy_to_redshift = TriggerDagRunOperator(
        task_id='trigger_youtube_copy_to_redshift',
        trigger_dag_id = 'youtube_copy_to_redshift',
        reset_dag_run=True,
    )
    get_youtube_data_task >> upload_to_s3_task >> trigger_youtube_copy_to_redshift