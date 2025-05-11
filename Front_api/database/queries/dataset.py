
import os , sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config import *


# Save dataset config mixe first saveing and saving dataset

INSERT_ON_CONFLICT_DATASET_CONFIG = """
INSERT INTO public."DatasetConfig"(
	 "datasetId", "userId", "yamlName", "yamlContent", "draftResult", "nbRows", "updatedAt")
	VALUES ( :datasetId, :userId, :yamlName, :yamlContent, :draftResult , :nbRows, now())
    ON CONFLICT ("datasetId") DO UPDATE
    SET "yamlName" = :yamlName, "yamlContent" = :yamlContent, "draftResult" = :draftResult , "nbRows" = :nbRows, "updatedAt" = now();
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

# INSERT_RULES_CONFIG = """
# INSERT INTO public."RulesConfig"(
# 	 "rulesId", "userId", "rulesName", "rulesContent", "datasetConfigId")
# 	VALUES ( :rulesId, :userId, :rulesName, :rulesContent, :datasetConfigId);
    
#     """
# INSERT_RULES_CONFIG_WITH_CAMPAIGN = """
# INSERT INTO public."RulesConfig"(
# 	 "rulesId", "userId", "rulesName", "rulesContent", "datasetConfigId", "campaignId")
# 	VALUES ( :rulesId, :userId, :rulesName, :rulesContent, :datasetConfigId , :campaignId);
#     ON CONFLICT (datasetId) DO UPDATE
#     SET yamlName = :yamlName, yamlContent = :yamlContent, draftResult = :draftResult , nbRows = :nbRows, updatedAt = now();
#     """

def insert_rules_config(rulesId: str, userId: str,  rulesName: str, rulesContent: str, datasetConfigId: int, campaignId: str = None) -> bool:  
    try:
        if campaignId == None:
            campaignId = ""
            session.execute(text(INSERT_ON_CONFLICT_RULES_CONFIG), {"rulesId": rulesId, "userId": userId, "rulesName": rulesName, "rulesContent": rulesContent, "datasetConfigId": datasetConfigId})
            session.commit()
            return True
        else:
            session.execute(text(INSERT_ON_CONFLICT_RULES_CONFIG_WITH_CAMPAIGN), {"rulesId": rulesId, "userId": userId, "rulesName": rulesName, "rulesContent": rulesContent, "datasetConfigId": datasetConfigId, "campaignId": campaignId})
            session.commit()
            return True
        
    except Exception as e:
        print("Error while inserting rules config", e)
        return False




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
	"id", "nbRows", "datasetConfigId", "ownerId", "status", "datasetName")
	VALUES ( :id, :nbRows, :datasetConfigId, :ownerId, :status, :datasetName);
    """

INSERT_DATASET_INFO_WITH_COMPAIGN = """
INSERT INTO public."Dataset"(
	"id", "nbRows", "datasetConfigId", "ownerId", "campaignId", "status", "datasetName")
	VALUES ( :id, :nbRows, :datasetConfigId, :ownerId, :campaignId, :status, :datasetName);
    """

def insert_dataset_info(dataset_row_id: str, datasetConfigId: int, ownerId: str, campaingId: str = None, status: str = "waiting", nbRows: int = 0, datasetName: str = None) -> bool:
    try:
        if campaingId == None:
            session.execute(text(INSERT_DATASET_INFO), {"id": dataset_row_id, "datasetConfigId": datasetConfigId, "ownerId": ownerId, "campaignId": campaingId, "status": status, "nbRows": nbRows, "datasetName": datasetName})
            session.commit()
        else:
            session.execute(text(INSERT_DATASET_INFO_WITH_COMPAIGN), { "id": dataset_row_id, "datasetConfigId": datasetConfigId, "ownerId": ownerId, "campaignId": campaingId, "status": status, "nbRows": nbRows, "datasetName": datasetName})
            session.commit()
        return True
    except Exception as e:
        print("Error while inserting dataset info", e)
        return False
    
    
UPDATE_FINISHED_DATASET_INFO = """ 
UPDATE public."Dataset"
SET 
    "FinishedAt" = NOW(),
    "generationError" = :generationError,
    "status" = :status,
     "TimeToGenerate" = (ROUND(EXTRACT(EPOCH FROM (NOW() - (SELECT "createdAt" FROM public."Dataset" WHERE "id" = :id)))) / 60)::integer
WHERE "id" = :id;
"""

def update_finished_dataset_info(row_id: str, generationError: str, status: str) -> bool:
    try:
        session.execute(text(UPDATE_FINISHED_DATASET_INFO), {"id": row_id, "generationError": generationError, "status": status})
        session.commit()
        return True
    except Exception as e:
        print("Error while updating dataset info", e)
        return False
    

UPDATE_DATASET_STATUS_INFO = """ 
UPDATE public."Dataset"
SET
    "status" = :status
WHERE "id" = :id;
"""

def update_dataset_status_info(row_id: str, status: str) -> bool:
    try:
        print("update_dataset_status_info")
        print("row_id -->", row_id)
        print("status -->", status)
        session.execute(text(UPDATE_DATASET_STATUS_INFO), {"id": row_id, "status": status})
        session.commit()
        return True
    except Exception as e:
        print("Error while updating dataset info", e)
        return False


UPDATE_STATUS_DATASET_INFO = """ 
UPDATE public."Dataset"
SET "status" = :status
    "generationError" = :generationError
WHERE "id" = :id;   
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
SELECT "id", "nbRows", "datasetConfigId","ownerId", "campaignId", "status", "FinishedAt", "TimeToGenerate" , "datasetName"
FROM public."Dataset"
WHERE "ownerId" = :ownerId
ORDER BY "FinishedAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""
def select_dataset_historical_offset(userId: str, offset: int) -> dict:
    # offset et le numero de page
    #"offset" is the number of row to skip
    #"offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_min = offset * nb_rows_to_return
    offset_max = offset_min + nb_rows_to_return
    try:
        request = session.execute(text(SELECT_DATASET_HISTORICAL_OFFSET), {"ownerId": userId, "offset_min": offset_min, "offset_max": offset_max})
        result = request.fetchall()
        return result
    except Exception as e:        
        print(f"Error while selecting dataset historical {userId}", e)
        return False
    




SELECT_DATASET_CONFIG_HISTORICAL_OFFSET = """
SELECT "datasetId", "yamlName", "yamlContent", "draftResult", "rulesId", "nbRows", "campaignId", "createdAt"
FROM public."DatasetConfig"
WHERE "userId" = :userId 
ORDER BY "createdAt" DESC
OFFSET :offset_min ROWS
FETCH NEXT :offset_max ROWS ONLY;
"""

def select_dataset_historical_config_offset(userId: str, offset: int) -> dict:
    # offset et le numero de page
    #"offset" is the number of row to skip
    #"offset_max" is the number of row to take

    nb_rows_to_return = 10
    offset_min = offset * nb_rows_to_return
    offset_max = offset_min + nb_rows_to_return
    try:
        request = session.execute(text(SELECT_DATASET_CONFIG_HISTORICAL_OFFSET), {"userId": userId, "offset_min": offset_min, "offset_max": offset_max})
        result = request.fetchall()
        return result
    except Exception as e:        
        print(f"Error while selecting dataset historical {userId}", e)
        return False
    

