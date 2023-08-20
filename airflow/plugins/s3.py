from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def upload_to_s3(data):
    src_date = data[0]
    s3_hook = S3Hook()
    s3_bucket = 'de-3-2'
    s3_folder = 'raw_data/youtube'
    s3_key = f'{s3_folder}/{src_date}/{src_date}.csv'
    
    s3_hook.load_string(
        string_data= data[1],
        key=s3_key,
        bucket_name=s3_bucket,
        replace=True
    )
    print(f"youtube data uploaded to {s3_bucket}/{s3_key}")
