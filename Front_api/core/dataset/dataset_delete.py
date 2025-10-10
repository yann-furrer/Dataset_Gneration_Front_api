import os
import sys
import json 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from fastapi import HTTPException
from core.checking import check_var_is_none

# dataset 
from database.queries.dataset import (
   delete_dataset_by_dataset_id
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

# delete_dataset_historical
def core_delete_dataset_by_dataset_id(datasetId: str, userId: str) -> bool:
    """
    Delete dataset form his s3 bucket
    """
    result_request = delete_dataset_by_dataset_id(datasetId, userId)
    if result_request:
        return True
    else:
        HTTPException(
            status_code=400,
            detail="Error while deleting dataset",
            headers={"WWW-Authenticate": "Bearer"},
        )
