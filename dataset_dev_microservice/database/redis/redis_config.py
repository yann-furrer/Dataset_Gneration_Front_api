import redis
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import json

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")


class RedisManager:
    def __init__(self):
        self.r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    def set_value(self, key: str, value: dict) -> None:
        if self.r is not None:
            self.r.set(key, json.dumps(value), ex=27000)
            

    def get(self, key: str) -> json:
        if self.r.get(key) is not None:
            try:
                return json.loads(self.r.get(key))
            except Exception as e:
                raise HTTPException (
                    status_code=400,
                    detail="Error while connecting to redis, process id not found"+ str(e),
                )
        else:
            return None

    def delete(self, key: str) -> None:
        if self.r is not None:
            self.r.delete(key)
