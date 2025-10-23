from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
load_dotenv()
# 1. Crée l'engine (connexion unique à PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
# 2. Crée une factory de sessions
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()




# Récupère le user id d'un token
SELECT_USER_ID_FROM_TOKEN = """
SELECT "userId" FROM public."APIHandle" WHERE "token" = :token;
"""
def select_user_id_from_token(token) -> str | bool :
    """
    Récupère le user id d'un token
    """
    try:
        result = session.execute(text(SELECT_USER_ID_FROM_TOKEN), {"token": token})
        row = result.mappings().first()
        print("row -->", row)
        if row is None:
            raise HTTPException(
                status_code=401,
                detail="API Key invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return row["userId"]
    except Exception as error:
         session.rollback()
         print("error -->",error)
         raise HTTPException(
                status_code=401,
                detail="API Key invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
