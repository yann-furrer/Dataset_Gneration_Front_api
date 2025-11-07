from utils.aws_secret import create_env_file_from_secret
print("load aws secret")
create_env_file_from_secret()
from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

