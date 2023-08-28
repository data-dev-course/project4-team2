from . import conn_rds_postgre
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import HTTPException

def fetch_comments_from_db(start_time=None, end_time=None, tag=None):
    try :
        if not start_time or not end_time:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
        else:
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        print(f'start : {start_time}, end : {end_time}')
        query = """
            SELECT recorded_time, content_Tag, SUM(comment_count) AS total_comment_count
            FROM public."test_DM_HourlyCommentSummary"
            WHERE recorded_time BETWEEN %s AND %s
        """
        params = [start_time, end_time]

        if tag:
            query += " AND content_tag = %s"
            params.append(tag)
        query += """
            GROUP BY recorded_time, content_Tag
            ORDER BY recorded_time
        """
        conn = conn_rds_postgre.connect_to_db()
        if not conn:
            return None  # 여기서 에러 처리는 라우터에서 합니다.
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        # 데이터 가공하여 원하는 형태로 구성
        processed_results = []
        current_recorded_time = None
        current_entry = None
        all_count = 0

        for recorded_time, content_tag, total_comment_count in results:
            all_count += total_comment_count

            if recorded_time != current_recorded_time:
                if current_entry is not None:
                    current_entry["all_count"] = all_count
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

        if current_entry is not None:
            current_entry["all_count"] = all_count
            processed_results.append(current_entry)
        
        return processed_results

    except Exception as e:
        print(f"error : {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the data.")





def fetch_grammar_state_from_db(start_time, end_time, tag=None):
    try:
        query = """
            SELECT recorded_time, content_tag, SUM(total_count) as total_count, 
                   SUM(incorrect_count) as incorrect_count, SUM(correct_count) as correct_count
            FROM public."test_DM_DailyGrammarStats"
            WHERE recorded_time BETWEEN %s AND %s
        """
        params = [start_time, end_time]
        
        if tag:
            query += " AND content_tag = %s"
            params.append(tag)
            
        query += """
            GROUP BY recorded_time, content_tag
            ORDER BY recorded_time, content_tag
        """
        
        conn = conn_rds_postgre.connect_to_db()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        processed_results = []
        current_recorded_time = None
        current_entry = None

        for recorded_time, content_tag, total_count, incorrect_count, correct_count in results:
            if recorded_time != current_recorded_time:
                if current_entry is not None:
                    # Calculate and add "all_tag"
                    total_total_count = sum(tag_data["total_count"] for tag_data in current_entry["tags"].values())
                    total_incorrect_count = sum(tag_data["incorrect_count"] for tag_data in current_entry["tags"].values())
                    total_correct_count = sum(tag_data["correct_count"] for tag_data in current_entry["tags"].values())
                    total_error_rate = (total_incorrect_count / total_total_count) * 100 if total_total_count > 0 else 0
                    
                    current_entry["tags"]["all_tag"] = {
                        "total_count": total_total_count,
                        "incorrect_count": total_incorrect_count,
                        "correct_count": total_correct_count,
                        "error_rate": total_error_rate
                    }
                    
                    processed_results.append(current_entry)
                    
                current_recorded_time = recorded_time
                current_entry = {
                    "recorded_time": recorded_time,
                    "tags": {}
                }
            
            current_entry["tags"].setdefault(content_tag, {
                "total_count": 0,
                "incorrect_count": 0,
                "correct_count": 0,
                "error_rate": 0
            })
            current_entry["tags"][content_tag]["total_count"] += total_count
            current_entry["tags"][content_tag]["incorrect_count"] += incorrect_count
            current_entry["tags"][content_tag]["correct_count"] += correct_count
            current_entry["tags"][content_tag]["error_rate"] = (current_entry["tags"][content_tag]["incorrect_count"] / current_entry["tags"][content_tag]["total_count"]) * 100
        
        if current_entry is not None:
            # Calculate and add "all_tag" for the last entry
            total_total_count = sum(tag_data["total_count"] for tag_data in current_entry["tags"].values())
            total_incorrect_count = sum(tag_data["incorrect_count"] for tag_data in current_entry["tags"].values())
            total_correct_count = sum(tag_data["correct_count"] for tag_data in current_entry["tags"].values())
            total_error_rate = (total_incorrect_count / total_total_count) * 100 if total_total_count > 0 else 0
            
            current_entry["tags"]["all_tag"] = {
                "total_count": total_total_count,
                "incorrect_count": total_incorrect_count,
                "correct_count": total_correct_count,
                "error_rate": total_error_rate
            }
            
            processed_results.append(current_entry)
        
        return processed_results
    
    except Exception as e:
        print(f"error: {e}")
        raise
