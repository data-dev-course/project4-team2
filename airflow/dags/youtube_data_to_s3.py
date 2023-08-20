from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta, date
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from airflow.providers.amazon.aws.hooks.s3 import S3Hook



def upload_to_s3(data):
    src_date = data[0]
    s3_hook = S3Hook()
    s3_bucket = 'de-3-2'
    s3_folder = 'raw_data/youtube'
    s3_key = f'{s3_folder}/{src_date}/{src_date}.csv'
    
    s3_hook.load_string(
        string_data= data[1],
        key=s3_key,
        bucket_name=s3_bucket,
        replace=True
    )
    print(f"youtube data uploaded to {s3_bucket}/{s3_key}")

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = Variable.get("youtube_api_key")

def youtube_search(publishedAfter,publishedBefore):
    youtube = build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
    latitude_seoul = 37.56667
    longtitude_seoul = 126.97806
    search_response = youtube.search().list(
        videoCategoryId="25",
        topicId="/m/098wr", # 지정된 주제와 관련된 리소스만 포함
        location=f"{latitude_seoul}, {longtitude_seoul}", 
        locationRadius='500km',
        type="video",
        part="id,snippet",
        maxResults=50,
        regionCode="KR", # 지정된 국가에서 볼 수 있는 동영상의 검색결과 반환
        relevanceLanguage='ko',# 지정된 언어와 가장 관련성이 높은 검색 결과 반환
        order="viewCount", #  조회수가 높은 순으로 정렬
        publishedAfter=publishedAfter,
        publishedBefore=publishedBefore
    ).execute()

    # 검색 결과에서 원하는 국가의 동영상만 필터링합니다.
    desired_country_code = "KR"
    filtered_results = []

    for item in search_response['items']:
        video_id = item['id']['videoId']
        channel_id = item['snippet']['channelId']

        # 해당 동영상을 업로드한 채널의 국가 정보를 가져옵니다.
        channel_response = youtube.channels().list(
            part="snippet",
            id=channel_id
        ).execute()

    # 채널의 국가 정보를 확인하여 원하는 국가의 동영상만 선택합니다.
        if 'country' in channel_response['items'][0]['snippet']:
            country_code = channel_response['items'][0]['snippet']['country']
            if country_code == desired_country_code:
                filtered_results.append(item)
                print(f"video_id: {video_id}, video_title: {item['snippet']['title']}, video_published_at:{item['snippet']['publishedAt']}, country:{channel_response['items'][0]['snippet']['country']}")
    print("총 동영상 개수:" ,len(search_response['items']))
    print("한국 채널의 동영상 개수: ", len(filtered_results))

    return filtered_results


def get_comments(item):
    youtube = build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
    video_id = item['id']['videoId']
    channel_id = item['snippet']['channelId']
    video_title = item['snippet']['title']
    video_published_at = item['snippet']['publishedAt']
    video_link = f"https://www.youtube.com/watch?v={video_id}"


    results = youtube.commentThreads().list(
        part="snippet, replies",
        videoId=video_id,
        textFormat="plainText",
        maxResults = 100 # 100
    ).execute()

    comments=[]

    for item1 in results["items"]:
        comment_id = item1["id"]
        comment = item1["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]
        comment_publishd_at = comment["snippet"]["publishedAt"]
        comment_updated_at = comment["snippet"]["updatedAt"]
        scr_date = datetime.now().strftime("%Y-%m-%d")
        comments.append([scr_date, video_id, channel_id, video_title, video_published_at, video_link, comment_id, author, text, comment_publishd_at, comment_updated_at])

    return comments


# rfc3339 형식으로 변환하는 함수
def convert(date):
    return date.isoformat(timespec='seconds')+'Z'


def get_data():
    comments = []
    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0) - timedelta(weeks=10) 
    end_date = start_date + timedelta(weeks=1)  


    for item in youtube_search(convert(start_date),convert(end_date)):
        try:
            comments.extend(get_comments(item))
        except HttpError as e:
            print(f"An HTTP error{e.resp.status} occurred:\n{e.content}")
    
        
    df = pd.DataFrame(comments, columns=[['scr_date','video_id','channel_id','video_title','video_published_at','video_link','comment_id','author','text', 'comment_publishd_at', 'comment_updated_at']])
    df['tag'] = 'youtube'
    scr_date = datetime.now().strftime("%Y-%m-%d")

    return (scr_date, df.to_csv(index=False))

DAG_ID = 'youtube_data_to_S3'

default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id=DAG_ID,
    default_args=default_args,
    start_date=datetime(2022, 8, 1),
    catchup=False,
    # schedule_interval="@daily",
) as dag:
    
    get_youtube_data_task = PythonOperator(
        task_id = 'get_youtube_data',
        python_callable=get_data
    )
    
    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        op_args=[get_youtube_data_task.output]
    )
    
    get_youtube_data_task >> upload_to_s3_task