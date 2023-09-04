
from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import WebDriverException
SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')

def get_driver():
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
    return driver
    
def lambda_handler(event, context):
    url = event.get('url')
    comments_list = []
    comment_link = url
    try:
        driver = get_driver()
        driver.get(url)
        while True:
            try:
                driver.implicitly_wait(10)
                driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div[2]/div[9]/a/span/span/span[1]').click()
            except:
                # logger.info(f'{url} - 스크롤 다운 끝 ')
                print(f'{url} - 스크롤 다운 끝 ')
                break
        
        list_sum = []
        print('수집 시작')
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
        
        # 카테고리 출력
        active_element = driver.find_element(By.XPATH, '//*[@class="Nlist_item _LNB_ITEM is_active"]/a/span[@class="Nitem_link_menu"]')
        active_text = active_element.text
        # print(active_text)
        # 세트로 변환
        list_sum = [(nickname, comment_date, comment, comment_link, created_news_time, active_text) for nickname, comment_date, comment in zip(list_nicknames, list_datetimes, list_comments)]

        driver.quit()
        print('수집 완료')
        print('comments_list:',list_sum)
        
        print(list_nicknames, list_datetimes, list_comments)
        driver.quit()
        
    except WebDriverException as e:
        print(f"Failed processing {url}. Reason: {e}")
        # logger.error(f"Failed processing {url}. Reason: {e}")
        driver.quit()
        return None, (url, str(e))

    return list_sum, None