import os
import sys
import json
from database.queries.dataset.dataset_insert import (
    insert_dataset_config,
    insert_rules_config,
)

# dataset
from database.queries.dataset.dataset_insert import insert_dataset_info

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException


# insert_dataset_config_info
def core_insert_dataset_config_info(
    datasetId: str,
    userId: str,
    yamlName: str,
    yamlContent: str,
    draftResult: str,
    nbRows: int,
) -> bool:
    """
    save dataset config
    """
    reuslt_request = insert_dataset_config(
        datasetId, userId, yamlName, yamlContent, draftResult, nbRows
    )

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )


# insert_rules_config_info
def core_insert_rules_config(
    rulesId: str,
    userId: str,
    rulesName: str,
    rulesContent: str,
    datasetConfigId: int,
    campaignId: str = None,
) -> bool:
    """
    save rules config
    """
    reuslt_request = insert_rules_config(
        rulesId, userId, rulesName, rulesContent, datasetConfigId, campaignId
    )
    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting rules config",
            headers={"WWW-Authenticate": "Bearer"},
        )


def core_insert_dataset_config_and_rules_config_info(
    datasetConfigId: str,
    userId: str,
    yamlName: str,
    yamlContent: dict,
    draftResult: dict,
    nbRows: int,
    rulesId: str,
    rulesName: str,
    rulesContent: str,
    campaignId: str = None,
) -> bool:
    """
    save dataset config
    """
    result_request_dataset_config = insert_dataset_config(
        datasetConfigId,
        userId,
        yamlName,
        json.dumps(yamlContent),
        json.dumps(draftResult),
        nbRows,
    )
    result_rules_config = None
    print("rulesContent", rulesContent)
    if rulesContent is not None:  # si rulesContent est None alors on ne fait rien
        result_rules_config = insert_rules_config(
            rulesId,
            userId,
            rulesName,
            json.dumps(rulesContent),
            datasetConfigId,
            campaignId,
        )

    if result_request_dataset_config and result_rules_config:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset config or dataset rules config , try again your yaml is not saved, maybe duplicate datasetId",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================


def inserting_dataset_info(
    dataset_row_id,
    datasetConfigId: int,
    ownerId: str,
    campaingId: str = None,
    status: str = "waiting",
    nbRows: int = 0,
    datasetName: str = "defaut name",
) -> bool:
    """
    Insert new dataset info in dataset
    """
    result_request = insert_dataset_info(
        dataset_row_id,
        datasetConfigId,
        ownerId,
        campaingId,
        status,
        nbRows,
        datasetName,
    )
    # print("result_request -->", result_request)
    if result_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while inserting dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )
