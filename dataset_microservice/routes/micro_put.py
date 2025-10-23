import os 
from utils.pg_db_provider import select_user_id_from_token
from fastapi.responses import JSONResponse
from utils.faker_handler import FakerHandler
from fastapi import Depends, APIRouter, HTTPException, Header, status, Request
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()
faker_handler = FakerHandler()


API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# Dépendance qui vérifie la clé reçue
def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key invalide"
        )


@router.put("/dev/insert_faker_type",
    summary="Ajoute un type faker de la base de données",
    description=(
        "Cette route permet d'ajouter un type faker de la base de données"
        "La 'api_key' est requis pour accéder à cette route."
        "Le paramètre 'faker_list' est requis et doit contenir une liste de valeurs Faker. format []"
        "Le paramètre 'faker_name' est requis et doit contenir le nom du type faker"
    ),
    tags=["dev"],
    responses={
        200: {
            "description": "Requête réussie — la liste des types Faker est renvoyée.",
            "content": {"application/json": {"example": {"message": "Faker type inserted successfully id : 12038908223" }}},
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
    }
)
async def insert_faker_type_dev(request: Request, api_key: str):
 
    body = await request.json()
    faker_list :list = body.get("faker_list", None)
    faker_name : str = body.get("faker_name", None)
    user_id = select_user_id_from_token(api_key)
    #Problème  # supprimer les accents
    if user_id is None or faker_name is None or isinstance(faker_list, list) is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="faker_name or faker_list is required"
        )
    
    #  Pour l'instant on renvois l'intégralité de la liste de valeurs contenant les différents types de données Faker
    #  Dans l'avenir on comparera les valeurs avec les types de données disponibles sur MongoDB
    response = await faker_handler.insert_faker_type_on_mongo_db(
        faker_type_name=faker_name, faker_list=faker_list, client_id=user_id
    )
    print("response : ", response)
    if response[0]:
        return JSONResponse(
            {"message": "Faker type inserted successfully id : " + response[1]}
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting faker type maybe the content is the same as the previous one",
            headers={"WWW-Authenticate": "Bearer"},
        )



@router.put("/insert_faker_type", dependencies=[Depends(verify_api_key)])
async def insert_faker_type(request: Request):
    body = await request.json()
    faker_list = body.get("faker_list", None)
    faker_name = body.get("faker_name", None)
    client_id = body.get("client_id", None)

    #  Pour l'instant on renvois l'intégralité de la liste de valeurs contenant les différents types de données Faker
    #  Dans l'avenir on comparera les valeurs avec les types de données disponibles sur MongoDB
    response = await faker_handler.insert_faker_type_on_mongo_db(
        faker_type_name=faker_name, faker_list=faker_list, client_id=client_id
    )
    print("response : ", response)
    if response[0]:
        return JSONResponse(
            {"message": "Faker type inserted successfully id : " + response[1]}
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting faker type maybe the content is the same as the previous one",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.patch("/update_faker_type", dependencies=[Depends(verify_api_key)])
async def update_faker_type(request: Request):
    body = await request.json()
    faker_type_id = body.get("faker_type_id", None)
    faker_list = body.get("new_faker_list", None)
    client_id = body.get("client_id", None)

    #  Pour l'instant on renvois l'intégralité de la liste de valeurs contenant les différents types de données Faker
    #  Dans l'avenir on comparera les valeurs avec les types de données disponibles sur MongoDB
    response = faker_handler.update_faker_type_on_mongo_db(
        faker_id=faker_type_id, new_faker_list=faker_list, client_id=client_id
    )
    print("response : ", response)
    if response:
        return JSONResponse({"message": "Faker type inserted successfully"})
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting faker type maybe the content is the same as the previous one",
            headers={"WWW-Authenticate": "Bearer"},
        )