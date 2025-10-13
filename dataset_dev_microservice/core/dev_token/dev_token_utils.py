import os
import sys
import yaml
from fastapi import HTTPException
# from core.dev_utils import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))




# Utilisé pour vérifier si le fichier yaml ou de règle est valide
def check_config_validity(yaml_content: dict, rules_content: list = []) -> dict:
    """
    Check if the yaml content is valid
    yaml_content : est au format yaml converti en json
    rules_content : est au format json de base
    """
    # Vérification basique des fichiers de config
    try:
        yaml_content = yaml.safe_load(yaml_content)
    except Exception as e:
        print("error -->", e)
      raise HTTPException(
            status_code=400,
            detail="Error while convert to yaml check your syntax " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if rules_content != [] and type(rules_content) != list:
      raise HTTPException(
            status_code=400,
            detail="Error while convert to rules check your syntax ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérification du fichier yaml
    # Vérification de la structure du fichier yaml
    dataset_name = yaml_content.get("dataset_name", "empty")
    numberOfRecords = yaml_content.get("numberOfRecords", "empty")
    fields = yaml_content.get("fields", "empty")
    bones = yaml_content.get("bones", "empty")
    return {"not valid": "ROUTE A FAIRE "}
