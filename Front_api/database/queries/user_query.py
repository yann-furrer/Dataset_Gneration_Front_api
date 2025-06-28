import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *



#Ajout d'un abonnement 
INSERT_SUBSCRIPTION = """
INSERT INTO public."Suscription"(
	 "userId", "stripeCustomerId", "stripeSubscriptionId", "stripePriceId", status, "currentPeriodEnd", "createdAt", "updatedAt", "suscriptionType", "nbRowsMaxSuscribed")
	VALUES (:userId, :stripeCustomerId, :stripeSubscriptionId, :stripePriceId, :status, :currentPeriodEnd, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :suscriptionType, :nbRowsMaxSuscribed);
"""
UPDATE_USER_QUOTA_USED = """
UPDATE public."API_handle" SET "quotaUsed" =  "quotaUsed" + :new_quota_used_to_sum, "updatedAt" = CURRENT_TIMESTAMP WHERE "userId" = :userId;
"""



def insert_subscription(userId : str, currentPeriodEnd : str, suscriptionType : str, nbRowsMaxSuscribed : int) -> bool:
    """
    Insert new subscription
    """
    try:
        session.execute(text(INSERT_SUBSCRIPTION), {"userId": userId, "stripeCustomerId": "stripeCustomerId", "stripeSubscriptionId" : "stripeSubscriptionId", "stripePriceId": 1, "status": "active", "currentPeriodEnd": currentPeriodEnd, "suscriptionType": suscriptionType, "nbRowsMaxSuscribed": nbRowsMaxSuscribed})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False
    

def update_quota_used(userId : str, new_quota_used_to_sum : int) -> bool:
    """
    Update quota used
    """
    try:
        session.execute(text(UPDATE_USER_QUOTA_USED), {"new_quota_used_to_sum": new_quota_used_to_sum, "userId": userId})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False
    
    