import os
import sys
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.datamesh import core_insert_dataset_config, core_delete_datamesh_by_datamesh_id, core_select_datamesh_by_datamesh_id, core_select_all_datamesh_by_user_id
from core.checking import get_session_token
from fastapi import APIRouter, HTTPException, Request, Depends, Body
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse


router = APIRouter()
security = HTTPBearer()  

@router.post("/datamesh/insert_dataset_config")
async def insert_dataset_config(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    datameshId = body.get("datameshId", None)
    datameshData = body.get("datameshData", None)
    datameshName = body.get("datameshName", None)
    if not datameshId or not datameshData or not datameshName:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_insert_dataset_config(datameshId, userId, datameshData, datameshName)
    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse({"message": "Datamesh config inserted!"})


@router.delete("/datamesh/delete_datamesh_by_datamesh_id")
async def delete_datamesh_by_datamesh_id(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    datameshId = body.get("datameshId", None)
    if not datameshId:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_delete_datamesh_by_datamesh_id(datameshId, userId)
    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail="Error while deleting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse({"message": "Datamesh config deleted!"})


@router.get("/datamesh/get_datamesh_by_datamesh_id")
async def get_datamesh_by_datamesh_id(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    datameshId = body.get("datameshId", None)
    if not datameshId:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_select_datamesh_by_datamesh_id(datameshId, userId)
    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(result_request)


@router.get("/datamesh/get_all_datamesh_by_user_id")
async def get_all_datamesh_by_user_id(request: Request, userId: str = Depends(get_session_token)):
    body = await request.json()
    offset = body.get("offset", None)
    if not offset:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = core_select_all_datamesh_by_user_id(userId, offset)
    if result_request is False:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(result_request)