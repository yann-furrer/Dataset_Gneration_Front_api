import uvicorn
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from utils.faker_handler import FakerHandler
from routes import micro_get, micro_delete, micro_put, micro_post

load_dotenv()

API_KEY = os.getenv("API_KEY")  # À changer/environner en production !


# Dépendance qui vérifie la clé reçue
def verify_api_key(api_key: str = Header(...)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key invalide"
        )


# Instanciation de la classe qui gère les types fakers
faker_handler = FakerHandler()

app = FastAPI()

# route api personnalisée
@app.get("/faker-api", include_in_schema=False)
async def get_lite_docs():
    """Page Swagger UI spéciale avec seulement certaines routes"""
    return get_swagger_ui_html(
        openapi_url="/openapi-faker-api.json", title="Documentation REST simplifiée"
    )


@app.get("/openapi-faker-api.json", include_in_schema=False)
async def get_openapi_lite():
    """Schéma OpenAPI restreint"""
    # Crée le schéma complet
    full_schema = get_openapi(
        title="Syntetica Api Microservice Dev",
        version="1.0.1",
        routes=app.routes,
        description="Cette Api permet d'interrragir avec les services de génération de variable fakers, la liste des routes est donc utilisable via un token généré sur le site syntetica.net",
    )

    # Filtre les routes voulues (ici: /special1 et /special2)
    allowed_routes = {"/dev/faker_name_list", "/dev/delete_faker_type/", "/dev/insert_faker_type"}
    full_schema["paths"] = {
        path: schema
        for path, schema in full_schema["paths"].items()
        if path in allowed_routes
    }

    return full_schema


app.include_router(micro_get.router)
app.include_router(micro_put.router)
app.include_router(micro_post.router)
app.include_router(micro_delete.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000, log_level="info")
