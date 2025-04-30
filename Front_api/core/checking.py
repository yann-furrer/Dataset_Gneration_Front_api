import os , sys, uuid
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from database.queries.security import check_session_token, check_user_api_token, check_user_suscription_limit, select_dev_token_info
from database.queries.dev_api import select_dev_token_info

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()
security = HTTPBearer()  

#  Function to generate a JWT token
def generate_user_api_token() -> str:
    # Préfixe requis
    prefixe = "dsg-"
    # Génération d'un UUID (universally unique identifier)
    uuid_str = str(uuid.uuid4()).replace('-', '')
    longueur_restante = 20 - len(prefixe)
    partie_uuid = uuid_str[:longueur_restante]
    token = prefixe + partie_uuid

    return token


def check_user_api_token(token : str, nb_rows_to_generate : int) -> bool:
    """
    Vérifie si le token est valide
    """
    try :
        token_info = select_dev_token_info(token)
        if token_info == False:
            raise HTTPException(
                status_code=400,
                detail=" Token not found or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )    
        return True
    
    except Exception as e:
        print("error -->", e)
        raise HTTPException(
            status_code=401,
            detail="User subscription not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )   



async def get_session_token(request: Request) -> str:
    """
    Extrait le token de session du header 'sessiontoken'.
    """
    session_token = dict(request.headers).get('sessiontoken')
    userId = check_session_token(session_token)
    print("userId -->", userId)
    if userId == False:
        raise HTTPException(
            status_code=401,
            detail="Session token not found or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return userId



async def check_user_limit_credit(request: Request, userId: str = Depends(get_session_token)) -> bool:
    """
    Vérifie si l'utilsateur à assez de crédit pour faire une requête
    """


    try :
        body = await request.json()
        nb_rows_to_generate = body.get("nb_rows_to_generate" , 0)
        if nb_rows_to_generate == 0:
            raise HTTPException(
                status_code=400,
                detail="nb_rows_to_generate is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        nb_rows_remaining =  check_user_suscription_limit(userId)[0]
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


