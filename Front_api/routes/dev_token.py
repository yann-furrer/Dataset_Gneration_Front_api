
import asyncio
import os , sys, re, json
from fastapi.responses import StreamingResponse
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import generate_user_api_token, get_session_token
from core.dev_token import insert_dev_token



router = APIRouter()
security = HTTPBearer()  

@router.get("/generate_token")
async def dev_token(request: Request, user_id: str = Depends(get_session_token)):
    token = generate_user_api_token()
    tokenPreview = token[:5] + "..." + token[-5:]
    insert_dev_token(user_id, token, tokenPreview, 0, 0, 0)
    return {"message": "Dev token granted!","user": user_id , "token": generate_user_api_token()}




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