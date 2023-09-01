from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.redshift_to_s3 import RedshiftToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import TaskInstance
from airflow.operators.dummy import DummyOperator

from airflow.models import Variable
from plugins import spell_checker
from datetime import datetime, timedelta

DAG_ID = 'Spell_Check'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 22),
    # catchup=True,
    # schedule_interval="0 */1 * * *"
    catchup=False,
    schedule_interval=None
) as dag:
    
    s3_key = "all_data/"+"{{ ds }}"+"/"+"{{ ds }}"+"_"+"{{ ts_nodash[9:11] }}"  # '%Y-%m-%d_%H' 형식

    # ad_hoc.all_data -> S3 ( UNLOAD ) 
    transfer_redshift_to_s3 = RedshiftToS3Operator(
    task_id="transfer_redshift_to_s3",
    redshift_conn_id = 'redshift_dev_db',
    s3_bucket = Variable.get('S3-BUCKET'),
    s3_key=s3_key,
    schema="adhoc",
    table="all_data",
    select_query="SELECT id, comment,\"tag\" FROM adhoc.all_data WHERE LEFT(scr_date, 13) = ''{{ ds }} {{ ts_nodash[9:11] }}'';",
    unload_options = ['FORMAT CSV','PARALLEL OFF', 'EXTENSION \'csv\'', 'ALLOWOVERWRITE'],
    table_as_file_name = True,
    
    )
    
    spell_check_and_load_s3 = PythonOperator(
        task_id='spell_check_and_load_s3',
        python_callable=spell_checker.spell_check_and_load_s3,
        params={
            "BUCKET": Variable.get("S3-BUCKET"),
            "AWS_DEFAULT_REGION": Variable.get("AWS_DEFAULT_REGION")
            # "EXTRACT_S3_PATH": s3_key+"/all_data_000.csv"
        }
        # templates_dict={
        #     "EXTRACT_S3_PATH":s3_key
        # }
    )
    
    
    
    check_spell_check_comment_table = RedshiftSQLOperator(
        task_id='check_spell_check_comment_table',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        CREATE TABLE IF NOT EXISTS analytics.spell_check_comment (
            id  VARCHAR(256),
            content_tag VARCHAR(10),
            result BOOLEAN,
            original_comment VARCHAR(65535),
            checked_comment VARCHAR(65535),
            errors_count INTEGER,
            checked_date TIMESTAMP
        );
        """ 
    )
    
    check_spell_check_word_table = RedshiftSQLOperator(
        task_id='check_spell_check_word_table',
        redshift_conn_id = 'redshift_dev_db',
        autocommit = True,
        sql = 
        """
        CREATE TABLE IF NOT EXISTS analytics.spell_check_word (
            id  VARCHAR(256),
            content_tag VARCHAR(10),
            original_word VARCHAR(65535),
            checked_word VARCHAR(65535),
            check_reult INTEGER,
            checked_date TIMESTAMP
        );
        """ 
    )
    
    copy_comment_checked_to_redshift = S3ToRedshiftOperator(
        task_id='copy_comment_checked_to_redshift',
        schema='analytics',
        table='spell_check_comment',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='spell_check_and_load_s3', key='spell_check_comment_path') }}",
        copy_options=[
            "CSV IGNOREHEADER 1", 
            "DATEFORMAT AS 'auto'", 
            "TIMEFORMAT AS 'auto'",
            "MAXERROR 5"
        ],
        redshift_conn_id='redshift_dev_db',
        method='APPEND'
    )
    
    
    copy_word_checked_to_redshift = S3ToRedshiftOperator(
        task_id='copy_word_checked_to_redshift',
        schema='analytics',
        table='spell_check_word',
        s3_bucket='de-3-2',
        s3_key="{{ ti.xcom_pull(task_ids='spell_check_and_load_s3', key='spell_check_word_path') }}",
        copy_options=[
            "CSV IGNOREHEADER 1", 
            "DATEFORMAT AS 'auto'", 
            "TIMEFORMAT AS 'auto'",
            "MAXERROR 5"
        ],
        redshift_conn_id='redshift_dev_db',
        method='APPEND'
    )
    
    # def check(**context):
    #     ti = context['task_instance']
    #     result_copy_comment = ti.xcom_pull(task_id='copy_comment_checked_to_redshift')
    #     result_word_comment = ti.xcom_pull(task_id='copy_word_checked_to_redshift')
        
    #     print("result_copy_comment state:",result_copy_comment)
    #     print("result_word_comment state:",result_word_comment)
        
    #     return "trigger_DM_group"
        
    # #
    # check_success = BranchPythonOperator(
    #     task_id='check_success',
    #     python_callable=check
        
    # )
    
    dummy_task = DummyOperator(
        task_id='dummy'
    )
    
    with TaskGroup(group_id='trigger_DM_group') as TriggerGroup:
        
        trigger_dm_HCS_to_rds = TriggerDagRunOperator(
            task_id='trigger_dm_HCS_to_rds',
            trigger_dag_id = 'DM_Hourly_Comment_Summary_To_RDS',
            reset_dag_run=False,
        )
        
        trigger_dm_DGS_to_rds = TriggerDagRunOperator(
            task_id='trigger_dm_DGS_to_rds',
            trigger_dag_id = 'DM_Daily_Grammer_Stats_To_RDS',
            reset_dag_run=False,
        )
        
        trigger_dm_HWC_to_rds = TriggerDagRunOperator(
            task_id='trigger_dm_HWC_to_rds',
            trigger_dag_id = 'DM_Hourly_Word_Correction_To_RDS_V2',
            reset_dag_run=False,
        )       
    
    transfer_redshift_to_s3 >> spell_check_and_load_s3 >> [check_spell_check_comment_table , check_spell_check_word_table]
    check_spell_check_comment_table >> copy_comment_checked_to_redshift  >> dummy_task
    check_spell_check_word_table >> copy_word_checked_to_redshift >> dummy_task
    dummy_task >>  TriggerGroup
    
    