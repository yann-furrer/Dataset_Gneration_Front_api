import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException
from core.checking import check_var_is_none

# dataset
from database.queries.dataset import (
    update_finished_dataset_info,
    update_status_dataset_info,
)

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASETCONFIG` et `RULESCONFIG`.
# ==============================================================

"""
vide
"""

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================


def update_finished_dataset(
    dataset_name: str, dataset_id: str, generation_error: str, status: str
) -> bool:
    """
    Update finished dataset
    """
    # print("datasetId -->", datasetId)
    # print("generationError -->", generationError)
    # print("status -->", status)
    reuslt_request = update_finished_dataset_info(
        dataset_name, dataset_id, generation_error, status
    )

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )


def update_status_dataset(dataset_id: str, status: str) -> bool:
    """
    Update status dataset
    """
    reuslt_request = update_status_dataset_info(dataset_id, status)

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating dataset status info",
            headers={"WWW-Authenticate": "Bearer"},
        )
