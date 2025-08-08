from fastapi.responses import JSONResponse
import os
import sys
import json
import uuid
import httpx
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.s3_handle import S3Manager

from core.queue_config import send_message_to_celery_queue, TaskSchema
from core.checking import get_session_token

# import pour la table dataset config
from core.dataset import (
    get_dataset_config_info,
    get_dataset_config_historical_offset,
    insert_dataset_config_and_rules_config_info,
    select_dataset_config_and_rules_config,
    select_yaml_content_dataset_config_name
)

# import pour la table Dataset
from core.dataset import (
    inserting_dataset_info,
    select_dataset_for_historical,
    update_finished_dataset,
    update_status_dataset,
    delete_dataset_historical,
    get_dataset_config_name_by_user_id
)

# import faket tpye utils
from utils.faker_type_utils import extract_all_faker_types

load_dotenv()


MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL")
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL",None)
print("MICRO_SERVICE_URL:", MICRO_SERVICE_URL)
if MICRO_SERVICE_URL is None:
    raise ValueError("MICRO_SERVICE_URL is not set in the environment variables.")


# Load faker name lsit
with open("./utils/faker_list.json", "r") as f:
    faker_list = json.load(f)
    set_faker_list = set(faker_list)

router = APIRouter()
security = HTTPBearer()
s3_manager = S3Manager()
# cette route ne génère pas de dataset mais elle permet de sauvegarder la configuration du dataset
# pour l'utilisateur
# pas besoinde vérifier le quota de l'utilisateur car il n'y a pas de génération de dataset


# cette route permet de récupérer la configuration du dataset
# elle ne génère pas de dataset donc pas besoin de vérifier le quota de l'utilisateur


@router.get("/dataset/get_dataset_config")
async def get_dataset(request: Request, userId: str = Depends(get_session_token)):
    """
    Get dataset config
    """
    body = await request.json()
    datasetId = body.get("datasetId", "")
    print("datasetId -->", datasetId)
    if datasetId == "":
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = get_dataset_config_info(datasetId, userId)

    if result_request != None:
        result = {
            "id": result_request[0],
            "datasetId": result_request[1],
            "userId": result_request[2],
            "yamlName": result_request[3],
            "yamlContent": result_request[4],
            "draftResult": result_request[5],
            "nbRows": result_request[6],
            "rulesid": result_request[7],
            "campaignid": result_request[8],
        }

        return result
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/dataset/get_dataset_historical")
async def get_dataset_historical(
    userId: str = Depends(get_session_token), page_number: int = -2
):
    """
    Get dataset
    """
    if page_number < 0:
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or superior to 0 or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # get_dataset_info
    result_request = select_dataset_for_historical(userId, page_number)
    if result_request != False:
        for item in result_request:
            if item["status"] == "success":
                print("item -->", item)
                item.update(
                    {
                        "S3_URL": s3_manager.generate_presigned_url(
                            item["clientId"], item["datasetNameSystem"]
                        )
                    }
                )
                del item["clientId"]
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete("/dataset/delete_dataset_historical")
async def delete_dataset_historical_route(
    config_system_name: str, datasetId: str, userId: str = Depends(get_session_token)
):
    """
    Delete dataset form his s3 bucket
    """
    delete_result = s3_manager.delete_s3_file(userId, config_system_name)
    print("delete_result -->", delete_result)
    if delete_result == True:
        print("delete_result 2 -->", delete_result)
        print("datasetId -->", datasetId)
        print("userId -->", userId)
        delete_db_repsonse = delete_dataset_historical(datasetId, userId)

        if delete_db_repsonse == True:
            return {"message": "Dataset deleted!"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Error while deleting dataset",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/dataset/get_dataset_config_historical")
# Le -2 permet de créer une erreur si l'utilisateur n'a pas fournit de page number
async def get_dataset_config_historical(
    userId: str = Depends(get_session_token), page_number: int = -2
):
    """
    Get dataset config
    """
    print("page_number -->", page_number)
    if type(page_number) != int:
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if page_number < 0:
        raise HTTPException(
            status_code=400,
            detail="page_number must be a positive integer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result_request = get_dataset_config_historical_offset(userId, page_number)

    if result_request != None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

    print("yamlName", yamlName)
    print("client_id", client_id)
    print("end_format", end_format)
    print("yaml_content", yamlContent)
    print("dataset_config_id", dataset_config_id)
    print("nbRows", nbRows)

    draftResult = {"test": "test"}
    if any(value == None for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # a faire
    result_request = insert_dataset_config_and_rules_config_info(
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
    function = body.get(
        "function", "preprocessing_generation"
    )  # description of the function to be executed on the celery queue
    body_value_list = [userId, end_format, yamlContent, dataset_config_id, nbRows]
    # faker_name_dict = body.get("faker_name_dict" , [])
    # print("--> faker_name_dict",faker_name_dict)

    faker_client_list = []
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MICRO_SERVICE_URL}/faker_name_list_front/{userId}",
            headers={"X-API-KEY": os.getenv("API_KEY")},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        else:
            faker_client_list = response.json()

    # requete pour recuperer le nom des fakers disponibles pour le client
    # pour que le set gloabal reste inchangé
    set_faker_list_copy = set_faker_list.copy()
    set_faker_list_copy.update(
        faker_client_list
    )  # list globale des noms de fonctions fakers client + de base
    faker_name_dict: list = extract_all_faker_types(yamlContent)

    missing_value = [elem for elem in faker_name_dict if elem not in set_faker_list]
    if missing_value != []:
        raise HTTPException(
            status_code=400,
            detail="Error while chechking faker name. A faker name is not exist add it to the faker_list.json file on a front missing_value : "
            + str(missing_value),
            headers={"WWW-Authenticate": "Bearer"},
        )

    print("success")

    inserting_dataset_info(
        dataset_row_id,
        dataset_config_id,
        userId,
        campaignid,
        "waiting",
        nbRows,
        dataset_name,
    )
    draftResult = {"test": "test"}
    if any(value == None for value in body_value_list):
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
            faker_name_dict=faker_name_dict,
            request_type="api",
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

    if result_request != None:
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
    datasetId = body.get("datasetId", None)
    if datasetId == None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result_request = update_status_dataset(datasetId, body.get("status", "unknown"))

    if result_request == True:
        return {"message": "Dataset updated !"}
    else:
        return HTTPException(
            status_code=400,
            detail="Error while updating dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/dataset/get_config_info")
async def get_config_info(datasetId: str, userId: str = Depends(get_session_token)):
    """
    Get dataset config
    """
    if datasetId == None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = select_dataset_config_and_rules_config(datasetId, userId)
    print("result_request -->", result_request)
    if result_request is not None:
        return result_request

# recup le contenue du yaml et ressort les variables 
@router.get("/rules/get_yaml_content_by_dataset_config_id")
async def get_yaml_content_by_dataset_config_id( datasetId: str, userId: str = Depends(get_session_token)):
    print("datasetId -->", datasetId)
    response = select_yaml_content_dataset_config_name(datasetId, userId)
    print(response)
    return JSONResponse(response)

@router.get("/rules/get_dataset_config_name_list")
async def get_dataset_config_name_list(userId: str = Depends(get_session_token)):
    type_dict = get_dataset_config_name_by_user_id(userId)
    return JSONResponse(type_dict)

# genère les règles de validation pour le dataset sample
@router.post("/rules/generate_rules")
async def generate_rules(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    user_prompt = body.get("user_prompt", None)
    dataset_id = body.get("dataset_id", None)

    if not user_prompt:
        raise HTTPException(
            status_code=400,
            detail="user_prompt is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
