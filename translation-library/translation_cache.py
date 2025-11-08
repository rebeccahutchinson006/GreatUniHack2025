import os
import redis
import json
import hashlib
from typing import Optional

class TranslationCache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = redis.from_url(
            redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        )
        self.default_ttl = 30 * 24 * 60 * 60  # 30 days
    
    def get(self, key: str) -> Optional[dict]:
        try:
            cached = self.redis_client.get(key)
            return json.loads(cached) if cached else None
        except (redis.RedisError, json.JSONDecodeError):
            return None
    
    def set(self, key: str, value: dict, ttl: Optional[int] = None):
        try:
            self.redis_client.setex(
                key, 
                ttl or self.default_ttl, 
                json.dumps(value)
            )
        except redis.RedisError:
            pass  # Fail silently for cache errors
    
    def clear(self, pattern: str = "*"):
        """Clear cache entries matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except redis.RedisError:
            pass