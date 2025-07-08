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



# # 3. Exemple de requête SELECT
# def get_all_users():
#     result = session.execute(text('SELECT * FROM public."User";'))
#     return result.fetchall()

# a= get_all_users()

# print(a)