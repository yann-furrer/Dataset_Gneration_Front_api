import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException
from core.checking import check_var_is_none


# dataset config
from database.queries.dataset import insert_dataset_config

# dataset
from database.queries.dataset import insert_dataset_info, insert_rules_config


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASETCONFIG` et `RULESCONFIG`.
# ==============================================================


# def insert_dataset_config_info(
#     datasetId: str,
#     userId: str,
#     yamlName: str,
#     yamlContent: str,
#     draftResult: str,
#     nbRows: int,
# ) -> bool:
#     """
#     save dataset config
#     """
#     reuslt_request = insert_dataset_config(
#         datasetId, userId, yamlName, yamlContent, draftResult, nbRows
#     )

#     if reuslt_request:
#         return True
#     else:
#       raise HTTPException(
#             status_code=400,
#             detail="Error while inserting dataset config , try again your yaml is not saved, maybe duplicate datasetId",
#             headers={"WWW-Authenticate": "Bearer"},
#         )


# insert_dataset_config_and_rules_config_info
def core_insert_dataset_config(
    dataset_config_id: str,
    user_id: str,
    yaml_name: str,
    yaml_content: dict,
    draft_result: dict,
    nb_rows: int,
    rules_id: str,
    rules_name: str,
    rules_content: dict,
    campaign_id: str = None,
) -> bool:
    """
    save dataset config
    """
    result_request_dataset_config = insert_dataset_config(
        dataset_config_id,
        user_id,
        yaml_name,
        json.dumps(yaml_content),
        json.dumps(draft_result),
        nb_rows,
    )
    result_rules_config = None
    if rules_content is not None:  # si rules_content est None alors on ne fait rien
        result_rules_config = insert_rules_config(
            rules_id,
            user_id,
            rules_name,
            json.dumps(rules_content),
            dataset_config_id,
            campaign_id,
        )

 


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================


# inserting_dataset_info_core
def core_inserting_dataset_info(
    dataset_row_id,
    dataset_config_id: int,
    owner_id: str,
    campaing_id: str = None,
    status: str = "waiting",
    nb_rows: int = 0,
    dataset_name: str = "defaut name",
) -> bool:
    """
    Insert new dataset info in dataset
    """
    result_request = insert_dataset_info(
        dataset_row_id,
        dataset_config_id,
        owner_id,
        campaing_id,
        status,
        nb_rows,
        dataset_name,
    )
    if result_request is True:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )


# insert_rules_config
def core_insert_rules_config(
    rules_id: str,
    user_id: str,
    rules_name: str,
    rules_content: str,
    dataset_config_id: int,
    campaign_id: str = None,
) -> bool:
    """
    save rules config
    """
    result_request = insert_rules_config(
        rules_id, user_id, rules_name, rules_content, dataset_config_id, campaign_id
    )
    if result_request is True:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )
