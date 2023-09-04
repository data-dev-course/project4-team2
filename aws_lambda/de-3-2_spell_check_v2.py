import json
from hanspell import spell_checker
import pandas as pd 


def lambda_handler(event, context):
    id_comment_list = event.get('id_comment_list')

    
    result_sentence = []
    result_word = []
    
    
    for id_comment in id_comment_list:
        try:
            comment_id = id_comment[0]
            comment = id_comment[1]
            content_tag = id_comment[2]
            result = spell_checker.check(comment).as_dict()
            result_sentence.append([comment_id, content_tag, result["result"], result["original"], result["checked"], result["errors"]])
        
            for original_word, checked_word in zip(result["original_list"], result["words_v2"]):
                result_word.append([comment_id, content_tag, original_word, checked_word[0], checked_word[1]])
   
        except Exception as e:
            print(f"Failed {id_comment}, Reason: {str(e)}")
            return None, None, (str(e))

    return result_sentence, result_word, None