import pickle
from typing import Any, List, Optional


class RedisClient:
    def __init__(self, host: str = "redis", port: int = 6379):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        import redis

        self.client = redis.Redis(host=self.host, port=self.port)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        if not self.client:
            self.connect()
        self.client.set(key, pickle.dumps(value), ex=ex)

    def get(self, key: str) -> Optional[Any]:
        if not self.client:
            self.connect()
        raw = self.client.get(key)
        return pickle.loads(raw) if raw is not None else None

    def keys(self, pattern: str) -> List[str]:
        if not self.client:
            self.connect()
        return [key.decode("utf-8") for key in self.client.keys(pattern)]