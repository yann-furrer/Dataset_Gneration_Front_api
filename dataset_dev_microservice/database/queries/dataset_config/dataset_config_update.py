import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session



# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASETCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
# ==============================================================




INSERT_OR_UPDATE_DATASET_CONFIG = """
INSERT INTO public."DatasetConfig"(
	"datasetId", "userId", "yamlName", "yamlContent", "draftResult", "nbRows", "updatedAt")
	VALUES ( :datasetId, :userId, :yamlName, :yamlContent, :draftResult , :nbRows, now())
    ON CONFLICT ("datasetId") DO UPDATE
    SET "yamlName" = :yamlName, "yamlContent" = :yamlContent, "draftResult" = :draftResult , "nbRows" = :nbRows, "updatedAt" = now();
    """

def insert_or_update_dataset_config(
    dataset_id: str,
    user_id: str,
    yaml_name: str,
    yaml_content: dict,
    draft_result: str,
    nbRows: int,
) -> bool:
    try:
        session.execute(
            text(INSERT_OR_UPDATE_DATASET_CONFIG),
            {
                "datasetId": dataset_id,
                "userId": user_id,
                "yamlName": yaml_name,
                "yamlContent": yaml_content,
                "draftResult": draft_result,
                "nbRows": nbRows,
            },
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while inserting dataset config", e)
        return False