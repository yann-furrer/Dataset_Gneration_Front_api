import os, sys, uuid
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer

from database.queries.security import (
    check_session_token,
    check_user_api_token,
    check_user_suscription_limit,
)
from database.queries.datamesh import (
    insert_dataset_config,
    delete_datamesh_by_datamesh_id,
    select_datamesh_by_datamesh_id,
    select_all_datamesh_by_user_id,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
load_dotenv()


router = APIRouter()
security = HTTPBearer()


def core_insert_dataset_config(
    datameshId: str, userId: str, datameshData: dict, datameshName: str
) -> bool:
    try:
        insert_dataset_config(datameshId, userId, datameshData, datameshName)
        return True
    except Exception as e:
        print("Error while inserting datamesh config", e)
        return False


def core_delete_datamesh_by_datamesh_id(datameshId: str, userId: str) -> bool:
    try:
        delete_datamesh_by_datamesh_id(datameshId, userId)
        return True
    except Exception as e:
        print(f"Error while deleting datamesh by datamesh id + {userId}", e)
        return False


def core_select_datamesh_by_datamesh_id(datameshId: str, userId: str) -> bool:
   
        result_request = select_datamesh_by_datamesh_id(datameshId, userId)
        if result_request is False:
            data_dict = {
                "id": "vide",
                "datameshId": "vide",
                "datameshName":"vide",
                "datameshData": "vide",
            }
            return data_dict
        else:
             data_dict = [
            {
                "id": item[0],
                "datameshId": item[1],
                "datameshName": item[2],
                "updatedAt": item[3],
            }
            for item in result_request
        ]





def core_select_all_datamesh_by_user_id(userId: str, offset: int) -> bool:
    result_request = select_all_datamesh_by_user_id(userId, offset)
    if result_request is False:
        data_dict = [
            {
                "id": "vide",
                "datameshId": "vide",
                "datameshName":"vide",
                "updatedAt": "vide",
            }
            
                    ]
        return data_dict
    
    data_dict = [
            {
                "id": item[0],
                "datameshId": item[1],
                "datameshName": item[2],
                "updatedAt": item[3],
            }
            for item in result_request
        ]
    return data_dict
