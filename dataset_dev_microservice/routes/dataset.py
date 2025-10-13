import os
import sys
import uuid
from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
    Query,
    HTTPException,
    Request,
    Depends,
    BackgroundTasks,
    Body,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from utils.config_utils import (
    get_dataset_config_from_dataset_config_id,
    get_rules_config_from_dataset_config_id,
)
from core.dev_token.dev_token_update import (
    core_update_api_credit_on_user,
    core_update_quota_used_by_token,
)
from core.checking import (
    check_dev_token,
    get_dev_token_info,
    core_select_api_credit_from_token,
    core_select_user_id_from_token,
)
from core.dev_utils import check_yaml_is_valid
from core.queue_config import send_message_to_celery_queue, TaskSchema
from schema.dataset_shema import (
    GenerateDatasetRequest,
    CheckYamlSuccessResponse,
    CheckYamlRequest,
    CheckYamlErrorDetail,
)

# stock tout les processus de génération en cours
generation_processes_list = {}

router = APIRouter()
security = HTTPBearer()


# utilitaire
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
        "Un token développeur valide est requis pour accéder à cette route."
        "Le statut retourné peut être : `waiting`, `running`, `success`, `error`, ou `None` si le processus est inconnu."
        "Lorsque le statut est `success`, un champs supplémentaire `s3_url` est retourné contenant le dataset généré. Attention, "
        "ce champs n'est disponible que 15 minutes avant expiration"
    ),
)
async def ping_generation_process(
    process_id: str = Query(
        ..., description="Identifiant unique du processus de génération"
    ),
    _=Depends(check_dev_token),
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


@router.post(
    "/dev/generate_dataset",
    summary="Générer un dataset (IDs de config OU contenu inline)",
    description=(
        "Cette route lance une génération de dataset en **mode dev**.\n\n"
        "Vous pouvez fournir **soit** des identifiants de configuration (`dataset_config_id`, `rules_config_id`),\n"
        "**soit** le contenu directement via `yaml_content` et/ou `rules_content`.\n\n"
        "• `dataset_config_id` *(optionnel)* : si renseigné, le contenu YAML stocké côté serveur **remplace** `yaml_content`.\n"
        "• `rules_config_id` *(optionnel)* : si renseigné, le contenu des règles côté serveur **remplace** `rules_content`.\n"
        "• `yaml_content` *(optionnel)* : contenu YAML converti en JSON quand vous n'utilisez pas `dataset_config_id`.\n"
        "• `rules_content` *(optionnel)* : règles en JSON quand vous n'utilisez pas `rules_config_id`.\n\n"
        "Priorité : en cas de doublon, **les IDs priment** sur les contenus inline.\n"
        "Crédit : le nombre de lignes (`numberOfRecords`) dans `yaml_content` détermine la consommation de crédits."
    ),
)
async def generate_dataset(
    request: Request,
    api_key: str,
    nb_credit: int = Depends(core_select_api_credit_from_token),
    body: GenerateDatasetRequest = Body(...),
):
    print("api_key -->", api_key)
    print("nb_credit -->", nb_credit)

    process_id = uuid.uuid4()
    celery_queue_id = uuid.uuid4()
    dataset_row_id = uuid.uuid4()
    user_id = core_select_user_id_from_token(api_key)
   
    # cas ou l'on passe directement des id
    dataset_config_id = body.dataset_config_id
    rules_id = body.rules_config_id  # id d'un rules config
    yaml_content = body.yaml_content or {}
    rules_content = body.rules_content or {}
    if dataset_config_id != "":
        yaml_content: dict = get_dataset_config_from_dataset_config_id(
            dataset_config_id, user_id
        )
    if rules_id != "":
        rules_content: dict = get_rules_config_from_dataset_config_id(
            rules_id, dataset_config_id, user_id
        )
    end_format = body.end_format
    dataset_name = yaml_content.get("datasetName", "dataset")
    nb_rows = yaml_content.get("numberOfRecords", 1000)
    faker_name_dict = body.faker_name_dict

    # check if token has enough credit
    if nb_credit * 1.1 < nb_rows:  # marge de 10%
        raise HTTPException(
            status_code=400,
            detail="Not enough credit",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # # Validation manuelle
    if any(value is None for value in [process_id, end_format, yaml_content, nb_rows]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields in the request body or None value",
        )

    send_message_to_celery_queue(
        TaskSchema(
            dataset_row_id=dataset_row_id,
            id=celery_queue_id,
            function="preprocessing_generation",
            dataset_name=dataset_name,
            client_id=process_id,
            end_format=end_format,
            yaml_content=yaml_content,
            rules=rules_content,
            dataset_config="__",
            faker_name_dict=faker_name_dict,
            request_type="dev",
        )
    )

    generation_processes_list[str(process_id)] = "waiting"
    print(generation_processes_list)

    # met à jour le nombre de crédits restant
    core_update_api_credit_on_user(user_id, nb_rows, operation="substract")
    # met à jour le nombre de crédits utilisés
    core_update_quota_used_by_token(api_key, nb_rows)
    return {
        "message": "Dataset {dataset_name} ajouter à queue ! with process_id {process_id}",
        "process_id": process_id,
        "nb_credit_used": nb_credit,
    }
    # return {"message": "Dataset {dataset_name} ajouter à queue ! with process_id {process_id}", "process_id": process_id}


@router.post("/dev/update_process_status/{process_id}")
async def update_process_status(request: Request, process_id: str):
    """
    update_process_status

    """
    body = await request.json()
    status = body.get("status", "unknown")
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
    description="Cette route prend un contenu YAML (déjà transformé en JSON), le valide et renvoie soit un succès, soit une liste d'erreurs.",
)
async def check_yaml(request_body: CheckYamlRequest, _=Depends(check_dev_token)):
    error_list = check_yaml_is_valid(request_body.yaml_content)

    if error_list:
        raise HTTPException(
            status_code=400,
            detail={
                "info": "Error while converting to rules. Check list of errors and fix it.",
                "error": error_list,
                "is_valid": False,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"message": "yaml is valid", "is_valid": True}
