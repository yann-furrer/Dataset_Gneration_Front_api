
import os , sys, re
from fastapi import APIRouter, HTTPException, Request, Depends
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

