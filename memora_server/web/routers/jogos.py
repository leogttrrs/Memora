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
    prefix="/jogos",
    tags=["jogos"]
)


@router.get("/")
def read_jogos(request: Request):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    jogos_planejados = []
    jogos_finalizados = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, nota FROM jogos WHERE circulo_id = %s ORDER BY id DESC",
            (circulo_ativo['id'],)
        )
        jogos_dados = cursor.fetchall()

        for item in jogos_dados:
            id_item = item[0]
            nome_item = item[1]
            nota = item[2]

            if nota is None:
                jogos_planejados.append({"id": id_item, "nome": nome_item})
            else:
                jogos_finalizados.append({"id": id_item, "nome": nome_item, "nota": nota})

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")

    return templates.TemplateResponse("jogos/jogos.html", {
        "request": request,
        "jogos_planejados": jogos_planejados,
        "jogos_finalizados": jogos_finalizados,
        "circulo_ativo": circulo_ativo,
        "user": user
    })


@router.post("/novo")
def create_jogo(request: Request, nome_jogo: str = Form(...), imagem: UploadFile = File(None)):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/jogos", status_code=303)

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

        cursor.execute(
            "INSERT INTO jogos (circulo_id, nome, imagem_capa) VALUES (%s, %s, %s)",
            (circulo_ativo['id'], nome_jogo, caminho_imagem)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/jogos", status_code=303)


@router.post("/remove-jogo/{jogo_id}")
def remove_jogo(request: Request, jogo_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM jogos WHERE ID = %s", (jogo_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/jogos", status_code=303)


@router.post("/marcar-finalizado/{jogo_id}")
def marcar_finalizado_jogo(request: Request, jogo_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE jogos SET finalizado = true, nota = %s WHERE id = %s",
            (nota, jogo_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.get("/desmarcar-finalizado/{jogo_id}")
def desmarcar_finalizado(jogo_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE jogos SET finalizado = false, nota = null WHERE id = %s",
            (jogo_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar finalizado: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.post("/alterar-nota/{jogo_id}")
def alterar_nota_jogo(request: Request, jogo_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE jogos SET nota = %s where id = %s", (nota, jogo_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.post("/update-comentario/{jogo_id}")
def update_comentario_jogo(jogo_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE jogos SET comentario = %s WHERE id = %s",
            (comentario, jogo_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.post("/{jogo_id}/update-capa")
def update_jogo_capa(jogo_id: int, imagem: UploadFile = File(...)):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/jogos?erro=tipo_invalido", status_code=303)

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
                "UPDATE jogos SET imagem_capa = %s WHERE id = %s",
                (caminho_imagem, jogo_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.post("/{jogo_id}/adicionar-foto")
def adicionar_foto_jogo(jogo_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/jogos/{jogo_id}?erro=arquivo_invalido", status_code=303)

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
            "INSERT INTO fotos_jogo (jogo_id, caminho_foto) VALUES (%s, %s)",
            (jogo_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)


@router.post("/fotos/remover/{foto_id}")
def remover_foto_jogo(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, jogo_id FROM fotos_jogo WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_relativo = row[0]
            jogo_id = row[1]
            caminho_arquivo = Path("static") / caminho_relativo

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_jogo WHERE id = %s", (foto_id,))
            conn.commit()

            conn.close()
            return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/jogos", status_code=303)


@router.get("/{jogo_id}")
def read_jogo_detalhe(request: Request, jogo_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    jogo_encontrado = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jogos WHERE id = %s AND circulo_id = %s", (jogo_id, circulo_ativo['id']))
        dados_jogo = cursor.fetchone()

        if dados_jogo:
            cursor.execute("SELECT * FROM fotos_jogo WHERE jogo_id = %s ORDER BY data_upload DESC", (jogo_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
                lista_fotos.append({
                    "id": foto[0],
                    "jogo_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3]
                })

            jogo_encontrado = {
                "id": dados_jogo[0],
                "circulo_id": dados_jogo[1],
                "nome": dados_jogo[2],
                "nota": dados_jogo[3],
                "finalizado": dados_jogo[4],
                "caminho_imagem": dados_jogo[5],
                "comentarios": dados_jogo[6],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao buscar detalhes: {e}")

    if not jogo_encontrado:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Jogo"},
            status_code=404
        )

    return templates.TemplateResponse(
        "jogos/jogo_detalhes.html",
        {"request": request, "jogo": jogo_encontrado, "fotos": lista_fotos, "circulo_ativo": circulo_ativo, "user": user}
    )