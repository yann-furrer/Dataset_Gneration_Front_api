import os , sys, uuid, yaml
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from database.queries.dev_api import insert_api_token, delete_api_token, update_quota_used, select_dev_token_info , update_quota_used
from core.dev_utils import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))



# Génération de token
def generate_token() -> str:
    # Préfixe requis
    prefixe = "dsg-"
    # Génération of UUID (universally unique identifier)
    uuid_str = str(uuid.uuid4()).replace('-', '')
    longueur_restante = 20 - len(prefixe)
    partie_uuid = uuid_str[:longueur_restante]
    token = prefixe + partie_uuid
    return token



#Liste tout les tokens d'un utilisateur
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
      
        response = [{"id": item[0], "tokenPreview": item[1], "quotaUsed": item[2], "price": item[3], "limit": item[4], "expiredAt": item[5]} for item in result_request]
        return response
    except Exception as e:
        print("error -->", e)
        HTTPException(
            status_code=401,
            detail="User subscription not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )



# Insertion d'un token dans la table APIHandle
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


# Suppression d'un token dans la table APIHandle
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



# Mise à jour du quota utilisé d'un token dans la table APIHandle
# Utilisé par le front pour mettre à jour le quota utilisé
def update_dev_quota_used(token : str, new_quota_used_to_sum : int) -> bool:
    """
    Update quota used
    """
    result_request = update_quota_used(token, new_quota_used_to_sum)
    if result_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )



# Utilisé pour vérifier si le fichier yaml ou de règle est valide
def check_config_validity(yaml_content : dict, rules_content : list = []) -> dict:
    """
    Check if the yaml content is valid
    yaml_content : est au format yaml converti en json
    rules_content : est au format json de base
    """
    #Vérification basique des fichiers de config
    try:
        yaml_content = yaml.safe_load(yaml_content)
    except Exception as e:
        print("error -->", e)
        HTTPException(
            status_code=400,
            detail="Error while convert to yaml check your syntax " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if rules_content != [] and type(rules_content) != list:
        HTTPException(
            status_code=400,
            detail="Error while convert to rules check your syntax " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    
    #Vérification du fichier yaml
        #Vérification de la structure du fichier yaml
    dataset_name = yaml_content.get("dataset_name" , "empty")
    numberOfRecords  = yaml_content.get("numberOfRecords" , "empty")
    fields = yaml_content.get("fields" , "empty")
    bones = yaml_content.get("bones" , "empty")
