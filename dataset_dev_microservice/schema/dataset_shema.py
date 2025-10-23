from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class GenerateDatasetRequest(BaseModel):
    end_format: str = Field(..., description="Format de sortie souhaité (ex: csv, json)")
    yaml_content: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contenu YAML sous forme d'objet JSON")
    rules_content: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Règles optionnelles de génération")
    campaignid: Optional[str] = Field(None, description="Identifiant de campagne, ignoré en mode dev")
    # function: Optional[str] = Field("preprocessing_generation", description="Nom de la fonction à exécuter")
    faker_name_dict: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Variables faker personnalisées")
    dataset_config_id: Optional[str] = Field(
        default_factory=str,
        description=(
            "Identifiant d'une config dataset **optionnel**. Si fourni, il **remplace** `yaml_content`."
        ),
    )
    rules_config_id: Optional[str] = Field(
        default_factory=str,
        description=(
            "Identifiant d'une config de règles **optionnel**. Si fourni, il **remplace** `rules_content`."
        ),
    )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "summary": "Avec IDs de configuration (prioritaires)",
                    "value": {
                        "end_format": "csv",
                        "dataset_config_id": "dcfg_123",
                        "rules_config_id": "rcfg_456",
                        "faker_name_dict": {"company": "name"}
                    }
                },
                {
                    "summary": "Avec contenu inline (sans IDs)",
                    "value": {
                        "end_format": "json",
                        "yaml_content": {
                            "datasetName": "ExempleDataset",
                            "numberOfRecords": 1000
                        },
                        "rules_content": {},
                        "faker_name_dict": {"faker_name": "company"}
                    }
                }
            ]
        }

class GenerateDatasetResponse(BaseModel):
    message: str
    process_id: str
    nb_credit_used : int
    nb_credit_remaining : int


class CheckYamlRequest(BaseModel):
    yaml_content: Dict[str, Any] = Field(..., description="Contenu YAML converti en objet JSON")

class CheckYamlErrorDetail(BaseModel):
    info: str
    error: List[str]
    is_valid: bool

class CheckYamlSuccessResponse(BaseModel):
    message: str
    is_valid: bool