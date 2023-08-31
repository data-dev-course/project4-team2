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
    dag_id="DM_Daily_Grammer_Stats_To_RDS",
    default_args = default_args ,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval=None
)as dag:

    s3_folder = "DM/"
    s3_key = "{{ ds }}"+"/"+"{{ ds }}"+"_"+"{{ ts_nodash[9:11] }}"
    # DM table - transform 
    create_dm = RedshiftSQLOperator(
        task_id='create_dm_daily_grammer_stats',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = ["""DROP TABLE IF EXISTS analytics.daily_grammer_stats""",
                """
                CREATE TABLE analytics.daily_grammer_stats AS (
                SELECT 
                    DATE_TRUNC('hour', a_a.comment_date) AS recorded_time,
                    c_c.content_tag,
                    COUNT(*) AS total_count,
                    SUM(CASE WHEN c_c.errors_count > 0 THEN 1 ELSE 0 END) AS incorrect_count,
                    SUM(CASE WHEN c_c.errors_count = 0 THEN 1 ELSE 0 END) AS correct_count,
                    ROUND(SUM(CASE WHEN c_c.errors_count > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate 
                FROM
                    "dev"."analytics"."spell_check_comment" AS c_c
                LEFT JOIN  
                    "dev"."adhoc"."all_data" AS a_a
                ON c_c.original_comment = a_a.comment
                WHERE comment_date >= CURRENT_DATE - INTERVAL '1 month'
                GROUP BY DATE_TRUNC('hour', a_a.comment_date), c_c.content_tag
                ORDER BY DATE_TRUNC('hour', a_a.comment_date) DESC, c_c.content_tag
                );
               """]
    )
    
    
    
    ### Transfer DM table from redshift to s3
    
    dm_to_s3 = RedshiftToS3Operator(
        task_id="transfer_redshift_to_s3",
        redshift_conn_id = 'redshift_dev_db',
        s3_bucket = Variable.get('S3-BUCKET'),
        s3_key=s3_folder+"daily_grammer_stats/"+s3_key,
        schema="analytics",
        table="daily_grammer_stats",
        select_query="SELECT * FROM analytics.daily_grammer_stats;",
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
        sql = ["DROP TABLE IF EXISTS daily_grammer_stats", """
                CREATE TABLE IF NOT EXISTS daily_grammer_stats(
                    recorded_time timestamp,
                    content_tag varchar(10),
                    total_count int,
                    incorrect_count int, 
                    correct_count int,
                    error_rate real
                );
               """
        ]
    )
    
   
   # Import s3 from rds
    s3_to_rds = PostgresOperator(
        task_id = "s3_to_rds",
        postgres_conn_id = 'postgres_default',
        autocommit = True,
        sql = f""" 
        SELECT aws_s3.table_import_from_s3(
            'daily_grammer_stats',
            '',
            '(format csv, HEADER TRUE)',
            '{Variable.get('S3-BUCKET')}',
            '{s3_folder}daily_grammer_stats/{s3_key}/daily_grammer_stats_000.csv',
            '{Variable.get('AWS_DEFAULT_REGION')}'
        );"""
    )
        
    create_dm >> dm_to_s3 >> check_created_table >> s3_to_rds
        
        
    
    
    