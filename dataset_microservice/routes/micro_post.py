import json
import os
from generator.rules_generator import RulesGenerator
from generator.webconfig_generator import WebConfigGenerator
from dataset_sample_generation import datasetSampleGeneration
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from fastapi.responses import JSONResponse

API_KEY = os.getenv("API_KEY")  # À changer/environner en production !


# Dépendance qui vérifie la clé reçue
def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key invalide"
        )

router = APIRouter()
@router.post("/dataset_sample", dependencies=[Depends(verify_api_key)])
async def dataset_sample(request: Request):
    body = await request.json()
    user_prompt = body.get("user_prompt", None)
    if user_prompt is None:
        return JSONResponse({"error": "user_prompt is required"}, status_code=400)
    dataset_sample_class = datasetSampleGeneration()
    dataset_sample = await dataset_sample_class.generate_sample(user_prompt=user_prompt)
    return JSONResponse({"dataset_sample": dataset_sample})


@router.post("/generate_webconfig", dependencies=[Depends(verify_api_key)])
async def generate_webconfig(request: Request):
    body = await request.json()
    client_id = body.get("client_id", None)
    json_sample = body.get("json_sample", None)
    print(json_sample)
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="client_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    webconfig_class = WebConfigGenerator(client_id=client_id)
    dataset_config = await webconfig_class.build_schema(input_data=json_sample)
    return JSONResponse(dataset_config)


##################### Routes pour la gestion des règles
@router.post("/generate_rules", dependencies=[Depends(verify_api_key)])
async def generate_rules(request: Request):
    body = await request.json()
    client_id = body.get("client_id", None)
    user_prompt = body.get("user_prompt", None)
    dataset_id = body.get("dataset_id", None)
    if not client_id:
        raise HTTPException(
            status_code=400,
            detail="client_id is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif len(user_prompt) < 50:
        raise HTTPException(
            status_code=400,
            detail="user_prompt is too short",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif len(user_prompt) > 1500:
        raise HTTPException(
            status_code=400,
            detail="user_prompt is too long",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Instanciation du générateur de règles
    rules_generator = RulesGenerator()

    # Récupération et parsing du YAML (attention à la signature des méthodes)
    yaml_config = rules_generator.get_yaml_config_file_by_id(
        user_id=client_id, dataset_id=dataset_id
    )
    # On suppose que get_yaml_config_file_by_id retourne déjà le YAML à parser
    rules_generator.parse_yaml_config( yaml_config=rules_generator.yaml_config)
    print(rules_generator.yaml_config)
    # Génération des règles
    rules = await rules_generator.generate_rules(user_prompt=user_prompt)

    # Nettoyage (éviter les triples quotes inutiles, par exemple)
    rules = rules.replace("```json", "")
    rules = rules.replace("```", "")

    return JSONResponse({"rules": json.loads(rules)})
