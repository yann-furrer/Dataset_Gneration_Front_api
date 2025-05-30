import uvicorn, os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Header, HTTPException, status, Depends, Request

from generator.yaml_generator import YamlGenerator
from dataset_sample_generation import datasetSampleGeneration
load_dotenv()


API_KEY = os.getenv("API_KEY")  # À changer/environner en production !

# Dépendance qui vérifie la clé reçue
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key invalide"
        )


app = FastAPI()



@app.get("/")
async def read_root():
    return {"msg": "Accès autorisé"}




@app.get("/dataset_microservice", dependencies=[Depends(verify_api_key)])
async def get_dataset():
    return JSONResponse({"[info]": "Welcome to this API, it is a micro service for generating datasets config"})


@app.post("/dataset_sample", dependencies=[Depends(verify_api_key)])
async def dataset_sample(request: Request):
        body = await request.json()
        user_prompt = body.get("user_prompt", None)
        if user_prompt is None:
            return JSONResponse({"error": "user_prompt is required"}, status_code=400)
        dataset_sample_class = datasetSampleGeneration()
        dataset_sample = await dataset_sample_class.generate_sample(user_prompt=user_prompt)
        return JSONResponse({"dataset_sample": dataset_sample})


@app.post("/get_dataset")
async def get_dataset(request: Request):
        body = await request.json()

        dataset_name = body.get("dataset_name", "new dataset")
        yaml_data = body.get("yaml_data", None)
        number_of_records = body.get("number_of_records", 1000)
        entrytpath = body.get("entrytpath", "root")
     
        dataset_config_class = YamlGenerator(dataset_name=dataset_name,sample_data=yaml_data, number_of_records=number_of_records, entrytpath=entrytpath)
        dataset_config = await dataset_config_class.execute(False)
        return JSONResponse({"dataset_config": dataset_config})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000, log_level="info")