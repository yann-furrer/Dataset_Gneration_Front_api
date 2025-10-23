import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `RULESCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `DATASETCONFIG` n'est possible.
# ==============================================================

SELECT_RULES_CONFIG_BY_DATASET_CONFIG_ID = """
SELECT "id", "rulesContent" FROM public."RulesConfig" WHERE "datasetConfigId" = :datasetConfigId AND "userId" = :userId;
"""
def select_rules_config_by_dataset_config_id(datasetConfigId: str, userId: str) -> dict | bool:
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : yamlContent
    """
    try:
        request = session.execute(text(SELECT_RULES_CONFIG_BY_DATASET_CONFIG_ID), {"datasetConfigId": datasetConfigId, "userId": userId})
        row = request.mappings().first()
        return row
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False
    
