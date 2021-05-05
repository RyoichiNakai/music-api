import boto3
from boto3.dynamodb.conditions import Key
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

def create_album(payload):
    # uuidの初期化
    new_uuid = uuid.uuid4().hex

    try:
        resp = table.query(
            IndexName="SK-Data_index",
            KeyConditionExpression=Key('sort_key').eq('artist_name') & Key('data').eq(payload['artist_name']) ,
        )
    except Exception as e:
        return return400(str(e))

    items = [
        {
            'partition_key': resp['Items'][0]['partition_key'], # 一意に決まるので[0]として問題なし
            'sort_key': 'album-{}'.format(new_uuid)
        },
        {
            'partition_key': 'album-{}'.format(new_uuid),
            'sort_key': 'album-name',
            'data': payload['name']
        },
        {
            'partition_key': 'album-{}'.format(new_uuid),
            'sort_key': 'album-genre',
            'data': payload['genre']
        }
    ]

    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
    except Exception as e:
        return return400(str(e))

    return return200({
        'message': 'Successfully! Add new record: id: album-{}, name: {}, genre: {}'.format(new_uuid, payload['name'], payload['genre'])
    })

def create_song(payload):
    # uuidの初期化
    new_uuid = uuid.uuid4().hex

    try:
        resp = table.query(
            IndexName="SK-Data_index",
            KeyConditionExpression=Key('sort_key').eq('artist_name') & Key('data').eq(payload['artist_name']) ,
        )
    except Exception as e:
        return return400(str(e))

    items = [
        {
            'partition_key': resp['Items'][0]['partition_key'], # 一意に決まるので[0]として問題なし
            'sort_key': 'song-{}'.format(new_uuid)
        },
        {
            'partition_key': 'song-{}'.format(new_uuid),
            'sort_key': 'song-artist_name',
            'data': payload['artist_name']
        },
        {
            'partition_key': 'song-{}'.format(new_uuid),
            'sort_key': 'song-name',
            'data': payload['name']
        },
        {
            'partition_key': 'song-{}'.format(new_uuid),
            'sort_key': 'song-release',
            'data': payload['release']
        }
    ]

    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
    except Exception as e:
        return return400(str(e))

    return return200({
        'message': 'Successfully! Add new record: id: song-{}, name: {}, release: {}, artist-name: {}'.format(new_uuid, payload['name'], payload['release'], payload['artist_name'])
    })

def create_artist(payload):
    # uuidの初期化
    new_uuid = uuid.uuid4().hex

    items = [
        {
            'partition_key': 'artist-{}'.format(new_uuid),
            'sort_key': 'artist_name',
            'data': payload['name'],
        },
        {
            'partition_key': 'artist-{}'.format(new_uuid),
            'sort_key': 'artist-{}'.format(new_uuid),
            'career_start': payload['career_start']
        }
    ]

    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    except Exception as e:
        return return400(str(e))

    return return200({
        'message': 'Successfully! Add new record: id: artist-{}, name: {}, career_start: {}'.format(new_uuid, payload['name'], payload['career_start'])
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
            return create_song(event['payload'])
        elif event['resource'] == '/albums':
            return create_album(event['payload'])
        elif event['resource'] == '/artists':
            return create_artist(event['payload'])

    return return400('bad request')
