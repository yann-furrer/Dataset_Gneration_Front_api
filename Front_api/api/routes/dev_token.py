
import asyncio
import os , sys, re, json
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import generate_user_api_token, get_session_token
from core.dev_token import insert_dev_token
import httpx
from dotenv import load_dotenv
load_dotenv()



router = APIRouter()
security = HTTPBearer()  

DEV_SERVICE_URL = os.getenv("DEV_SERVICE_URL")
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# DEV_SERVICE_URL = os.getenv("DEV_SERVICE_URL",None)
print("DEV_SERVICE_URL:", DEV_SERVICE_URL)
if DEV_SERVICE_URL is None:
    raise ValueError("DEV_SERVICE_URL is not set in the environment variables.")


@router.post("/dev/generate_token")
async def generate_dev_token(request: Request, userId: str = Depends(get_session_token)):
    session_token = dict(request.headers).get('sessiontoken')
    print("session_token -->", session_token)
  
    async with httpx.AsyncClient() as client:
        print("micro service url:", DEV_SERVICE_URL)
        response = await client.post(f"{DEV_SERVICE_URL}/generate_token", headers={"sessiontoken": session_token})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(response.json())


@router.get("/dev/get_tokens_info")
async def get_tokens_info (request: Request, userId: str = Depends(get_session_token)):
    session_token = dict(request.headers).get('sessiontoken')
    print("session_token -->", session_token)
  
    async with httpx.AsyncClient() as client:
        print("micro service url:", DEV_SERVICE_URL)
        response = await client.get(f"{DEV_SERVICE_URL}/get_tokens_info", headers={"sessiontoken": session_token})
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(response.json())

@router.delete("/dev/delete_token")
async def delete_token(request: Request, token_id: str, user_id: str = Depends(get_session_token)):
    session_token = dict(request.headers).get('sessiontoken')
    async with httpx.AsyncClient() as client:
        print("micro service url:", DEV_SERVICE_URL)
        response = await client.delete(f"{DEV_SERVICE_URL}/delete_token/{token_id}", headers={"sessiontoken": session_token})
        print("response:", response)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()