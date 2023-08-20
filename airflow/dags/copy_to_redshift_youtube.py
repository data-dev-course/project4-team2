from airflow import DAG
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator


default_args = {
    
}
with DAG(
    dag_id="copy_to_redshift_youtube",
    default_args = default_args ,
    catchup=False,
    schedule_interval=None
)as dag:
    

    check_table_created_task = RedshiftSQLOperator(
        task_id='check_table_created',
        redshift_conn_id = 'redshift_conn_id',
        autocommit = True,
        sql = 
        """
        CREATE TABLE IF NOT EXISTS raw_data.tb_youtube (
            scr_date TIMESTAMP,
            video_id VARCHAR(128),
            channel_id TIMESTAMP,
            title TIMESTAMP,
            video_published_at TIMESTAMP,
            video_link VARCHAR(1024) 
            comment_id TIMESTAMP,
            author VARCHAR(128),
            comment TEXT,
            comment_publishd_at TIMESTAMP,
            comment_date TIMESTAMP,
            tag VARCHAR(15)
        );
        """ 
    )
    
    copy_to_redshift_task = S3ToRedshiftOperator(
        task_id='s3_to_redshift',
        schema='raw_data',
        table='tb_youtube',
        s3_bucket='de-3-2',
        s3_key='raw_data/youtube/',
        redshift_conn_id = 'redshift_conn_id',
        copy_options=[
            "CSV IGNOREHEADER 1",
            "DATEFORMAT AS 'auto'",
            "TIMEFORMAT AS 'auto'"
        ],
        method='APPEND'
    )
         
    check_table_created_task >> copy_to_redshift_task 
        
    
    

    