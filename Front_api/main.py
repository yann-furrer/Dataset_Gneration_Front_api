import httpx
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from routes.dataset import dataset_post, dataset_get, dataset_delete
from routes import sse, dev_token, user, dataset_sample, stripe, datamesh
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
app = FastAPI()



# Configuration CORS
origins = [
    "http://localhost:3000",  # Remplacez par votre domaine frontend en développement
    "https://d8bd-2a02-842a-41-2201-b8a0-4372-4c23-4b90.ngrok-free.app",
    "https://datasetgenerationfront-dev.up.railway.app"
    # Vous pouvez ajouter d'autres origines si nécessaire
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
# app.include_router(gpt.router)
app.include_router(sse.router)
app.include_router(user.router)
app.include_router(dev_token.router)


app.include_router(dataset_delete.router)
app.include_router(dataset_post.router)
app.include_router(dataset_get.router)

app.include_router(dataset_sample.router)
app.include_router(datamesh.router)
app.include_router(stripe.router)

@app.get("/welcome")
async def welcome():
    return {"message": "Welcome to the FastAPI API"}

@app.get("/ping_microservice")
async def ping_microservice():
    async with httpx.AsyncClient() as client:
        MICRO_SERVICE_URL = os.getenv("MICRO_SERVICE_URL")
        print("micro service url:", MICRO_SERVICE_URL)
        response = await client.get(f"{MICRO_SERVICE_URL}/pinged_microservice", headers={"X-API-KEY": os.getenv("API_KEY")})
        print("response:", response.json())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()