# core/redis_client.py

import redis.asyncio as redis_lib

redis = redis_lib.from_url(
    "redis://:Rhbgnjy2004@127.0.0.1:6379/0",
    decode_responses=True
)
