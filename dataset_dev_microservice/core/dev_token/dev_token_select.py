import os
import sys
from fastapi import HTTPException
from database.queries.dev_token.dev_token_select import (
    
    select_dev_token_info, select_api_credit_from_user_id, select_consumption_token_by_user_id
)
# from core.dev_utils import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))




# Récupère le nombre de lignes consommées par un utilisateur
def core_select_consumption_token_by_user_id(userId: str) -> int:
    """
    Récupère le nombre de lignes consommées par un utilisateur
    """
    result_request: int = select_consumption_token_by_user_id(userId)

    if result_request is False:
          raise HTTPException(
                status_code=400,
                detail="Error while inserting new token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else :
        return {"consumption": result_request["sum"]}




# Liste tout les tokens d'un utilisateur
def core_select_dev_token_info(userId: str) -> bool:
    """
    List all API tokens
    """
    try:
        result_request = select_dev_token_info(userId)

        if result_request is False:
          raise HTTPException(
                status_code=400,
                detail="Error while inserting new token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return result_request
    except Exception as e:
        print("error -->", e)
        raise HTTPException(
            status_code=401,
            detail="User subscription not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_select_api_credit_from_user_id(userId: str) -> int:
    """
Retourne le nombre de crédits d'un utilisateur
    """
    result_request = select_api_credit_from_user_id(userId)

    if result_request is False:
          raise HTTPException(
                status_code=400,
                detail="Error while inserting new token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else :
        return {"credit": result_request["ApiCredit"]}

    