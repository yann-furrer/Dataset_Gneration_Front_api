from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
)
from core.dataset_config.dataset_config_select import (
    core_select_all_rules_data_by_dataset_config_id,
)
from core.checking import core_select_user_id_from_api_key

router = APIRouter()
security = HTTPBearer()


@router.get(
    "/dev/get_all_rules_data",
    summary="Récupère toutes les règles de configuration associées à un dataset config",
    description=(
        "Cette route permet de récupérer toutes les règles de configuration associées à un dataset config"
        "Le `api_key` est requis pour accéder à cette route."
        "Le paramètre `dataset_config_id` est requis et doit contenir un identifiant de dataset config."
    ),
    tags=["dev"],
    responses={
        200: {
            "description": "Requête réussie — les règles de configuration associées à un dataset config ont été récupérées.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "rulesId": "0166f009f410461bb6de45688525ea8c",
                            "rulesName": "New rule",
                        },
                        {
                            "rulesId": "0166f009f410461bb6de45688525ea8s",
                            "rulesName": "fre",
                        },
                    ]
                }
            },
        },
        400: {
            "description": "API Key invalide",
            "content": {"application/json": {"example": {"detail": "Invalid API key"}}},
        },
        500: {
            "description": "Erreur interne du serveur.",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def get_all_rules_data(api_key: str, dataset_config_id: str):
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : rulesContent
    """
    # rajouter le created at plus tard quand la bdd sera mise à jour
    user_id: str = core_select_user_id_from_api_key(api_key)
    data = core_select_all_rules_data_by_dataset_config_id(dataset_config_id, user_id)
    return data
