
import os , sys, json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import  HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_limit_credit, get_session_token
from core.user import insert_subscription, insert_subscription_for_connexion_callback, get_subscription, update_quota
router = APIRouter()
security = HTTPBearer()  



@router.get("/user/update_quota")
async def update_quota_consumption(userId : str, nbRows: str):
    """
    Add subscription to user
    """
    result_request : bool = update_quota(userId, int(nbRows))
    print("result_request -->", result_request)
    return {"message": "Quota updated!"}



@router.get("/user/get_subscription")
async def get_subscription_type(userId : str):
    """
    Add subscription to user, en cas d'erreur renvoie l'abonnement explorer (le gratuit et le plus limité)
    """
    sub = get_subscription(userId)
    print("sub -->", sub)
    print(sub)
    return {"subscriptionType": sub}

# Utilisable que par stripe pour la création de la souscription
@router.post("/user/launch_subscription")
async def launch_subscription(request: Request, userId: str):
    """
    Add subscription to user
    """
    a = insert_subscription_for_connexion_callback(userId, "en cours")
    # Check if the user is already subscribed
    return {"message": "Subscription added!"}
   

# Utilisable que par stripe pour la création de la souscription

@router.get("/add_suscription")
async def add_subscription(request: Request , userId : str = Depends(get_session_token)):
    print("userId -->", userId)
    """
    Add subscription to user
    """
    print(request)
    # Check if the user is already subscribed
    # if check_user_subscription(userId) == True:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="User is already subscribed",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    # Insert new subscription
    result_request = insert_subscription(userId, "2023-10-01", "free", 1000)
    
    if result_request == True:
        return {"message": "Subscription added!"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while adding subscription maybe duplicate susbcription",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.get("/generete_request")
async def generete_request(request: Request , userId : str = Depends(check_user_limit_credit)):
        """
        Add subscription to user
        """
        body = await request.json()
        nb_rows_to_generate = body.get("nb_rows_to_generate" , 0)
      
      
        return {"message": "Request generated!"}
