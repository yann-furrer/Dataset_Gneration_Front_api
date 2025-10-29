from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from core.checking import get_session_token, check_var_is_none
from dotenv import load_dotenv
import os
import sys
import json
import uuid 
import httpx
from utils.faker_type_utils import extract_all_faker_types
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

#dataset config 
from core.dataset.dataset_insert import (
    core_insert_dataset_config)

#dataset 
from core.dataset.dataset_insert import core_inserting_dataset_info
from core.dataset.dataset_update import update_finished_dataset, update_status_dataset
from core.queue_config import send_message_to_celery_queue, TaskSchema

router = APIRouter()
security = HTTPBearer()
load_dotenv()

# Load faker name lsit
with open("./utils/faker_list.json", "r") as f:
    faker_list = json.load(f)
    set_faker_list = set(faker_list)

MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL")
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
print("api key -->", API_KEY)
# MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL",None)
print("MICRO_SERVICE_URL:", MICRO_SERVICE_URL)
if MICRO_SERVICE_URL is None:
    raise ValueError("MICRO_SERVICE_URL is not set in the environment variables.")


# ------------------------------------------------------------------------------
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `dataset`
# ------------------------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement les datasets générés par le back.
#   - Aucune interaction avec `rulesoconfig` ici.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `datasetconfig` et `rulesoconfig`.
# ------------------------------------------------------------------------------


@router.post("/dataset/generate_dataset")
async def generate_dataset(request: Request, userId: str = Depends(get_session_token)):
    """
    generate_dataset

    """
    celery_queue_id = uuid.uuid4()
    dataset_row_id = uuid.uuid4()
    body = await request.json()
    dataset_name = body.get("dataset_name", "nom du dataset par defaut")
    end_format = body.get("end_format", None)
    yamlContent = body.get("yaml_content", None)
    rulesContent = body.get("rulesContent", None)
    dataset_config_id = body.get("dataset_config_id", None)
    campaignid = body.get(
        "campaignid", None
    )  # pour l'instant on ne prend pas en compte le campaignid
    nbRows = body.get("nbRows", 1)
    dataset_config_parent_id = body.get("dataset_parent_id", None)
    dataset_fields_list = body.get("dataset_fields_list", None)
    function = "preprocessing_generation"  # description of the function to be executed on the celery queue
    body_value_list = [userId, end_format, yamlContent, dataset_config_id, nbRows]
    # faker_name_dict = body.get("faker_name_dict" , [])
    # # print("--> faker_name_dict",faker_name_dict)

    # faker_client_list = []
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(
    #         f"{MICRO_SERVICE_URL}/faker_name_list_front/{userId}",
    #         headers={"X-API-KEY": os.getenv("API_KEY")},
    #     )
    #     if response.status_code != 200:
    #         raise HTTPException(status_code=response.status_code, detail=response.text)
    #     else:
    #         faker_client_list = response.json()

    # print("usefeeferId -->", userId)
    # # requete pour recuperer le nom des fakers disponibles pour le client
    # # pour que le set gloabal reste inchangé
    # set_faker_list_copy = set_faker_list.copy()
    # set_faker_list_copy.update(
    #     faker_client_list
    # )  # list globale des noms de fonctions fakers client + de base
    # faker_name_dict: list = extract_all_faker_types(yamlContent)

    # missing_value = [elem for elem in faker_name_dict if elem not in set_faker_list]
    # if missing_value != []:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Error while chechking faker name. A faker name is not exist add it to the faker_list.json file on a front missing_value : "
    #         + str(missing_value),
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )

    print("success")

    core_inserting_dataset_info(
        dataset_row_id,
        dataset_config_id,
        userId,
        campaignid,
        "waiting",
        nbRows,
        dataset_name,
    )
    draftResult = {"test": "test"}
    if any(value is None for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Ajout de la tache dans la queue rabbitmq
    send_message_to_celery_queue(
        TaskSchema(
            dataset_row_id=dataset_row_id,
            id=celery_queue_id,
            function=function,
            dataset_name=dataset_name,
            client_id=userId,
            end_format=end_format,
            yaml_content=yamlContent,
            rules=rulesContent,
            dataset_config=dataset_config_id,
            faker_name_dict=[],
            request_type="api",
            dataset_config_parent_id=dataset_config_parent_id,
            dataset_fields_list=dataset_fields_list
        )
    )
    return {"message": "Dataset {dataset_name} ajouter à queue !"}



@router.post("/dataset/update_finished_dataset")
# cette route est uniquement appellé par le back il faudra a terme verfier que c'est bien le back qui appelle
async def update_finished_dataset_info(request: Request):
    """
    update_finished_dataset

    """
    body = await request.json()
    datasetId = body.get("datasetId", None)
    dataset_name = body.get("dataset_name", None)
    status = body.get("status", "unknown")
    if None in [datasetId, dataset_name, status]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result_request = update_finished_dataset(
        dataset_name, datasetId, body.get("generationError", "0"), status
    )

    if result_request is not None:
        return {"message": "Dataset updated !"}
    else:
        return HTTPException(
            status_code=400,
            detail="Error while updating dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/dataset/update_dataset_status")
# cette route est uniquement appellé par le back il faudra a terme verfier que c'est bien le back qui appelle
async def update_dataset_status(request: Request):
    """
    update_dataset_status

    """
    body = await request.json()
    dataset_id = body.get("datasetId", None)
    check_var_is_none(dataset_id)
  

    result_request = update_status_dataset(dataset_id, body.get("status", "unknown"))

    if result_request is True:
        return {"message": "Dataset updated !"}
    else:
        return HTTPException(
            status_code=400,
            detail="Error while updating dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
    



# genère les règles de validation pour le dataset sample
@router.post("/rules/generate_rules")
async def generate_rules(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()

    user_prompt = body.get("user_prompt", None)
    dataset_id = body.get("dataset_id", None)
    check_var_is_none(user_prompt, dataset_id)
    

    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.post(
            f"{MICRO_SERVICE_URL}/generate_rules",
            headers={"X-API-KEY": os.getenv("API_KEY")},
            json={
                "client_id": userId,
                "user_prompt": user_prompt,
                "dataset_id": dataset_id,
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(response.json())

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `datasetconfig`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `rulesoconfig` ici.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `datasetconfig` et `rulesoconfig`.
# ==============================================================



@router.post("/dataset/save_dataset_config")
async def save_dataset_config_and_rules_config(
    request: Request, userId: str = Depends(get_session_token)
):
    """
    save_dataset_config2

    """
    body = await request.json()
    yamlName = body.get("yamlName", None)
    client_id = userId
    end_format = body.get("end_format", None)
    yamlContent = body.get("yaml_content", None)
    # rules = body.get("rules" , None)
    rulesId = body.get("rulesId", "idrulestest123")
    rulesName = body.get("rulesName", "rule nom")
    rulesContent = body.get("rulesContent", None)
    dataset_config_id = body.get("dataset_config_id", None)
    campaignid = body.get(
        "campaignid", None
    )  # pour l'instant on ne prend pas en compte le campaignid
    nbRows = body.get("nbRows", None)
    body_value_list = [
        yamlName,
        client_id,
        end_format,
        yamlContent,
        dataset_config_id,
        nbRows,
    ]

    # print("yamlName", yamlName)
    # print("client_id", client_id)
    print("end_format", end_format)
    # print("yaml_content", yamlContent)
    print("dataset_config_id", dataset_config_id)
    print("nbRows", nbRows)
    # print("xrulesContent", rulesContent)

    draftResult = {"test": "test"}
    check_var_is_none(body_value_list)
  

    # a faire
    result_request = core_insert_dataset_config(
        dataset_config_id,
        userId,
        yamlName,
        yamlContent,
        draftResult,
        nbRows,
        rulesId,
        rulesName,
        rulesContent,
        campaignid,
    )

    # Ajout de la tache dans la queue rabbitmq
    # send_message_to_celery_queue(TaskSchema(id=celery_queue_id, function="preprocessing_generation", dataset_name=dataset_name, client_id=client_id, end_format=end_format, yaml_content=yaml_content, rules=rules, dataset_config=dataset_config))
    return {"message": "GSave Config and Rules Config!"}


