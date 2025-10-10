import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text



# requete de suppression des tokens
DELETE_DEV_TOKEN = """
DELETE FROM public."APIHandle" WHERE "id" = :id;
"""


def delete_api_token(token_id: str) -> bool:
    """
    Delete API token
    """
    try:
        session.execute(text(DELETE_DEV_TOKEN), {"id": token_id})
        session.commit()
        return True
    except Exception as error:
        session.rollback()
        print("delete error -->", error)
        return False