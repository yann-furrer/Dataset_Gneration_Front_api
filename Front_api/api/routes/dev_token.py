
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


@router.get("/dev/generate_token")
async def generate_dev_token(request: Request, userId: str = Depends(get_session_token)):
    session_token = dict(request.headers).get('sessiontoken')
    print("session_token -->", session_token)
  
    async with httpx.AsyncClient() as client:
        print("micro service url:", DEV_SERVICE_URL)
        response = await client.post(f"{DEV_SERVICE_URL}/generate_token", headers={"sessiontoken": session_token})
        print("response:", response.json())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    return JSONResponse(response.json())



user_connections = {}

@router.get("/dev/sse/{token}")
async def sse(user_id: str = Depends(get_session_token)):
    if user_id not in user_connections:
        user_connections[user_id] = asyncio.Queue()

    async def event_generator():
        try:
            while True:
                message = await user_connections[user_id].get()
                yield f"data: {json.dumps({'message': message})}\n\n"
        except asyncio.CancelledError:
            del user_connections[user_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")





@router.post("/sse/notify/{user_id}")
async def notify(user_id: str, message: Dict[str, Any] = Body(...)):
    print("user connected", user_connections)
    if user_id not in user_connections:
        raise HTTPException(status_code=404, detail="Utilisateur non connecté")
    
    
    await user_connections[user_id].put(message)
    return {"status": "success", "message": "Notification envoyée"}