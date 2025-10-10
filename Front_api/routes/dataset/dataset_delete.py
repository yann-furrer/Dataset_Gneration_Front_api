import os
import sys

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.s3_handle import S3Manager

from core.checking import get_session_token

 


# import pour la table Dataset
from core.dataset.dataset_delete import core_delete_dataset_by_dataset_id



load_dotenv()


MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL")
API_KEY = os.getenv("API_KEY")  # À changer/environner en production !
# MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL",None)
print("MICRO_SERVICE_URL:", MICRO_SERVICE_URL)
if MICRO_SERVICE_URL is None:
    raise ValueError("MICRO_SERVICE_URL is not set in the environment variables.")




router = APIRouter()
security = HTTPBearer()
s3_manager = S3Manager()





@router.delete("/dataset/delete_dataset_historical")
async def delete_dataset_historical_route(
    config_system_name: str, datasetId: str, userId: str = Depends(get_session_token)
):
    """
    Delete dataset form his s3 bucket
    """
    delete_result = s3_manager.delete_s3_file(userId, config_system_name)
    print("delete_result -->", delete_result)
    if delete_result:
        print("delete_result 2 -->", delete_result)
        print("datasetId -->", datasetId)
        print("userId -->", userId)
        delete_db_repsonse = core_delete_dataset_by_dataset_id(datasetId, userId)

        if delete_db_repsonse:
            return {"message": "Dataset deleted!"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Error while deleting dataset",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
