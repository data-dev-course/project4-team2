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
def aws_lambda_webtoon_titles_crawling():
    lambda_hook = LambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )
    
    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_webtoon_title_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps({})

        )
        response_payload = json.loads(response['Payload'].read())
        columns = ['day','title','webtoon_link','scr_date' ]
        print(f'title 읽어오기 성공, len : {len(response_payload)}')
        # print(response_payload)
        df = pd.DataFrame(response_payload, columns = columns)
        # print(df)
        return df
    except Exception as e:
        print(f'webtoon title lambda 실행 실패. {str(e)}')  # 실패한 경우 URL과 함께 예외 반환
        
        

def extract_content_from_lambda(title,webtoon_link, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_webtoon_contents_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps({
                                "title" : title,
                                "webtoon_link" : webtoon_link
                                })
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (webtoon_link, str(e))  # 실패한 경우 URL과 함께 예외 반환

def extract_content_from_lambda_wrapper(args):
    title, webtoon_link, lambda_hook = args
    return extract_content_from_lambda(title, webtoon_link, lambda_hook)    

def extract_content(webtoon_title):
    lambda_hook = LambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )
    # print(f'extract_webtoon_content 시작, len(webtoon_title) : {len(webtoon_title)}')
    # print(webtoon_title)

    titles = webtoon_title['title']
    webtoon_links = webtoon_title['webtoon_link']
    print(webtoon_links[0])
    results = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        # extract_comment_from_lambda 함수의 인자가 (url, title, content_name, lambda_hook)이므로 이를 tuple로 묶어줍니다.
        # executor.map에 넘겨주기 위해 zip을 사용합니다.
        args_list = zip(titles,   webtoon_links, [lambda_hook]*len(titles))
        
        for success_result, failure_result in executor.map(extract_content_from_lambda_wrapper, args_list):
            try:
                if success_result:
                    results.append(success_result[0])  # 첫 번째 요소만 추가
                if failure_result:  # 실패한 경우에는 failed_urls에 추가
                    failed_urls.append(failure_result)
            except Exception as e:
                print(f"Error while processing results: {e}")
                continue
    # log용
    # print(f'comment thread 마친 후 results 최종')
    # print(results)
    
    
    for item in results:
        item['webtoon_categories'] = json.loads(item['webtoon_categories'])
        
    print("Failed URLs:")
    for url, error in failed_urls:
        print(f"URL: {url}, Error: {error}")

    columns = ["title", "content_name", "content_link", "content_date", "scr_date", "webtoon_categories"]
    df_results = pd.DataFrame(columns=columns)
    for result in results:
        df_temp = pd.DataFrame(result, columns=columns)
        df_results = pd.concat([df_results, df_temp], ignore_index=True)
    
    
    
    df_results['scr_date'] = pd.to_datetime(SCRIPY_START_TIME, format='%Y-%m-%d_%H')
    grouped = df_results.groupby(['title', 'content_name', 'content_link', 'content_date', 'scr_date']).agg({'webtoon_categories': lambda x: ','.join(list(x))}).reset_index()

    # print('content 최종 return : ')
    # print(grouped)
    return grouped
    






def extract_comment_from_lambda(url,title,content_name, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_webtoon_comment_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps({"content_link": url,
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
    # print(url, title, content_name, lambda_hook)
    return extract_comment_from_lambda(url, title, content_name, lambda_hook)        
def extract_webtoon_comment(df):
    lambda_hook = LambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )
    print(f'extract_webtoon_comment 시작, len(df) : {len(df)}')

    urls = df['content_link']
    titles = df['title']
    content_names = df['content_name']
    # print(urls)
    results = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        # extract_comment_from_lambda 함수의 인자가 (url, title, content_name, lambda_hook)이므로 이를 tuple로 묶어줍니다.
        # executor.map에 넘겨주기 위해 zip을 사용합니다.
        args_list = zip(urls, titles, content_names, [lambda_hook]*len(urls))
        
        for success_result, failure_result in executor.map(extract_comment_from_lambda_wrapper, args_list):
            try:
                if success_result:
                    # print(success_result)
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
    
    
    df_results['comment_date'] = pd.to_datetime(df_results['comment_date'], errors='coerce')
    df_results['scr_date'] = pd.to_datetime(SCRIPY_START_TIME, format='%Y-%m-%d_%H')
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
    global AWS_DEFAULT_REGION, BUCKET 

    # Airflow에서 전달된 파라미터를 추출
    AWS_DEFAULT_REGION = kwargs.get('params', {}).get('AWS_DEFAULT_REGION')
    BUCKET = kwargs.get('params', {}).get('BUCKET')

    webtoon_title = aws_lambda_webtoon_titles_crawling()
    print('webtoon_title type : ',type(webtoon_title))
    print(f' title 스크래핑 종료, len(webtoon_title) = {len(webtoon_title)}')
    # 여기까진 성공
    
    webtoon_contents = extract_content(webtoon_title)
    webtoon_comment = extract_webtoon_comment(webtoon_contents)
    print(webtoon_comment)
    print(f'len of news_title : {len(webtoon_title)},  news_comment : {len(webtoon_comment)}')
    news_title_path = load_to_s3(webtoon_contents, 'webtoon_contents')
    news_comment_path = load_to_s3(webtoon_comment, 'webtoon_comment')
    
    # XCom에 값을 저장
    ti = kwargs['ti']  # TaskInstance 객체 가져오기
    ti.xcom_push(key='news_title_path', value=news_title_path)
    ti.xcom_push(key='news_comment_path', value=news_comment_path)