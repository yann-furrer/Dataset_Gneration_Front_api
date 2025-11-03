from dotenv import load_dotenv
from routes.dev_token import dev_token_get, dev_token_post, dev_token_delete
from routes.dataset import dataset_post, dataset_get, dataset_put
from routes.dataset_config import (
    dataset_config_get,
    dataset_config_delete,
    dataset_config_put,
)
from routes.rules_config import rules_config_put, rules_config_delete, rules_config_get
from schema.dataset_shema import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

load_dotenv()
app = FastAPI()

# Configuration CORS

origins = [
    "https://syntetica.net",  # ton site prod
    "https://www.syntetica.net",  # version avec www
    "http://localhost:3000",  # ton front local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # origines autorisées
    allow_credentials=True,  # cookies / sessions autorisés
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # méthodes HTTP autorisées
    allow_headers=[
        "content-type",
        "authorization",
        "sessiontoken",
    ],  # headers autorisés
)


# route api personnalisée
@app.get("/dataset-api", include_in_schema=False)
async def get_dataset_docs():
    """Page Swagger UI spéciale avec seulement certaines routes"""
    return get_swagger_ui_html(
        openapi_url="/openapi-dataset-api.json", title="Documentation REST simplifiée"
    )


@app.get("/dataset-config-api", include_in_schema=False)
async def get_dataset_config_docs():
    """Page Swagger UI spéciale avec seulement certaines routes"""
    return get_swagger_ui_html(
        openapi_url="/openapi-dataset-config-api.json", title="Documentation REST simplifiée"
    )




@app.get("/rules-api", include_in_schema=False)
async def get_rules_docs():
    """Page Swagger UI spéciale avec seulement certaines routes"""
    return get_swagger_ui_html(
        openapi_url="/openapi-rules-api.json", title="Documentation REST simplifiée"
    )


@app.get("/openapi-dataset-api.json", include_in_schema=False)
async def get_openapi_dataset():
    """Schéma OpenAPI restreint"""
    # Crée le schéma complet
    full_schema = get_openapi(
        title="Syntetica Api Dataset Dev",
        version="1.0.1",
        routes=app.routes,
        description="Cette Api permet d'interrragir avec les services de génération de datasets, la liste des routes est donc utilisable via un token généré sur le site syntetica.net",
    )
    # Filtre les routes voulues (ici: /special1 et /special2)
    allowed_routes = {"/dev/dataset_list", "/dev/dataset_download_link"}
    full_schema["paths"] = {
        path: schema
        for path, schema in full_schema["paths"].items()
        if path in allowed_routes
    }

    return full_schema


@app.get("/openapi-rules-api.json", include_in_schema=False)
async def get_openapi_rules():
    """Schéma OpenAPI restreint"""
    # Crée le schéma complet
    full_schema = get_openapi(
        title="Syntetica Api Rules Dev",
        version="1.0.1",
        routes=app.routes,
        description="Cette Api permet d'interrragir avec les services de règles pour la génération de datasets, la liste des routes est donc utilisable via un token généré sur le site syntetica.net",
    )
    # Filtre les routes voulues (ici: /special1 et /special2)
    allowed_routes = {"/dev/delete_rules_config", "/dev/get_all_rules_data", "/dev/create_rules_config"}
    full_schema["paths"] = {
        path: schema
        for path, schema in full_schema["paths"].items()
        if path in allowed_routes
    }

    return full_schema


@app.get("/openapi-dataset-config-api", include_in_schema=False)
async def get_openapi_test():
    """Schéma OpenAPI restreint"""
    # Crée le schéma complet
    full_schema = get_openapi(
        title="Syntetica Api Dataset Config Dev",
        version="1.0.1",
        routes=app.routes,
        description="Cette Api permet d'interrragir avec les services de dataset configuration pour la génération de datasets, la liste des routes est donc utilisable via un token généré sur le site syntetica.net",
    )
    # Filtre les routes voulues (ici: /special1 et /special2)
    allowed_routes = {
        "/dev/check_dataset_config_is_valid",
        "/dev/ping_generation_process",
        "/dev/generate_dataset",
    }
    full_schema["paths"] = {
        path: schema
        for path, schema in full_schema["paths"].items()
        if path in allowed_routes
    }

    return full_schema



# Route user pour le dev
# @app.get("/openapi-rules-config-api.json", include_in_schema=False)
# async def get_openapi_rules_config():
#     """Schéma OpenAPI restreint"""
#     # Crée le schéma complet
#     full_schema = get_openapi(
#         title="Syntetica Api Dataset Config Dev",
#         version="1.0.1",
#         routes=app.routes,
#         description="Cette Api permet d'interrragir avec les services de dataset configuration pour la génération de datasets, la liste des routes est donc utilisable via un token généré sur le site syntetica.net",
#     )
#         # Filtre les routes voulues (ici: /special1 et /special2)
#     allowed_routes = {"/dev/check_dataset_config_is_valid", "/dev/ping_generation_process", "/dev/generate_dataset"}
#     full_schema["paths"] = {
#         path: schema
#         for path, schema in full_schema["paths"].items()
#         if path in allowed_routes
#     }
#     return full_schema


app.include_router(dev_token_get.router)
app.include_router(dev_token_post.router)
app.include_router(dev_token_delete.router)

app.include_router(dataset_post.router)
app.include_router(dataset_get.router)
app.include_router(dataset_put.router)

# app.include_router(dataset_config_post.router)
app.include_router(dataset_config_get.router)
app.include_router(dataset_config_delete.router)
app.include_router(dataset_config_put.router)

app.include_router(rules_config_put.router)
app.include_router(rules_config_delete.router)
app.include_router(rules_config_get.router)

if __name__ == "__main__":
    import uvicorn
    print("Starting dev dataset api...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
