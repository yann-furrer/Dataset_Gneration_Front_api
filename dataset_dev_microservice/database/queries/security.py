
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *





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
    


CHECK_API_TOKEN = """
SELECT "quotaUsed", "price", "limit", "expire"  FROM public."API_handle" WHERE "token" = :token;
"""


def check_user_api_token(token):
    """
    Check if token is valid for requesting API
    """
    try:
        request = session.execute(text(CHECK_API_TOKEN), {"token": token})
        result = request.fetchone()
        return result[0]
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False

