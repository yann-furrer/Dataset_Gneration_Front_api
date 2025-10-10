import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session



# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================



UPDATE_FINISHED_DATASET_INFO = """ 
UPDATE public."Dataset"
SET 
    "FinishedAt" = NOW(),
    "generationError" = :generationError,
    "status" = :status,
    "datasetNameSystem" = :dataset_name_system,
     "TimeToGenerate" = (ROUND(EXTRACT(EPOCH FROM (NOW() - (SELECT "createdAt" FROM public."Dataset" WHERE "id" = :id)))) / 60)::integer
WHERE "id" = :id;
"""
# dataset_name_system est le nom du dataset qui a été généré par le back et qui est stocké dans un s3
def update_finished_dataset_info(
    dataset_name_system: str, row_id: str, generation_error: str, status: str
) -> bool:
    try:
        session.execute(
            text(UPDATE_FINISHED_DATASET_INFO),
            {
                "id": row_id,
                "generationError": generation_error,
                "status": status,
                "dataset_name_system": dataset_name_system,
            },
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while updating dataset info", e)
        return False



UPDATE_DATASET_STATUS_INFO = """ 
UPDATE public."Dataset"
SET
    "status" = :status
WHERE "id" = :id;
"""
def update_status_dataset_info(row_id: str, status: str) -> bool:
    try:
        # print("update_status_dataset_info")
        # print("row_id -->", row_id)
        # print("status -->", status)
        session.execute(
            text(UPDATE_DATASET_STATUS_INFO), {"id": row_id, "status": status}
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while updating dataset info", e)
        return False



