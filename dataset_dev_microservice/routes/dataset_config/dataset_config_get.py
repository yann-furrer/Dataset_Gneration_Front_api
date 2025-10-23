from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
)
from core.dataset_config.dataset_config_select import (
    core_select_rules_config_by_dataset_config_id,
)

from core.checking import core_select_user_id_from_api_key


router = APIRouter()
security = HTTPBearer()


@router.get("/dev/get_rules_config_content")
async def get_rules_config_content(api_key: str, dataset_config_id: str):
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : rulesContent
    """
    user_id: str = core_select_user_id_from_api_key(api_key)
    rulesContent = core_select_rules_config_by_dataset_config_id(
        dataset_config_id, user_id
    )
    return rulesContent


# @router.get("/dev/get_all_rules_data")
# async def get_all_rules_data( api_key: str ,dataset_config_id: str):
#     """
#     Récupère le dataset config d'un user à partir du userId et du datasetConfigId
#     args : datasetConfigId, userId
#     return : rulesContent
#     """
#     # rajouter le created at plus tard quand la bdd sera mise à jour
#     user_id : str =core_select_user_id_from_api_key(api_key)
#     data = core_select_all_rules_data_by_dataset_config_id(dataset_config_id, user_id)
#     return data
