import pandas as pd
import requests
from datetime import datetime
import time
import multiprocessing as mp
from multiprocessing import Manager
import logging
import os 
import boto3 
from dotenv import load_dotenv
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


dotenv_path = Path(".env")
load_dotenv(dotenv_path = dotenv_path)

AWS_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AWS_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_DEFAULT_REGION = 'ap-northeast-2'
BUCKET = 'de-3-2'

URL = "https://news.naver.com/main/ranking/popularMemo.naver"
SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 로그 파일 핸들러 설정
file_handler = logging.FileHandler(f'{SCRIPY_START_TIME}_log.txt')
# 로그에 핸들러 추가
logger.addHandler(file_handler)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


def scripy_news_title(url):
    """
    각 언론사 별 댓글 많은 순 ( 최대 20개로 추측중 ) 뉴스 기사를 스크래핑하여 데이터프레임으로 반환하는 함수
    Input:
        url (str) : 스크래핑을 진행하기위한 URL 
        now (datetime) : 크롤링이 작동한 시간
    Output:
        result_df (dataframe) : [ 언론사 이름, 언론사 별 댓글많은 순 정리된 URL ] 이 담겨있는 데이터프레임
    """

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
    result_df['scrapy_time'] = SCRIPY_START_TIME
    
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


def scripy_comment(args):
    url, processed_count, total_urls, failed_count, failed_urls = args  # 인자를 unpack


    driver = None
    
    try :
        list_sum = []
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')
        driver = webdriver.Chrome( options=options) # service=service,
        driver.implicitly_wait(3)
        driver.get(url)
        driver.implicitly_wait(3)
        
        try :
            while True:
                driver.find_element(By.XPATH,'//*[@id="cbox_module"]/div[2]/div[9]/a/span/span/span[1]').click()
                driver.implicitly_wait(2)
        except:
            # print(f'{url} finish click more button ') 
            logger.info(f'{url} finish click more button ')
        
        # 댓글 작성자
        nicknames = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
        list_nicknames = [nick.text for nick in nicknames]
        
        # 댓글 작성 시간
        datetimes = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
        list_datetimes = [datetime.text for datetime in datetimes]
        
        # 댓글 내용
        comments = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
        list_comments = [comment.text for comment in comments]
        
        # 뉴스 작성 시간
        created_news_time = driver.find_elements(By.CSS_SELECTOR,'span.media_end_head_info_datestamp_time')[0].get_attribute('data-date-time')
        
        # 세트로 변환
        list_sum = [(nickname, datetime, comment, url, created_news_time, SCRIPY_START_TIME) for nickname, datetime, comment in zip(list_nicknames, list_datetimes, list_comments)]
        processed_count.value += 1

    except WebDriverException as e:
        # print(f"Failed processing {url}. Reason: {e}")
        logger.error(f"Failed processing {url}. Reason: {e}")
        failed_count.value += 1
        failed_urls.append((url, str(e)))  # URL과 함께 실패 이유를 저장

    finally:
        if driver:  # driver가 None이 아닌 경우에만 (즉, 초기화된 경우에만) quit() 호출
            driver.quit()
        # print(f'{url} is finish and len of list is {len(list_sum)} by {mp.current_process().name}')
        # print(f'Processed: {processed_count.value}/{total_urls}. Failed: {failed_count.value}')
        logger.info(f'{url} is finish and len of list is {len(list_sum)} by {mp.current_process().name}')
        logger.info(f'Processed: {processed_count.value}/{total_urls}. Failed: {failed_count.value}')
    
    return list_sum

def run_multi_process_scripy_comment(url_list):
    start_time = time.time()
    cpu_count = mp.cpu_count() 
    manager = Manager()
    processed_count = manager.Value('i', 0)  # integer 타입의 공유 변수 초기화
    failed_count = manager.Value('i', 0)    # 실패한 URL의 수를 기록하는 공유 변수
    failed_urls = manager.list()             # 실패한 URL들을 저장하는 공유 리스트

    # url_list의 각 URL과 공유 변수들, 리스트를 튜플로 묶어서 전달
    args_list = [(url, processed_count, len(url_list), failed_count, failed_urls) for url in url_list]
    result = []
    
    # print(f'current cpu is {cpu_count}, and multiprocessing use {cpu_count}')
    logger.info(f'current cpu is {cpu_count}, and multiprocessing use {cpu_count*2}')
    pool = mp.Pool(int(cpu_count) * 2)
    
    
    
    for row_result in pool.map(scripy_comment, args_list):
        result += row_result
    pool.close()
    pool.join()
    end_time = time.time()
    # print(f'총 소요시간 : {end_time-start_time}')
    # print(f'Total URLs: {len(url_list)}, Processed URLs: {processed_count.value}, Failed URLs: {failed_count.value}')
    # print(f"List of Failed URLs: {[fail[0] for fail in failed_urls]}")  # 실패한 URL만 출력
    # print(f"Reasons of Failure: {[fail[1] for fail in failed_urls]}")   # 실패 이유 출력
    
    logger.info(f'총 소요시간 : {end_time-start_time}')
    logger.info(f'Total URLs: {len(url_list)}, Processed URLs: {processed_count.value}, Failed URLs: {failed_count.value}')
    logger.info(f"List of Failed URLs: {[fail[0] for fail in failed_urls]}")  # 실패한 URL만 출력
    logger.info(f"Reasons of Failure: {[fail[1] for fail in failed_urls]}")   # 실패 이유 출력


    return result, list(failed_urls)  # 추가된 부분: 실패한 URL 리스트 반환


def load_to_s3(data, dir, data_type='df'):
    client = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION
                          )

    base_key = f'raw_data/news/{dir}/{SCRIPY_START_DAY}/{SCRIPY_START_TIME}'

    # 파일 이름 중복 검사 및 수정
    if data_type == 'df':
        extension = '.csv'
    elif data_type == 'log':
        extension = '.txt'
    else:
        raise ValueError("Invalid data_type. Choose 'df' or 'log'.")

    key = base_key + extension
    counter = 1
    while True:
        try:
            client.head_object(Bucket=BUCKET, Key=key)  # 오브젝트가 존재하는지 확인
            counter += 1
            key = base_key + f'-{counter}' + extension  # 기존 이름 뒤에 "-n" 추가
        except:
            break

    # S3에 업로드
    if data_type == 'df':
        csv_buffer = data.to_csv(index=False, encoding='utf-8-sig')
        try:
            response = client.put_object(Body=csv_buffer, Bucket=BUCKET, Key=key)
            logger.info(f"업로드 성공: {key}")
        except Exception as e:
            logger.error(f"업로드 실패: {e}")

    elif data_type == 'log':
        try:
            with open(data, 'rb') as f:
                client.upload_fileobj(f, BUCKET, key)
            logger.info(f"업로드 성공: {key}")
        except Exception as e:
            logger.error(f"업로드 실패: {e}")

    

def main():
    news_title = scripy_news_title(URL)
    url_list = list(news_title.comment_link)[-10:]
    result, failed_urls = run_multi_process_scripy_comment(url_list)  # 실패한 URL 리스트 받아오기

    news_comment = pd.DataFrame(result, columns = ['nickname', 'comment_time', 'comment', 'comment_link', 'created_news_time','scrapy_time'])
    for url, reason in failed_urls:
        # print(f"Failed URL: {url}, Reason: {reason}")
        logger.info(f"Failed URL: {url}, Reason: {reason}")
    
    load_to_s3(news_title, 'news_title')
    load_to_s3(news_comment, 'news_comment')
    time.sleep(3)
    
    load_to_s3(f'{SCRIPY_START_TIME}_log.txt', 'news_log', data_type='log')

    
        # 로그 파일 초기화 (옵션)
    with open(f'{SCRIPY_START_TIME}_log.txt', 'w') as f:
        f.truncate()
    
if __name__ == '__main__':
    main()




