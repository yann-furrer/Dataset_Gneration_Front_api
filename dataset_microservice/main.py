import uvicorn
import os
import sys
import json 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Header, HTTPException, status, Depends, Request

from generator.webconfig_generator import WebConfigGenerator
from dataset_sample_generation import datasetSampleGeneration
from utils.faker_handler import FakerHandler
from generator.rules_generator import RulesGenerator

load_dotenv()


API_KEY = os.getenv("API_KEY")  # À changer/environner en production !


# Dépendance qui vérifie la clé reçue
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key invalide"
        )


# Instanciation de la classe qui gère les types fakers
faker_handler = FakerHandler()

app = FastAPI()


@app.get("/")
async def read_root():
    return {"msg": "Accès autorisé"}


@app.get("/pinged_microservice")
async def ping_microservice():
    return {"message": "pong"}


@app.get("/dataset_microservice", dependencies=[Depends(verify_api_key)])
async def get_dataset():
    return JSONResponse(
        {
            "[info]": "Welcome to this API, it is a micro service for generating datasets config"
        }
    )


@app.post("/dataset_sample", dependencies=[Depends(verify_api_key)])
async def dataset_sample(request: Request):
    body = await request.json()
    user_prompt = body.get("user_prompt", None)
    if user_prompt is None:
        return JSONResponse({"error": "user_prompt is required"}, status_code=400)
    dataset_sample_class = datasetSampleGeneration()
    dataset_sample = await dataset_sample_class.generate_sample(user_prompt=user_prompt)
    return JSONResponse({"dataset_sample": dataset_sample})


@app.post("/generate_webconfig", dependencies=[Depends(verify_api_key)])
async def generate_webconfig(request: Request):
    body = await request.json()
    client_id = body.get("client_id", None)
    json_sample = body.get("json_sample", None)
    print(json_sample)
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="client_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    webconfig_class = WebConfigGenerator(client_id=client_id)
    dataset_config = await webconfig_class.build_schema(input_data=json_sample)
    return JSONResponse(dataset_config)


##################### Routes pour la gestion des règles
@app.post("/generate_rules", dependencies=[Depends(verify_api_key)])
async def generate_rules(request: Request):
    body = await request.json()
    client_id = body.get("client_id", None)
    user_prompt = body.get("user_prompt", None)
    dataset_id = body.get("dataset_id", None)
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="client_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif len(user_prompt) < 50:
        raise HTTPException(
            status_code=400,
            detail="user_prompt is too short",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif len(user_prompt) > 1500:
        raise HTTPException(
            status_code=400,
            detail="user_prompt is too long",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Instanciation du générateur de règles
    rules_generator = RulesGenerator()

    # Récupération et parsing du YAML (attention à la signature des méthodes)
    yaml_config = rules_generator.get_yaml_config_file_by_id(
        user_id=client_id, dataset_id=dataset_id
    )
    # On suppose que get_yaml_config_file_by_id retourne déjà le YAML à parser
    rules_generator.parse_yaml_config( yaml_config=rules_generator.yaml_config)
    print(rules_generator.yaml_config)
    # Génération des règles
    rules = await rules_generator.generate_rules(user_prompt=user_prompt)

    # Nettoyage (éviter les triples quotes inutiles, par exemple)
    rules = rules.replace("```json", "")
    rules = rules.replace("```", "")

    return JSONResponse({"rules": json.loads(rules)})

##################### Routes pour la gestion des types de données Faker


@app.get("/faker_name_list/{user_id}", dependencies=[Depends(verify_api_key)])
async def get_faker_list(user_id: str):
    """
    Retourne la liste des types de données Faker disponibles sans le contenu.
    """
    faker_types = faker_handler.get_grouped_faker_types_by_client(client_id=user_id)
    print("faker_types:", faker_types)
    return JSONResponse(faker_types)


@app.get("/faker_name_list_front/{user_id}", dependencies=[Depends(verify_api_key)])
async def get_faker_list(user_id: str):
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


@app.get(
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


@app.put("/insert_faker_type", dependencies=[Depends(verify_api_key)])
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


@app.patch("/update_faker_type", dependencies=[Depends(verify_api_key)])
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


@app.delete(
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
    if response == True:  # Retournne True si la suppression a réussi
        return JSONResponse({"message": "Faker type deleted successfully"})
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting faker content not exist or already deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/get_sum_of_faker_type")
async def get_sum_of_faker_type(client_id: str):
    """
    Retourne la liste des valeurs de données Faker disponibles pour un type donné.
    """
    faker_types = faker_handler.count_documents(filte_dict={"client_id": client_id})
    print("faker_types:", faker_types)
    return JSONResponse(faker_types)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000, log_level="info")
