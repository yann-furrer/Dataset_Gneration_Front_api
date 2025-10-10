from dotenv import load_dotenv
from fastapi import FastAPI
from routes.dev_token import  dev_token_get , dev_token_post, dev_token_delete
from routes import dataset
from schema.dataset_shema import *
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
app = FastAPI()



# Configuration CORS

origins = [
    "https://syntetica.net",      # ton site prod
    "https://www.syntetica.net",  # version avec www
    "http://localhost:3000",      # ton front local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,               # origines autorisées
    allow_credentials=True,              # cookies / sessions autorisés
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # méthodes HTTP autorisées
    allow_headers=["content-type", "authorization", "sessiontoken"],  # headers autorisés
)

app.include_router(dev_token_get.router)
app.include_router(dev_token_post.router)
app.include_router(dev_token_delete.router)
app.include_router(dataset.router)
