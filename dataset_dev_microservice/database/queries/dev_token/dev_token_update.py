import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text

UPDATE_QUOTA_DEV_TOKEN_FROM_USER_ID = """
UPDATE public."Suscription" SET "ApiCredit" =  "ApiCredit" + :new_credit_used_to_sum WHERE "userId" = :userId;
"""


def add_api_credit_on_user(user_id: str, new_credit_used_to_sum: int) -> bool:
    """
    Update quota used
    """
    print("test")
    print("user_id -->", user_id, "new_quota_used_to_sum -->", new_credit_used_to_sum)
    try:
        session.execute(
            text(UPDATE_QUOTA_DEV_TOKEN_FROM_USER_ID),
            {"new_credit_used_to_sum": int(new_credit_used_to_sum), "userId": user_id},
        )
        session.commit()
        return True
    except Exception as error:
        session.rollback()
        print("error -->", error)
        return False