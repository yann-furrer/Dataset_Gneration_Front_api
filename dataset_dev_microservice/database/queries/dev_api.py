
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *



SELECT_DEV_TOKEN = """
SELECT   "id", "tokenPreview", "quotaUsed", "price", "limit", "expiredAt" FROM public."APIHandle" WHERE "userId" = :userId;
"""

def select_dev_token_info(userId : str) -> bool:
    try:
        result = session.execute(text(SELECT_DEV_TOKEN), {"userId": userId})
        row = result.fetchall()
        print("row -->", row)
        return row
    except Exception as error:
        session.rollback()
        print("error -->",error)
        return False

# requete d'insertion des tokens
INSERT_DEV_TOKEN = """
INSERT INTO public."APIHandle" ("userId", "token", "tokenPreview", "quotaUsed", "price", "limit", "createdAt", "updatedAt") 
VALUES (:userId, :token, :tokenPreview, :quotaUsed, :price, :limit, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
"""



def insert_api_token(userId : str, token : str, tokenPreview : str, quotaUsed : int = 0, price : float = 0, limit : int = -1) -> bool:
    """
    Insert new API token
    quotaUsed compte le nombre de lignes générées
    """
    try:
        session.execute(text(INSERT_DEV_TOKEN), {"userId": userId, "token": token, "tokenPreview" : tokenPreview, "quotaUsed": quotaUsed, "price": price, "limit": limit})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False   
    
# insert_api_token("cm961zmgm0001w1g27a457qf9", "123456789", 0, 0.01, 10)

# requete de suppression des tokens
DELETE_DEV_TOKEN = """
DELETE FROM public."APIHandle" WHERE "id" = :id;
"""
def delete_api_token(token_id : str) -> bool:
    """
    Delete API token
    """
    try:
        session.execute(text(DELETE_DEV_TOKEN), {"id": token_id})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False


#requete de modification du quota utilisé
UPDATE_QUOTA_DEV_TOKEN = """
UPDATE public."APIHandle" SET "quotaUsed" =  "quotaUsed" + :new_quota_used_to_sum, "updatedAt" = CURRENT_TIMESTAMP WHERE "id" = :token_id;
"""

def update_quota_used(token_id : str, new_quota_used_to_sum : int) -> bool: 
    """
    Update quota used
    """
    try:
        session.execute(text(UPDATE_QUOTA_DEV_TOKEN), {"new_quota_used_to_sum": int(new_quota_used_to_sum), "token_id": token_id})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False

# requete de verification du prix du token

# requete de mise à jour du prix 
# requete de mise à jour du quota utilisé