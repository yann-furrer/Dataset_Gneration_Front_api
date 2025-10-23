from fastapi.security import HTTPBearer
from fastapi import APIRouter, HTTPException, Request, Body
from core.dataset_config.dataset_config_update import (
    core_check_dataset_config_is_valid,
    core_insert_dataset_config_and_rules_config_info,
)
from core.checking import core_select_user_id_from_api_key

router = APIRouter()
security = HTTPBearer()

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
# ==============================================================


@router.post(
    "/dev/check_dataset_config_is_valid",
    summary="Vérifie si le dataset config est valide",
    description=(
        "Cette route permet de vérifier si le dataset config est valide"
        "Le `api_key` est requis pour accéder à cette route."
        "Le paramètre `yaml_content` est requis et doit contenir un dictionnaire de données."
        "Il représente le contenu YAML converti en JSON."
    ),
    tags=["dev"],
    responses={
        200: {
            "description": "Requête réussie — le dataset config est valide.",
            "content": {
                "application/json": {
                    "examples": {  # <--- ✅ "examples" au pluriel
                        "Cas valide": {
                            "summary": "Dataset correct",
                            "description": "Tous les champs sont conformes.",
                            "value": {
                                "message": "Dataset config is valid",
                                "is_valid": True,
                            },
                        },
                        "Cas invalide": {
                            "summary": "Dataset incorrect",
                            "description": "Certaines règles sont invalides.",
                            "value": {
                                "isvalid": False,
                                "error": [
                                    "Dans le champ 'join_3bis', le champ 'type' n'est pas valide, il ne peut être 'float', 'integer', 'string', 'boolean', 'date', 'array', 'object' ou 'id'."
                                ],
                            },
                        },
                    }
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
async def check_dataset_config_is_valid(
    api_key: str,
    yaml_content: dict = Body(
        ..., description=" dataset configuration convertie en json"
    ),
    end_format: str = Body(..., description="format du fichier yaml"),
):
    """
    Vérifie si le dataset config est valide
    """
    # body = await request.json()
    # data_config_json = body.get("yaml_content", None)
    # Problème il faut que le format di fochier influe sur la
    # valdiité du yaml_content
    end_format = end_format.lower()
    user_id = core_select_user_id_from_api_key(api_key)
    result_request = core_check_dataset_config_is_valid(
        yaml_content, user_id, end_format
    )
    return result_request


@router.post("/dev/create_dataset_config")
async def create_dataset_config(
    request: Request,
    api_key: str,
) -> dict:
    """
    Ajoute une nouvelle dataset config
    """
    body = await request.json()
    yaml_content = body.get("yaml_content", None)
    if None in [yaml_content]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_insert_dataset_config_and_rules_config_info(
        api_key, yaml_content
    )

    if result_request[0]:
        return {"message": "Dataset config created!", "dataset_id": result_request[1]}


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `RULESCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `DATASETCONFIG` n'est possible.
# ==============================================================
