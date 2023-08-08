import pandas as pd
import requests
from datetime import datetime
import time
import multiprocessing as mp

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

global count 
count = 0

def scripy_news_list(url,now):
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
    result_df['scrapy_time'] = now
    
    return result_df.reset_index(drop=True)

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
        
        data.append({"rank": rank, "title": title, "comment_count": comment_count, "link": link, "comment_link": comment_link})

    df = pd.DataFrame(data)
    df['press'] = press
    return df


def scripy_content(url):
    global count
    count += 1
    print(f'count is {count}')
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
        print(f'{url} finish more btn') 
    
    # 댓글 작성자
    nicknames = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_nick')
    list_nicknames = [nick.text for nick in nicknames]
    
    # 댓글 작성 시간
    datetimes = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]
    
    # 댓글 내용
    contents = driver.find_elements(By.CSS_SELECTOR, 'span.u_cbox_contents')
    list_contents = [content.text for content in contents]
    
    # 세트로 변환
    # list_sum = list(zip(list_nicknames, list_datetimes, list_contents))
    list_sum = [(nickname, datetime, content, url) for nickname, datetime, content in zip(list_nicknames, list_datetimes, list_contents)]

    
    # 드라이버 종료
    driver.quit()
    
    print(f'{url} is finish and len df is {len(list_sum)}')
    return list_sum


def main():
    start = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
    start_time = time.time()
    url = "https://news.naver.com/main/ranking/popularMemo.naver"
    df_news_list = scripy_news_list(url,start)
    print(f'len df_news_list is {len(df_news_list)}')
    url_list = list(df_news_list.comment_link)
    
    cpu_count = mp.cpu_count()
    print(f'current cpu is {cpu_count}, and multiprocessing use {cpu_count}')
    pool = mp.Pool(cpu_count)
    result = []
    
    for row in pool.map(scripy_content,url_list):
        result += row
    pool.close()
    pool.join()
    
    end_time = time.time()
    
    print(f'걸린시간 : {end_time-start_time}')
    
    pd.DataFrame(result).to_csv('result.csv')
    
    
    
    # pool.map(scripy_content,url_list)
    
    # pool.close()
    # pool.join
    
    
if __name__ == '__main__':
    main()




