from bs4 import BeautifulSoup
import pandas as pd
import requests
from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor
import json
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.hooks.lambda_function import LambdaHook
import botocore

# Lambda Pool 최대 크기 수정
class CustomLambdaHook(LambdaHook):
    
    def get_conn(self):
        session, endpoint_url = self._get_session()
        config = botocore.config.Config(max_pool_connections=50)
        return session.client('lambda', region_name=self.region_name, endpoint_url=endpoint_url, config=config)




SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')

BUCKET = ""
URL = ""

def scripy_news_title(url):
    header = {"user-agent": "Mozilla/5.0"}
    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.select('.rankingnews_box')

    name = []
    link = []

    for item in items :
        name.append(item.select('div > a > strong')[0].get_text())
        link.append(item.select('div > a')[0]['href'])
        
    df_press= pd.DataFrame({'press': name, 'url':link})
    
    result_df = pd.DataFrame()
    for index, row in df_press.iterrows():
        # print(row.press,row.url)
        # print(index)
        if index ==0 :
            result_df = scrip_rank_news(row.press,row.url)
        else :
            result_df = pd.concat([result_df,scrip_rank_news(row.press,row.url)])
    
    
    result_df['scr_date'] = pd.to_datetime(SCRIPY_START_TIME, format='%Y-%m-%d_%H')
    print(f'len df_news_list is {len(result_df)}')

    return result_df.reset_index(drop=True).sort_values('comment_count', ascending = False)

def scrip_rank_news(press,url):
    header = {"user-agent": "Mozilla/5.0"}

    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, 'html.parser')
    news_list = soup.find_all("li", class_="as_thumb")
    data = []


    for news in news_list:
        rank = int(news.find("em", class_="list_ranking_num").text)  # 순위를 int로 변환
        title = news.find("strong", class_="list_title").text
        comment_count_text = news.find("span", class_="list_comment").text.strip()
        comment_count_text = comment_count_text.replace(',', '')  # 쉼표 제거
        comment_count = int(comment_count_text.split()[1])  # 댓글 수를 int로 변환
        link = news.find("a", class_="_es_pc_link")["href"]
        
        # 기존 링크에서 article ID 추출
        path_components = link.split("/")
        article_id = path_components[-1].split("?")[0]
        
        # 새로운 형식의 comment 링크 생성
        comment_link = f"https://n.news.naver.com/article/comment/{path_components[4]}/{article_id}"
        
        data.append({"rank": rank, "title": title, "comment_count": comment_count, "title_link": link, "comment_link": comment_link})

    df = pd.DataFrame(data)
    df['press'] = press
    return df

def extract_comment_from_lambda(url, lambda_hook):

    try:
        response = lambda_hook.invoke_lambda(
            function_name='de-3-2_news_crawling',
            invocation_type='RequestResponse',
            payload=json.dumps({"url": url})
        )
        response_payload = json.loads(response['Payload'].read())
        return response_payload, None  # 성공한 경우
    except Exception as e:
        return None, (url, str(e))  # 실패한 경우 URL과 함께 예외 반환
    
def extract_comments(urls):

    lambda_hook = CustomLambdaHook(
        aws_conn_id='conn_aws_de_3_2',  # Airflow connection ID
        region_name=AWS_DEFAULT_REGION
    )

    results = []
    failed_urls = []

    with ThreadPoolExecutor(max_workers=50) as executor:  # max_workers는 동시에 호출할 Lambda의 최대 개수
        for success_result, failure_result in executor.map(extract_comment_from_lambda, urls, [lambda_hook]*len(urls)):
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

    columns = ["author", "comment_date", "comment", "comment_link", "created_news_date", "category"]
    df_results = pd.DataFrame(columns=columns)
    print(df_results.head())
    for result in results:
        df_temp = pd.DataFrame(result, columns=columns)
        df_results = pd.concat([df_results, df_temp], ignore_index=True)

        
    
    
    # 주어진 KST와 UTC의 차이를 나타내는 timedelta 생성
    kst_offset = timedelta(hours=9)  # KST는 UTC+9

    # news_time 열의 값을 KST 시간에서 KST와 UTC의 차이를 빼서 UTC 시간으로 변환
    df_results['created_news_date'] = df_results['created_news_date'].apply(lambda kst_time: datetime.strptime(kst_time, '%Y-%m-%d %H:%M:%S') - kst_offset)
    
    df_results['created_news_date'] = pd.to_datetime(df_results['created_news_date'])

    # datetime 형식 변환
    def convert_to_datetime(date_str):
        try:
            return pd.to_datetime(date_str, format='%Y.%m.%d. %H:%M:%S')
        except:
            return pd.to_datetime(date_str, format='%Y.%m.%d. %H:%M')

    df_results['comment_date'] = df_results['comment_date'].apply(convert_to_datetime)    
    
    df_results['scr_date'] = pd.to_datetime(SCRIPY_START_TIME, format='%Y-%m-%d_%H')
    print(df_results.info())
    print(df_results.head())
    return df_results



def load_to_s3(data, dir, aws_conn_id='conn_aws_de_3_2'):
    s3_hook = S3Hook(aws_conn_id=aws_conn_id)

    base_key = f'raw_data/news/{dir}/{SCRIPY_START_DAY}/{SCRIPY_START_TIME}'
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
    URL = kwargs.get('params', {}).get('url')
    AWS_DEFAULT_REGION = kwargs.get('params', {}).get('AWS_DEFAULT_REGION')
    BUCKET = kwargs.get('params', {}).get('BUCKET')

    news_title = scripy_news_title(URL)
    urls = list(news_title.comment_link)
    
    news_comment = extract_comments(urls)
    
    print(f'len of news_title : {len(news_title)},  news_comment : {len(news_comment)}')
    news_title_path = load_to_s3(news_title, 'news_title')
    news_comment_path = load_to_s3(news_comment, 'news_comment')
    
    # XCom에 값을 저장
    ti = kwargs['ti']  # TaskInstance 객체 가져오기
    ti.xcom_push(key='news_title_path', value=news_title_path)
    ti.xcom_push(key='news_comment_path', value=news_comment_path)
    


