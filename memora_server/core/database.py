import psycopg2
from dotenv import load_dotenv
import os

if os.getenv("ENV") != "production":
    load_dotenv(".env.development")


def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        return psycopg2.connect(db_url)
    else:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB"),
        )