import boto3
import uuid
import json
from decimal import Decimal

# DynamoDbの接続先

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music-api')

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

def return200(res_body):
    return {
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
    return {
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

def create_artist(payload):
    # uuidの初期化
    new_uuid = uuid.uuid4().hex

    name = {
        'partition_key': 'artist-{}'.format(new_uuid),
        'sort_key': 'artist_name',
        'data': payload['name'],
    }
    career_start = {
        'partition_key': 'artist-{}'.format(new_uuid),
        'sort_key': 'artist-{}'.format(new_uuid),
        'career_start': payload['career_start']
    }

    try:
        with table.batch_writer() as batch:
            batch.put_item(Item=name)
            batch.put_item(Item=career_start)

    except Exception as e:
        return return400(str(e))

    return return200({
        'message': 'Successfully! Add new record: id: artist-{}, name: {}'.format(new_uuid, payload['name'])
    })

def lambda_handler(event, context):

    # ルーティングの決定
    if event['method'] == 'GET':

        if event['resource'] == '/songs':
            return get_songs()
        elif event['resource'] == '/albums':
            return get_albums()

    elif event['method'] == 'POST':

        if event['resource'] == '/songs':
            return create_song()
        elif event['resource'] == '/albums':
            return create_album()
        elif event['resource'] == '/artists':
            return create_artist(event['payload'])

    return return400('bad request')
