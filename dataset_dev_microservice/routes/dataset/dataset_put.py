from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
    Depends,
)
from database.redis.redis_config import RedisManager
from core.checking import core_check_server_token

router = APIRouter()
security = HTTPBearer()

Redis = RedisManager()


@router.put("/server/update_pourcentage")
async def update_pourcentage(
    process_id: str,
    server_token=Depends(core_check_server_token),
):
    data = Redis.get(process_id)
    data["current_rows"] = int(data["current_rows"]) + 25000
    data["pourcentage"] = (
        (data["current_rows"] or 1) / int(data["nb_rows"]) * 100
    )  # avoid ZeroDIvisionError
    if data["pourcentage"] >= 100:  # Le dataset est généré

        Redis.delete(process_id)
        return {
            "status": "finish",
            "progess": 1,
            "pourcentage": 100,
        }
    print(data, flush=True)
    Redis.set_value(process_id, data)
    return {
        "status": data["status"],
        "progess": data["pourcentage"] / 100,
        "pourcentage": data["pourcentage"],
    }
