import pandas as pd
import requests
from datetime import datetime
import time

from concurrent.futures import ThreadPoolExecutor, as_completed


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

completed_threads = 0

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
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)
    driver.implicitly_wait(3)
    return driver


def fetch_comments(driver, url):
    comments_list = []

    try:
        driver.get(url)
        while True:
            try:
                driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div[2]/div[9]/a/span/span/span[1]').click()
            except:
                logger.info(f'{url} - 스크롤 다운 끝 ')
                break
        
        elements = {
            'nicknames': 'span.u_cbox_nick',
            'datetimes': 'span.u_cbox_date',
            'comments': 'span.u_cbox_contents',
            'news_time': 'span.media_end_head_info_datestamp_time'
        }

        data = {}
        for key, selector in elements.items():
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            if key == 'news_time':
                data[key] = elems[0].get_attribute('data-date-time')
            else:
                data[key] = [elem.text for elem in elems]
        
        comments_list = list(zip(data['nicknames'], data['datetimes'], data['comments'],
                                 [url]*len(data['nicknames']), [data['news_time']]*len(data['nicknames']),
                                 [SCRIPY_START_TIME]*len(data['nicknames'])))

    except WebDriverException as e:
        logger.error(f"Failed processing {url}. Reason: {e}")
        return None, (url, str(e))

    return comments_list, None


def process_url(url):
    with initialize_driver() as driver:
        comments, failed = fetch_comments(driver, url)
        driver.quit()  # 리소스를 해제하는 코드 추가
        return comments, failed




def run_multi_thread_scripy_comment(url_list):
    global completed_threads
    core_count = os.cpu_count()
    max_threads = min(int(core_count * 0.75), len(url_list))
    
    results = []
    failed_urls = []

    with ThreadPoolExecutor(max_threads) as executor:
        # URL 별로 스레드에 작업 제출
        future_to_url = {executor.submit(process_url, url): url for url in url_list}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            completed_threads += 1  # 완료된 스레드 수 증가
            logger.info(f"Progress: {completed_threads}/{len(url_list)}")
            
            try:
                comments, failed = future.result()
                if comments:
                    results.extend(comments)
                    logger.info(f'URL {url} processed successfully with {len(comments)} comments.')
                if failed:
                    failed_urls.append(failed)
                    logger.error(f'URL {url} failed with reason: {failed}.')
            except Exception as exc:
                logger.error(f'URL {url} generated an exception: {exc}')

    logger.info(f'수집 성공한 뉴스 개수: {len(url_list)}, 수집된 전체 댓글 수: {len(results)}, 실패한 뉴스 개수: {len(failed_urls)}')
    logger.info(f"List of Failed URLs: {failed_urls}")

    return results, failed_urls


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
    start_time = time.time()
    news_title = scripy_news_title(URL)
    url_list = list(news_title.comment_link)[-10:]
    result, failed_urls = run_multi_thread_scripy_comment(url_list)  # 멀티스레딩으로 변경
    
    news_comment = pd.DataFrame(result, columns = ['nickname', 'comment_time', 'comment', 'comment_link', 'created_news_time','scrapy_time'])
    news_comment.to_csv('multi.csv')
    for url in failed_urls:
        # print(f"Failed URL: {url}, Reason: {reason}")
        logger.info(f"Failed URL: {url}")
    
    load_to_s3(news_title, 'news_title')
    load_to_s3(news_comment, 'news_comment')
    time.sleep(3)
    
    load_to_s3(f'{SCRIPY_START_TIME}_log.txt', 'news_log', data_type='log')
    end_time = time.time()
    logger.info(f'총 소요시간 : {end_time-start_time}')
    
        # 로그 파일 초기화 (옵션)
    with open(f'{SCRIPY_START_TIME}_log.txt', 'w') as f:
        f.truncate()
    
if __name__ == '__main__':
    main()




