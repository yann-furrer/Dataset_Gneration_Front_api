from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from core.checking import     get_session_token


from core.dev_token.dev_token_select import (
    core_select_dev_token_info, core_select_api_credit_from_user_id,
    core_select_consumption_token_by_user_id
)


router = APIRouter()
security = HTTPBearer()


@router.get("/dev/get_consumption_info")
async def get_consumption_info(user_id: str = Depends(get_session_token)):
    response = core_select_consumption_token_by_user_id(user_id)
    return response

@router.get("/dev/get_tokens_info")
async def get_tokens_info(user_id: str = Depends(get_session_token)):
    response = core_select_dev_token_info(user_id)
    return response


@router.get("/dev/get_credit_info")
async def get_credit_info(user_id: str = Depends(get_session_token)):
    response = core_select_api_credit_from_user_id(user_id)

    return response