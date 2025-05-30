import os , sys, json
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends, Body
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
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
async def dataset_sample(request: Request):
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


@router.post("/microservice/generate_dataset_config")
async def generate_dataset_config(request: Request):
    body = await request.json()
    
    dataset_name = body.get("dataset_name", "new dataset")
    yaml_data = body.get("yaml_data", None)
    number_of_records = body.get("number_of_records", 1000)
    entrytpath = body.get("entrytpath", "root")

    async with httpx.AsyncClient() as client:
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.post(f"{MICRO_SERVICE_URL}/generate_dataset_config", 
            headers={"X-API-KEY": os.getenv("API_KEY")},
            json={"dataset_name": dataset_name, "yaml_data": 
            yaml_data, "number_of_records": number_of_records, 
            "entrytpath": entrytpath})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)