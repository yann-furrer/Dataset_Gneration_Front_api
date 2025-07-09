
import os , sys, json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import  HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_limit_credit, get_session_token
from core.user import insert_subscription
router = APIRouter()
security = HTTPBearer()  

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
