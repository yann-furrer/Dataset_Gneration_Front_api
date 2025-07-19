import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *



#Retourne l'abonnement d'un user
GET_SUBSCRIPTION = """
SELECT "suscriptionType" FROM public."Suscription" WHERE "userId" = :userId;
"""
def get_user_subscription(userId : str) -> bool:
    """
    Insert new subscription
    """
    try:
        request = session.execute(text(GET_SUBSCRIPTION), {"userId": userId})
        result = request.fetchone()
        return result[0]
    except Exception as error:
         session.rollback()
         print("error -->",error)

#Ajout d'un abonnement 
INSERT_SUBSCRIPTION = """
INSERT INTO public."Suscription"(
	 "userId", "stripeCustomerId", "stripeSubscriptionId", "stripePriceId", status, "currentPeriodEnd", "createdAt", "updatedAt", "suscriptionType", "nbRowsMaxSuscribed")
	VALUES (:userId, :stripeCustomerId, :stripeSubscriptionId, :stripePriceId, :status, :currentPeriodEnd, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :suscriptionType, :nbRowsMaxSuscribed);
"""
UPDATE_USER_QUOTA_USED = """
UPDATE public."APIHandle" SET "quotaUsed" =  "quotaUsed" + :new_quota_used_to_sum, "updatedAt" = CURRENT_TIMESTAMP WHERE "userId" = :userId;
"""

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
    



# Cette requete est utilisée pour vérifier si un abonnement existe déjà lors de la connexion sur le front
INSERT_SUBSCRIPTION_IF_NOT_EXIST = """
INSERT INTO public."Suscription"(
	 "userId", status, "currentPeriodEnd", "createdAt", "updatedAt", "suscriptionType", "nbRowsMaxSuscribed")
	VALUES (:userId, :status, :currentPeriodEnd, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :suscriptionType, :nbRowsMaxSuscribed)
	ON CONFLICT ("userId") DO NOTHING;
    """

def insert_subscription_if_not_exist(userId : str, status : str, currentPeriodEnd : str, suscriptionType : str = "Explorer", nbRowsMaxSuscribed : int = 3000) -> bool:
    """
    Insert new subscription
    """
    try:
        session.execute(text(INSERT_SUBSCRIPTION_IF_NOT_EXIST), {"userId": userId, "status" : status, "status": "active", "currentPeriodEnd": currentPeriodEnd, "suscriptionType": suscriptionType, "nbRowsMaxSuscribed": nbRowsMaxSuscribed})
        session.commit()
        return True
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False   
    

#Statistique pour l'abonnment

SELECT_NBROWS_BY_DATASET = """

SELECT 
SUM("nbRows"),
EXTRACT(day FROM "createdAt") AS day_number
FROM public."Dataset"
WHERE "ownerId" = :ownerId
  AND "status" != 'error'
  AND "createdAt" >= date_trunc('month', current_date)
  AND "createdAt" < date_trunc('month', current_date + interval '1 month')
GROUP BY day_number;
"""

def select_nbrows_by_dataset(userId : str) -> tuple:
    try:
        result = session.execute(text(SELECT_NBROWS_BY_DATASET), {"ownerId": userId})
        row = result.fetchall()
       
        nb_rows = [elem[0] for elem in row]
        day_number = [elem[1] for elem in row]

        return (nb_rows, day_number)
    except Exception as error:
        session.rollback()
        print("error -->",error)
        return False
    

SELECT_STAT_BY_USER = """
SELECT SUM("nbRows") AS "sumrows", COUNT("id") AS "sumdataset"
FROM public."Dataset" WHERE "ownerId" = :userId
GROUP BY date_trunc('month', "createdAt");
"""



def select_statistics_by_user(userId : str) -> bool:
    try:
        result = session.execute(text(SELECT_STAT_BY_USER), {"userId": userId})
        row = result.fetchone()
        print("row -->", row)
        return row
    except Exception as error:
        session.rollback()
        print("error -->",error)
