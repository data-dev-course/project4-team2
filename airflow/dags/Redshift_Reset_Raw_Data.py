from datetime import datetime

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator as RedshiftSQLOperator
from airflow.models import Variable

DAG_ID = "init_redshift_raw_data"
dag = DAG(
    DAG_ID,
    schedule_interval=None,
    start_date=datetime(2023, 8, 17),
    catchup=False,
)

init_redshift_news_title_table = RedshiftSQLOperator(
    task_id='init_redshift_news_title_table',
    sql='''
    DROP TABLE IF EXISTS raw_data.tb_news_title;
    ''',
    postgres_conn_id='redshift_dev_db',
    dag=dag,
)

init_redshift_news_comment_table = RedshiftSQLOperator(
    task_id='init_redshift_news_comment_table',
    sql='''
    DROP TABLE IF EXISTS raw_data.tb_news_comment;
    ''',
    postgres_conn_id='redshift_dev_db',
    dag=dag,
)

init_redshift_webtoon_title_table = RedshiftSQLOperator(
    task_id='init_redshift_webtoon_title_table',
    sql='''
    DROP TABLE IF EXISTS raw_data.tb_webtoon_title;
    ''',
    postgres_conn_id='redshift_dev_db',
    dag=dag,
)

init_redshift_webtoon_comment_table = RedshiftSQLOperator(
    task_id='init_redshift_webtoon_comment_table',
    sql='''
    DROP TABLE IF EXISTS raw_data.tb_webtoon_comment;
    ''',
    postgres_conn_id='redshift_dev_db',
    dag=dag,
)


init_redshift_news_title_table >> init_redshift_news_comment_table

init_redshift_webtoon_title_table >> init_redshift_webtoon_comment_table