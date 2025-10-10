import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text


SELECT_CONSUMPTION_TOKEN_BY_USER_ID = """
SELECT SUM("quotaUsed") FROM public."APIHandle"
 WHERE "userId" = :userId;
"""
def select_consumption_token_by_user_id(userId: str) -> int | bool:
    try:
        result = session.execute(text(SELECT_CONSUMPTION_TOKEN_BY_USER_ID), {"userId": userId})
        row = result.mappings().first()
        return row
    except Exception:
        session.rollback()
        return False


SELECT_DEV_TOKEN = """
SELECT   "id", "tokenPreview", "quotaUsed", "expiredAt" FROM public."APIHandle" WHERE "userId" = :userId;
"""


def select_dev_token_info(userId: str) -> dict | bool:
    try:
        result = session.execute(text(SELECT_DEV_TOKEN), {"userId": userId})
        row = result.mappings().all()
        return row
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False


SELECT_APICREDIT_FROM_USER_ID = """
SELECT "ApiCredit" FROM public."Suscription" WHERE "userId" = :userId;
"""


def select_api_credit_from_user_id(userId: str) -> int | bool:
    try:
        result = session.execute(
            text(SELECT_APICREDIT_FROM_USER_ID), {"userId": userId}
        )
        row = result.mappings().first()
        return row
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False


SELECT_TOKEN_BY_USERID = """
    SELECT "token" FROM public."APIHandle" WHERE "userId" = :userId;
"""


def select_token_by_user_id(user_id: str) -> bool:
    try:
        request = session.execute(text(SELECT_TOKEN_BY_USERID), {"userId": user_id})
        result = request.fetchone()
        return result[0]
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False
