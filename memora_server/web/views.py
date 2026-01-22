# memora_server/web/views.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from fastapi.templating import Jinja2Templates
from core.database import get_connection

# Precisamos descobrir onde estamos para achar o HTML
# Como este arquivo está dentro de 'web/', o BASE_DIR muda um pouco
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# O arquivo index.html está na mesma pasta que este arquivo python
INDEX_PATH = os.path.join(CURRENT_DIR, "index.html")
FILMES_PATH = os.path.join(CURRENT_DIR, "filmes.html")
SERIES_PATH = os.path.join(CURRENT_DIR, "series.html")
JOGOS_PATH = os.path.join(CURRENT_DIR, "jogos.html")
RECEITAS_PATH = os.path.join(CURRENT_DIR, "receitas.html")
VIAGENS_PATH = os.path.join(CURRENT_DIR, "viagens.html")

templates = Jinja2Templates(directory=CURRENT_DIR)

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/filmes")
def read_filmes(request: Request):
    filmes_planejados = []
    filmes_assistidos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, nota FROM filmes ORDER BY id DESC")
        filmes_dados = cursor.fetchall()

        for item in filmes_dados:
            id_item = item[0]
            nome_item = item[1]
            nota = item[2]

            if nota is None:
                filmes_planejados.append({"id": id_item, "nome": nome_item})
            else:
                filmes_assistidos.append({"id": id_item, "nome": nome_item, "nota": nota})

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")

    return templates.TemplateResponse("filmes.html", {
        "request": request,
        "filmes_planejados": filmes_planejados,
        "filmes_assistidos": filmes_assistidos
    })

@router.post("/filmes/novo")
def create_filme(request: Request, nome_filme: str = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO filmes (nome) VALUES (%s)", (nome_filme,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/filmes", status_code=303)

@router.get("/filmes/{filme_id}")
def read_filme_detalhe(request: Request, filme_id: int):
    filme_encontrado = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        dados = cursor.fetchone()

        if dados:
            filme_encontrado = {
                "id": dados[0],
                "nome": dados[1],
                "nota": dados[2],
                "assistido": dados[3]
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    if not filme_encontrado:
        return templates.TemplateResponse(
            "filme_nao_encontrado.html",
            {"request": request},
            status_code=404
        )

    return templates.TemplateResponse("filme_detalhes.html", {
        "request": request,
        "filme": filme_encontrado
    })

@router.get("/series", response_class=HTMLResponse)
def read_series():
    try:
        with open(SERIES_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>series.html não encontrado!</h1>"

@router.get("/jogos", response_class=HTMLResponse)
def read_jogos():
    try:
        with open(JOGOS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>jogos.html não encontrado!</h1>"

@router.get("/receitas", response_class=HTMLResponse)
def read_receitas():
    try:
        with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>receitas.html não encontrado!</h1>"

@router.get("/viagens", response_class=HTMLResponse)
def read_viagens():
    try:
        with open(VIAGENS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>viagens.html não encontrado!</h1>"