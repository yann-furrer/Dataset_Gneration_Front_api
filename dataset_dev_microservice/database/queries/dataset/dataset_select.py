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
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================



    
SELECT_ALL_S3_URL_DATASET = """
SELECT "s3Url", "id", "campaignId" FROM public."Dataset" WHERE "ownerId" = :ownerId AND "s3Url" IS NOT NULL;
"""
def select_all_s3_url_from_dataset(user_id: str) -> dict:
    try:
        request = session.execute(text(SELECT_ALL_S3_URL_DATASET), {"ownerId": user_id})
        result = request.fetchall()
        return result
    except Exception as e:
        print("Error while selecting all s3Url from dataset with this user", e)
        session.rollback()
        return False



# compaign_id not  implemented
SELECT_ALL_S3_URL_BY_COMPAIGN_DATASET = """
SELECT "s3Url", "id", "campaignId" FROM public."Dataset" WHERE "ownerId" = :ownerId
    AND "CampaignId" = :campaignId
    AND "s3Url" IS NOT NULL;
"""
def select_all_s3_url_by_campaign_from_dataset(compaign_id: str, user_id: str) -> tuple:
    try:
        request = session.execute(
            text(SELECT_ALL_S3_URL_DATASET),
            {"compaignId": compaign_id, "ownerId": user_id},
        )
        result = request.fetchone()
        return result
    except Exception as e:
        session.rollback()
        print(f"Error while selecting all s3Url from dataset {compaign_id}", e)
        return False
    



SELECT_DATASET_HISTORICAL_OFFSET = """
SELECT "id", "nbRows", "datasetConfigId","ownerId", "campaignId", "status", "FinishedAt", "TimeToGenerate" , "datasetName", "datasetNameSystem"
FROM public."Dataset"
WHERE "ownerId" = :ownerId
ORDER BY "FinishedAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""
def select_dataset_historical_offset(user_id: str, offset: int) -> dict:
    # offset et le numero de page
    # "offset" is the number of row to skip
    # "offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_min = offset * nb_rows_to_return
    offset_max = offset_min + nb_rows_to_return
    try:
        request = session.execute(
            text(SELECT_DATASET_HISTORICAL_OFFSET),
            {"ownerId": user_id, "offset_min": offset_min, "offset_max": offset_max},
        )
        result = request.fetchall()
        return result
    except Exception as e:
        print(f"Error while selecting dataset historical {user_id}", e)
        session.rollback()
        return False
    


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET CONFIG `
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================

SELECT_DATASET_CONFIG = """
SELECT * FROM public."DatasetConfig" WHERE "datasetId" = :datasetId AND "userId" = :userId;
"""


def select_dataset_config(dataset_id: str, user_id: str) -> bool:
    try:
        request = session.execute(
            text(SELECT_DATASET_CONFIG), {"datasetId": dataset_id, "userId": user_id}
        )
        result = request.fetchone()
        return result
    except Exception as e:
        session.rollback()
        print(f"Error while selecting dataset config from user {user_id}", e)
        return False
    


SELECT_DATASET_CONFIG_HISTORICAL_OFFSET = """
SELECT "datasetId", "yamlName", "draftResult", "rulesId", "nbRows", "campaignId", "createdAt"
FROM public."DatasetConfig"
WHERE "userId" = :userId 
ORDER BY "createdAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""
def select_dataset_historical_config_offset(user_id: str, offset: int) -> dict:
    # offset et le numero de page
    # "offset" is the number of row to skip
    # "offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_min = offset * nb_rows_to_return
    offset_max = offset_min + nb_rows_to_return
    try:
        request = session.execute(
            text(SELECT_DATASET_CONFIG_HISTORICAL_OFFSET),
            {"userId": user_id, "offset_min": offset_min, "offset_max": offset_max},
        )
        result = request.fetchall()
        return result
    except Exception as e:
        print(f"Error while selecting dataset historical {user_id}", e)
        return False
    


SELECT_YAML_CONTENT_BY_DATASET_CONFIG_ID = """
SELECT "yamlContent" FROM public."DatasetConfig" WHERE "datasetId" = :datasetId AND "userId" = :userId;
"""

SELECT_RULES_CONTENT_BY_DATASET_CONFIG_ID = """
SELECT "rulesContent" FROM public."RulesConfig" WHERE "datasetConfigId" = :datasetConfigId AND "userId" = :userId;
"""
def select_yaml_and_rules_content_by_dataset_config_id(
    dataset_id: str, user_id: str
) -> dict:
    try:
        request_yaml = session.execute(
            text(SELECT_YAML_CONTENT_BY_DATASET_CONFIG_ID),
            {"datasetId": dataset_id, "userId": user_id},
        )
        result_yaml = request_yaml.fetchone()

        request_rules = session.execute(
            text(SELECT_RULES_CONTENT_BY_DATASET_CONFIG_ID),
            {"datasetConfigId": dataset_id, "userId": user_id},
        )
        result_rules = request_rules.fetchone()
        return {
            "yamlContent": (
                dict(result_yaml._mapping)["yamlContent"] if result_yaml else []
            ),
            "rulesContent": (
                dict(result_rules._mapping)["rulesContent"] if result_rules else []
            ),
        }
    except Exception as e:
        session.rollback()
        print(f"Error while selecting yaml content by dataset config id {dataset_id}", e)
        return False