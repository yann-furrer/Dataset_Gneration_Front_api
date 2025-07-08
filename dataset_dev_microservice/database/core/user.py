import os , sys 
from fastapi import HTTPException
from database.queries.user_query import insert_subscription


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

def insert_user_subscription(userId : str, status : str, currentPeriodEnd : str,  subscriptionType : str, nbRowsMaxSubscribed : int) -> bool:
    """
    Insert new API token
    """
    reuslt_request = insert_subscription(userId, status, currentPeriodEnd, subscriptionType, nbRowsMaxSubscribed)

    if reuslt_request == True:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )