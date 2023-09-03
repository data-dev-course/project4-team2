from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from airflow.providers.amazon.aws.transfers.redshift_to_s3 import RedshiftToS3Operator
from airflow.models import Variable
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.external_task_sensor import ExternalTaskSensor
from airflow.utils.state import State
from datetime import datetime, timedelta


default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id="DM_Hourly_Comment_Summary_To_RDS",
    default_args = default_args ,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval=None
)as dag:
    
    # sensor = ExternalTaskSensor(
    #     task_id='wait_for_spell_check',
    #     external_dag_id='Spell_Check',
    #     external_task_ids=['copy_comment_checked_to_redshift', 'copy_word_checked_to_redshift'],
    #     failed_states=[State.SKIPPED],
    #     mode='poke'
    # )
    

    s3_folder = "DM/"
    s3_key = "{{ ds }}"+"/"+"{{ ds }}"+"_"+"{{ ts_nodash[9:11] }}"
    
    # DM table - transform 
    create_dm = RedshiftSQLOperator(
        task_id='create_dm_hourly_comment_summary',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = ["""
        DROP TABLE IF EXISTS analytics.hourly_comment_summary;""",
        """
        CREATE TABLE analytics.hourly_comment_summary AS (
            SELECT DATE_TRUNC('hour', scr_date) AS "recorded_time",
                COUNT(*) AS "comment_count",
                "tag" AS "content_tag"
            FROM "dev"."adhoc"."all_data"
            WHERE scr_date >= CURRENT_DATE - INTERVAL '1 month'
            GROUP BY DATE_TRUNC('hour', scr_date), "tag"
            ORDER BY "recorded_time" DESC
        );
        """]
    )
    
    
    
    ### Transfer DM table from redshift to s3
    dm_to_s3 = RedshiftToS3Operator(
        task_id="transfer_redshift_to_s3",
        redshift_conn_id = 'redshift_dev_db',
        s3_bucket = Variable.get('S3-BUCKET'),
        s3_key=s3_folder+"hourly_comment_summary/"+s3_key,
        schema="analytics",
        table="hourly_comment_summary",
        select_query="SELECT * FROM analytics.hourly_comment_summary;",
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
        sql = ["DROP TABLE IF EXISTS hourly_comment_summary;","""
                CREATE TABLE IF NOT EXISTS hourly_comment_summary(
                recorded_time timestamp,
                comment_count int,
                content_tag varchar(10)
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
            'hourly_comment_summary',
            '',
            '(format csv, HEADER TRUE)',
            '{Variable.get('S3-BUCKET')}',
            '{s3_folder}hourly_comment_summary/{s3_key}/hourly_comment_summary_000.csv',
            '{Variable.get('AWS_DEFAULT_REGION')}'
        );"""
    )

    create_dm >> dm_to_s3 >> check_created_table >> s3_to_rds
        
        
    
    
    