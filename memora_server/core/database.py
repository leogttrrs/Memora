import psycopg2
from dotenv import load_dotenv
import os

load_dotenv(".env.development")

ENV = os.getenv("ENV", "development")

def get_connection():
    if ENV == "production":
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    else:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )
