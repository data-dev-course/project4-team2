from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import json

SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')
SCRIPY_START_DAY = datetime.now().strftime('%Y-%m-%d')

BASE_URL = 'https://comic.naver.com/webtoon/weekday.nhn'

def get_driver(url):
    try :
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--user-data-dir=/tmp/user-data')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--v=99')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--data-path=/tmp/data-path')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--homedir=/tmp')
        chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        chrome_options.binary_location = "/opt/python/bin/headless-chromium"
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='/opt/python/bin/chromedriver')
        driver.get(url)
        driver.implicitly_wait(3)
        driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)
        SCROLL_PAUSE_TIME = 0.3
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
        print(f'{url} finish click more button ') 
        # logger.info(f'{url} finish click more button ')
        
    finally :
        # 스크롤을 아래까지내린 후 페이지 소스 읽어오는 try 문
        html = driver.page_source                       # 현재 driver에 나타난 창의 page_source(html) 가져오기
        soup = BeautifulSoup(html, 'html.parser')       # html 파싱(parsing)을 위해 BeautifulSoup에 넘겨주기

        
        return  driver,soup

    

def get_webtoon_title_contents(title, url):
    driver = None
    # 1. 현재 시간 정보를 가져옵니다.
    now = datetime.now()
    
    # 2. 해당 시간의 시간 정보를 가져와서 0 ~ 24 사이의 값
    today_hour = now.hour 
    try:
        driver, soup = get_driver(url)
        driver.quit()
        title_contents = []
        title_index = soup.select('.EpisodeListList__item--M8zq4')
        if title_index:  # title_index가 비어있지 않은 경우에만 첫 번째 요소 작업
            index = title_index[today_hour]
            content_name = index.select(".EpisodeListList__title--lfIzU")[0].get_text()
            content_link = f'https://comic.naver.com{index.find("a", class_="EpisodeListList__link--DdClU")["href"]}'
            content_date = index.select(".date")[0].get_text()
            tag_elements = soup.find_all('a', class_='TagGroup__tag--xu0OH')
            webtoon_categories = [tag.get_text()[1:] for tag in tag_elements]
            
            title_contents.append({
                'title': title,
                'content_name': content_name,
                'content_link': content_link,
                'content_date': content_date,
                'scrapy_time': SCRIPY_START_TIME,
                'webtoon_categories' : json.dumps(webtoon_categories)
            })
            print(f'첫 번째 목차 수집완료-{title}')
    
        # 4. 로그 메시지 출력
        print(f'회차: 위에서부터 {today_hour} 번째, 목차 수집완료-{title}')
    
    except WebDriverException as e:
        print(f"Failed processing {url}. Reason: {e}")
    finally:
        if driver:
            driver.quit()
    return title_contents

def lambda_handler(event, context):
    title = event.get('title')
    webtoon_link = event.get('webtoon_link')
    

    webtoon_contents = get_webtoon_title_contents(title, webtoon_link)


    return webtoon_contents