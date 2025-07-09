
import asyncio
import os , sys, re, json
from fastapi.responses import StreamingResponse
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_api_token, get_session_token
from core.dev_token import generate_token, insert_dev_token, delete_dev_token, list_dev_tokens, update_quota_used



router = APIRouter()
security = HTTPBearer()  



# Liste tout les tokens d'un utilisateur
@router.get("/get_tokens_info")
async def get_tokens_info(user_id: str = Depends(get_session_token)):
    response = list_dev_tokens(user_id)
    return response
# Vérifie si le token est valide
@router.get("/generate_token")
async def dev_token(user_id: str = Depends(get_session_token)):
    token = generate_token()
    limit = -1
    insert_dev_token(user_id, limit)
    return {"message": "Dev token granted!", "token": token}

#Supprime le token d'un utilisateur
@router.delete("/delete_token/{token_id}")
async def delete_token(token_id: str, user_id: str = Depends(get_session_token)):
    response = delete_dev_token(token_id)
   
    return {"message": "Dev token deleted!"}    

@router.post("/update_token_limit/{token_id}")
async def update_token(token_id: str, limit: int, user_id: str = Depends(get_session_token)):
    pass


#route utiliser par le front pour mettre à jour le quota utilisé
@router.post("/update_token_quota/{token}")
async def update_token_used(token: str, new_quota_used_to_sum: int, user_id: str = Depends(get_session_token), _ = Depends(check_user_api_token)):
    response = update_quota_used(token, new_quota_used_to_sum)
    return {"message": "Dev token updated!"}

    