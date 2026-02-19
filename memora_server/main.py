from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from web.routers import filmes, series, jogos, receitas, viagens

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(filmes.router)
app.include_router(series.router)
app.include_router(jogos.router)
app.include_router(receitas.router)
app.include_router(viagens.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})