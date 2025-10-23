import os
import sys

from fastapi import HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session

DELETE_RULES_CONFIG_BY_RULES_ID = """
DELETE FROM public."RulesConfig" WHERE "rulesId" = :rulesId AND "userId" = :userId;
"""

def delete_rules_config_by_rules_id(rules_id: str, user_id: str) -> bool:
    """
    Supprime les configurations de dataset et de règles associées à un utilisateur
    """
    try:
        result =session.execute(
            text(DELETE_RULES_CONFIG_BY_RULES_ID),
            {
                "rulesId": rules_id,
                "userId": user_id,
            },
        )
        session.commit()
        if result.rowcount < 1:
            raise HTTPException(
                status_code=400,
                detail="Error while deleting rules config, maybe the rules_id is not exist",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    except Exception as e:
        session.rollback()
        print("Error while deleting rules config", e)
        raise   HTTPException(
            status_code=400,
            detail="Error while deleting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
