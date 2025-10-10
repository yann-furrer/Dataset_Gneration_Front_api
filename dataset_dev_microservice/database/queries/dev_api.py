import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import session, text


# SELECT_DEV_TOKEN = """
# SELECT   "id", "tokenPreview", "quotaUsed", "expiredAt" FROM public."APIHandle" WHERE "userId" = :userId;
# """


# def select_dev_token_info(userId: str) ->  dict | bool:
#     try:
#         result = session.execute(text(SELECT_DEV_TOKEN), {"userId": userId})
#         row = result.mappings().all()
#         return row
#     except Exception as error:
#         session.rollback()
#         print("error -->", error)
#         return False


# requete d'insertion des tokens
# INSERT_DEV_TOKEN = """
# INSERT INTO public."APIHandle" ("userId", "token", "tokenPreview", "quotaUsed", "createdAt", "updatedAt")
# VALUES (:userId, :token, :tokenPreview, :quotaUsed, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
# """


# def insert_api_token(
#     userId: str,
#     token: str,
#     tokenPreview: str,
#     quotaUsed: int = 0,
# ) -> bool:
#     """
#     Insert new API token
#     quotaUsed compte le nombre de lignes générées
#     """
#     try:
#         session.execute(
#             text(INSERT_DEV_TOKEN),
#             {
#                 "userId": userId,
#                 "token": token,
#                 "tokenPreview": tokenPreview,
#                 "quotaUsed": quotaUsed,

#             },
#         )
#         session.commit()
#         return True
#     except Exception as error:
#         session.rollback()
#         print("error -->", error)
#         return False


# insert_api_token("cm961zmgm0001w1g27a457qf9", "123456789", 0, 0.01, 10)


# # requete de suppression des tokens
# DELETE_DEV_TOKEN = """
# DELETE FROM public."APIHandle" WHERE "id" = :id;
# """


# def delete_api_token(token_id: str) -> bool:
#     """
#     Delete API token
#     """
#     try:
#         session.execute(text(DELETE_DEV_TOKEN), {"id": token_id})
#         session.commit()
#         return True
#     except Exception as error:
#         session.rollback()
#         print("error -->", error)
#         return False


# requete de modification du quota utilisé
# UPDATE_QUOTA_DEV_TOKEN_FROM_USER_ID = """
# UPDATE public."Suscription" SET "ApiCredit" =  "ApiCredit" + :new_credit_used_to_sum WHERE "userId" = :userId;
# """


# def add_api_credit_on_user(user_id: str, new_credit_used_to_sum: int) -> bool:
#     """
#     Update quota used
#     """
#     print("test")
#     print("user_id -->", user_id, "new_quota_used_to_sum -->", new_credit_used_to_sum)
#     try:
#         session.execute(
#             text(UPDATE_QUOTA_DEV_TOKEN_FROM_USER_ID),
#             {"new_credit_used_to_sum": int(new_credit_used_to_sum), "userId": user_id},
#         )
#         session.commit()
#         return True
#     except Exception as error:
#         session.rollback()
#         print("error -->", error)
#         return False


# SELECT_TOKEN_BY_USERID = """
# SELECT "token" FROM public."APIHandle" WHERE "userId" = :userId;
# """


# def select_token_by_user_id(user_id: str) -> bool:
#     try:
#         request = session.execute(text(SELECT_TOKEN_BY_USERID), {"userId": user_id})
#         result = request.fetchone()
#         return result[0]
#     except Exception as error:
#         session.rollback()
#         print("error -->", error)
#         return False


# requete de verification du prix du token

# requete de mise à jour du prix
# requete de mise à jour du quota utilisé
