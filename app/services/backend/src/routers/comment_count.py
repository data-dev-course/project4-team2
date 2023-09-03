from fastapi import APIRouter, HTTPException, Depends, Query,status
from datetime import datetime, timedelta
from ..database import fetch_query
current_time = datetime.now()
start_example = (current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
end_example = current_time.strftime('%Y-%m-%d %H:%M:%S')


router = APIRouter()

@router.get(
    "/",
    summary="데이터 수집 현황 - [ 댓글 수집 현황, 시간별 수집 현황 ]",
    description="""
## Summary :
각 태그 별, 전체 태그로 해서 각 날짜 ( 1시간 단위 ) 별 수집된 댓글의 개수 현황를 보여줍니다

## Parameters:

- `start_time`: 시작 시간을 지정합니다. 
    - 포맷: 'YYYY-MM-DD HH:MM:SS'
    - 예: '2023-01-01 12:00:00'
  
- `end_time`: 끝 시간을 지정합니다. 
    - 포맷: 'YYYY-MM-DD HH:MM:SS'
    - 예: '2023-01-02 12:00:00'
    
- `tag`: 특정 태그와 관련된 댓글을 필터링 하기 위해 사용됩니다.

## Note:

시작 시간과 끝 시간을 모두 지정하지 않으면, 기본적으로 최근 24시간 동안의 댓글을 반환합니다.  
태그를 지정하지 않으며면, 전체 태그를 반환합니다.  

## Request Example:
- GET /comment_count/?start_Time=2023-08-27 22:12:03&end_time=2023-08-28 22:12:03
- GET /comment_count/?tag=youtube
- GET /comment_count/

**Response:**

- **200 OK**  
요청이 성공적으로 처리되었으며, 해당 조건에 맞는 댓글 목록을 반환합니다.  
응답 본문 예시:
```json
[
  {
    "recorded_time": "2023-08-27T23:00:00",
    "tags": [
      {
        "content_tag": "news",
        "total_comment_count": 14838
      },
      {
        "content_tag": "webtoon",
        "total_comment_count": 17429719
      },
      {
        "content_tag": "youtube",
        "total_comment_count": 13893
      }
    ],
    "all_count": 17474672
  },...
```
- **204 No Content**  
해당 기간 또는 태그에 맞는 댓글이 존재하지 않을 경우 반환됩니다. 본문 내용이 없음을 나타냅니다.

- **500 Internal Server Error**  
서버 내부 오류 또는 데이터베이스 연결 실패 시 반환됩니다.
응답 본문 예시:
```json
{
    "detail": "Unable to connect to the database."
}
```

    """
)
async def get_comments(
    start_time: str = Query(default=start_example, example=start_example, description="시작 시간"),
    end_time: str = Query(default=end_example, example=end_example, description="끝 시간"),
    tag: str = Query(None, description="태그 [ youtube, news, webtoon ]")
):
    try:
        print('start get_comment')
        results = fetch_query.fetch_comments_from_db(start_time, end_time, tag)
        
        if not results:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

        # 데이터 가공하여 원하는 형태로 구성
        processed_results = []
        current_recorded_time = None
        current_entry = None
        all_count = 0

        for recorded_time, content_tag, total_comment_count in results:
            # 각 시간대가 바뀔 때 all_count를 0으로 초기화합니다.
            if recorded_time != current_recorded_time:
                all_count = 0

            all_count += total_comment_count

            if recorded_time != current_recorded_time:
                if current_entry is not None:
                    processed_results.append(current_entry)
                current_recorded_time = recorded_time
                current_entry = {
                    "recorded_time": recorded_time,
                    "tags": []
                }
            
            current_entry["tags"].append({
                "content_tag": content_tag,
                "total_comment_count": total_comment_count
            })
            current_entry["all_count"] = all_count  # 각 시간대별로 all_count 업데이트

        if current_entry is not None:
            processed_results.append(current_entry)
        
        return processed_results  # 데이터 가공 후의 결과 반환
    
    except ConnectionError:  # 데이터베이스 연결에 실패한 경우에 대한 예외
        raise HTTPException(status_code=500, detail="Unable to connect to the database.")
    except Exception as e:  # 다른 예외들을 처리하기 위한 코드
        raise HTTPException(status_code=500, detail=str(e))
