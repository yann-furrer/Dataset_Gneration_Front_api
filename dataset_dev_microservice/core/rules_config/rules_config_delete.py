from database.queries.rules_config.rules_config_delete import delete_rules_config_by_rules_id

from fastapi import HTTPException
from core.checking import core_select_user_id_from_api_key



def core_delete_rules_config_by_rules_id(rules_id: str, api_key: str) -> bool:
    """
    Supprime les configurations de dataset et de règles associées
    """
    user_id = core_select_user_id_from_api_key(api_key)
    if None in [rules_id, user_id]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    reuslt_request = delete_rules_config_by_rules_id(rules_id, user_id)

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=404,
            detail="Error while deleting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
 