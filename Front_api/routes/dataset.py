
import os , sys, json, uuid
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import  HTTPBearer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.s3_handle import S3Manager

from core.queue_config import send_message_to_celery_queue, TaskSchema
from core.checking import check_user_limit_credit, get_session_token
from core.user import insert_subscription
#import pour la table dataset config
from core.dataset import insert_dataset_config_info, get_dataset_config_info, get_dataset_config_historical_offset, insert_rules_config_info, insert_dataset_config_and_rules_config_info, select_dataset_config_and_rules_config
#import pour la table Dataset
from core.dataset import inserting_dataset_info, select_all_s3_url_from_dataset, select_dataset_for_historical, update_finished_dataset, update_status_dataset


router = APIRouter()
security = HTTPBearer()  
s3_manager = S3Manager()
# cette route ne génère pas de dataset mais elle permet de sauvegarder la configuration du dataset
# pour l'utilisateur
# pas besoinde vérifier le quota de l'utilisateur car il n'y a pas de génération de dataset
 

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
        result = {"id": result_request[0],"datasetId": result_request[1] ,"userId": result_request[2], "yamlName": result_request[3], "yamlContent": result_request[4], "draftResult": result_request[5], "nbRows": result_request[6], "rulesid": result_request[7], "campaignid": result_request[8]}
        
        return result
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset config",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.get("/dataset/get_dataset_historical")
async def get_dataset_historical(userId : str = Depends(get_session_token), page_number: int = -2):
    """
    Get dataset 
    """
    if page_number < 0:
        raise HTTPException(
            status_code=400,
            detail="page_number must be an integer or superior to 0 or missing in body",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # get_dataset_info
    result_request = select_dataset_for_historical(userId, page_number)
    if result_request != False:
        for item in result_request:
            if item["status"] == "success":
                print("item -->", item)
                item.update( {"S3_URL" : s3_manager.generate_presigned_url(item["clientId"], item["datasetNameSystem"])})
                del item["clientId"]
        return result_request
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while getting dataset historical",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.get("/dataset/get_dataset_config_historical")
# Le -2 permet de créer une erreur si l'utilisateur n'a pas fournit de page number
async def get_dataset_config_historical( userId : str = Depends(get_session_token), page_number: int = -2):
    """
    Get dataset config
    """
    print("page_number -->", page_number)
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
    

  

@router.post("/dataset/save_dataset_config")
async def save_dataset_config_and_rules_config(request: Request , userId : str = Depends(get_session_token)):
    """
    save_dataset_config2

    """
    body = await request.json()
    yamlName = body.get("yamlName" , None)
    client_id = userId
    end_format = body.get("end_format" , None)
    yamlContent = body.get("yaml_content" , None)
    # rules = body.get("rules" , None)
    rulesId = body.get("rulesId" , "idrulestest123")
    rulesName = body.get("rulesName" , "rule nom")
    rulesContent = body.get("rulesContent" , None)
    dataset_config_id = body.get("dataset_config_id" , None)
    campaignid = body.get("campaignid" , None) # pour l'instant on ne prend pas en compte le campaignid
    nbRows = body.get("nbRows" , None)
    body_value_list = [yamlName, client_id, end_format, yamlContent, dataset_config_id, nbRows]

    print("yamlName",yamlName)
    print("client_id",client_id)
    print("end_format",end_format)
    print("yaml_content",yamlContent)
    print("dataset_config_id",dataset_config_id)
    print("nbRows",nbRows)

    draftResult = {"test": "test"}
    if any(value == None for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
            headers={"WWW-Authenticate": "Bearer"},
        )
#a faire 
    result_request = insert_dataset_config_and_rules_config_info(dataset_config_id, userId, yamlName, yamlContent, draftResult, nbRows, rulesId, rulesName, rulesContent, campaignid)
    

        # Ajout de la tache dans la queue rabbitmq
    # send_message_to_celery_queue(TaskSchema(id=celery_queue_id, function="preprocessing_generation", dataset_name=dataset_name, client_id=client_id, end_format=end_format, yaml_content=yaml_content, rules=rules, dataset_config=dataset_config))
    return {"message": "GSave Config and Rules Config!"}




@router.post("/dataset/generate_dataset")
async def generate_dataset(request : Request, userId : str = Depends(get_session_token)):
    """
    generate_dataset

    """
    celery_queue_id =uuid.uuid4()
    dataset_row_id = uuid.uuid4()
    body = await request.json()
    dataset_name = body.get("dataset_name" , "nom du dataset par defaut")
    end_format = body.get("end_format" , None)
    yamlContent = body.get("yaml_content" , None)
    rulesContent = body.get("rulesContent" , None)
    dataset_config_id = body.get("dataset_config_id" , None)
    campaignid = body.get("campaignid" , None) # pour l'instant on ne prend pas en compte le campaignid
    nbRows = body.get("nbRows" , 1)
    function = body.get("function" , "preprocessing_generation") # description of the function to be executed on the celery queue
    body_value_list = [userId, end_format, yamlContent, dataset_config_id, nbRows]
    faker_name_dict = body.get("faker_name_dict" , [])
    # print("--> faker_name_dict",faker_name_dict)

  
    inserting_dataset_info(dataset_row_id ,dataset_config_id, userId, campaignid, "waiting",  nbRows, dataset_name)
    draftResult = {"test": "test"}
    if any(value == None for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
            headers={"WWW-Authenticate": "Bearer"},
        )    

        # Ajout de la tache dans la queue rabbitmq
    send_message_to_celery_queue(TaskSchema(dataset_row_id=dataset_row_id, id=celery_queue_id, function=function, dataset_name=dataset_name, client_id=userId, end_format=end_format, yaml_content=yamlContent, rules=rulesContent, dataset_config=dataset_config_id, faker_name_dict=faker_name_dict))
    return {f"message": "Dataset {dataset_name} ajouter à queue !"}


@router.post("/dataset/update_finished_dataset")
#cette route est uniquement appellé par le back il faudra a terme verfier que c'est bien le back qui appelle
async def update_finished_dataset_info(request: Request ):
    """
    update_finished_dataset

    """
    body = await request.json()
    datasetId = body.get("datasetId" , None)
    dataset_name = body.get("dataset_name" , None)
    status = body.get("status" , "unknown")
    if None in [datasetId, dataset_name, status]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result_request = update_finished_dataset(dataset_name, datasetId, body.get("generationError" , "0"), status)

    if result_request != None:
        return {"message": "Dataset updated !"}
    else:
        return HTTPException(
            status_code=400,
            detail="Error while updating dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

@router.post("/dataset/update_dataset_status")
#cette route est uniquement appellé par le back il faudra a terme verfier que c'est bien le back qui appelle
async def update_dataset_status(request: Request ):
    """
    update_dataset_status

    """
    body = await request.json()
    datasetId = body.get("datasetId" , None)
    if datasetId == None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result_request = update_status_dataset(datasetId, body.get("status" , "unknown"))

    if result_request == True:
        return {"message": "Dataset updated !"}
    else:
        return HTTPException(
            status_code=400,
            detail="Error while updating dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
@router.get("/dataset/get_config_info")
async def get_config_info(datasetId: str, userId : str = Depends(get_session_token)):
    """
    Get dataset config
    """
    if datasetId == None:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result_request = select_dataset_config_and_rules_config(datasetId, userId)
    print("result_request -->", result_request)
    if result_request != None:
        return result_request