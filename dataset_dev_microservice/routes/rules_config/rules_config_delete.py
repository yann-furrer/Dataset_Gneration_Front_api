from fastapi.security import HTTPBearer
from fastapi import APIRouter
from core.rules_config.rules_config_delete import core_delete_rules_config_by_rules_id


router = APIRouter()
security = HTTPBearer()


@router.delete(
    "/dev/delete_rules_config",
    summary="Supprime les configurations de règles associées à un utilisateur",
    description=(
        "Cette route permet de supprimer les configurations de règles associées à un utilisateur"
        "Le `api_key` est requis pour accéder à cette route."
        "Le paramètre `rules_id` est requis et doit contenir un identifiant de règles."
    ),
    tags=["dev"],
    responses={
        200: {
            "description": "Requête réussie — les configurations de règles associées à un utilisateur ont été supprimées.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Rules config 0166f009f410461bb6de45688525ea8c deleted!"
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
async def delete_rules_config(
    api_key: str,
    rules_id: str,
) -> dict:
    request: bool = core_delete_rules_config_by_rules_id(rules_id, api_key)
    if request:
        return {"message": f"Rules config {rules_id} deleted!"}
