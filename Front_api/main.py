from fastapi import FastAPI
from api.routes import sse, dev_token, user, dataset, dataset_sample

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware


# Configuration CORS
origins = [
    "http://localhost:3000",  # Remplacez par votre domaine frontend en développement
    "https://votredomaine.com",  # Remplacez par votre domaine frontend en production
    "https://d8bd-2a02-842a-41-2201-b8a0-4372-4c23-4b90.ngrok-free.app"
    # Vous pouvez ajouter d'autres origines si nécessaire
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Inclusion des routes
# app.include_router(gpt.router)
app.include_router(sse.router)
app.include_router(user.router)
app.include_router(dev_token.router)
app.include_router(dataset.router)
app.include_router(dataset_sample.router)

@app.get("/welcome")
async def welcome():
    return {"message": "Welcome to the FastAPI API"}