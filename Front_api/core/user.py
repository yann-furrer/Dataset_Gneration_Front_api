import os , sys , json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from database.queries.user_query import insert_subscription , insert_subscription_if_not_exist, get_user_subscription, update_quota_used, select_nbrows_by_dataset, select_statistics_by_user

with open("subSysteminfo.json") as f:
    subSystemInfo = json.load(f)



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))




def get_subscription(userId : str) -> str:
    """
    Insert new subscription
    """

    result_request : str = get_user_subscription(userId)
    if result_request == None:
       result_request = "Explorer"
    return result_request




def insert_user_subscription(userId : str, status : str,  subscriptionType : str = "Explorer", period : str = "month") -> bool:
    """
    Insert new API token
    """

    currentPeriodEnd = datetime.now()
    if period == "years":
        currentPeriodEnd  += relativedelta(years=1)
    elif period == "month":
        currentPeriodEnd += relativedelta(months=1)

    nbRowsMaxSubscribed = subSystemInfo[subscriptionType]["maxRows"]
    reuslt_request = insert_subscription(userId, status, currentPeriodEnd, subscriptionType, nbRowsMaxSubscribed)

    if reuslt_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def insert_subscription_for_connexion_callback(userId : str, status : str,  subscriptionType : str = "Explorer", period : str = "month") -> bool:
    """
    Check if user is already subscribed
    Insert new subscription
    """


    currentPeriodEnd = datetime.now(timezone.utc).replace(tzinfo=None)
    if period == "years":
        currentPeriodEnd  += relativedelta(years=1)
    elif period == "month":
        currentPeriodEnd += relativedelta(months=1)

    nbRowsMaxSubscribed = subSystemInfo[subscriptionType]["maxRows"]
    
    response_status : bool =  insert_subscription_if_not_exist(userId, status, currentPeriodEnd.strftime("%Y-%m-%d %H:%M:%S.%f"), subscriptionType, nbRowsMaxSubscribed) 
    if response_status == False:
        HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return True
    



def update_quota(userId : str, nb_rows : int) -> bool:
    """
    Update quota used
    """
    response_status : bool =  update_quota_used(userId, nb_rows)
    if response_status == False:
        HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:    
        return True



#Statistique pour l'abonnment


def get_rows_generated(userId : str) -> bool:
    """
    Insert new subscription
    """
    # type (nbrows : int, day_number : int)
    result_request : bool = select_nbrows_by_dataset(userId)
    if result_request == False:
        HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )

    else:
        return result_request
    

def get_statistics(userId : str) -> bool:
    """
    Insert new subscription
    """
    # type (nbrows : int, day_number : int)
    result_request : tuple   = select_statistics_by_user(userId)
    if result_request == False:
        HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if result_request == None:
        return (0, 0)
    else:
        return result_request