import os , sys, uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from database.queries.dev_api import insert_api_token, delete_api_token, update_quota_used, select_dev_token_info, check_quota_dev_token


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))



#  Function to generate a token
def generate_token() -> str:
    # Préfixe requis
    prefixe = "dsg-"
    # Génération of UUID (universally unique identifier)
    uuid_str = str(uuid.uuid4()).replace('-', '')
    longueur_restante = 20 - len(prefixe)
    partie_uuid = uuid_str[:longueur_restante]
    token = prefixe + partie_uuid

    return token


def list_dev_tokens(userId : str) -> bool:
    """
    List all API tokens
    """
    try:
        result_request = select_dev_token_info(userId)
        
        if result_request == False:
            HTTPException(
                status_code=400,
                detail="Error while inserting new token",
                headers={"WWW-Authenticate": "Bearer"},
            )
      
        response = [{"id": item[0], "tokenPreview": item[1], "quotaUsed": item[2], "price": item[3], "limit": item[4], "createdAt": item[5], "updatedAt": item[6]} for item in result_request]
        return response
    except Exception as e:
        print("error -->", e)
        HTTPException(
            status_code=401,
            detail="User subscription not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

def insert_dev_token(userId : str, limit : int, expire : datetime = datetime.now() + timedelta(days=365)) -> bool:
    """
    Insert new API token
    """
    token = generate_token()
    result_request = insert_api_token(userId, token, "*"*17+token[17:], limit)
    if result_request == False:
        HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )



def delete_dev_token(token_id : str) -> bool:
    """
    Delete API token
    """
    result_request = delete_api_token(token_id)
    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while deleting token",
            headers={"WWW-Authenticate": "Bearer"},
        )









def update_dev_quota_used(token : str, new_quota_used_to_sum : int) -> bool:
    """
    Update quota used
    """
    quota_response = check_quota_dev_token(token)
    result_request = update_quota_used(token, new_quota_used_to_sum)
    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )
