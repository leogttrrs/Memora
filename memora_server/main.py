from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from core.database import get_connection
import os

from web.routers import filmes, series, jogos, receitas, viagens, auth, circulos

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="uma-chave-muito-secreta-memora-2026")

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(auth.router)
app.include_router(circulos.router)
app.include_router(filmes.router)
app.include_router(series.router)
app.include_router(jogos.router)
app.include_router(receitas.router)
app.include_router(viagens.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get('user')
    lista_circulos = []
    lista_convites = []

    if user:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, c.nome, mc.papel, c.emoji 
                FROM circulos c
                JOIN membros_circulo mc ON c.id = mc.circulo_id
                WHERE mc.usuario_id = %s
                ORDER BY 
                    CASE WHEN mc.papel = 'admin' THEN 1 ELSE 2 END ASC, 
                    c.data_criacao ASC
            """, (user['id'],))
            for row in cursor.fetchall():
                lista_circulos.append({"id": row[0], "nome": row[1], "papel": row[2], "emoji": row[3] or '🪐'})

            cursor.execute("""
                SELECT conv.id, circ.nome, circ.emoji 
                FROM convites conv
                JOIN circulos circ ON conv.circulo_id = circ.id
                WHERE conv.email_convidado = %s
            """, (user['email'],))
            for row in cursor.fetchall():
                lista_convites.append({"id": row[0], "nome_circulo": row[1], "emoji": row[2]})

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao buscar dados do lobby: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "circulos": lista_circulos,
        "convites": lista_convites
    })


@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(request: Request):
    user = request.session.get('user')
    circulo_ativo = request.session.get('circulo_ativo')

    if not user or not circulo_ativo:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "circulo_ativo": circulo_ativo
    })