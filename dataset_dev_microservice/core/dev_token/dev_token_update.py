from fastapi import APIRouter, HTTPException

from database.queries.dev_token.dev_token_update import (
    update_api_credit_on_user,
    update_quota_used_by_token,
)


# Mise à jour du quota utilisé d'un token dans la table APIHandle
# Utilisé par le front pour mettre à jour le quota utilisé
def core_update_api_credit_on_user(
    user_id: str, credit: int, operation: str = "substract"
) -> bool:
    """
    Update quota used
    """
    print("user_id -->", user_id, "new_quota_used_to_sum -->", credit)
    result_request = update_api_credit_on_user(user_id, credit, operation)
    if result_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_update_quota_used_by_token(token: str, credit: int) -> bool:
    """
    Met à jour le nombre de crédits d'un utilisateur
    operation : substract ou sum
    credit : nombre de crédits à ajouter ou à retirer
    """
    print("user_id -->", token, "credit -->", credit)
    result_request = update_quota_used_by_token(token, credit)
    if result_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )
