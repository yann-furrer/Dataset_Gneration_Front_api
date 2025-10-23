from fastapi.security import HTTPBearer
from database.redis.redis_config import RedisManager
from fastapi import APIRouter, HTTPException, Depends, Query
from core.checking import check_dev_token, core_select_user_id_from_api_key
from core.dataset.dataset_select import core_select_all_s3_url_from_dataset
from core import s3_handle

router = APIRouter()
security = HTTPBearer()
Redis = RedisManager()
S3manager = s3_handle.S3Manager()


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
    responses={
        200: {
            "description": "Requête réussie — le statut du processus de génération.",
            "content": {
                "application/json": {
                    "example": {
                            "status": {
                                "status": "waiting",
                                "pourcentage": 0,
                                "nb_rows": 1000000,
                                "current_rows": 0
                            }
                    }
                }
            },
        },
            400: {
            "description": "API Key invalide",
            "content": {
                "application/json": {
                    "example": {    "detail": "Le process_id fourni est invalide ou expiré."
}
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
        500: {
            "description": "Erreur interne du serveur.",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def ping_generation_process(
    process_id: str = Query(
        ..., description="Identifiant unique du processus de génération"
    ),
        api_key: str = Query(..., description="Clé API"),
    _ =Depends(check_dev_token, use_cache=True),
):
    """
    Retourne le statut actuel d’un processus de génération de dataset initié via `/dev/generate_dataset`.

    - **process_id** : l’identifiant du processus (UUID) retourné lors de l’appel initial.
    - **status** peut être : `"waiting"`, `"running"`, `"success"`, `"error"`, ou `None` si le processus est inconnu.
    """
    status = Redis.get(process_id)
    # status = generation_processes_list.get(process_id)
    if status is None:
        raise HTTPException(
            status_code=400,
            detail="Le process_id fourni est invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"status": status}


# S3 bucket
@router.get(
    "/dev/dataset_list",
    summary="Retourne la liste des datasets généré téléchargeable",
    description=(
        "Retourne la liste des datasets généré téléchargeable"
        "`datasetName` : nom du dataset , "
        "`datasetNameSystem` : nom du dataset avec un id lors de la génération (nom conservé  dans le bucket s3) ,"
        "`nbRows` : nombre de lignes du dataset ,"
        "`datasetConfigId` : id du dataset config ,"
        "`createdAt` : date de création du dataset"
    ),
    tags=["S3"],
    responses={
        200: {
            "description": "Requête réussie — la liste des datasets généré téléchargeable.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "datasetName": "NouveauDataset",
                            "datasetNameSystem": "NouveauDataset269457de-e788-4af9-80ef-c72dd035c5fc.json",
                            "nbRows": 1212300,
                            "datasetConfigId": "bfa0389da4f2485497e74fd4ab7f3f98",
                            "createdAt": "2025-10-13T09:30:19.770000",
                        },
                        {
                            "datasetName": "Nouveau Dataset",
                            "datasetNameSystem": "Nouveau Datasetad3dc7b4-5433-4c22-8699-798dd1c259a0.json",
                            "nbRows": 102220,
                            "datasetConfigId": "ea1e330dd6b34dbe96612f7a4fdfc8e9",
                            "createdAt": "2025-10-13T10:10:03.359000",
                        },
                    ]
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
        500: {
            "description": "Erreur interne du serveur.",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def list_dataset_to_download(api_key: str = Query(..., description="API key")):
    """
    Retourne la liste des datasets à télécharger
    """
    user_id = core_select_user_id_from_api_key(api_key)
    dataset_list = core_select_all_s3_url_from_dataset(user_id)

    return dataset_list


@router.get(
    "/dev/dataset_download_link",
    summary="Retourne le lien de téléchargement d'un dataset",
    description=(
        "Retourne le lien de téléchargement d'un dataset à partir du nom du dataset"
        "Le lien de téléchargement est généré automatiquement par le back pour une duré de 15 minutes"
        " Le paramètre `dataset_name_system` est le nom du dataset avec un id lors de la génération (nom conservé  dans le bucket s3)"
        " Le paramètre `api_key` est requis pour accéder à cette route."
    ),
    tags=["S3"],
    responses={
        200: {
            "description": "Requête réussie — le lien de téléchargement d'un dataset.",
            "content": {
                "application/json": {
                    "example": {
                        "dataset_name": "NouveauDataset269457de-e78fc.json",
                        "url": "https://dataset-generation-endpoint-storage.s3.amazonaws.com/user_id/NouveauDataset269457de-e78fc.json",
                        "expire time": "15mn",
                    }
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
        500: {
            "description": "Erreur interne du serveur.",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def dataset_to_download(
    api_key: str = Query(..., description="API key"),
    dataset_name_system: str = Query(..., description="Nom du dataset"),
):
    """
    Retourne le lien de téléchargement d'un dataset
    """
    user_id = core_select_user_id_from_api_key(api_key)
    print("user_id -->", user_id)
    print("dataset_name_system", dataset_name_system)
    link = S3manager.generate_presigned_url(user_id, dataset_name_system)
    return {"url": link, "dataset_name": dataset_name_system, "expire time": "15mn"}
