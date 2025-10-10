from fastapi import APIRouter, HTTPException

from database.queries.dev_token.dev_token_update import (
    add_api_credit_on_user,
)


# Mise à jour du quota utilisé d'un token dans la table APIHandle
# Utilisé par le front pour mettre à jour le quota utilisé
def core_add_api_credit_on_user(user_id: str, new_quota_used_to_sum: int) -> bool:
    """
    Update quota used
    """
    print("user_id -->", user_id, "new_quota_used_to_sum -->", new_quota_used_to_sum)
    result_request = add_api_credit_on_user(user_id, new_quota_used_to_sum)
    if result_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )