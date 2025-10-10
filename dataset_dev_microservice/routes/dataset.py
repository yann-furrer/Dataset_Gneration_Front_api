
import os
import sys
import uuid
from fastapi.security import  HTTPBearer
from fastapi import APIRouter,Query, HTTPException, Request, Depends, BackgroundTasks, Body
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from core.checking import  check_dev_token, get_dev_token_info
from core.dev_utils import check_yaml_is_valid
from core.queue_config import send_message_to_celery_queue, TaskSchema
from schema.dataset_shema import (
    GenerateDatasetRequest, CheckYamlSuccessResponse, CheckYamlRequest, CheckYamlErrorDetail)

#stock tout les processus de génération en cours
generation_processes_list = {}

router = APIRouter()
security = HTTPBearer()  

#utilitaire
def delete_generation_process(process_id: str, status: str) -> bool:
    """
    delete_generation_process
    """
    if status == "success":
        del generation_processes_list[process_id]



# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `S3 et DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================



@router.get(
    "/dev/ping_generation_process",
    summary="Vérifie le statut d'un processus de génération",
    description=(
        "Cette route permet de vérifier le statut d'un dataset en cours de génération. "
        "Le `process_id` est fourni en tant que paramètre de requête, il preivent de la requête de `/dev/generate_dataset`. "
        "Un token développeur valide est requis pour accéder à cette route." \
        "Le statut retourné peut être : `waiting`, `running`, `success`, `error`, ou `None` si le processus est inconnu."
        "Lorsque le statut est `success`, un champs supplémentaire `s3_url` est retourné contenant le dataset généré. Attention, "
        "ce champs n'est disponible que 15 minutes avant expiration"
    ),
)
async def ping_generation_process(
    process_id: str = Query(..., description="Identifiant unique du processus de génération"),
    _ = Depends(check_dev_token)
):
    """
    Retourne le statut actuel d’un processus de génération de dataset initié via `/dev/generate_dataset`.

    - **process_id** : l’identifiant du processus (UUID) retourné lors de l’appel initial.
    - **status** peut être : `"waiting"`, `"running"`, `"success"`, `"error"`, ou `None` si le processus est inconnu.
    """
    print("process_id -->", process_id)
    print("generation_processes_list -->", generation_processes_list)

    status = generation_processes_list.get(process_id)
    if status is None:
        raise HTTPException(
            status_code=400,
            detail="Le process_id fourni est invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"status": status}


async def generate_dataset(
    request: Request,
    api_key: str = Depends(get_dev_token_info),
    body: GenerateDatasetRequest = Body(...)
):
    print("api_key -->", api_key)
    process_id = uuid.uuid4()
    celery_queue_id = uuid.uuid4()
    dataset_row_id = uuid.uuid4()

    end_format = body.end_format
    yamlContent = body.yaml_content
    dataset_name = yamlContent.get("datasetName")
    nbRows = yamlContent.get("numberOfRecords", 1)
    rulesContent = body.rulesContent
    function = body.function
    faker_name_dict = body.faker_name_dict

    # Validation manuelle
    if any(value is None for value in [process_id, end_format, yamlContent, nbRows]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
        )

    send_message_to_celery_queue(
        TaskSchema(
            dataset_row_id=dataset_row_id,
            id=celery_queue_id,
            function=function,
            dataset_name=dataset_name,
            client_id=process_id,
            end_format=end_format,
            yaml_content=yamlContent,
            rules=rulesContent,
            dataset_config="__",
            faker_name_dict=faker_name_dict,
            request_type="dev"
        )
    )

    generation_processes_list[str(process_id)] = "waiting"

    return {"message": "Dataset {dataset_name} ajouter à queue ! with process_id {process_id}", "process_id": process_id}



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



# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `S3 et DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================



@router.post(
    "/dev/check_yaml",
    response_model=CheckYamlSuccessResponse,
    responses={
        400: {
            "model": CheckYamlErrorDetail,
            "description": "Erreur dans le contenu YAML fourni",
        }
    },
    summary="Valide un contenu YAML transformé en JSON",
    description="Cette route prend un contenu YAML (déjà transformé en JSON), le valide et renvoie soit un succès, soit une liste d'erreurs."
)
async def check_yaml(request_body: CheckYamlRequest, _ = Depends(check_dev_token)):
    error_list = check_yaml_is_valid(request_body.yaml_content)

    if error_list:
        raise HTTPException(
            status_code=400,
            detail={
                "info": "Error while converting to rules. Check list of errors and fix it.",
                "error": error_list,
                "is_valid": False
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": "yaml is valid", "is_valid": True}