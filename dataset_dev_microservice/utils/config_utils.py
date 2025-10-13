
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from database.config import session, text

GET_DATASET_CONFIG = """
SELECT "yamlContent" FROM public."DatasetConfig" WHERE "datasetId" = :datasetConfigId AND "userId" = :userId;
"""
def get_dataset_config_from_dataset_config_id(dataset_config_id, user_id) -> bool:    
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : yamlContent
    """
    try:
        request = session.execute(text(GET_DATASET_CONFIG), {"datasetConfigId": dataset_config_id, "userId": user_id})
        row = request.mappings().first()
        return row
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False
    
GET_RULES_CONFIG = """
SELECT "rulesContent" FROM public."RulesConfig" WHERE "rulesId" = :rulesId AND "userId" = :userId AND "datasetConfigId" = :datasetConfigId;
"""
def get_rules_config_from_dataset_config_id(rules_config_id : str, dataset_config_id :str,   user_id :str) -> bool:    
    """
    Récupère le dataset config d'un user à partir du userId et du datasetConfigId
    args : datasetConfigId, userId
    return : yamlContent
    """
    try:
        request = session.execute(text(GET_RULES_CONFIG), {"rulesId": rules_config_id,"datasetConfigId": dataset_config_id, "userId": user_id})
        row = request.mappings().first()
        return row
    except Exception as error:
         session.rollback()
         print("error -->",error)
         return False