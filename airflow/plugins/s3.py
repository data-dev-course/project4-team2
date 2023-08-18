from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable

def upload_to_s3(**kwargs):
    print(kwargs['name'])
    print(kwargs['name'])
    # s3_hook = S3Hook(aws_conn_id=s3_conn_id)
    # s3_bucket = Variable.get("s3_bucket_name")
    # s3_folder = 'raw_data/youtube/'
    # s3_key = f'{s3_folder}/{dataframe[0]/dataframe[0].csv}'
    
    
    # s3_hook.load_string(
    #     string_data=dataframe,
    #     key=s3_key,
    #     bucket_name=s3_bucket,
    #     replace=True
    # )
