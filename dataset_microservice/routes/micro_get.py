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
faker_handler = FakerHandler()
router = APIRouter()



@router.get("/")
async def read_root():
    return {"msg": "Accès autorisé à l'API micro service"}


@router.get("/pinged_microservice")
async def ping_microservice():
    return {"message": "pong"}


@router.get("/dataset_microservice", dependencies=[Depends(verify_api_key)])
async def get_dataset():
    return JSONResponse(
        {
            "[info]": "Welcome to this API, it is a micro service for generating datasets config"
        }
    )



@router.get("/faker_name_list/")
async def get_faker_list(api_key: str):
    """
    Retourne la liste des types de données Faker disponibles sans le contenu.
    """
    print("api_key -->", api_key)
    user_id = select_user_id_from_token(api_key)
    print("user_id -->", user_id)
    faker_types = faker_handler.get_grouped_faker_types_by_client(client_id=user_id)
    return JSONResponse(faker_types)



@router.get("/dev/faker_name_list",
    summary="Retourne le nom et le faker_id de l'ensemble des fakers de l'utilisateur ",        
    tags=["dev"],
    description=(
        "Cette route permet de récupérer le nom et le faker_id de l'ensemble des fakers de l'utilisateur"
        "Le `api_key` est requis pour accéder à cette route."
    ),
            responses={
        200: {
            "description": "Requête réussie — la liste des types Faker est renvoyée.",
            "content": {
                "application/json": {
                    "example": [
                        {"faker_type_name": "first_name", "faker_type_id": "fk_1a2b3c"},
                        {"faker_type_name": "email", "faker_type_id": "fk_4d5e6f"},
                        {"faker_type_name": "address", "faker_type_id": "fk_7g8h9i"}
                    ]
                }
            },
        },
        401: {
            "description": "API Key invalide",
            "content": {
                "application/json": {"example": {"detail": "Invalid API key"}}
            },
        },
        500: {
            "description": "Erreur interne du serveur.",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },        )
async def get_faker_list_brent(api_key: str):
    """
    Retourne la liste des types de données Faker disponibles sans le contenu.
    """
    print("api_key -->", api_key)
    user_id = select_user_id_from_token(api_key)
    print("user_id -->", user_id)
    faker_types = faker_handler.find_many(filter_dict={"client_id": user_id}, projection_dict={"_id": 0, "faker_type_name": 1, "faker_type_id": 1})
    return JSONResponse(faker_types)



@router.get("/faker_name_list_front/{user_id}", dependencies=[Depends(verify_api_key)])
async def get_faker_list_front(user_id: str):
    """
    Retourne la liste des des nom de fakerdisponibles pour le client.
    """
    faker_types = faker_handler.find_many(
        filter_dict={"client_id": user_id, "faker_type_name": {"$exists": True}},
        projection_dict={"_id": 0, "faker_type_name": 1},
    )
    faker_name_list = [
        item["faker_type_name"]
        for item in faker_types
        if "faker_type_name" in item and item["faker_type_name"] != ""
    ]
    return JSONResponse(faker_name_list)



@router.get(
    "/faker_content_list/{user_id}/{faker_type_id}",
    dependencies=[Depends(verify_api_key)],
)
async def get_faker_content_list(user_id: str, faker_type_id: str):
    """
    Retourne la liste des valeurs de données Faker disponibles pour un type donné.
    """
    faker_types = faker_handler.get_faker_type_on_mongo_db_by_client_id(
        filter_dict={"client_id": user_id, "faker_type_id": faker_type_id},
        projection_dict={"_id": 0, "list": 1},
    )
    return JSONResponse(faker_types)



@router.get("/get_sum_of_faker_type")
async def get_sum_of_faker_type(client_id: str):
    """
    Retourne la liste des valeurs de données Faker disponibles pour un type donné.
    """
    faker_types = faker_handler.count_documents(filte_dict={"client_id": client_id})
    print("faker_types:", faker_types)
    return JSONResponse(faker_types)



# @router.get("/dev/get_content_of_faker_type")
# async def get_content_of_faker_type(faker_type_id: str, api_key: str):
#     """
#     Retourne la liste des valeurs de données Faker disponibles pour un type donné.
#     """
#     user_id = select_user_id_from_token(api_key)
#     print("user_id -->", user_id)
#     faker_types = faker_handler.find_one(filter_dict={"faker_type_id": faker_type_id, "client_id": user_id}, projection={"_id": 0, "list": 1})
#     return JSONResponse(faker_types)