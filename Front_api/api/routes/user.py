
import os , sys, json, httpx
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import  HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_limit_credit, get_session_token
from core.user import insert_subscription, insert_subscription_for_connexion_callback, get_subscription, update_quota, get_rows_generated, get_statistics



MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL")
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL",None)
print("MICRO_SERVICE_URL:", MICRO_SERVICE_URL)
if MICRO_SERVICE_URL is None:
    raise ValueError("MICRO_SERVICE_URL is not set in the environment variables.")


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


# Statistique pour l'abonnment
@router.get("/statistics/generated_row_monthly")
async def get_rows_generated_monthly(userId : str = Depends(get_session_token)):
        """
        Add subscription to user
        """
        data = get_rows_generated(userId)
        if data == False:
            raise HTTPException(
                status_code=400,
                detail="Error while getting dataset historical",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if data == None:
             return {"nbrows": list(range(1, 31)), "day_number":  [0] * 30}
        

        return {"nbrows": data[0], "day_number": data[1]}

@router.get("/statistics/get_main_statistics")
async def get_main_statistics(userId : str = Depends(get_session_token)):
        """
        Add subscription to user
        """
        data = get_statistics(userId)
        if data == False:
            raise HTTPException(
                status_code=400,
                detail="Error while getting dataset historical",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return{"nbrows": data[0], "number_of_dataset": data[1]}




# /get_sum_of_faker_type


@router.get("/microservice/count_faker_type/")
async def delete_faker_type(userId: str = Depends(get_session_token)):
    
    
    
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.get(f"{MICRO_SERVICE_URL}/get_sum_of_faker_type?client_id={userId}",
            headers={"X-API-KEY": os.getenv("API_KEY")})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return JSONResponse( response.json())