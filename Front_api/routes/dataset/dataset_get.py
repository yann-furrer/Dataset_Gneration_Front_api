from fastapi.responses import JSONResponse
import os
import sys

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from core.checking import get_session_token
from utils.s3_handle import S3Manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# import dataset
from core.dataset.dataset_select import (
    core_select_dataset_historical_offset,
    core_select_dataset_name_system_with_dataset_id,
)

# import dataset config
from core.dataset.dataset_select import (
    core_select_dataset_config,
    core_select_dataset_historical_config_offset,
    core_select_dataset_config_by_dataset_id,
    core_select_dataset_config_name_by_user_id,
    core_select_yaml_content_by_dataset_config_id,
    core_select_yaml_and_rules_content_by_dataset_config_id,
)

load_dotenv()
router = APIRouter()
security = HTTPBearer()
s3_manager = S3Manager()


# ------------------------------------------------------------------------------
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `datasetconfig`
# ------------------------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `rulesoconfig` ici.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `datasetconfig` et `rulesoconfig`.
# ------------------------------------------------------------------------------


@router.get("/dataset/get_dataset_config")
async def get_dataset(request: Request, datasetId :str ,  userId: str = Depends(get_session_token)):
    """
    Get dataset config
    """
    if datasetId == "":
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_select_dataset_config(datasetId, userId)

    if result_request is not None:
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


@router.get("/dataset/get_dataset_config_historical")
# Le -2 permet de créer une erreur si l'utilisateur n'a pas fournit de page number
async def get_dataset_config_historical(
    userId: str = Depends(get_session_token), page_number: int = -2
):
    """
    Get dataset config
    """
    print("page_number -->", type(page_number))
    print("userId -->", userId)
    if type(page_number) is not int:
        print("page_number is not int")
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if page_number < 0:
        print("page_number is not int2")

        raise HTTPException(
            status_code=400,
            detail="page_number must be a positive integer",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result_request = core_select_dataset_historical_config_offset(userId, page_number)
    print("result_request -->", result_request)
    if result_request is not None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )


# recup le contenue du yaml et ressort les variables
@router.get("/rules/get_yaml_content_by_dataset_config_id")
async def get_yaml_content_by_dataset_config_id(
    datasetId: str, userId: str = Depends(get_session_token)
):
    response = core_select_yaml_content_by_dataset_config_id(datasetId, userId)
    print(response)
    return JSONResponse(response)


@router.get("/rules/get_yaml_content_by_dataset_id")
async def get_dataset_config_by_dataset_id(
    datasetId: str, userId: str = Depends(get_session_token)
):
    print("datasetId -->", datasetId)
    response = core_select_dataset_config_by_dataset_id(datasetId, userId)
    print(response)

    return JSONResponse(response)


@router.get("/rules/get_dataset_config_name_list")
async def get_dataset_config_name_list(userId: str = Depends(get_session_token)):
    type_dict = core_select_dataset_config_name_by_user_id(userId)
    return JSONResponse(type_dict)


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
    result_request = core_select_yaml_and_rules_content_by_dataset_config_id(datasetId, userId)
    print("result_request -->", result_request)
    if result_request is not None:
        return result_request


# ------------------------------------------------------------------------------
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `dataset`
# ------------------------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement les datasets générés par le back.
#   - Aucune interaction avec `rulesoconfig` ici.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `datasetconfig` et `rulesoconfig`.
# ------------------------------------------------------------------------------


# A sécuriser
@router.get("/get_dataset_system_name")
async def get_dataset_system_name_of_dataset_config(datasetConfigId: str, userId: str):
    dataset_system_name: str = core_select_dataset_name_system_with_dataset_id(
        datasetConfigId, userId
    )
    if not dataset_system_name or not dataset_system_name:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse({"dataset_system_name": dataset_system_name})


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
    result_request = core_select_dataset_historical_offset(userId, page_number)
    if result_request:
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
