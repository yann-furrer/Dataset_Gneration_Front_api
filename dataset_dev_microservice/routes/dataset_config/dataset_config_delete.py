
from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
)
from core.dataset_config.dataset_config_delete import core_delete_dataset_config_and_rules_config_by_user_id
router = APIRouter()
security = HTTPBearer()

@router.delete("/dev/delete_config", description="Supprime un configuration de dataset et ses confuguration de règles associés")
async def create_dataset_config(
    
    api_key: str,
    dataset_config_id :str
):
    core_delete_dataset_config_and_rules_config_by_user_id(dataset_config_id, api_key, dataset_config_id)

    return {"message": "Config deleted!"}

