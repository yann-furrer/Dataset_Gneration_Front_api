import os , sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import  HTTPException
from fastapi.security import HTTPBearer
#datasetConfig and rulesConfig
from database.queries.dataset import insert_dataset_config, select_dataset_config, update_finished_dataset_info, select_dataset_historical_config_offset, insert_rules_config
#dataset
from database.queries.dataset import update_status_dataset_info, update_finished_dataset_info, insert_dataset_info, select_all_s3_url_from_dataset, select_dataset_historical_offset, update_dataset_status_info

from utils.s3_handle import S3Manager




# requete sur la table datasetconfig

def insert_dataset_config_info(datasetId: str, userId: str,  yamlName: str, yamlContent: str, draftResult: str, nbRows: int) -> bool:
    """
    save dataset config
    """
    reuslt_request = insert_dataset_config(datasetId, userId, yamlName, yamlContent, draftResult, nbRows)

    if reuslt_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )


def insert_rules_config_info(rulesId: str, userId: str,  rulesName: str, rulesContent: str, datasetConfigId: int, campaignId: str = None) -> bool:
    """
    save rules config
    """
    reuslt_request = insert_rules_config(rulesId, userId,  rulesName, rulesContent, datasetConfigId, campaignId)
    if reuslt_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def insert_dataset_config_and_rules_config_info(datasetConfigId: str, userId: str,  yamlName: str, yamlContent: dict, draftResult: dict, nbRows: int, rulesId: str, rulesName: str, rulesContent: str, campaignId: str = None) -> bool:
    """
    save dataset config
    """
    result_request_dataset_config = insert_dataset_config(datasetConfigId, userId, yamlName, json.dumps(yamlContent), json.dumps(draftResult), nbRows)
    result_rules_config = None
    print("rulesContent", rulesContent)
    if rulesContent != None: # si rulesContent est None alors on ne fait rien
        result_rules_config = insert_rules_config(rulesId, userId,  rulesName, json.dumps(rulesContent), datasetConfigId, campaignId)

    if result_request_dataset_config == True and result_rules_config == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset config or dataset rules config , try again your yaml is not saved, maybe duplicate datasetId",
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
    {"id": item[0], "nbRows": item[1], "datasetConfigId": item[2],"clientId": item[3], "campaignId": item[4],
    "status": item[5], "FinishedAt": item[6], "TimeToGenerate": item[7], "datasetName": item[8],"datasetNameSystem": item[9]}
                for item in result_request
                ]
    return data_dict












# requete sur la table dataset

def inserting_dataset_info(dataset_row_id, datasetConfigId: int, ownerId: str, campaingId: str = None,  status: str = "waiting", nbRows: int = 0, datasetName: str = "defaut name") -> bool:
    """
    Insert new dataset info in dataset
    """
    result_request = insert_dataset_info(dataset_row_id, datasetConfigId, ownerId, campaingId, status, nbRows, datasetName)

    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )

def update_finished_dataset(dataset_name: str, datasetId: str, generationError: str, status: str) -> bool:
    """
    Update finished dataset
    """
    print("datasetId -->", datasetId)
    print("generationError -->", generationError)
    print("status -->", status)
    reuslt_request = update_finished_dataset_info(dataset_name,datasetId, generationError, status)

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
    reuslt_request = update_dataset_status_info(datasetId, status)

    if reuslt_request == True:
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
    if result_request != None:
        data_dict = [
        
        {"url_presigned":  s3_manager.generate_presigned_urls(item[0]), "id": item[1], "campaignId": item[2]} 
            for item in result_request
            ]
        s3_manager.generate_presigned_urls()
        
        return data_dict
    else:
        HTTPException(
            status_code=400,
            detail=f"Error while getting S3 url datasetId not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_dataset_config_historical_offset(userId: str, offset: int) -> dict:
    """
    Get dataset config
    """
    result_request = select_dataset_historical_config_offset(userId, offset)
    if result_request != None:
        data_dict = [
        {"datasetId": item[0], "yamlName": item[1], "yamlContent": item[2], "draftResult": item[3], "ruleId": item[4], "nbrows": item[5], "compaignId": item[6], "createdAt": item[7]}
            for item in result_request
            ]
        return data_dict
       
    else:
        HTTPException(
            status_code=400,
            detail=f"Error while getting dataset config maybe offset is too high {offset}",
            headers={"WWW-Authenticate": "Bearer"},
        )