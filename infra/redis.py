import redis
from core.config import settings

# Use redis.from_url so REDIS_URL can be a full URI and support auth
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def set_idempotency(key: str, value: str, ttl=3600):
    redis_client.setex(key, ttl, value)


def get_idempotency(key: str):
    return redis_client.get(key)


def push_event(queue: str, payload: dict):
    redis_client.lpush(queue, str(payload))