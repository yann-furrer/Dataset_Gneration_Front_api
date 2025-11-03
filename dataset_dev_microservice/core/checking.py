import os, sys, uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.security import HTTPBearer
from database.queries.security import (
    check_session_token,
    check_existing_dev_token,
    select_user_id_from_token,
)
from database.queries.dev_token.dev_token_select import select_token_by_user_id
from database.queries.security import (
    check_user_suscription_limit,
    select_api_credit_from_token,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.env_handle import load_env_from_file
load_env_from_file()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()
security = HTTPBearer()


def core_check_server_token(server_token: str = Query(...)) -> bool:
    """
    Vérifie si le token est valide
    """
    if server_token == os.getenv("SERVER_TOKEN"):
        return True
    else:
        raise HTTPException(
            status_code=401,
            detail="Server token not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_select_user_id_from_api_key(api_key: str) -> str:
    """
    Retourne le nombre de crédits d'un utilisateur ou retourne une erreur
    si le token n'est pas reconnu
    """
    user_id: str | bool = select_user_id_from_token(api_key)
    if user_id is False:
        raise HTTPException(
            status_code=400,
            detail="Error Api keys not recognized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return user_id["userId"]


def core_select_api_credit_from_token(api_key: str) -> int:
    """
    Retourne le nombre de crédits d'un utilisateur ou retourne une erreur
    si le token n'est pas reconnu
    """
    nb_credit: int | bool = select_api_credit_from_token(api_key)

    if nb_credit is False:
        raise HTTPException(
            status_code=400,
            detail="Error token not recognized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return nb_credit["ApiCredit"]


def get_token_by_user_id(user_id: str) -> bool:
    """
    Vérifie si le token est valide
    """
    try:
        token = select_token_by_user_id(user_id)
        print("userId niv 1 -->", token)
        if token is False:
            raise HTTPException(
                status_code=401,
                detail="Le token de dev n'est pas reconnu",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token
    except Exception as e:
        print("error -->", e)
        return ""


async def check_dev_token(request: Request) -> bool:

    param = request.query_params
    token = param.get("api_key", "None")
    print("token -->", token)
    bool_response = check_existing_dev_token(token)
    if bool_response is False:
        raise HTTPException(
            status_code=401,
            detail="Le token de dev n'est pas reconnu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return bool


# def check_dev_token_validity(token: str, nb_rows_to_generate: int) -> bool:
#     """
#     Vérifie si le token est valide
#     """
#     try:
#         token_info = select_validity_token(token)
#         if token_info is False:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Token not found or invalid",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         # Une marge de 10% est ajoutée pour ne pas avoir de problème de calcul en la faveur du clientr
#         if (nb_rows_to_generate + token_info["quotaUsed"]) > token_info[
#             "limit"
#         ] * 1.10 and datetime.now() < token_info["expireAt"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail=" Not enough credit",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )

#         if token_info["expire"] < datetime.now():
#             raise HTTPException(
#                 status_code=400,
#                 detail=" Token expired",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         elif token["quotaUsed"] >= token_info["limit"]:
#             raise HTTPException(
#                 status_code=400,
#                 detail=" Not enough credit",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#             return True

#     except Exception as e:
#         print("error -->", e)
#         raise HTTPException(
#             status_code=401,
#             detail="User subscription not found or invalid",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#         return False


async def get_session_token(request: Request) -> str:
    """
    Extrait le token de session du header 'sessiontoken et retourne le userId'.
    """
    session_token = dict(request.headers).get("sessiontoken")
    print("session_token -->", session_token)
    userId = check_session_token(session_token)
    print("userId -->", userId)
    if userId is False:
        raise HTTPException(
            status_code=401,
            detail="Session token not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return userId


async def get_dev_token_info(request: Request) -> str:
    """
    Extrait le token api du param 'api_key'.
    """
    param = request.query_params
    api_key = param.get("api_key", "None")
    print("api_key -->", api_key)
    body_data = await request.json()
    # token = body_data.get("token" , "None")
    nb_rows_to_generate = body_data.get("yaml_content", {}).get("numberOfRecords", 0)

    token_check: bool = check_dev_token(api_key)
    print("token_check -->", token_check)
    if token_check == False:
        raise HTTPException(
            status_code=401,
            detail="Session token not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_check


async def check_user_limit_credit(
    request: Request, userId: str = Depends(get_session_token)
) -> bool:
    """
    Vérifie si l'utilsateur à assez de crédit pour faire une requête
    """

    try:
        body = await request.json()
        nb_rows_to_generate = body.get("nb_rows_to_generate", 0)
        if nb_rows_to_generate == 0:
            raise HTTPException(
                status_code=400,
                detail="nb_rows_to_generate is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        nb_rows_remaining = check_user_suscription_limit(userId)[0]
        if nb_rows_to_generate > nb_rows_remaining:
            raise HTTPException(
                status_code=400,
                detail="Not enough credit",
                headers={"WWW-Authenticate": "Bearer"},
            )
        #  La requete est valide
        return userId

    except Exception as e:

        print("error -->", e)
        raise HTTPException(
            status_code=401,
            detail="User subscription not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
