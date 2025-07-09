import httpx, os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from routes import dev_token, dataset
from schema.dataset_shema import *
load_dotenv()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


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
    # allow_credentials=True,
    # allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dev_token.router)
app.include_router(dataset.router)
