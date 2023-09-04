

from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
SCRIPY_START_TIME = datetime.now().strftime('%Y-%m-%d_%H')


def get_driver(url):
    driver = None
    try:
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
        SCROLL_PAUSE_TIME = 0.2
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
    return driver
    
def lambda_handler(event, context):
    MAX_COMMENT_NUM = 50000
    url = event.get('content_link')
    title = event.get('title')
    content_name = event.get('content_name')
    print(f'전달받은 인자 content_link : {url}, title : {title}, content_name : {content_name}')
    list_sum = []
    
    try:
        driver  = get_driver(url)
        comment_num = 0
        count = 0
        
        try:
            while comment_num < MAX_COMMENT_NUM:
                driver.implicitly_wait(3)
                time.sleep(0.1)
                driver.implicitly_wait(3)
                if count == 0:
                    driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[8]/a/span[1]').click()
                else:
                    driver.find_element(By.XPATH, '//*[@id="cbox_module"]/div/div[7]/a/span/span/span[1]').click()
                count += 1
                comment_num = len(driver.find_elements(By.CSS_SELECTOR, 'div.u_cbox_area'))
                print(comment_num)
        except WebDriverException as e:
            print(e)
            print('더보기 클릭 끝')
        
        finally :
            print(f'더보기 클릭 횟수 : ', count)    
            comment_nicknames = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
            list_nicknames = [nick.text for nick in comment_nicknames]
    
            comment_ids = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_id')
            list_ids = [id.text for id in comment_ids]
    
            comment_texts = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
            list_texts = [id.text for id in comment_texts]
    
            comment_dates = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
            list_dates = [date.get_attribute("data-value") for date in comment_dates]
    
            list_sum = [(title, content_name, nickname, id, datetime, comment, SCRIPY_START_TIME) for nickname, id, datetime, comment in zip(list_nicknames, list_ids, list_dates, list_texts)]
            print(f'{title} - {content_name} 의 댓글 수 : {comment_num}')
            return list_sum, None  # 성공 시

    except WebDriverException as e:
        print(f"Failed processing {url}. Reason: {e}")
        # logger.error(f"Failed processing {url}. Reason: {e}")
        return None, (url, str(e))  # 실패 시

