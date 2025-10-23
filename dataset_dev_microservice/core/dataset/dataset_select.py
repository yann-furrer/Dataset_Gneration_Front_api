import os
import sys
from fastapi import HTTPException
from core.s3_handle import S3Manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# dataset et s3
from database.queries.dataset.dataset_select import (
    select_all_s3_url_from_dataset,
    select_dataset_config,
    select_dataset_historical_offset,
    select_yaml_and_rules_content_by_dataset_config_id,
)

# dataset config
from database.queries.dataset.dataset_select import (
    select_dataset_historical_config_offset,
)

# from fastapi.security import HTTPBearer

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `S3 et DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================


s3_manager = S3Manager()


def core_select_all_s3_url_from_dataset(ownerId: str) -> dict:
    """
    Get S3 url
    """
    result_request = select_all_s3_url_from_dataset(ownerId)

    if result_request is None:
        raise HTTPException(
            status_code=400,
            detail="Error while getting S3 url datasetId not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result_request

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================
# get_dataset_config_info
def core_select_dataset_config(datasetId: str, userId: str) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_config(datasetId, userId)
    print("result_request s3 -->", result_request)
    if result_request != None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def select_dataset_for_historical(userId: str, offset: int) -> dict:
    result_request = select_dataset_historical_offset(userId, offset)
    data_dict = [
        {
            "id": item[0],
            "nbRows": item[1],
            "datasetConfigId": item[2],
            "clientId": item[3],
            "campaignId": item[4],
            "status": item[5],
            "FinishedAt": item[6],
            "TimeToGenerate": item[7],
            "datasetName": item[8],
            "datasetNameSystem": item[9],
        }
        for item in result_request
    ]
    return data_dict


def select_dataset_config_and_rules_config(datasetId: str, userId: str) -> dict:
    result_request = select_yaml_and_rules_content_by_dataset_config_id(
        datasetId, userId
    )
    if (
        result_request == False
        or result_request == None
        or result_request["yamlContent"] == []
    ):
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config or rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result_request


# get_dataset_config_historical_offset
def core_select_dataset_historical_config_offset(userId: str, offset: int) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_historical_config_offset(userId, offset)
    

    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail=f"Error while getting dataset config maybe offset is too high {offset}",
            headers={"WWW-Authenticate": "Bearer"},
        )
