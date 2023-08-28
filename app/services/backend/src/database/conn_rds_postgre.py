# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/
import os
import boto3
import psycopg2
import json
from botocore.exceptions import ClientError


from dotenv import load_dotenv
# .env 파일의 경로 설정
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# .env 파일 로드
load_dotenv(dotenv_path)


# 환경 변수 사용
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def get_secret():

    secret_name = "dev/de-3-2/fastapi"
    region_name = "ap-northeast-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    # Your code goes here.
    return json.loads(secret)



def connect_to_db():
    secrets = get_secret()
    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            user=secrets['username'],
            password=secrets['password'],
            dbname=secrets['dbname']
        )
        print("Successfully connected to the database!")
        return connection
    except Exception as e:
        print(f"Error while connecting to the database: {e}")
        return None

