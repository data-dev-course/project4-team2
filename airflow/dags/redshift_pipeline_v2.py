from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import logging
DAG_ID = 'redshift_pipeline_v2'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 17),
    catchup=False,
    schedule_interval="20 * * * *",
) as dag:
    
    # JOIN
    table_news_join = RedshiftSQLOperator(
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
    table_webtoon_join = RedshiftSQLOperator(
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
    
    # all_data 원본 테이블이 없다면 생성 
    check_created_all_data = RedshiftSQLOperator(
        task_id='check_created_all_data',
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
    
    
   
    def get_Redshift_connection():
        # autocommit is False by default
        hook = PostgresHook(postgres_conn_id='redshift_dev_db')
        return hook.get_conn().cursor()

    # 중복 제거된 all_data 테이블을 위한 작업 
    # 1. 원본 테이블을 임시 테이블에 CTAS 
    # 2. 임시 테이블에 union한 값을 insert
    # 3. 원본 테이블 모든 데이터 delete  
    # 4. 임시 테이블에서 ROW_NUMBER() 를 통해 중복 제거 후 원본 테이블에 insert
    
    @task
    def deduplicate_and_load():
        cur = get_Redshift_connection()
        # 1. 원본 테이블을 임시 테이블에 CTAS 
        create_all_data_temp_table_sql = """CREATE TEMP TABLE all_data_temp AS SELECT * FROM adhoc.all_data;""" 
    
        # 2. 임시 테이블에 union한 값을 insert
        # UNION -> INSERT :  tb_youtube, tb_news, tb_webtoon -> all_data
        union_and_insert_to_temp_table_sql =  """
            INSERT INTO all_data_temp (
            SELECT generate_uuid() AS id, 'youtube' AS "tag", title, author, category, comment, comment_date, scr_date FROM raw_data.tb_youtube
            UNION SELECT generate_uuid() AS id, 'news' AS "tag", title, author, category, comment, comment_date, scr_date FROM adhoc.tb_news
            UNION SELECT generate_uuid() AS id, 'webtoon' AS "tag", title, id, webtoon_categories, comment, comment_date, scr_date FROM adhoc.tb_webtoon);
            """ 
        logging.info(create_all_data_temp_table_sql)
        logging.info(union_and_insert_to_temp_table_sql)

        try:
            cur.execute(create_all_data_temp_table_sql)
            cur.execute(union_and_insert_to_temp_table_sql)
            cur.execute("COMMIT;")
        except Exception as e:
            cur.execute("ROLLBACK;")
            raise

        
        # 3. 원본 테이블 모든 데이터 delete 
        # 4. 임시 테이블에서 ROW_NUMBER() 를 통해 중복 제거 후 원본 테이블에 insert
        alter_all_data_sql = """DELETE FROM adhoc.all_data; 
                    INSERT INTO adhoc.all_data 
                    SELECT id, "tag", title, author, category, comment, comment_date, scr_date FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY comment ORDER BY scr_date ASC) seq
                    FROM all_data_temp)
                    WHERE seq = 1;
                    """
        logging.info(alter_all_data_sql)
        
        try:
            cur.execute(alter_all_data_sql)
            cur.execute("COMMIT;")
        except Exception as e:
            cur.execute("ROLLBACK;")
            raise
    
    trigger_spell_check = TriggerDagRunOperator(
        task_id='trigger_spell_check',
        trigger_dag_id = 'Spell_Check',
        reset_dag_run=True,
    )
        
    
    table_news_join>> check_created_all_data
    table_webtoon_join >> check_created_all_data
    
    check_created_all_data >> deduplicate_and_load() >> trigger_spell_check