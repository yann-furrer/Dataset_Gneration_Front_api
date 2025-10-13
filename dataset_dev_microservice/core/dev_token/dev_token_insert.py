import os, sys, uuid, yaml
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from database.queries.dev_token.dev_token_insert import (
    insert_api_token,
)


# Génération de token
def generate_token() -> str:
    # Préfixe requis
    prefixe = "dsg-"
    # Génération of UUID (universally unique identifier)
    uuid_str = str(uuid.uuid4()).replace("-", "")
    longueur_restante = 20 - len(prefixe)
    partie_uuid = uuid_str[:longueur_restante]
    token = prefixe + partie_uuid
    return token


# Insertion d'un token dans la table APIHandle
# insert_dev_token
def core_insert_api_token(userId: str, limit: int, token: str) -> bool:
    """
    Insert new API token
    """
    expire: datetime = datetime.now() + timedelta(days=365)
    result_request = insert_api_token(userId, token, "*" * 17 + token[17:])
    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )
