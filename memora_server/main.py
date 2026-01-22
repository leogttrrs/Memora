from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from api import endpoints
from web import views

app = FastAPI(title="Memora System")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(endpoints.router, prefix="/api", tags=["api"])

app.include_router(views.router, tags=["web"])