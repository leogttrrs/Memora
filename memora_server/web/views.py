# memora_server/web/views.py
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from fastapi.templating import Jinja2Templates
from core.database import get_connection
import shutil
import uuid
from pathlib import Path

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
def create_filme(request: Request, nome_filme: str = Form(...), imagem: UploadFile = File(None)):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:

            if imagem.content_type not in TIPOS_VALIDOS:
                print(f"Arquivo rejeitado: {imagem.content_type}")
                return RedirectResponse(url="/filmes", status_code=303)

            extensao = imagem.filename.split(".")[-1]
            nome_arquivo = f"{uuid.uuid4()}.{extensao}"

            pasta_destino = Path("static/uploads")
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho_final = pasta_destino / nome_arquivo

            with open(caminho_final, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)
            caminho_imagem = f"uploads/{nome_arquivo}"

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO filmes (nome, imagem_capa) VALUES (%s, %s)", (nome_filme, caminho_imagem))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/filmes", status_code=303)


@router.post("/filmes/{filme_id}/update-capa")
def update_filme_capa(
        filme_id: int,
        imagem: UploadFile = File(...)
):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if imagem and imagem.filename:

            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/filmes?erro=tipo_invalido", status_code=303)

            extensao = imagem.filename.split(".")[-1]
            nome_arquivo = f"{uuid.uuid4()}.{extensao}"

            pasta_destino = Path("static/uploads")
            pasta_destino.mkdir(parents=True, exist_ok=True)
            caminho_final = pasta_destino / nome_arquivo

            with open(caminho_final, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)

            caminho_imagem = f"uploads/{nome_arquivo}"

        if caminho_imagem:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE filmes SET imagem_capa = %s WHERE id = %s",
                (caminho_imagem, filme_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)

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
                "assistido": dados[3],
                "caminho_imagem": dados[4]
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

    return templates.TemplateResponse(
        "filme_detalhes.html",
        {"request": request,"filme": filme_encontrado}
    )

@router.post("/filmes/remove-plan/{filme_id}")
def remove_plan_filme(request: Request, filme_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM filmes WHERE ID = %s", (filme_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/filmes", status_code=303)

@router.post("/filmes/mark-as-watched/{filme_id}")
def mark_as_watched_filme(request: Request, filme_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE filmes SET assistido = true, nota = %s WHERE id = %s",
            (nota, filme_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)

@router.post("/filmes/alterar-nota/{filme_id}")
def alterar_nota_filme(request: Request, filme_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        print(filme_id)
        print(nota)

        cursor.execute(
            "UPDATE filmes SET nota = %s where id = %s", (nota, filme_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)

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