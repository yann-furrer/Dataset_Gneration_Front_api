import os , sys, json
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_limit_credit, get_session_token

from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import httpx

load_dotenv()
MICRO_SERVICE_URL = "https://microservice-dataset-dev.up.railway.app"
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL",None)
print("MICRO_SERVICE_URL:", MICRO_SERVICE_URL)
if MICRO_SERVICE_URL is None:
    raise ValueError("MICRO_SERVICE_URL is not set in the environment variables.")


router = APIRouter()
security = HTTPBearer()  

@router.post("/microservice/dataset_sample")
async def dataset_sample(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    user_prompt = body.get("user_prompt", None)
    if user_prompt is None:
        return JSONResponse({"error": "user_prompt is required"}, status_code=400)
    # Request to the microservice to generate dataset sample
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.post(f"{MICRO_SERVICE_URL}/dataset_sample", json={"user_prompt": user_prompt}, headers={"X-API-KEY": os.getenv("API_KEY")})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    dataset_sample = response.json().get("dataset_sample")
    return JSONResponse({"dataset_sample": dataset_sample})

# genère la config de la structure de données pour le front
@router.post("/microservice/generate_webconfig")
async def generate_dataset_config(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    json_sample = body.get("json_sample", None)
    
    if not json_sample:
        raise HTTPException(
            status_code=400,
            detail="json_sample is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with httpx.AsyncClient(timeout=15) as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.post(f"{MICRO_SERVICE_URL}/generate_webconfig", 
            headers={"X-API-KEY": os.getenv("API_KEY")},
            json={"client_id": userId, "json_sample": json_sample})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return JSONResponse(response.json())


# ressort toutes les nom de type de données faker disponible pour l'id utilisateur
@router.get("/microservice/get_faker_name_list")
async def get_faker_name_list(request: Request, userId: str = Depends(get_session_token)):
   
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.get(f"{MICRO_SERVICE_URL}/faker_name_list/"+userId, 
            headers={"X-API-KEY": os.getenv("API_KEY")},)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return JSONResponse( response.json())



# ressort toutes les nom de type de données faker disponible pour l'id utilisateur
@router.get("/microservice/faker_content_list/{faker_type_id}")
async def get_faker_name_list(request: Request,faker_type_id: str, userId: str = Depends(get_session_token)):
   
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.get(f"{MICRO_SERVICE_URL}/faker_content_list/"+userId+"/"+faker_type_id, 
            headers={"X-API-KEY": os.getenv("API_KEY")},)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return JSONResponse( response.json())


@router.put("/microservice/insert_faker_type")
async def insert_faker_type(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    faker_type_name = body.get("faker_name", None)
    faker_type_id = body.get("faker_type_id", None)
    faker_list = body.get("faker_list", None)
    category = body.get("category", None)

    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.put(f"{MICRO_SERVICE_URL}/insert_faker_type", 
            headers={"X-API-KEY": os.getenv("API_KEY")},
            json={"client_id": userId, "faker_name": faker_type_name, "faker_type_id": faker_type_id, "faker_list": faker_list, "category": category, "description": "None"})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return JSONResponse( response.json())




@router.patch("/microservice/update_faker_type")
async def insert_faker_type(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
   


    faker_type_id = body.get("faker_type_id", None)
    faker_list = body.get("new_faker_list", None)
    print("userId -->", userId)
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.patch(f"{MICRO_SERVICE_URL}/update_faker_type", 
            headers={"X-API-KEY": os.getenv("API_KEY")},
            json={"client_id": userId, "faker_type_id": faker_type_id, "new_faker_list": faker_list})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
    return JSONResponse( response.json())

@router.delete("/microservice/delete_faker_type/{faker_type_id}")





@router.delete("/microservice/delete_faker_type/{faker_type_id}")
async def delete_faker_type(request: Request,faker_type_id: str, userId: str = Depends(get_session_token)):
    
    
    if not faker_type_id:
        raise HTTPException(
            status_code=400,
            detail="faker_type_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.delete(f"{MICRO_SERVICE_URL}/delete_faker_type/{faker_type_id}/{userId}",
            headers={"X-API-KEY": os.getenv("API_KEY")})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return JSONResponse( response.json())