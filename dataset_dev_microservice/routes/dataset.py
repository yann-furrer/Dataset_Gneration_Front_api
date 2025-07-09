
import os , sys, json, uuid
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from fastapi.security import  HTTPBearer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from core.queue_config import send_message_to_celery_queue, TaskSchema
from core.checking import  check_user_api_token, check_dev_token

from core.queue_config import send_message_to_celery_queue, TaskSchema


router = APIRouter()
security = HTTPBearer()  

generation_processes_list = {}

def delete_generation_process(process_id: str, status: str) -> bool:
    """
    delete_generation_process
    """
    if status == "success":
        del generation_processes_list[process_id]


@router.post("/dev/generate_dataset")
async def generate_dataset(request : Request, _ : str = Depends(check_user_api_token)):
    """
    generate_dataset

    """
    process_id= uuid.uuid4()
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
    body_value_list = [process_id, end_format, yamlContent, dataset_config_id, nbRows]
    faker_name_dict = body.get("faker_name_dict" , [])
    draftResult = {"test": "test"}
    if any(value == None for value in body_value_list):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
            headers={"WWW-Authenticate": "Bearer"},
        )    

        # Ajout de la tache dans la queue rabbitmq
    send_message_to_celery_queue(TaskSchema(dataset_row_id=dataset_row_id, id=celery_queue_id, function=function, dataset_name=dataset_name, client_id=process_id, end_format=end_format, yaml_content=yamlContent, rules=rulesContent, dataset_config=dataset_config_id, faker_name_dict=faker_name_dict, request_type="dev"))
    # Ajout de la tache dans la liste des taches en cours
    generation_processes_list[str(process_id)] = "waiting"
    return {f"message": "Dataset {dataset_name} ajouter à queue ! with process_id {process_id}", "process_id": process_id}




@router.post("/dev/update_process_status/{process_id}")
async def update_process_status(request: Request, process_id: str):
    """
    update_process_status

    """
    body = await request.json()
    status = body.get("status" , "unknown")
    if None in [process_id, status]:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    generation_processes_list[process_id] = status
    BackgroundTasks.run_task(delete_generation_process, process_id, status)
    return {"message": "Generation process updated !"}


# Cette route est pingée par le back pour vérifier si le process_id est valide
@router.get("/dev/get_generation_status/{process_id}")
async def get_generation_status(process_id: str, _  = Depends(check_dev_token)):
    """
    get_generation_status

    """
    status = generation_processes_list.get(process_id, None)
    if status == None:
        raise HTTPException(
            status_code=400,
            detail="Error while getting generation status youe process_id is not valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return status