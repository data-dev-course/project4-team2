from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from datetime import datetime, timedelta

DAG_ID = 'redshift_pipeline'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval=None
) as dag:
    
    # JOIN
    table_news_join_task = RedshiftSQLOperator(
        task_id='table_news_join',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = ['DROP TABLE IF EXISTS adhoc.tb_news;',"""
        CREATE TABLE adhoc.tb_news AS
        (SELECT DISTINCT nc.scr_date, title, author, category, comment, comment_date
        FROM raw_data.tb_news_comment AS nc
        LEFT JOIN raw_data.tb_news_title AS nt
        ON nc.comment_link=nt.comment_link);
        """ 
        ]
    )
    table_webtoon_join_task = RedshiftSQLOperator(
        task_id='table_webtoon_join',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = ['DROP TABLE IF EXISTS adhoc.tb_webtoon;',"""
        CREATE TABLE adhoc.tb_webtoon AS
        (SELECT DISTINCT wcm.scr_date, wcm.title, webtoon_categories, id, comment, comment_date
        FROM raw_data.tb_webtoon_comment AS wcm
        LEFT JOIN raw_data.tb_webtoon_content AS wct
        ON wcm.title = wct.title);
        """ 
        ]
    )
    
    check_created_table_task = RedshiftSQLOperator(
        task_id='check_created_table',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        CREATE TABLE IF NOT EXISTS adhoc.all_data (
            id VARCHAR(256),
            "tag" VARCHAR(10),
            title VARCHAR(1028),
            author VARCHAR(512),
            category VARCHAR(1024),
            comment VARCHAR(65535),
            comment_date TIMESTAMP,
            scr_date TIMESTAMP
        );
        """ 
    )
    
    # UNION - tb_youtube, tb_news, tb_webtoon -> all_data
    table_union_task = RedshiftSQLOperator(
        task_id='table_union',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        INSERT INTO adhoc.all_data (
        SELECT generate_uuid() AS id, 'youtube' AS "tag", title, author, category, comment, comment_date, scr_date FROM raw_data.tb_youtube
        UNION SELECT generate_uuid() AS id, 'news' AS "tag", title, author, category, comment, comment_date, scr_date FROM adhoc.tb_news
        UNION SELECT generate_uuid() AS id, 'webtoon' AS "tag", title, id, webtoon_categories, comment, comment_date, scr_date FROM adhoc.tb_webtoon);
        """ 
    )
    
    # Deduplication
    table_deduplication_task = RedshiftSQLOperator(
        task_id='table_deduplication',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        DELETE FROM adhoc.all_data
        WHERE id NOT IN(
            SELECT MIN(id)
            FROM adhoc.all_data
            GROUP BY comment
        );
        """ 
    )
    
    
    
    table_news_join_task >> table_webtoon_join_task  >> check_created_table_task >> table_union_task >> table_deduplication_task