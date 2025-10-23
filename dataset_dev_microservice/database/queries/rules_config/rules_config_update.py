import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session
from psycopg2.extras import Json
INSERT_OR_UPDATE_RULES_CONFIG = """
INSERT INTO public."RulesConfig"(
	"rulesId", "userId", "rulesName", "rulesContent", "datasetConfigId")
	VALUES ( :rulesId, :userId, :rulesName, :rulesContent, :datasetConfigId)
    ON CONFLICT ("rulesId") DO UPDATE
    SET "rulesName" = :rulesName, "rulesContent" = :rulesContent;
    """

def insert_or_update_rules_config(
    rules_id: str,
    user_id: str,
    rules_name: str,
    rules_content: dict,
    dataset_config_id: int,
) -> bool:
    try:
        session.execute(
            text(INSERT_OR_UPDATE_RULES_CONFIG),
            {
                "rulesId": rules_id,
                "userId": user_id,
                "rulesName": rules_name,
                "rulesContent": Json(rules_content),
                "datasetConfigId": dataset_config_id,
            },
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while inserting rules config", e)