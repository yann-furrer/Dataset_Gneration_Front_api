
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *





# Vérifie si le token possède bien les droits pour faire une requête
SELECT_VALIDITY_TOKEN = """
SELECT "userId", "quotaUsed", "price", "limit", "expireAt"  FROM public."APIHandle" WHERE "token" = :token;
"""

def select_validity_token(token):
    """
    Check if token is valid for requesting session
    """
    try:
        print("token -->", token)
        request = session.execute(text(SELECT_VALIDITY_TOKEN), {"token": token})
        result = request.fetchone()
        response = [{"id": result[0], "quotaUsed": result[1], "price": result[2], "limit": result[3], "expireAt": result[4]}]
        return response
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False



# Verifie si le token existe dans l'api, utilisé pour le commandes sans génération
CHECK_DEV_TOKEN = """
SELECT "id" FROM public."APIHandle" WHERE "token" = :token;
"""

def check_existing_dev_token(token):
    """
    Check if token is valid for requesting API
    """
    try:
        request = session.execute(text(CHECK_DEV_TOKEN), {"token": token})
        result = request.fetchone()
        return result[0]
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False




CHECK_SUSCRIPTION_LIMIT = """
SELECT ("nbRowsMaxSuscribed" - "nbRowsUsed") AS "nb_rows_remaining"  FROM public."Suscription" WHERE "userId"= :userId;
"""

def check_user_suscription_limit(userId: str) -> bool:
    """
    Check if token is valid for requesting API
    """
    try:
        request = session.execute(text(CHECK_SUSCRIPTION_LIMIT), {"userId": userId})
        result = request.fetchone()
        return result
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False
    

#Check if sessions token is valid

CHECK_SESSION_TOKEN = """
SELECT "userId" FROM public."Session" WHERE "sessionToken" = :token;
"""



def check_session_token(token):
    """
    Check if token is valid for requesting session
    """
    try:
        print("token -->", token)
        request = session.execute(text(CHECK_SESSION_TOKEN), {"token": token})
        result = request.fetchone()
        return result[0]
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False