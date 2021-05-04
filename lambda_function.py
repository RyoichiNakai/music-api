from __future__ import print_function
import boto3
import uuid
from decimal import Decimal

# DynamoDbの接続先

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music-api')

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

def return200(res_body):
    return{
        'statusCode': 200,
        'body': json.dumps(
            res_body,
            default=decimal_default_proc
        )
    }

def return400(message_str):
    body = {
        'errorMessage': message_str
    }
    return{
        'statusCode': 400,
        'body': json.dumps(body)
    }

def get_songs():
    # 引数はリクエストパラメータをstr型のListで受け取る
    # それをテーブルで探索する
    return

def get_albums():
    # 引数はリクエストパラメータをstr型のListで受け取る
    # それをテーブルで探索する
    return

def create_album():
    # uuidの初期化
    new_uuid = uuid.uuid4().hex
    return

def create_song():
    # uuidの初期化
    new_uuid = uuid.uuid4().hex
    # print(type(new_uuid))
    
    return

def create_artist():
    # uuidの初期化
    new_uuid = uuid.uuid4().hex
    return

def lambda_handler(event, context):
    print(event)

    # ルーティングの決定
    if event['httpMethod'] == 'GET':
        if event['resource'] == '/songs':
            get_songs()
        elif event['resource'] == '/albums':
            get_albums()
    elif event['httpMethod'] == 'POST':
        if event['resource'] == '/songs':
            create_song()
        elif event['resource'] == '/albums':
            create_album()
        elif event['resource'] == '/artists':
            create_artist()

if __name__ == '__main__':
    create_song()