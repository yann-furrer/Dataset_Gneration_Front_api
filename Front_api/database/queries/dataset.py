
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *


# Save dataset config mixe first saveing and saving dataset

INSERT_ON_CONFLICT_DATASET_CONFIG = """
INSERT INTO public."DatasetConfig"(
	 "datasetId", "userId", "yamlName", "yamlContent", "draftResult", "nbRows", "updatedAt")
	VALUES ( :datasetId, :userId, :yamlName, :yamlContent, :draftResult , :nbRows, now());
    ON CONFLICT (datasetId) DO UPDATE
    SET yamlName = :yamlName, yamlContent = :yamlContent, draftResult = :draftResult , nbRows = :nbRows, updatedAt = now();
    """
# Par defaut on laisse le champs rulesId et campaingId vide car il sera ajouter dès la creation de celui ci dans le front
# cela evite de complexifier la requete pour ajouter les rules
def insert_dataset_config(datasetId: str, userId: str,  yamlName: str, yamlContent: str, draftResult: str, nbRows: int) -> bool:
    try:
        session.execute(text(INSERT_ON_CONFLICT_DATASET_CONFIG), {"datasetId": datasetId, "userId": userId, "yamlName": yamlName, "yamlContent": yamlContent, "draftResult": draftResult, "nbRows": nbRows})
        session.commit()
        return True
    except Exception as e:
        print("Error while inserting dataset config", e)
        return False
    
# insert_dataset_config("kzejfklgjreklg",  "cm97k3e4y0000w1fx7081kk5e"
# ,"yaml titre dataset", '{"yann": "dataset"}','{"ebauche": "dataset"}', 12345987873)



SELECT_DATASET_CONFIG = """
SELECT * FROM public."DatasetConfig" WHERE "datasetId" = :datasetId AND "userId" = :userId;
"""

def select_dataset_config(datasetId: str, userId: str) -> bool:
    try:
        request = session.execute(text(SELECT_DATASET_CONFIG), {"datasetId": datasetId, "userId": userId})
        result = request.fetchone()
        return result
    except Exception as e:
        print(f"Error while selecting dataset config from user {userId}", e)
        return False
    

INSERT_DATASET_INFO = """
INSERT INTO public."Dataset"(
	"nbRows", "datasetConfigId", "ownerId", "campaignId", "status")
	VALUES ( :nbRows", :datasetConfigId, :ownerId, :campaignId, :status);
    """

def insert_dataset_info(datasetConfigId: int, ownerId: str, campaingId: str = None, status: str = "waiting") -> bool:
    try:
        if campaingId == None:
            campaingId = ""
        session.execute(text(INSERT_DATASET_INFO), {"datasetConfigId": datasetConfigId, "ownerId": ownerId, "campaignId": campaingId, "status": status})
        session.commit()
        return True
    except Exception as e:
        print("Error while inserting dataset info", e)
        return False
    
    
UPDATE_FINISHED_DATASET_INFO = """ 
UPDATE public."Dataset"(
SET "s3Url" = :s3Url, 
    "FinishedAt" = :FinishedAt,
    "generationError" = :generationError,
    "status" = :status
    "TimeToGenerate" = (SELECT "createdAt" FROM "DatasetConfig" WHERE "datasetId" = :datasetId),
    "generationError" = :generationError,
WHERE "datasetId" = :datasetId;
"""

def update_finished_dataset_info(datasetId: str, s3Url: str, FinishedAt: str, generationError: str, status: str) -> bool:
    try:
        session.execute(text(UPDATE_FINISHED_DATASET_INFO), {"datasetId": datasetId, "s3Url": s3Url, "FinishedAt": FinishedAt, "generationError": generationError, "status": status})
        session.commit()
        return True
    except Exception as e:
        print("Error while updating dataset info", e)
        return False

UPDATE_STATUS_DATASET_INFO = """ 
UPDATE public."Dataset"(
SET "status" = :status
    "generationError" = :generationError,

WHERE "datasetId" = :datasetId;
"""

def update_status_dataset_info(datasetId: str, status: str, generationError: str= None) -> bool:
    try:
        session.execute(text(UPDATE_STATUS_DATASET_INFO), {"datasetId": datasetId, "status": status, "generationError": generationError})
        session.commit()
        return True
    except Exception as e:
        print("Error while updating dataset info", e)
        return False
    



SELECT_ALL_S3_URL_DATASET = """
SELECT "s3Url", "id", "campaignId" FROM public."Dataset" WHERE "ownerId" = :ownerId AND "s3Url" IS NOT NULL;
"""
def select_all_s3_url_from_dataset(userId: str) -> dict:
    try:
        request = session.execute(text(SELECT_ALL_S3_URL_DATASET), {"ownerId": userId})
        result = request.fetchall()
        return result
    except Exception as e:
        print(f"Error while selecting all s3Url from dataset with this user", e)
        return False


SELECT_ALL_S3_URL_BY_COMPAIGN_DATASET = """
SELECT "s3Url", "id", "campaignId" FROM public."Dataset" WHERE "ownerId" = :ownerId
    AND "CampaignId" = :campaignId
    AND "s3Url" IS NOT NULL;
"""
def select_all_s3_url_by_campaign_from_dataset(compaignId: str, userId: str) -> tuple :
    try:
        request = session.execute(text(SELECT_ALL_S3_URL_DATASET), {"compaignId": compaignId, "ownerId": userId})
        result = request.fetchone()
        return result
    except Exception as e:
        print(f"Error while selecting all s3Url from dataset {compaignId}", e)
        return False
    

SELECT_DATASET_HISTORICAL_OFFSET = """
SELECT "id", "datasetId", "nbRows", "datasetConfigId", "campaignId", "status", "FinishedAt", "TimeToGenerate" 
FROM public."Dataset"
WHERE "userId" = :userId 
ORDER BY FinishedAt DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""
def select_dataset_historical_offset(userId: str, offset: int) -> dict:
    # offset et le numero de page
    #"offset" is the number of row to skip
    #"offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_max = offset * nb_rows_to_return 
    offset_min = offset_max - nb_rows_to_return
    try:
        request = session.execute(text(SELECT_DATASET_HISTORICAL_OFFSET), {"userId": userId, "offset_min": offset_min, "offset_max": offset})
        result = request.fetchall()
        return result
    except Exception as e:        
        print(f"Error while selecting dataset historical {userId}", e)
        return False
    




SELECT_DATASET_CONFIG_HISTORICAL_OFFSET = """
SELECT "datasetId", "yamlName", "yamlContent", "draftResult", "ruleId", "nbrows", "compaignId"
FROM public."DatasetConfig"
WHERE "userId" = :userId 
ORDER BY createdAt DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""

def select_dataset_historical_config_offset(userId: str, offset: int) -> dict:
    # offset et le numero de page
    #"offset" is the number of row to skip
    #"offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_max = offset * nb_rows_to_return 
    offset_min = offset_max - nb_rows_to_return
    try:
        request = session.execute(text(SELECT_DATASET_CONFIG_HISTORICAL_OFFSET), {"userId": userId, "offset_min": offset_min, "offset_max": offset_max})
        result = request.fetchall()
        return result
    except Exception as e:        
        print(f"Error while selecting dataset historical {userId}", e)
        return False