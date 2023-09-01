from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator as RedshiftSQLOperator
from airflow.models import Variable
from plugins import webtoon_crawling

DAG_ID = "Hourly_Webtoon_Crawling"
dag = DAG(
    DAG_ID,
    schedule_interval="0 0 * * *",
    start_date=datetime(2023, 8, 20),
    catchup=False,
)

# 댓글많은 순의 뉴스를 크롤링해 S3_raw_data에 적재하는거까지의 PythonOperator
extract_and_load_s3 = PythonOperator(
    dag=dag,
    task_id="extract_and_load_s3",
    python_callable=webtoon_crawling.extract_and_load_s3,
    params={
        "BUCKET": Variable.get("S3-BUCKET"),
        "AWS_DEFAULT_REGION": Variable.get("AWS_DEFAULT_REGION"),
    },
)


check_raw_data_schema = RedshiftSQLOperator(
    task_id='create_raw_data_schema',
    sql='''
    CREATE SCHEMA IF NOT EXISTS raw_data;
    ''',
    postgres_conn_id='redshift_dev_db',  # Make sure to set up the Redshift connection in Airflow
    dag=dag,
)



check_redshift_webtoon_content_table = RedshiftSQLOperator(
    task_id='check_redshift_webtoon_content_table',
    sql='''
    CREATE TABLE IF NOT EXISTS raw_data.tb_webtoon_content (
    title VARCHAR(512),
    content_name VARCHAR(512),
    conetne_link VARCHAR(512),
    content_date TIMESTAMP,
    scr_date TIMESTAMP,
    webtoon_categories VARCHAR(1024)
    );
    ''',
    postgres_conn_id='redshift_dev_db',  # Make sure to set up the Redshift connection in Airflow
    dag=dag,
)

check_redshift_webtoon_comment_table = RedshiftSQLOperator(
    task_id='check_redshift_webtoon_comment_table',
    sql='''
    CREATE TABLE IF NOT EXISTS raw_data.tb_webtoon_comment (
        title VARCHAR(512),
        content_name VARCHAR(512),
        nickname VARCHAR(512),
        id VARCHAR(512),
        comment_date TIMESTAMP,
        comment VARCHAR(65535),
        scr_date TIMESTAMP
    );
    ''',
    postgres_conn_id='redshift_dev_db',  # Make sure to set up the Redshift connection in Airflow
    dag=dag,
)

copy_to_redshift = S3ToRedshiftOperator(
        task_id='s3_to_redshift_webtoon_content',
        schema='raw_data',
        table='tb_webtoon_content',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='extract_and_load_s3', key='webtoon_content_path') }}",
        copy_options=[
            "CSV IGNOREHEADER 1", 
            "DATEFORMAT AS 'auto'", 
            "TIMEFORMAT AS 'auto'",
            "MAXERROR 5"
        ],
        aws_conn_id='conn_aws_de_3_2',
        redshift_conn_id='redshift_dev_db',
    )

copy_comment_to_redshift = S3ToRedshiftOperator(
        task_id='s3_to_redshift_webtoon_comment',
        schema='raw_data',
        table='tb_webtoon_comment',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='extract_and_load_s3', key='webtoon_comment_path') }}",
        copy_options=[
            "CSV IGNOREHEADER 1", 
            "DATEFORMAT AS 'auto'", 
            "TIMEFORMAT AS 'auto'",
            "MAXERROR 5"
        ],
        aws_conn_id='conn_aws_de_3_2',
        redshift_conn_id='redshift_dev_db',
    )

extract_and_load_s3 >> check_raw_data_schema

check_raw_data_schema >> check_redshift_webtoon_content_table
check_raw_data_schema >> check_redshift_webtoon_comment_table

check_redshift_webtoon_content_table >> copy_to_redshift
check_redshift_webtoon_comment_table >> copy_comment_to_redshift