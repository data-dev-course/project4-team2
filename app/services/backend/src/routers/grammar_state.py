from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query,status
from datetime import datetime, timedelta
from ..database import fetch_query

current_time = datetime.now()
start_example = (current_time - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
end_example = current_time.strftime('%Y-%m-%d %H:%M:%S')

router = APIRouter()

@router.get(
    "/",
    summary="문법 상태 가져오기",
    description="""
## Summary :
각 태그 별, 전체 태그로 해서  전체 문장개수,문법이 틀린 문장, 문법 맞춘 문장, 문장 오류율 ( 백분율 ) 을 보여줍니다.
    
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
- GET /grammar_state/?start_Time=2023-08-27 22:12:03&end_time=2023-08-28 22:12:03
- GET /grammar_state/?tag=youtube
- GET /grammar_state/

**Response:**    
    
    
- **200 OK**  
요청이 성공적으로 처리되었으며, 해당 조건에 맞는 댓글 목록을 반환합니다.  
응답 본문 예시:
```json
    [
  {
    "recorded_time": "2023-08-28T00:00:00",
    "tags": {
      "news": {
        "total_count": 100,
        "incorrect_count": 98,
        "correct_count": 7,
        "error_rate": 98
      },
      "webtoon": {
        "total_count": 2100,
        "incorrect_count": 999,
        "correct_count": 1177,
        "error_rate": 47.57142857142857
      },
      "youtube": {
        "total_count": 100,
        "incorrect_count": 39,
        "correct_count": 23,
        "error_rate": 39
      },
      "all_tag": {
        "total_count": 2300,
        "incorrect_count": 1136,
        "correct_count": 1207,
        "error_rate": 49.391304347826086
      }
    }
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
async def get_grammar_state(
    start_time: str = Query(default=start_example, example=start_example, description="시작 시간"),
    end_time: str = Query(default=end_example, example=end_example, description="끝 시간"),
    tag: str = Query(None, description="태그 [ youtube, news, webtoon ]")):
    try:
        if not start_time or not end_time:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        
        results = fetch_query.fetch_grammar_state_from_db(start_time, end_time, tag)
        
        if not results:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        
        return results
    
    except ConnectionError:  # 데이터베이스 연결에 실패한 경우에 대한 예외
        raise HTTPException(status_code=500, detail="Unable to connect to the database.")
