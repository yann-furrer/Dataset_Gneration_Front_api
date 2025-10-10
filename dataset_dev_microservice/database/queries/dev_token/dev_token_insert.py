import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text


INSERT_DEV_TOKEN = """
INSERT INTO public."APIHandle" ("userId", "token", "tokenPreview", "quotaUsed", "createdAt", "updatedAt") 
VALUES (:userId, :token, :tokenPreview, :quotaUsed, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
"""


def insert_api_token(
    userId: str,
    token: str,
    token_preview: str,
    quota_used: int = 0,
) -> bool:
    """
    Insert new API token
    quotaUsed compte le nombre de lignes générées
    """
    try:
        session.execute(
            text(INSERT_DEV_TOKEN),
            {
                "userId": userId,
                "token": token,
                "tokenPreview": token_preview,
                "quotaUsed": quota_used,
            },
        )
        session.commit()
        return True
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False
