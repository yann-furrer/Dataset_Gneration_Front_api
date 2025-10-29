from fastapi.params import Body
from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, Request
from core.rules_config.rules_config_update import core_insert_or_update_rules_config
from core.checking import (
    core_select_user_id_from_api_key,
)
import uuid
from core.rules_utils import RulesUtils
router = APIRouter()
security = HTTPBearer()

@router.put("/dev/create_rules_config", summary="Ajoute une nouvelle configuration de règles", description=(
    "Cette route permet d'ajouter une nouvelle configuration de règles"
    "Le `api_key` est requis pour accéder à cette route."
    "Le paramètre `rules_content` est requis et doit contenir un dictionnaire de données."
    "Le paramètre `dataset_config_id` est requis et doit contenir un identifiant de dataset config."
),
               tags=["dev"],
               responses={
                   200: {
                       "description": "Requête réussie — la configuration de règles a été ajoutée.",
                       "content": {
                           "application/json": {
                               "example": {
                                   "message": "Rules config created!",
                                   "rules_id": "0166f009f410461bb6de45688525ea8c",
                               }
                           }
                       }
                   },
                       400: {
                           "description": "API Key invalide",
                           "content": {
                               "application/json": {
                                   "example": {"detail": "Invalid API key"}
                               }
                           }
                       },
                       500: {
                           "description": "Erreur interne du serveur.",
                           "content": {
                               "application/json": {"example": {"detail": "Internal Server Error"}}
                           },
                       },
                })  
async def create_rules_config(
    request: Request,
    api_key: str,
    rules_content: list = Body(..., description="Contenu YAML converti en objet JSON"),
    dataset_config_id: str = Body(..., description="Identifiant de la configuration de dataset"),
) -> dict:
    body = await request.json()

    # rules_content = body.get("rules_content", None)
    # data_config_id = body.get("dataset_config_id", None)
    user_id = core_select_user_id_from_api_key(api_key)
    rules_id = str(uuid.uuid4().hex) if body.get("rules_id", None) is None else body.get("rules_id")
    rules_utils = RulesUtils(rules_content, rules_id, dataset_config_id, api_key)

    rules_check : list = rules_utils.check_rules()
    if None in [rules_content, user_id, dataset_config_id]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if len(rules_check) > 0:
        raise HTTPException(
            status_code=404,
            detail={"message": "Error while checking rules", "errors": rules_check},
            headers={"WWW-Authenticate": "Bearer"},
        )
    response = core_insert_or_update_rules_config(
        rules_id=rules_id,
        user_id=user_id,
        rules_name="rules_name",
        rules_content=rules_content,
        dataset_config_id=dataset_config_id,
    )
    print("api_key -->", api_key)
    if response is True:
        return {"message": "Rules config created!", "rules_id": rules_id}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while creating rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
