import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session


DELETE_DATASET_CONFIG_AND_RULES_CONFIG_BY_USER_ID = """
BEGIN;
DELETE FROM public."DatasetConfig" WHERE "datasetId" = :datasetId AND "userId" = :userId;
DELETE FROM public."RulesConfig" WHERE "datasetConfigId" = :datasetConfigId AND "userId" = :userId AND "datasetConfigId" = :datasetConfigId;
COMMIT;
"""

def delete_dataset_config_and_rules_config_by_user_id(datasetId: str, userId: str, datasetConfigId: str) -> bool:
    """
    Supprime les configurations de dataset et de règles associées à un utilisateur
    """
    try:
        session.execute(
            text(DELETE_DATASET_CONFIG_AND_RULES_CONFIG_BY_USER_ID),
            {
                "datasetId": datasetId,
                "userId": userId,
                "datasetConfigId": datasetConfigId,
            },
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while deleting dataset config and rules config", e)
        return False
    

DELETE_RULES_CONFIG_BY_RULES_ID = """
DELETE FROM public."RulesConfig" WHERE "datasetConfigId" = :datasetConfigId AND "userId" = :userId AND "datasetConfigId" = :datasetConfigId;
"""