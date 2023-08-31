from airflow import DAG
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

scr_date = datetime.now().strftime('%Y-%m-%d')
default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3)
}
with DAG(
    dag_id="youtube_copy_to_redshift",
    default_args = default_args ,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval=None
)as dag:
    

    check_table_created_task = RedshiftSQLOperator(
        task_id='check_table_created',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        CREATE TABLE IF NOT EXISTS raw_data.tb_youtube (
            scr_date TIMESTAMP,
            video_id VARCHAR(128),
            channel_id VARCHAR(128),
            title VARCHAR(1028),
            category VARCHAR(128),
            video_published_at TIMESTAMP,
            video_link TEXT,
            comment_id VARCHAR(128),
            author VARCHAR(256),
            comment VARCHAR(30000),
            comment_publishd_at TIMESTAMP,
            comment_date TIMESTAMP
        );
        """ 
    )
    
    copy_to_redshift_task = S3ToRedshiftOperator(
        task_id='s3_to_redshift',
        schema='raw_data',
        table='tb_youtube',
        s3_bucket='de-3-2',
        s3_key=f'raw_data/youtube/{scr_date}/{scr_date}.csv',
        redshift_conn_id = 'redshift_dev_db',
        copy_options=[
            "CSV IGNOREHEADER 1",
            "DATEFORMAT AS 'auto'",
            "TIMEFORMAT AS 'auto'"
        ],
        method='APPEND'
    )
    

    check_table_created_task >> copy_to_redshift_task 
        
    
    

    