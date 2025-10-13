from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from core.checking import get_session_token


from core.dev_token.dev_token_delete import delete_dev_token


router = APIRouter()
security = HTTPBearer()


# Supprime le token d'un utilisateur
@router.delete("/dev/delete_token/{token_id}")
async def delete_token(token_id: str, user_id: str = Depends(get_session_token)):
    response = delete_dev_token(token_id)
    if response is False:
        raise HTTPException(status_code=400, detail="Error while deleting token")
    return {"message": "Dev token deleted!"}
