from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class GenerateDatasetRequest(BaseModel):
    end_format: str = Field(..., description="Format de sortie souhaité (ex: csv, json)")
    yaml_content: Dict[str, Any] = Field(..., description="Contenu YAML sous forme d'objet JSON")
    rulesContent: Optional[Dict[str, Any]] = Field(None, description="Règles optionnelles de génération")
    campaignid: Optional[str] = Field(None, description="Identifiant de campagne, ignoré en mode dev")
    function: Optional[str] = Field("preprocessing_generation", description="Nom de la fonction à exécuter")
    faker_name_dict: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Variables faker personnalisées")

    class Config:
        schema_extra = {
            "example": {
                "end_format": "csv",
                "yaml_content": {
                    "datasetName": "ExempleDataset",
                    "numberOfRecords": 100
                },
                "rulesContent": {},
                "campaignid": None,
                "function": "preprocessing_generation",
                "faker_name_dict": {
                    "faker_name": "company"
                }
            }
        }

class GenerateDatasetResponse(BaseModel):
    message: str
    process_id: str