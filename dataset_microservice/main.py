import uvicorn, asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from generator.yaml_generator import YamlGenerator



app = FastAPI()


@app.get("/dataset_microservice")
async def get_dataset(request: Request):
    return JSONResponse({"[info]": "Welcome to this API, it is a micro service for generating datasets config"})

@app.post("/get_dataset/{dataset_name}")
async def get_dataset(request: Request, dataset_name: str):
        body = await request.json()
        dataset_name = body.get("dataset_name", "new dataset")
        yaml_data = body.get("yaml_data", None)
        number_of_records = body.get("number_of_records", 1000)
        entrytpath = body.get("entrytpath", "root")
     
        dataset_config_class = YamlGenerator(dataset_name=dataset_name,sample_data=yaml_data, number_of_records=number_of_records, entrytpath=entrytpath)
        dataset_config = asyncio.run(dataset_config_class.execute(False))
        return JSONResponse({"dataset_config": dataset_config})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000, log_level="info")