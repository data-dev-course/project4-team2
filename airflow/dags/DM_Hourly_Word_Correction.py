from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from airflow.providers.amazon.aws.transfers.redshift_to_s3 import RedshiftToS3Operator
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator

from datetime import datetime, timedelta


default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id="DM_Hourly_Word_Correction_To_RDS",
    default_args = default_args ,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval=None
)as dag:

    s3_folder = "DM/"
    
    # DM table - transform 
    create_dm = RedshiftSQLOperator(
        task_id='create_dm_hour_word_corretion',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = ["DROP TABLE IF EXISTS analytics.hour_word_corretion;",
                """
                CREATE TABLE analytics.hour_word_corretion AS (
                    SELECT DATE_TRUNC('hour', checked_date) AS recorded_time,
                        original_word AS incorrect_word,
                        checked_word AS corrected_word,
                        content_tag,
                        check_reult
                    FROM "dev"."analytics"."spell_check_word"
                    WHERE recorded_time >= CURRENT_DATE - INTERVAL '1 month'
                    AND original_word !~ '[ㄱ-ㅎㅏ-ㅣㅋㅎㅉ]+'
                    AND checked_word !~ '[ㄱ-ㅎㅏ-ㅣㅋㅎㅉ]+'
                );
                """]
    )
    
    
    s3_folder = "DM/"
    s3_key = "{{ ds }}"+"/"+"{{ ds }}"+"_"+"{{ ts_nodash[9:11] }}"
    
    # Transfer DM table from redshift to s3
    dm_to_s3 = RedshiftToS3Operator(
        task_id="transfer_redshift_to_s3",
        redshift_conn_id = 'redshift_dev_db',
        s3_bucket = Variable.get('S3-BUCKET'),
        s3_key=s3_folder+"hour_word_corretion/"+s3_key,
        schema="analytics",
        table="hour_word_corretion",
        select_query="SELECT * FROM analytics.hour_word_corretion;",
        unload_options = ['FORMAT CSV','PARALLEL OFF', 'EXTENSION \'csv\'', 'ALLOWOVERWRITE'],
        table_as_file_name = True,
    )
    
    # file_sensor = S3KeySensor(
    #     task_id='s3_key_sensor'
    # ) 
    
    # Check if table exists
    check_created_table = PostgresOperator(
        task_id = "check_create_table",
        postgres_conn_id = 'postgres_default',
        autocommit = True,
        sql = ["DROP TABLE IF EXISTS hour_word_corretion;", 
                """
                CREATE TABLE hour_word_corretion (
                    recorded_time timestamp,
                    incorrect_word varchar(65535), 
                    corrected_word varchar(65535),
                    content_tag varchar(10),
                    check_reult int
               );
            """]
    )
    
    # Import s3 from rds
    s3_to_rds = PostgresOperator(
        task_id = "s3_to_rds",
        postgres_conn_id = 'postgres_default',
        autocommit = True,
        sql = f""" 
        SELECT aws_s3.table_import_from_s3(
            'hour_word_corretion',
            '',
            '(format csv, HEADER TRUE)',
            '{Variable.get('S3-BUCKET')}',
            '{s3_folder}hour_word_corretion/{s3_key}/hour_word_corretion_000.csv',
            '{Variable.get('AWS_DEFAULT_REGION')}'
        );"""
    )

        
        
    create_dm >> dm_to_s3 >> check_created_table >> s3_to_rds
        
        
    
    
    