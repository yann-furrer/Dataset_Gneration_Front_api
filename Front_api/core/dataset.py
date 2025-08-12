import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException

# datasetConfig and rulesConfig
from database.queries.dataset import (
    insert_dataset_config,
    insert_rules_config,
    select_dataset_config,
    select_dataset_historical_config_offset,
    select_yaml_and_rules_content_by_dataset_config_id,
    select_dataset_config_name_by_user_id,
    select_yaml_content_by_dataset_config_id,
)

# dataset
from database.queries.dataset import (
    insert_dataset_info,
    select_dataset_name_system_with_dataset_id,
    select_all_s3_url_from_dataset,
    select_dataset_historical_offset,
    update_finished_dataset_info,
    update_status_dataset_info,
    delete_dataset_by_dataset_id,
)

from utils.s3_handle import S3Manager


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


def select_yaml_content_dataset_config_name(datasetId: str, userId: str) -> dict:
    if datasetId is None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif userId is None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = select_yaml_content_by_dataset_config_id(datasetId, userId)
    # print("result_request -->", result_request)
    if result_request is not None:
        data_dict = result_request[0].get("fields", {})

        type_dict = get_type_and_name_from_yaml_content(data_dict, None)

        # print("data_dict -->", get_type_and_namr_from_yaml_content(data_dict, {}, {}))
        return type_dict

    else:
        HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def insert_dataset_config_info(
    datasetId: str,
    userId: str,
    yamlName: str,
    yamlContent: str,
    draftResult: str,
    nbRows: int,
) -> bool:
    """
    save dataset config
    """
    reuslt_request = insert_dataset_config(
        datasetId, userId, yamlName, yamlContent, draftResult, nbRows
    )

    if reuslt_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )


def insert_rules_config_info(
    rulesId: str,
    userId: str,
    rulesName: str,
    rulesContent: str,
    datasetConfigId: int,
    campaignId: str = None,
) -> bool:
    """
    save rules config
    """
    result_request = insert_rules_config(
        rulesId, userId, rulesName, rulesContent, datasetConfigId, campaignId
    )
    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def insert_dataset_config_and_rules_config_info(
    datasetConfigId: str,
    userId: str,
    yamlName: str,
    yamlContent: dict,
    draftResult: dict,
    nbRows: int,
    rulesId: str,
    rulesName: str,
    rulesContent: str,
    campaignId: str = None,
) -> bool:
    """
    save dataset config
    """
    result_request_dataset_config = insert_dataset_config(
        datasetConfigId,
        userId,
        yamlName,
        json.dumps(yamlContent),
        json.dumps(draftResult),
        nbRows,
    )
    result_rules_config = None
    print("rulesContent", rulesContent)
    if rulesContent != None:  # si rulesContent est None alors on ne fait rien
        result_rules_config = insert_rules_config(
            rulesId,
            userId,
            rulesName,
            json.dumps(rulesContent),
            datasetConfigId,
            campaignId,
        )

    if result_request_dataset_config and result_rules_config:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset config or dataset rules config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_dataset_config_name_by_user_id(userId: str) -> list[dict]:
    result_request: dict[tuple] = select_dataset_config_name_by_user_id(userId)

    if result_request is not None:
        data_dict = [
            {"datasetName": item[0], "datasetId": item[1]} for item in result_request
        ]
        return data_dict
    else:
        HTTPException(
            status_code=400,
            detail="Error while getting dataset config name by user id",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_dataset_config_info(datasetId: str, userId: str) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_config(datasetId, userId)
    print("result_request s3 -->", result_request)
    if result_request != None:
        return result_request
    else:
        HTTPException(
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
        HTTPException(
            status_code=400,
            detail="Error while getting dataset config or rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result_request


"""
Séparation des requetes, pour la gestion des datasets
Ici se trouve les requetes sur la table dataset mais il est possible qu'une fonction utilise une autre table

"""

######### requete sur la table DATASET #########

"""
INSERT QUERY
"""


def inserting_dataset_info_core(
    dataset_row_id,
    datasetConfigId: int,
    ownerId: str,
    campaingId: str = None,
    status: str = "waiting",
    nbRows: int = 0,
    datasetName: str = "defaut name",
) -> bool:
    """
    Insert new dataset info in dataset
    """
    result_request = insert_dataset_info(
        dataset_row_id,
        datasetConfigId,
        ownerId,
        campaingId,
        status,
        nbRows,
        datasetName,
    )
    print("result_request -->", result_request)
    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )


"""
SELECT QUERY
"""


def select_dataset_name_system_with_dataset_id_core(datasetId: str, userId: str) -> str:
    response_request = select_dataset_name_system_with_dataset_id(datasetId, userId)
    if not response_request:
        raise HTTPException(
            status_code=400,
            detail="Error while selecting dataset name system with dataset id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return response_request[0]


def update_finished_dataset(
    dataset_name: str, datasetId: str, generationError: str, status: str
) -> bool:
    """
    Update finished dataset
    """
    print("datasetId -->", datasetId)
    print("generationError -->", generationError)
    print("status -->", status)
    reuslt_request = update_finished_dataset_info(
        dataset_name, datasetId, generationError, status
    )

    if reuslt_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while updating dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )


def update_status_dataset(datasetId: str, status: str) -> bool:
    """
    Update status dataset
    """
    reuslt_request = update_status_dataset_info(datasetId, status)

    if reuslt_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while updating dataset status info",
            headers={"WWW-Authenticate": "Bearer"},
        )


# def update_finished_dataset(datasetId: str, s3Url: str, FinishedAt: str, generationError: str, status: str) -> bool:

# déclaration de la classe S3Manager
s3_manager = S3Manager()


def select_all_s3_url_dataset(ownerId: str) -> dict:
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
        HTTPException(
            status_code=400,
            detail="Error while getting S3 url datasetId not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_dataset_config_historical_offset(userId: str, offset: int) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_historical_config_offset(userId, offset)
    if result_request != None:
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
        HTTPException(
            status_code=400,
            detail=f"Error while getting dataset config maybe offset is too high {offset}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def delete_dataset_historical(datasetId: str, userId: str) -> bool:
    """
    Delete dataset form his s3 bucket
    """
    result_request = delete_dataset_by_dataset_id(datasetId, userId)
    if result_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while deleting dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
