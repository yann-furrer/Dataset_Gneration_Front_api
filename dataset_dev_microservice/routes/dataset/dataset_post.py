import uuid
from database.redis.redis_config import RedisManager
from fastapi.security import HTTPBearer
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    Body,
)
from core.queue_config import send_message_to_celery_queue, TaskSchema
from schema.dataset_shema import (
    GenerateDatasetRequest,
    GenerateDatasetResponse,
)
from core.checking import (
    core_select_api_credit_from_token,
    core_select_user_id_from_api_key,
)
from utils.config_utils import (
    get_dataset_config_from_dataset_config_id,
    get_rules_config_from_dataset_config_id,
)
from core.dev_token.dev_token_update import (
    core_update_api_credit_on_user,
    core_update_quota_used_by_token,
)

router = APIRouter()
security = HTTPBearer()
Redis = RedisManager()


@router.post(
    "/dev/generate_dataset",
    summary="Générer un dataset (IDs de config OU contenu inline)",
    response_model=GenerateDatasetResponse,
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
    responses={
        200: {
            "description": "Requête réussie — la liste des types Faker est renvoyée.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Dataset yannfurrer ajouté à la queue avec process_id 745abf24-5cf9-43de-b5ef-fb96551e441b",
                        "process_id": "745abf24-5cf9-43de-b5ef-fb96",
                        "nb_credit_used": 12130,
                        "nb_credit_remaining": 1002118520,
                    }
                }
            },
        },
        400: {
            "description": "API Key invalide",
            "content": {
                "application/json": {
                    "example": {"detail": "La parameter `end_format` doit être json, csv, xml ou sql"}
        }
            },
        },
            401: {
            "description": "API Key invalide",
            "content": {
                "application/json": {
                    "example": {"detail": "Error Api keys not recognized"}
                }
            },
        },
    },  

)
async def generate_dataset(
    request: Request,
    api_key: str,
    nb_credit: int = Depends(core_select_api_credit_from_token),
    body: GenerateDatasetRequest = Body(...),
):
    print("api_key -->", api_key)
    print("nb_credit -->", nb_credit)

    process_id = str(uuid.uuid4())
    celery_queue_id = uuid.uuid4()
    dataset_row_id = uuid.uuid4()
    user_id = core_select_user_id_from_api_key(api_key)

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
    if end_format not in ["json", "csv", "xml", "sql"]:
        raise HTTPException(
            status_code=400,
            detail="end_format must be json, csv, xml or sql",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
            client_id=user_id,
            end_format=end_format,
            yaml_content=yaml_content,
            rules=rules_content,
            dataset_config="__",
            faker_name_dict=faker_name_dict,
            request_type="dev",
            dev=True,
            dev_process_id=process_id,
        )
    )

    # generation_processes_list[str(process_id)] = "waiting"
    (
        Redis.set_value(
            process_id,
            {
                "status": "waiting",
                "pourcentage": 0,
                "nb_rows": nb_rows,
                "current_rows": 0,
            },
        ),
    )

    # print(generation_processes_list)

    # met à jour le nombre de crédits restant
    core_update_api_credit_on_user(user_id, nb_rows, operation="substract")
    # met à jour le nombre de crédits utilisés
    core_update_quota_used_by_token(api_key, nb_rows)

    return GenerateDatasetResponse(
        message=f"Dataset {dataset_name} ajouté à la queue avec process_id {process_id}",
        process_id=str(process_id),
        nb_credit_used=int(nb_rows),
        nb_credit_remaining=int(nb_credit),
    )


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
    data = Redis.get(process_id)
    data["status"] = status
    Redis.set_value(process_id, data)
    # generation_processes_list[process_id] = status
    # BackgroundTasks.run_task(delete_generation_process, process_id, status)
    return {"message": "Generation process updated !"}
