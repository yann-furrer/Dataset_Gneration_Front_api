import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text



UPDATE_QUOTA_USED_BY_TOKEN = """
UPDATE public."APIHandle" SET "quotaUsed" =  "quotaUsed" + :credit WHERE "token" = :token;
"""
def update_quota_used_by_token(token: str, credit: int) -> bool:
    """
    Met à jour le nombre de crédits d'un utilisateur
    operation : substract ou sum
    credit : nombre de crédits à ajouter ou à retirer
    """
    try:
        session.execute(
            text(UPDATE_QUOTA_USED_BY_TOKEN),
            {"credit": int(credit), "token": token},
        )
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False


UPDATE_SUM_QUOTA_DEV_TOKEN_FROM_USER_ID = """
UPDATE public."Suscription" SET "ApiCredit" =  "ApiCredit" + :credit WHERE "userId" = :userId;
"""

UPDATE_SUBSTRACT_QUOTA_DEV_TOKEN_FROM_USER_ID = """
UPDATE public."Suscription" SET "ApiCredit" =  GREATEST("ApiCredit" - :credit, 0) WHERE "userId" = :userId;
"""


def update_api_credit_on_user(user_id: str, credit: int, operation: str = "substract") -> bool:
    """
    Met à jour le nombre de crédits d'un utilisateur
    operation : substract ou sum
    credit : nombre de crédits à ajouter ou à retirer
    """
    print("test")
    print("user_id -->", user_id, "credit -->", credit)
    try:
        if operation == "substract":
            session.execute(
                text(UPDATE_SUBSTRACT_QUOTA_DEV_TOKEN_FROM_USER_ID),
                {"credit": int(credit), "userId": user_id},
            )
        else:
            session.execute(
                text(UPDATE_SUM_QUOTA_DEV_TOKEN_FROM_USER_ID),
                {"credit": int(credit), "userId": user_id},
            )
        session.commit()
        return True
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False
