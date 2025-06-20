import os
import redis.asyncio as redis
from redis.exceptions import ConnectionError
from dotenv import load_dotenv

load_dotenv()

try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        db=0,
        decode_responses=True
    )
except ConnectionError as e:
    print("A problem occured while connecting to the redis server.")