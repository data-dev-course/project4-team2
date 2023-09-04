from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

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
        # last_height = driver.execute_script("return document.body.scrollHeight")
        # while True :
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #     # Wait to load page
        #     time.sleep(SCROLL_PAUSE_TIME)

        #     # Calculate new scroll height and compare with last scroll height
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break
        #     last_height = new_height
            
    except :
        print(f'{url} finish click more button ') 
        # logger.info(f'{url} finish click more button ')
        
    finally :
        # 스크롤을 아래까지내린 후 페이지 소스 읽어오는 try 문
        html = driver.page_source                       # 현재 driver에 나타난 창의 page_source(html) 가져오기
        soup = BeautifulSoup(html, 'html.parser')       # html 파싱(parsing)을 위해 BeautifulSoup에 넘겨주기

        
        return  driver,soup

def get_webtoon_titles(url):
    driver, soup = get_driver(url)
    driver.quit()
    result = []

    days = soup.select('.WeekdayMainView__daily_all_item--DnTAH')
    for day in days:
        selected_day = day.select('.WeekdayMainView__heading--tHIYj')[0].get_text()
        titles = day.select('.DailyListItem__info_area--aS5RC')
        for title in titles:
            webtoon_title = title.select('.ContentTitle__title--e3qXt')[0].get_text()
            webtoon_url = f'https://comic.naver.com{title.find("a", class_="ContentTitle__title_area--x24vt")["href"]}'
            result.append({
                'day': selected_day,
                'title': webtoon_title,
                'webtoon_link': webtoon_url,
                'scr_date': SCRIPY_START_TIME
            })
    print('웹툰 제목 수집 완료')
    return result
    

def lambda_handler(event, context):
    days = ["월요웹툰", "화요웹툰", "수요웹툰", "목요웹툰", "금요웹툰", "토요웹툰", "일요웹툰"]
    
    # 현재 요일의 이전 요일에 해당하는 값을 가져오기
    current_day_index = datetime.today().weekday()  # 현재 요일의 인덱스
    before_day_index = (current_day_index - 1) % len(days)
    before_day_value = days[before_day_index]

    webtoon_titles = get_webtoon_titles(BASE_URL)
    filtered_titles = [title for title in webtoon_titles if title['day'] == before_day_value]
    return filtered_titles