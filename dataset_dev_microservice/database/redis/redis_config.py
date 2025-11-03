import redis
import os
from fastapi import HTTPException
import json
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from utils.env_handle import load_env_from_file
load_env_from_file()
REDIS_URL = os.getenv("REDIS_URL")
class RedisManager:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_URL, decode_responses=True, password=None, ssl=True, ssl_cert_reqs="required")

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

redis_manager = RedisManager()
redis_manager.set_value("test", {"test": "test"})
