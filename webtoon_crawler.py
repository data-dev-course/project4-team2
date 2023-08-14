from bs4 import BeautifulSoup

from datetime import datetime

import time
import pandas as pd
import multiprocessing as mp
from multiprocessing import Manager, Value
import logging
import os 
import boto3 
from dotenv import load_dotenv
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException


dotenv_path = Path(".env")
load_dotenv(dotenv_path = dotenv_path)

BASE_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
MAX_PAGE_NUM = 20
MAX_COMMENT_NUM = 100
AWS_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AWS_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_DEFAULT_REGION = 'ap-northeast-2'
BUCKET = 'de-3-2'

SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 로그 파일 핸들러 설정
file_handler = logging.FileHandler(f'{SCRIPY_START_TIME}_log.txt')
# 로그에 핸들러 추가
logger.addHandler(file_handler)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))





#driver 실행
def get_driver_and_soup(url):
    driver, soup = None, None
    # 스크롤 맨 아래까지 내려가는 try 문
    try :
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless=new')
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
        driver = webdriver.Chrome( options=options) # service=service,
        time.sleep(0.5)
        driver.get(url)
        driver.implicitly_wait(3)
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True :
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            
    except :
        # print(f'{url} finish click more button ') 
        logger.info(f'{url} finish click more button ')
        
    # 스크롤을 아래까지내린 후 페이지 소스 읽어오는 try 문
    html = driver.page_source                       # 현재 driver에 나타난 창의 page_source(html) 가져오기
    soup = BeautifulSoup(html, 'html.parser')       # html 파싱(parsing)을 위해 BeautifulSoup에 넘겨주기

        
    return  driver,soup

def get_webtoon_titles(url):
    #웹툰 기본 페이지에서 데이터 가져오기
    driver,soup = get_driver_and_soup(url)
    driver.quit()
    result = []
    
    days = soup.select('.WeekdayMainView__daily_all_item--DnTAH')
    for day in days :
        selected_day =day.select('.WeekdayMainView__heading--tHIYj')[0].get_text()
        titles = day.select('.DailyListItem__info_area--aS5RC')
        for title in titles :
            webtoon_title = title.select('.ContentTitle__title--e3qXt')[0].get_text()
            webtoon_url = f'https://comic.naver.com{title.find("a", class_ = "ContentTitle__title_area--x24vt")["href"]}'
            result.append([selected_day,webtoon_title,webtoon_url])
            # print(f'[{selected_day}]-[{webtoon_title}]-[{webtoon_url}]')
            
    df = pd.DataFrame(result, columns = ['day','title','webtoon_link'])
    df['scrapy_time'] = SCRIPY_START_TIME
    logger.info(f'웹툰 제목 수집 완료')
    return df

def get_webtoon_title_contents(title,url):
    try :
        driver,soup = get_driver_and_soup(url)
        driver.quit()
        df = pd.DataFrame()
        title_contents = []
        title_index = soup.select('.EpisodeListList__item--M8zq4')
        for index in title_index :
            content_name = index.select(".EpisodeListList__title--lfIzU")[0].get_text()
            content_link = f'https://comic.naver.com{index.find("a", class_ = "EpisodeListList__link--DdClU")["href"]}'
            content_date = index.select(".date")[0].get_text()
            # print(f'{content_name} - {content_link} - {content_date}')
            title_contents.append([title,content_name,content_link,content_date,SCRIPY_START_TIME])

        df = pd.DataFrame(title_contents, columns = ['title','content_name', 'content_link', 'content_date','scrapy_time'])
        # print(f'finish __get_webtoon_title_contents__-{title}')
        logger.info(f'목차 수집완료-{title}')
    except WebDriverException as e:
        # print(f"Failed processing {url}. Reason: {e}")
        logger.error(f"Failed processing {url}. Reason: {e}")
    finally:
        if driver:  # driver가 None이 아닌 경우에만 (즉, 초기화된 경우에만) quit() 호출
            driver.quit()
    return df

def get_comments(args):
    url, title, content_name, current_title_num, total_titles, current_content_num, total_contents = args
    try :
        driver, soup = get_driver_and_soup(url)
        comment_num = 0

        count = 0
        try :
            while(comment_num < MAX_COMMENT_NUM) :
                if count == 0 :
                    driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[8]/a/span[1]').click()
                else :
                    driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[7]/a/span/span/span[1]').click()
                count += 1
                comment_num = len(driver.find_elements(By.CSS_SELECTOR, 'div.u_cbox_area'))


                # print(f'len comment = ', comment_num)
                # print('count :', count)
        except :
            # print(f'{title} - {content_name} 의 댓글 수 : {comment_num}')
            logger.info(f'{title} - {content_name} 의 댓글 수 : {comment_num}')

        comment_nicknames = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
        list_nicknames = [nick.text for nick in comment_nicknames]

        comment_ids = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_id')
        list_ids = [id.text for id in comment_ids]

        comment_texts = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
        list_texts = [id.text for id in comment_texts]

        comment_dates = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
        list_dates=[]
        for date in comment_dates:
            list_dates.append(date.get_attribute("data-value")) 

        list_sum = [(title, content_name, nickname, id, datetime, comment, SCRIPY_START_TIME) for nickname, id, datetime, comment in zip(list_nicknames, list_ids, list_dates, list_texts)]

    except WebDriverException as e:
        # print(f"Failed processing {url}. Reason: {e}")
        logger.error(f"Failed processing {url}. Reason: {e}")
        
    finally :
        if driver :
            driver.quit()
        # print(f'{url} is finish and len of list is {len(list_sum)} by {mp.current_process().name}')
        # df = pd.DataFrame(list_sum, columns = ['title','content_name','nickname','id','comment_date','comment','scrapy_time'])
        # print(f"[Title {current_title_num}/{total_titles} | Content {current_content_num}/{total_contents}] Collected {comment_num} comments for {title} - {content_name}")
        logger.info(f"[Title {current_title_num}/{total_titles} | Content {current_content_num}/{total_contents}] Collected {comment_num} comments for {title} - {content_name}")
    return list_sum

def run_multi_process_get_comments(contents_list, current_title_num, total_titles):
    start_time = time.time()
    
    extended_contents_list = [(link, title, content_name, current_title_num, total_titles, idx+1, len(contents_list)) for idx, (link, title, content_name) in enumerate(contents_list)]
    pool = mp.Pool(2)
    result = []
    for row in pool.map(get_comments, extended_contents_list):
        result += row
    pool.close()
    pool.join()
    end_time = time.time()
    logger.info(f'총 소요시간 : {end_time-start_time}')
    
    return result

def load_to_s3(data, dir, data_type='df'):
    client = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION
                          )

    base_key = f'raw_data/webtoon/{dir}/{SCRIPY_START_DAY}/{SCRIPY_START_TIME}'

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
    # 현재 요일을 구합니다.
    days = ["월요웹툰", "화요웹툰", "수요웹툰", "목요웹툰", "금요웹툰", "토요웹툰", "일요웹툰"]
    current_day = days[datetime.today().weekday()]  # 0: 월요일, 1: 화요일, ...

    webtoon_titles = get_webtoon_titles(BASE_URL)
    filtered_titles = webtoon_titles[webtoon_titles['day'] == current_day][:5]  # 현재 요일의 웹툰만 필터링
    total_titles = len(filtered_titles)

    all_comments = []

    for idx, row in enumerate(filtered_titles.iterrows()):
        _, row = row
        current_title_num = idx + 1  # 0-based index to 1-based index
        webtoon_contents = get_webtoon_title_contents(row['title'], row['webtoon_link'])
        webtoon_comments = run_multi_process_get_comments(webtoon_contents[['content_link', 'title', 'content_name']].values.tolist(), current_title_num, total_titles)
        all_comments.extend(webtoon_comments)
    
    webtoon_all_comments = pd.DataFrame(all_comments, columns=['title', 'content_name', 'nickname', 'id', 'comment_date', 'comment', 'scrapy_time'])
    
    load_to_s3(webtoon_titles,'title')
    
    load_to_s3(webtoon_contents, 'contents')
    load_to_s3(webtoon_all_comments, 'omments')
    time.sleep(3)
    
    load_to_s3(f'{SCRIPY_START_TIME}_log.txt', 'webtoon_log', data_type='log')
    
            # 로그 파일 초기화 (옵션)
    with open(f'{SCRIPY_START_TIME}_log.txt', 'w') as f:
        f.truncate()
    # pd.DataFrame(all_comments, columns=['title', 'content_name', 'nickname', 'id', 'comment_date', 'comment', 'scrapy_time']).to_csv('result_webtoon.csv', index=False)
if __name__ == '__main__':
    main()

