from fastapi import HTTPException
from database.queries.dataset_config.dataset_config_select import (
    select_rules_config_by_dataset_config_id,
    select_all_rules_data_by_dataset_config_id,
)


def core_select_rules_config_by_dataset_config_id(
    datasetConfigId: str, userId: str
) -> bool:
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : yamlContent
    """
    result_request = select_rules_config_by_dataset_config_id(datasetConfigId, userId)
    if result_request is not None:
        
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while selecting dataset config by dataset config id",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_select_all_rules_data_by_dataset_config_id(
    datasetConfigId: str, userId: str
) -> bool:
    """
    Récupère les informations rules config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : yamlContent
    """
    result_request = select_all_rules_data_by_dataset_config_id(datasetConfigId, userId)
    if result_request is not None:
        return result_request


