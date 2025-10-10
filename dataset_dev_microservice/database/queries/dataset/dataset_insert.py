import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from config import text, session



# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `RULESCONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `RULESCONFIG`.
# ==============================================================


INSERT_ON_CONFLICT_RULES_CONFIG = """
INSERT INTO public."RulesConfig"(
	"rulesId", "userId", "rulesName", "rulesContent", "datasetConfigId")
	VALUES ( :rulesId, :userId, :rulesName, :rulesContent, :datasetConfigId)
    ON CONFLICT ("rulesId") DO UPDATE
    SET "rulesName" = :rulesName, "rulesContent" = :rulesContent;
    """

INSERT_ON_CONFLICT_RULES_CONFIG_WITH_CAMPAIGN = """
INSERT INTO public."RulesConfig"(
	"rulesId", "userId", "rulesName", "rulesContent", "datasetConfigId", "campaignId")
	VALUES ( :rulesId, :userId, :rulesName, :rulesContent, :datasetConfigId, "campaignId")
    ON CONFLICT ("rulesId") DO UPDATE
    SET "rulesName" = :rulesName, "rulesContent" = :rulesContent, "campaignId" = :campaignId;
    """
def insert_rules_config(
    rulesId: str,
    userId: str,
    rules_name: str,
    rules_content: str,
    dataset_config_id: int,
    campaign_id: str = None,
) -> bool:
    try:
        if campaign_id is None:
            campaign_id = ""
            session.execute(
                text(INSERT_ON_CONFLICT_RULES_CONFIG),
                {
                    "rulesId": rulesId,
                    "userId": userId,
                    "rulesName": rules_name,
                    "rulesContent": rules_content,
                    "datasetConfigId": dataset_config_id,
                },
            )
            session.commit()
            return True
        else:
            session.execute(
                text(INSERT_ON_CONFLICT_RULES_CONFIG_WITH_CAMPAIGN),
                {
                    "rulesId": rulesId,
                    "userId": userId,
                    "rulesName": rules_name,
                    "rulesContent": rules_content,
                    "datasetConfigId": dataset_config_id,
                    "campaignId": campaign_id,
                },
            )
            session.commit()
            return True

    except Exception as e:
        session.rollback()
        print("Error while inserting rules config", e)
        return False
    
# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET CONFIG`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================

INSERT_ON_CONFLICT_DATASET_CONFIG = """
INSERT INTO public."DatasetConfig"(
	 "datasetId", "userId", "yamlName", "yamlContent", "draftResult", "nbRows", "updatedAt")
	VALUES ( :datasetId, :userId, :yamlName, :yamlContent, :draftResult , :nbRows, now())
    ON CONFLICT ("datasetId") DO UPDATE
    SET "yamlName" = :yamlName, "yamlContent" = :yamlContent, "draftResult" = :draftResult , "nbRows" = :nbRows, "updatedAt" = now();
    """
# Par defaut on laisse le champs rulesId et campaign_id vide car il sera ajouter dès la creation de celui ci dans le front
# cela evite de complexifier la requete pour ajouter les rules
def insert_dataset_config(
    datasetId: str,
    userId: str,
    yamlName: str,
    yamlContent: str,
    draftResult: str,
    nbRows: int,
) -> bool:
    try:
        session.execute(
            text(INSERT_ON_CONFLICT_DATASET_CONFIG),
            {
                "datasetId": datasetId,
                "userId": userId,
                "yamlName": yamlName,
                "yamlContent": yamlContent,
                "draftResult": draftResult,
                "nbRows": nbRows,
            },
        )
        session.commit()

        return True
    except Exception as e:
        session.rollback()
        print("Error while inserting dataset config", e)
        return False
    


# ==============================================================
# 🚦 ROUTES LIÉES UNIQUEMENT À LA TABLE `DATASET`
# --------------------------------------------------------------
# 🔍 Contexte :
#   - Ces routes manipulent uniquement la configuration des datasets.
#   - Aucune interaction avec `RULESCONFIG` n'est possible.
#   - Dans d'autres fichiers, certaines routes peuvent être hybrides
#     et toucher à la fois `DATASET` et `D`.
# ==============================================================


INSERT_DATASET_INFO = """
INSERT INTO public."Dataset"(
	"id", "nbRows", "datasetConfigId", "ownerId", "status", "datasetName")
	VALUES ( :id, :nbRows, :datasetConfigId, :ownerId, :status, :datasetName);
    """

INSERT_DATASET_INFO_WITH_COMPAIGN = """
INSERT INTO public."Dataset"(
	"id", "nbRows", "datasetConfigId", "ownerId", "campaignId", "status", "datasetName")
	VALUES ( :id, :nbRows, :datasetConfigId, :ownerId, :campaignId, :status, :datasetName);
    """
def insert_dataset_info(
    dataset_row_id: str,
    dataset_config_id: int,
    ownerId: str,
    campaign_id: str = None,
    status: str = "waiting",
    nbRows: int = 0,
    datasetName: str = None,
) -> bool:
    try:
        if campaign_id is None:
            session.execute(
                text(INSERT_DATASET_INFO),
                {
                    "id": dataset_row_id,
                    "datasetConfigId": dataset_config_id,
                    "ownerId": ownerId,
                    "campaignId": campaign_id,
                    "status": status,
                    "nbRows": nbRows,
                    "datasetName": datasetName,
                },
            )
            session.commit()
        else:
            session.execute(
                text(INSERT_DATASET_INFO_WITH_COMPAIGN),
                {
                    "id": dataset_row_id,
                    "datasetConfigId": dataset_config_id,
                    "ownerId": ownerId,
                    "campaignId": campaign_id,
                    "status": status,
                    "nbRows": nbRows,
                    "datasetName": datasetName,
                },
            )
            session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error while inserting dataset info", e)
        return False
