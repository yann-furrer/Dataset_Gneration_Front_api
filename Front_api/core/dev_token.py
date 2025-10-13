import os, sys, uuid
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer
from database.queries.dev_api import (
    insert_api_token,
    delete_api_token,
    update_quota_used,
)


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


def insert_dev_token(
    userId: str, token: str, tokenPreview: str, quotaUsed: int, price: float, limit: int
) -> bool:
    """
    Insert new API token
    """
    reuslt_request = insert_api_token(
        userId, token, tokenPreview, quotaUsed, price, limit
    )
    if reuslt_request == True:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting new token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def delete_dev_token(token: str) -> bool:
    """
    Delete API token
    """
    reuslt_request = delete_api_token(token)
    if reuslt_request == True:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def update_dev_quota_used(token: str, new_quota_used_to_sum: int) -> bool:
    """
    Update quota used
    """
    reuslt_request = update_quota_used(token, new_quota_used_to_sum)
    if reuslt_request == True:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating quota used",
            headers={"WWW-Authenticate": "Bearer"},
        )
