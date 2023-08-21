import io
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import json
import logging

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup



from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator as RedshiftSQLOperator
from airflow.models import Variable


from plugins import news_crawling

DAG_ID = "Hourly_News_Crawling"
dag = DAG(
    DAG_ID,
    schedule_interval="5 * * * *",
    start_date=datetime(2023, 8, 17),
    catchup=False,
)

# 댓글많은 순의 뉴스를 크롤링해 S3_raw_data에 적재하는거까지의 PythonOperator
extract_and_load_s3 = PythonOperator(
    dag=dag,
    task_id="extract_and_load_s3",
    python_callable=news_crawling.extract_and_load_s3,
    params={
        "url": Variable.get("NEWS_BASE_URL"),
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



check_redshift_news_title_table = RedshiftSQLOperator(
    task_id='check_redshift_news_title_table',
    sql='''
    CREATE TABLE IF NOT EXISTS raw_data.tb_news_title (
        rank INT,
        title VARCHAR(512),
        comment_count INT,
        title_link VARCHAR(1024),
        comment_link VARCHAR(1024),
        press VARCHAR(256),
        scr_date TIMESTAMP
    );
    ''',
    postgres_conn_id='redshift_dev_db',  # Make sure to set up the Redshift connection in Airflow
    dag=dag,
)

check_redshift_news_comment_table = RedshiftSQLOperator(
    task_id='check_redshift_news_comment_table',
    sql='''
    CREATE TABLE IF NOT EXISTS raw_data.tb_news_comment (
        author VARCHAR(512),
        comment_date TIMESTAMP,
        comment VARCHAR(65535),
        title_link VARCHAR(1024),
        created_news_date TIMESTAMP,
        category VARCHAR(128),
        scr_date TIMESTAMP
        
    );
    ''',
    postgres_conn_id='redshift_dev_db',  # Make sure to set up the Redshift connection in Airflow
    dag=dag,
)

copy_to_redshift = S3ToRedshiftOperator(
        task_id='s3_to_redshift_news_title',
        schema='raw_data',
        table='tb_news_title',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='extract_and_load_s3', key='news_title_path') }}",
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
        task_id='s3_to_redshift_news_comment',
        schema='raw_data',
        table='tb_news_comment',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='extract_and_load_s3', key='news_comment_path') }}",
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

check_raw_data_schema >> check_redshift_news_title_table
check_raw_data_schema >> check_redshift_news_comment_table

check_redshift_news_title_table >> copy_to_redshift
check_redshift_news_comment_table >> copy_comment_to_redshift