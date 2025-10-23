from fastapi import HTTPException
from database.queries.dataset_config.dataset_config_delete import delete_dataset_config_and_rules_config_by_user_id

def core_delete_dataset_config_and_rules_config_by_user_id(datasetId: str, userId: str, datasetConfigId: str) -> bool:
    """
    Supprime les configurations de dataset et de règles associées à un utilisateur
    """
    result_request = delete_dataset_config_and_rules_config_by_user_id(datasetId, userId, datasetConfigId)
    if result_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting dataset config and rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )