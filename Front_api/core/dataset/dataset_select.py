import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException
from core.checking import check_var_is_none
from utils.s3_handle import S3Manager

# dataset et s3
from database.queries.dataset import (
    select_dataset_historical_offset,
    select_all_s3_url_from_dataset,
    select_dataset_name_system_with_dataset_id,
)


# datasetConfig and rulesConfig
from database.queries.dataset import (
    select_dataset_config,
    select_yaml_and_rules_content_by_dataset_config_id,
    select_dataset_config_name_by_user_id,
    select_yaml_content_by_dataset_config_id,
    select_dataset_config_by_dataset_id,
    select_dataset_historical_config_offset,
)

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASETCONFIG` et `RULESCONFIG`.
# ==============================================================


def get_type_and_name_from_yaml_content(
    yamlContent: dict, type_dict: dict = None
) -> tuple:
    """
    Récupère les types et noms des champs à partir du contenu YAML.
    Retourne un tuple contenant les types et les noms des champs.
    """
    if type_dict is None:
        type_dict = {}

    for elem in yamlContent:
        if elem.get("type") is not None:

            type_dict[elem.get("fieldName")] = elem.get("type")
        elif elem.get("fakerType") is not None:
            type_dict[elem.get("fieldName")] = elem.get(
                "fakerType"
            )  # ← j’ai corrigé ici aussi

        if elem.get("type", "null") in ["object", "array"]:
            get_type_and_name_from_yaml_content(elem["fields"], type_dict)

    return type_dict


# select_yaml_content_dataset_config_name
def core_select_yaml_content_by_dataset_config_id(datasetId: str, userId: str) -> dict:

    check_var_is_none(datasetId, userId)

    result_request = select_yaml_content_by_dataset_config_id(datasetId, userId)
    # print("result_request -->", result_request)
    if result_request is not None:
        data_dict = result_request[0].get("fields", {})

        type_dict = get_type_and_name_from_yaml_content(data_dict, None)

        # print("data_dict -->", get_type_and_namr_from_yaml_content(data_dict, {}, {}))
        return type_dict

    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_select_dataset_config_by_dataset_id(datasetId: str, userId: str) -> dict:

    check_var_is_none(datasetId, userId)
    result_request = select_dataset_config_by_dataset_id(datasetId, userId)
    if result_request is not None:
        data_dict = result_request[0].get("fields", {})

        type_dict = get_type_and_name_from_yaml_content(data_dict, None)

        # print("data_dict -->", get_type_and_namr_from_yaml_content(data_dict, {}, {}))
        return type_dict

    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


# get_dataset_config_name_by_user_id
def core_select_dataset_config_name_by_user_id(userId: str) -> list[dict]:
    result_request: dict[tuple] = select_dataset_config_name_by_user_id(userId)

    if result_request is not None:
        data_dict = [
            {"datasetName": item[0], "datasetId": item[1]} for item in result_request
        ]
        return data_dict
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config name by user id",
            headers={"WWW-Authenticate": "Bearer"},
        )


# get_dataset_config_info
def core_select_dataset_config(datasetId: str, userId: str) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_config(datasetId, userId)
    print("result_request s3 -->", result_request)
    if result_request is not None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


# select_dataset_config_and_rules_config
def core_select_yaml_and_rules_content_by_dataset_config_id(
    datasetId: str, userId: str
) -> dict:
    result_request = select_yaml_and_rules_content_by_dataset_config_id(
        datasetId, userId
    )
    if (
        result_request is False
        or result_request is None
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
    print("result_request 2 -->", result_request)
    if result_request is not None:
        data_dict = [
            {
                "datasetId": item[0],
                "yamlName": item[1],
                "draftResult": item[2],
                "rulesId": item[3],
                "nbRows": item[4],
                "campaignId": item[5],
                "createdAt": item[6],
            }
            for item in result_request
        ]
        return data_dict

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Error while getting dataset config maybe offset is too high {offset}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================


# déclaration de la classe S3Manager
s3_manager = S3Manager()


# select_all_s3_url_dataset
def core_select_all_s3_url_from_dataset(ownerId: str) -> dict:
    """
    Get S3 url
    """
    result_request = select_all_s3_url_from_dataset(ownerId)
    if result_request is not None:
        data_dict = [
            {
                "url_presigned": s3_manager.generate_presigned_urls(item[0]),
                "id": item[1],
                "campaignId": item[2],
            }
            for item in result_request
        ]
        s3_manager.generate_presigned_urls()

        return data_dict
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting S3 url datasetId not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


# select_dataset_for_historical
def core_select_dataset_historical_offset(userId: str, offset: int) -> dict:
    result_request = select_dataset_historical_offset(userId, offset)
    if result_request is False:
        data_dict = [
            {
                "id": "vide",
                "nbRows": "vide",
                "datasetConfigId": "vide",
                "clientId": "vide",
                "campaignId": "vide",
                "status": "vide",
                "FinishedAt": "vide",
                "TimeToGenerate": "vide",
                "datasetName": "vide",
                "datasetNameSystem": "vide",
                "isApi": "vide",
            }
        ]
    print("data_dict -->", result_request)
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
            "isApi": item[10],
        }
        for item in result_request
    ]
    return data_dict


# select_dataset_name_system_with_dataset_id_core
def core_select_dataset_name_system_with_dataset_id(datasetId: str, userId: str) -> str:
    response_request = select_dataset_name_system_with_dataset_id(datasetId, userId)
    if not response_request:
        raise HTTPException(
            status_code=400,
            detail="Error while selecting dataset name system with dataset id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return response_request[0]
