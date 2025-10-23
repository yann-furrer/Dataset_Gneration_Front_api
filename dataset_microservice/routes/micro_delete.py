import os
from utils.pg_db_provider import select_user_id_from_token
from fastapi.responses import JSONResponse
from utils.faker_handler import FakerHandler

from fastapi import Depends, APIRouter, HTTPException, Header, status


API_KEY = os.getenv("API_KEY")  # À changer/environner en production !


# Dépendance qui vérifie la clé reçue
def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key invalide"
        )


router = APIRouter()
faker_handler = FakerHandler()


@router.delete(
    "/delete_faker_type/{faker_type_id}/{client_id}",
    dependencies=[Depends(verify_api_key)],
)
async def delete_faker_type(client_id: str, faker_type_id: str):
    if not client_id and not faker_type_id:
        raise HTTPException(
            status_code=400,
            detail="client_id or faker_type_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response = faker_handler.delete_faker_type_on_mongo_db(faker_type_id, client_id)
    if response:  # Retournne True si la suppression a réussi
        return JSONResponse({"message": "Faker type deleted successfully"})
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting faker content not exist or already deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete(
    "/dev/delete_faker_type/",
    summary="Supprime un type faker de la base par son id",
    description=(
        "Cette route permet de supprimer un type faker de la base de données par son id"
    ),
    tags=["dev"],
    responses={
        200: {
            "description": "Requête réussie — la liste des types Faker est renvoyée.",
            "content": {"application/json": {"example": {"message": "Faker type deleted successfully"}}},
        },
        401: {
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
async def delete_faker_type_dev(faker_type_id: str, api_key: str):
    user_id = select_user_id_from_token(api_key)
    if not user_id and not faker_type_id:
        raise HTTPException(
            status_code=400,
            detail="client_id or faker_type_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    response = faker_handler.delete_faker_type_on_mongo_db(faker_type_id, user_id)
    if response == True:  # Retournne True si la suppression a réussi
        return JSONResponse({"message": "Faker type deleted successfully"})
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting faker content not exist or already deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
