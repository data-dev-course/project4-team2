import boto3
import pandas as pd
from datetime import datetime
from airflow.providers.amazon.aws.hooks.lambda_function import LambdaHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from concurrent.futures import ThreadPoolExecutor
import json
import botocore
import asyncio
    

CHECKED_START_TIME = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
CHECKED_START_TIME_S3 = datetime.utcnow().strftime('%Y-%m-%d_%H')
CHECKED_START_DAY = datetime.utcnow().strftime('%Y-%m-%d')

BUCKET = ""

def read_csv_from_s3(bucket_name, file_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    try: 
        df = pd.read_csv(response['Body'])
        return df
    except Exception as e:
        print(str(e))
    return None

# Lambda Pool 최대 크기 수정
class CustomLambdaHook(LambdaHook):
    
    def get_conn(self):
        session, endpoint_url = self._get_session()
        config = botocore.config.Config(max_pool_connections=50)
        return session.client('lambda', region_name=self.region_name, endpoint_url=endpoint_url, config=config)
    
def spell_check_from_lambda_v1(id_comment, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_spell_check',
            invocation_type='RequestResponse',
            payload=json.dumps({"id_comment": id_comment})
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (id_comment, str(e))  # 실패한 경우 URL과 함께 예외 반환

def spell_check_from_lambda_v2(id_comment_list, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_spell_check_v2',
            invocation_type='RequestResponse',
            payload=json.dumps({"id_comment_list": id_comment_list})
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (str(e))  # 실패한 경우 URL과 함께 예외 반환

async def spell_check_from_lambda_async(id_comment_list, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_spell_check_v2',
            invocation_type='RequestResponse',
            payload=json.dumps({"id_comment_list": id_comment_list})
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (str(e))  # 실패한 경우 URL과 함께 예외 반환

# 1. 통으로 리스트를 람다에 넣어버림
# 2. 비동기 100 X 1000 ?
# 스레드풀은 굳이 ?

def spell_check_all(id_comment_list):
    
    lambda_hook = CustomLambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )

    try:
        success_result, failure_result = spell_check_from_lambda_v2(id_comment_list, lambda_hook)
        if failure_result:
            print(failure_result)
    except Exception as e:
        print(str(e))


    df_comment_columns = ["id",  "result","original_comment", "checked_comment", "errors_count"]
    df_word_columns = ["id","original_word", "checked_word", "check_reult"]
    
    df_comment = pd.DataFrame(success_result[0], columns=df_comment_columns)
    df_word = pd.DataFrame(success_result[1] , columns=df_word_columns)
    
    
    df_comment['checked_date'] = CHECKED_START_TIME
    df_word['checked_date'] = CHECKED_START_TIME
    
    
    print(df_comment.head())
    print(df_word.head())
    
    return df_comment, df_word 

async def spell_check_async(id_comment_list):
    lambda_hook = CustomLambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )

    try:
        success_result, failure_result = await spell_check_from_lambda_async(id_comment_list, lambda_hook)
        if failure_result:
            print(failure_result)
    except Exception as e:
        print(str(e))


    df_comment_columns = ["id",  "result","original_comment", "checked_comment", "errors_count"]
    df_word_columns = ["id","original_word", "checked_word", "check_reult"]
    
    df_comment = pd.DataFrame(success_result[0], columns=df_comment_columns)
    df_word = pd.DataFrame(success_result[1] , columns=df_word_columns)
    
    
    df_comment['checked_date'] = CHECKED_START_TIME
    df_word['checked_date'] = CHECKED_START_TIME
    
    
    # print(df_comment.head())
    # print(df_word.head())
    
    return df_comment, df_word

async def spell_check_chunk(id_comment_chunk):
    df_comment, df_word = await spell_check_async(id_comment_chunk)
    return df_comment, df_word

async def main(id_comment_list):
    
    
    chunk_size = 100
    chunks = [id_comment_list[i:i + chunk_size] for i in range(0, len(id_comment_list), chunk_size)]
    
    tasks = []
    for chunk in chunks:
        tasks.append(spell_check_chunk(chunk))
    
    results = await asyncio.gather(*tasks)
    
    
    df_comment_columns = ["id",  "result","original_comment", "checked_comment", "errors_count"]
    df_word_columns = ["id","original_word", "checked_word", "check_reult"]
    
    df_comment = pd.DataFrame(columns=df_comment_columns)
    df_word = pd.DataFrame( columns=df_word_columns)
    
    # results에는 spell_check_all의 결과가 들어있음
    for comment_result, word_result in results:
        df_comment = pd.concat([df_comment, comment_result], ignore_index=True)
        df_word = pd.concat([df_word, word_result], ignore_index=True)

    return df_comment, df_word
        
def spell_check_thread_pool(id_comment_list):

    lambda_hook = CustomLambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )

    results_sentence = []
    results_word = []
    failed_results = []

    with ThreadPoolExecutor(max_workers=50) as executor:  # max_workers는 동시에 호출할 Lambda의 최대 개수
        for success_result, failure_result in executor.map(spell_check_from_lambda_v2, id_comment_list, [lambda_hook]*len(id_comment_list)):
            try:
                if success_result:
                    if success_result[0]: 
                        for result_sentence in success_result[0]:
                            results_sentence.append(result_sentence)  # sentence 추가
                        for result_word in success_result[1]:
                            results_word.append(result_word) # words 추가
                if failure_result:  # 실패한 경우에는 failure_result에 추가
                    failed_results.append(failure_result)
            except Exception as e:
                print(f"Error while processing results: {e}")
                continue

    print("Failed Results:")
    print(failed_results)
    
    return results_sentence, results_word

def load_to_s3(data, dir, aws_conn_id='conn_aws_de_3_2'):
    s3_hook = S3Hook(aws_conn_id=aws_conn_id)

    base_key = f'spell_check/{dir}/{CHECKED_START_DAY}/{CHECKED_START_TIME_S3}'
    key = base_key + ".csv"
    counter = 1
    
    # Check if the object exists
    while s3_hook.check_for_key(key, bucket_name=BUCKET):
        counter += 1
        key = base_key + f'-{counter}' + ".csv"

    csv_buffer = data.to_csv(index=False, encoding='utf-8-sig')
    
    try:
        s3_hook.load_string(
            string_data=csv_buffer,
            key=key,
            bucket_name=BUCKET,
            replace=True
        )
        print(f"업로드 성공: {key}")
        return key
    except Exception as e:
        print(f"업로드 실패: {e}")

def spell_check_and_load_s3(**kwargs):
    global AWS_DEFAULT_REGION, BUCKET
    
    EXTRACT_S3_PATH = "all_data/"+kwargs['ds']+"/"+kwargs['ds']+"_"+kwargs['ts_nodash'][9:11]+"/all_data_000.csv"
    AWS_DEFAULT_REGION = kwargs.get('params', {}).get('AWS_DEFAULT_REGION')
    BUCKET = kwargs.get('params', {}).get('BUCKET')
    
    
    
    # s3에서 all_data (.csv)를 dataframe으로 가져오기 
    df = read_csv_from_s3(BUCKET, EXTRACT_S3_PATH)
   
    print(f"Fetching data from S3 bucket: {BUCKET}, key: {EXTRACT_S3_PATH}")
    print("original_df" , len(df))
    
    # dataframe을 list로 
    id_comment_list = df.values.tolist()
    
    df_comment_columns = ["id", "content_tag", "result","original_comment", "checked_comment", "errors_count"]
    df_word_columns = ["id","content_tag", "original_word", "checked_word", "check_reult"]
    
    comment = [] 
    word = []
    
    chunk_size = 1
    if 1 <= len(df) < 1000:
        chunk_size = int(df * 0.1)+1
    else:
        chunk_size = 100
        
    grouped_lists = [id_comment_list[i:i+chunk_size] for i in range(0, len(id_comment_list), chunk_size)]
    
    print("------grouped lists size ", len(grouped_lists))
    

    comment, word = spell_check_thread_pool(grouped_lists)

    
    df_comment = pd.DataFrame(comment, columns=df_comment_columns)
    df_word = pd.DataFrame(word, columns=df_word_columns)
    
    df_comment['checked_date'] = CHECKED_START_TIME
    df_word['checked_date'] = CHECKED_START_TIME
    
    # df_comment, df_word = spell_check_thread_pool(id_comment_list)
    # df_comment, df_word = spell_check_all(id_comment_list)

    # # asyncio 루프 생성 및 실행
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(id_comment_list))
    
    # df_comment, df_word = asyncio.run(main(id_comment_list))
    
    
    print(df_comment.head())
    print(df_word.head())
    print("df_comment size:", len(df_comment))
    print("df_word size:", len(df_word))
    
    spell_check_comment_path = load_to_s3(df_comment, "comment")
    spell_check_word_path = load_to_s3(df_word, "word")
    
    # XCom에 값을 저장
    ti = kwargs['ti']  # TaskInstance 객체 가져오기
    ti.xcom_push(key='spell_check_comment_path', value=spell_check_comment_path)
    ti.xcom_push(key='spell_check_word_path', value=spell_check_word_path)