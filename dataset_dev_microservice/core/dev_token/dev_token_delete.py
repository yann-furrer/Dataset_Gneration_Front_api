import os
import sys
from fastapi import HTTPException
from database.queries.dev_token.dev_token_delete import (
    delete_api_token,
)

from core.dev_utils import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))




def delete_dev_token(token_id: str) -> bool:
    """
    Delete API token
    """
    result_request = delete_api_token(token_id)
    if result_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while deleting token",
            headers={"WWW-Authenticate": "Bearer"},
        )