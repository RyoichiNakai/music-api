from __future__ import print_function
import boto3
import uuid
import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

# DynamoDbの接続先

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('demo_test')

# ElastiCacheの設定

elasticache_config_endpoint = "clusterforlambdatest.4agk2e.cfg.apne1.cache.amazonaws.com:11211"
nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
nodes = map(lambda x: (x[1], int(x[2])), nodes)
memcache_client = HashClient(nodes)


def get_person(id, name):
    response = table.get_item(
        Key={
            'test_id': id,
            'name': name
        }
    )
    return response['Item']


def get_persons():
    response = table.scan()
    return response['Items']


def lambda_handler(event, context):
    """
    This function puts into memcache and get from it.
    Memcache is hosted using elasticache
    """
    # Create a random UUID... this will be the sample element we add to the cache.
    uuid_inserted = uuid.uuid4().hex
    # Put the UUID to the cache.
    memcache_client.set('uuid', uuid_inserted)
    # Get item (UUID) from the cache.
    uuid_obtained = memcache_client.get('uuid')
    if uuid_obtained.decode("utf-8") == uuid_inserted:
        # this print should go to the CloudWatch Logs and Lambda console.
        print ("Success: Fetched value %s from memcache" %(uuid_inserted))
    else:
        raise Exception("Value is not the same as we put :(. Expected %s got %s" %(uuid_inserted, uuid_obtained))

    return "Fetched value from memcache: " + uuid_obtained.decode("utf-8")