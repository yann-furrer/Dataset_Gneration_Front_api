from fastapi import HTTPException
from core.dev_utils import check_yaml_is_valid
from core.checking import core_select_user_id_from_api_key
from database.queries.dataset_config.dataset_config_update import (
    insert_or_update_dataset_config,
)
import uuid
from psycopg2.extras import Json

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
# ==============================================================


# Ce composant n'a pas besoin de route api il vérifie si la dataset cnfig est bon
def core_check_dataset_config_is_valid(yaml_content: dict, user_id: str, end_format: str) -> bool:
    # ajouter le created at plus tard quand la bdd sera mise à jour connexion pour verifier si le mec possède les types fakers dans la bdd
    error_list: list = check_yaml_is_valid(yaml_content, user_id, end_format)
    if error_list["isvalid"]:
        return {"message": "Dataset config is valid", "is_valid": True}
    else:
        return error_list


def core_insert_dataset_config_and_rules_config_info(
    api_key: str,
    yaml_content: dict,
    draftResult: dict = {"test": "test"},
) -> tuple[bool, str]:
    """
    Ajotue une nouvelle dataset config
    """

    user_id = core_select_user_id_from_api_key(api_key)
    # Verifier si le yaml est valide
    error_list: list = check_yaml_is_valid(yaml_content, user_id)
    if error_list["isvalid"] is False:
        raise HTTPException(
            status_code=400,
            detail={"message": "Error while checking yaml.", "info": error_list},
            headers={"WWW-Authenticate": "Bearer"},
        )

    u = uuid.uuid4()
    dataset_id = str(u.hex)
    dataset_name = yaml_content.get("datasetName", "dataset")
    nb_rows = yaml_content.get("numberOfRecords", 1000)
    print(dataset_id)
    result_request_dataset_config = insert_or_update_dataset_config(
        dataset_id=dataset_id,
        user_id=user_id,
        yaml_name=dataset_name,
        yaml_content=Json(yaml_content),
        draft_result=Json({"test": "test"}),
        nbRows=nb_rows,
    )
    print("result_request_dataset_config",result_request_dataset_config)
    if result_request_dataset_config:
        return (True, dataset_id)
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset config or dataset rules config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )
