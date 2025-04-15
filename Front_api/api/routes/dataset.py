
import os , sys, json
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import  HTTPBearer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from core.checking import check_user_limit_credit, get_session_token
from core.user import insert_subscription
#import pour la table dataset config
from core.dataset import insert_dataset_config_info, get_dataset_config_info, get_dataset_config_historical_offset
#import pour la table Dataset
from core.dataset import insert_dataset_info, select_all_s3_url_from_dataset, select_dataset_for_historical
router = APIRouter()
security = HTTPBearer()  

# cette route ne génère pas de dataset mais elle permet de sauvegarder la configuration du dataset
# pour l'utilisateur
# pas besoinde vérifier le quota de l'utilisateur car il n'y a pas de génération de dataset
@router.post("/dataset/save_dataset_config")
async def save_dataset_config(request: Request , userId : str = Depends(get_session_token)):
    """
    Save dataset to user
    """
    body = await request.json()
    datasetId = body.get("datasetId" , "")
    yamlName = body.get("yamlName" , "")
    yamlContent = body.get("yamlContent" , "")
    draftResult = body.get("draftResult" , "")
    nbRows = body.get("nbRows" , "")
    body_value_list = [datasetId, yamlName, yamlContent, draftResult, nbRows]

    if any(value == "" for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = insert_dataset_config_info(datasetId, userId, yamlName, json.dumps(yamlContent), json.dumps(draftResult), nbRows)

    if result_request == True:
        return {"message": "Dataset saved!"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error when saving dataset, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

# cette route permet de récupérer la configuration du dataset
# elle ne génère pas de dataset donc pas besoin de vérifier le quota de l'utilisateur
@router.get("/dataset/get_dataset_config")
async def get_dataset(request: Request , userId : str = Depends(get_session_token)):
    """
    Get dataset config
    """
    body = await request.json()
    datasetId = body.get("datasetId" , "")
    print("datasetId -->", datasetId)
    if datasetId == "":
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = get_dataset_config_info(datasetId, userId)

    if result_request != None:
        return {"id": result_request[0],"datasetId": result_request[1] ,"userId": result_request[2], "yamlName": result_request[3], "yamlContent": result_request[4], "draftResult": result_request[5], "nbRows": result_request[6], "rulesid": result_request[7], "campaignid": result_request[8]}
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
# Il faudra faire une route qui permet de faire un appel en lot de 10 requetes
# pour eviter la surcharge de la base de donnée
@router.get("/dataset/get_s3_url")
async def get_s3_url(userId : str = Depends(get_session_token)):
    """
    Get S3 url
    """
    # body = await request.json()
    # datasetId = body.get("datasetId" , "")
    # ownerId = body.get("ownerId" , "")
    if userId == "":
        raise HTTPException(
            status_code=400,
            detail="User Not Found or error in the request please check session token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = select_all_s3_url_from_dataset(userId)
    
    if result_request != None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Error while getting S3 url from userid not found",
            headers={"WWW-Authenticate": "Bearer"},
        )       
    
@router.post("/dataset/get_dataset_historical")
async def get_dataset_historical(request : Request, userId : str = Depends(get_session_token)):
    """
    Get dataset 
    """
    body = await request.json()
    page_number = body.get("page_number" , 0)
    if type(page_number) != int:
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if page_number < 0:
        raise HTTPException(
            status_code=400,
            detail="page_number must be a positive integer",
            headers={"WWW-Authenticate": "Bearer"},
            )
        
    result_request = select_dataset_for_historical(userId, page_number)

    if result_request != None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.post("/dataset/get_dataset_config_historical")
async def get_dataset_config_historical(request : Request, userId : str = Depends(get_session_token)):
    """
    Get dataset config
    """
    body = await request.json()
    page_number = body.get("page_number" , 0)
    if type(page_number) != int:
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if page_number < 0:
        raise HTTPException(
            status_code=400,
            detail="page_number must be a positive integer",
            headers={"WWW-Authenticate": "Bearer"},
            )
        
    result_request = get_dataset_config_historical_offset(userId, page_number)

    if result_request != None:
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )