from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.lambda_function import LambdaHook
import botocore

SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')

def aws_lambda_webtoon_contents_crawling():
    lambda_hook = LambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )
    
    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_webtoon_contents_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps()
        )
        response_payload = json.loads(response['Payload'].read())
        columns = ['title','content_name','content_link','content_date','scr_date','webtoon_categories' ]
        
        df = pd.DataFrame(response_payload, columns = columns)
        return df
    except Exception as e:
        print(str(e))  # 실패한 경우 URL과 함께 예외 반환
    

def extract_comment_from_lambda(url,title,content_name, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_webtoon_comment_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps({"url": url,
                                "title" : title,
                                "content_name" : content_name
                                })
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (url, str(e))  # 실패한 경우 URL과 함께 예외 반환
    
def extract_comment_from_lambda_wrapper(args):
    url, title, content_name, lambda_hook = args
    return extract_comment_from_lambda(url, title, content_name, lambda_hook)    
    
def extract_webtoon_comment(df):
    lambda_hook = LambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )
    

    urls = df['content_link']
    titles = df['title']
    content_names = df['content_name']
    
    results = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        # extract_comment_from_lambda 함수의 인자가 (url, title, content_name, lambda_hook)이므로 이를 tuple로 묶어줍니다.
        # executor.map에 넘겨주기 위해 zip을 사용합니다.
        args_list = zip(urls, titles, content_names, [lambda_hook]*len(urls))
        
        for success_result, failure_result in executor.map(extract_comment_from_lambda_wrapper, args_list):
            try:
                if success_result:
                    results.append(success_result[0])  # 첫 번째 요소만 추가
                if failure_result:  # 실패한 경우에는 failed_urls에 추가
                    failed_urls.append(failure_result)
            except Exception as e:
                print(f"Error while processing results: {e}")
                continue

    print("Failed URLs:")
    for url, error in failed_urls:
        print(f"URL: {url}, Error: {error}")

    columns = ["title", "content_name", "nickname", "id", "comment_date", "comment","scr_date"]
    df_results = pd.DataFrame(columns=columns)
    for result in results:
        df_temp = pd.DataFrame(result, columns=columns)
        df_results = pd.concat([df_results, df_temp], ignore_index=True)
    
    return df_results

def load_to_s3(data, dir, aws_conn_id='conn_aws_de_3_2'):
    s3_hook = S3Hook(aws_conn_id=aws_conn_id)

    base_key = f'raw_data/webtoon/{dir}/{SCRIPY_START_DAY}/{SCRIPY_START_TIME}'
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


    

def extract_and_load_s3(**kwargs):
    global AWS_DEFAULT_REGION, BUCKET, URL 

    # Airflow에서 전달된 파라미터를 추출
    AWS_DEFAULT_REGION = kwargs.get('params', {}).get('AWS_DEFAULT_REGION')
    BUCKET = kwargs.get('params', {}).get('BUCKET')

    webtoon_title = aws_lambda_webtoon_contents_crawling()

    webtoon_comment = extract_webtoon_comment(webtoon_title)
    
    print(f'len of news_title : {len(webtoon_title)},  news_comment : {len(webtoon_comment)}')
    news_title_path = load_to_s3(webtoon_title, 'webtoon_title')
    news_comment_path = load_to_s3(webtoon_comment, 'webtoon_comment')
    
    # XCom에 값을 저장
    ti = kwargs['ti']  # TaskInstance 객체 가져오기
    ti.xcom_push(key='news_title_path', value=news_title_path)
    ti.xcom_push(key='news_comment_path', value=news_comment_path)