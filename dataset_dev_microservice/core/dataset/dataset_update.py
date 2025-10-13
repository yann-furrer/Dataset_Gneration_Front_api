import os
import sys
from fastapi import HTTPException

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from database.queries.dataset import (
    update_finished_dataset_info,
    update_status_dataset_info,
)

# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `S3 et DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================


def update_finished_dataset(
    dataset_name: str, datasetId: str, generationError: str, status: str
) -> bool:
    """
    Update finished dataset
    """
    print("datasetId -->", datasetId)
    print("generationError -->", generationError)
    print("status -->", status)
    reuslt_request = update_finished_dataset_info(
        dataset_name, datasetId, generationError, status
    )

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating dataset info",
            headers={"WWW-Authenticate": "Bearer"},
        )


def update_status_dataset(datasetId: str, status: str) -> bool:
    """
    Update status dataset
    """
    reuslt_request = update_status_dataset_info(datasetId, status)

    if reuslt_request:
        return True
    else:
        raise HTTPException(
            status_code=400,
            detail="Error while updating dataset status info",
            headers={"WWW-Authenticate": "Bearer"},
        )
