import pandas as pd
import requests
from datetime import datetime
import time
import multiprocessing as mp
import os 
import boto3 
from dotenv import load_dotenv
from pathlib import Path
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

dotenv_path = Path(".env")
load_dotenv(dotenv_path = dotenv_path)

AWS_ACCESS_KEY_ID = os.getenv('aws_access_key_id')
AWS_SECRET_ACCESS_KEY = os.getenv('aws_secret_access_key')
AWS_DEFAULT_REGION = 'ap-northeast-2'

URL = "https://news.naver.com/main/ranking/popularMemo.naver"
SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')


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

    return result_df.reset_index(drop=True).sort_values('comment_count')

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


def scripy_comment(url):
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
        print(f'{url} finish click more button ') 
    
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
    
    # 드라이버 종료
    driver.quit()
    
    print(f'{url} is finish and len df is {len(list_sum)} by {mp.current_process().name}')
    return list_sum

def run_multi_process_scripy_comment(url_list):
    start_time = time.time()
    cpu_count = mp.cpu_count()
    print(f'current cpu is {cpu_count}, and multiprocessing use {cpu_count}')
    pool = mp.Pool(cpu_count)
    result = []
    for row in pool.map(scripy_comment,url_list):
        result += row
    pool.close()
    pool.join()
    end_time = time.time()
    
    print(f'댓글 수집 걸린시간 : {end_time-start_time}')
    return result

def load_to_s3(df, dir):

    client = boto3.client('s3',
                    aws_access_key_id = AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
                    region_name = AWS_DEFAULT_REGION
                    )

    bucket = 'de-3-2'
    key = f'raw_data/news/{dir}/{SCRIPY_START_DAY}/{SCRIPY_START_TIME}.csv'  # 파일 확장자를 명시적으로 추가

    # 데이터프레임을 바로 S3에 업로드
    csv_buffer = df.to_csv(index=False, encoding = 'utf-8-sig')
    try:
        response = client.put_object(Body=csv_buffer, Bucket=bucket, Key=key)
        print("업로드 성공")
    except Exception as e:
        print("업로드 실패:", str(e))
    

def main():
    news_title = scripy_news_title(URL)
    url_list = list(news_title.comment_link)
    result = run_multi_process_scripy_comment(url_list)
    news_comment = pd.DataFrame(result, columns = ['nickname', 'comment_time', 'comment', 'comment_link', 'created_news_time','scrapy_time'])
    load_to_s3(news_title, 'news_title')
    load_to_s3(news_comment, 'news_comment')
    
if __name__ == '__main__':
    main()




