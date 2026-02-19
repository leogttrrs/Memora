from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import os
import shutil
import uuid
from pathlib import Path
from fastapi.templating import Jinja2Templates
from core.database import get_connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=BASE_DIR)

router = APIRouter(
    prefix="/filmes",
    tags=["filmes"]
)

@router.get("/")
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

    return templates.TemplateResponse("filmes/filmes.html", {
        "request": request,
        "filmes_planejados": filmes_planejados,
        "filmes_assistidos": filmes_assistidos
    })


@router.post("/novo")
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


@router.get("/desmarcar-assistido/{filme_id}")
def desmarcar_assistido(filme_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE filmes SET assistido = false, nota = null WHERE id = %s",
            (filme_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar assistido: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)


@router.post("/remove-filme/{filme_id}")
def remove_filme(request: Request, filme_id: int):
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


@router.post("/mark-as-watched/{filme_id}")
def mark_as_watched_filme(request: Request, filme_id: int, nota: int = Form(...)):
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


@router.post("/alterar-nota/{filme_id}")
def alterar_nota_filme(request: Request, filme_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE filmes SET nota = %s where id = %s", (nota, filme_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)


@router.post("/update-comentario/{filme_id}")
def update_comentario_filme(filme_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE filmes SET comentario = %s WHERE id = %s",
            (comentario, filme_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)


@router.post("/{filme_id}/update-capa")
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


@router.post("/{filme_id}/adicionar-foto")
def adicionar_foto_filme(filme_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/filmes/{filme_id}?erro=arquivo_invalido", status_code=303)

    try:
        extensao = arquivo.filename.split(".")[-1]
        nome_novo = f"{uuid.uuid4()}.{extensao}"
        caminho_relativo = f"uploads/{nome_novo}"

        caminho_absoluto = Path("static") / caminho_relativo
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fotos_filme (filme_id, caminho_foto) VALUES (%s, %s)",
            (filme_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)


@router.post("/fotos/remover/{foto_id}")
def remover_foto_filme(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, filme_id FROM fotos_filme WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_arquivo = Path("static") / row[0]
            filme_id = row[1]

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_filme WHERE id = %s", (foto_id,))
            conn.commit()

            conn.close()
            return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/filmes", status_code=303)


@router.get("/{filme_id}")
def read_filme_detalhe(request: Request, filme_id: int):
    filme_encontrado = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM filmes WHERE id = %s", (filme_id,))
        dados_filme = cursor.fetchone()

        if dados_filme:
            cursor.execute("SELECT * FROM fotos_filme WHERE filme_id = %s ORDER BY data_upload DESC", (filme_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
                lista_fotos.append({
                    "id": foto[0],
                    "filme_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3]
                })

            filme_encontrado = {
                "id": dados_filme[0],
                "nome": dados_filme[1],
                "nota": dados_filme[2],
                "assistido": dados_filme[3],
                "caminho_imagem": dados_filme[4],
                "comentarios": dados_filme[5],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao buscar detalhes do filme: {e}")

    if not filme_encontrado:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Filme"},
            status_code=404
        )

    return templates.TemplateResponse(
        "filmes/filme_detalhes.html",
        {"request": request,"filme": filme_encontrado, "fotos": lista_fotos}
    )