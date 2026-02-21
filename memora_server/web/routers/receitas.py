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
    prefix="/receitas",
    tags=["receitas"]
)


@router.get("/")
def read_receitas(request: Request):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    receitas_planejadas = []
    receitas_provadas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, nota FROM receitas WHERE circulo_id = %s ORDER BY id DESC",
            (circulo_ativo['id'],)
        )
        receitas_dados = cursor.fetchall()

        for item in receitas_dados:
            id_item = item[0]
            nome_item = item[1]
            nota = item[2]

            if nota is None:
                receitas_planejadas.append({"id": id_item, "nome": nome_item})
            else:
                receitas_provadas.append({"id": id_item, "nome": nome_item, "nota": nota})

        print(receitas_provadas)
        print(receitas_planejadas)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")

    return templates.TemplateResponse("receitas/receitas.html", {
        "request": request,
        "receitas_planejadas": receitas_planejadas,
        "receitas_provadas": receitas_provadas,
        "circulo_ativo": circulo_ativo,
        "user": user
    })


@router.post("/novo")
def create_receita(
        request: Request,
        nome_receita: str = Form(...),
        ingredientes: str = Form(None),
        modo_preparo: str = Form(None),
        imagem: UploadFile = File(None)
):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/receitas?erro=tipo_invalido", status_code=303)

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
            """
            INSERT INTO receitas (circulo_id, nome, ingredientes, modo_preparo, imagem_capa) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (circulo_ativo['id'], nome_receita, ingredientes, modo_preparo, caminho_imagem)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/receitas", status_code=303)


@router.post("/{receita_id}/update-capa")
def update_receita_capa(receita_id: int, imagem: UploadFile = File(...)):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/receitas?erro=tipo_invalido", status_code=303)

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
            cursor.execute("UPDATE receitas SET imagem_capa = %s WHERE id = %s", (caminho_imagem, receita_id))
            conn.commit()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/update-comentario/{receita_id}")
def update_comentario_receitas(receita_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET comentario = %s WHERE id = %s", (comentario, receita_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/update-ingredientes/{receita_id}")
def update_ingredientes_receitas(receita_id: int, ingredientes: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET ingredientes = %s WHERE id = %s", (ingredientes, receita_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar ingredientes: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/update-modo-preparo/{receita_id}")
def update_modo_preparo_receitas(receita_id: int, modo_preparo: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET modo_preparo = %s WHERE id = %s", (modo_preparo, receita_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar modo_preparo: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.get("/desmarcar-provada/{receita_id}")
def desmarcar_provada(receita_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET provada = false, nota = null WHERE id = %s", (receita_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar provada: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/remove-receita/{receita_id}")
def remove_receita(request: Request, receita_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM receitas WHERE ID = %s", (receita_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    return RedirectResponse(url="/receitas", status_code=303)


@router.post("/marcar-provada/{receita_id}")
def mark_as_watched_receita(request: Request, receita_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET provada = true, nota = %s WHERE id = %s", (nota, receita_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/alterar-nota/{receita_id}")
def alterar_nota_receita(request: Request, receita_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE receitas SET nota = %s where id = %s", (nota, receita_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/{receita_id}/adicionar-foto")
def adicionar_foto_receita(receita_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/receitas/{receita_id}?erro=arquivo_invalido", status_code=303)
    try:
        extensao = arquivo.filename.split(".")[-1]
        nome_novo = f"{uuid.uuid4()}.{extensao}"
        caminho_relativo = f"uploads/{nome_novo}"
        caminho_absoluto = Path("static") / caminho_relativo
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_receita (receita_id, caminho_foto) VALUES (%s, %s)",
                       (receita_id, caminho_relativo))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)


@router.post("/fotos/remover/{foto_id}")
def remover_foto_receita(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, receita_id FROM fotos_receita WHERE id = %s", (foto_id,))
        row = cursor.fetchone()
        if row:
            caminho_relativo = row[0]
            receita_id = row[1]
            caminho_arquivo = Path("static") / caminho_relativo
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
            cursor.execute("DELETE FROM fotos_receita WHERE id = %s", (foto_id,))
            conn.commit()
            conn.close()
            return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/receitas", status_code=303)


@router.get("/{receita_id}")
def read_receita_detalhe(request: Request, receita_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    receita_encontrada = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM receitas WHERE id = %s AND circulo_id = %s", (receita_id, circulo_ativo['id']))
        dados_receita = cursor.fetchone()

        if dados_receita:
            cursor.execute("SELECT * FROM fotos_receita WHERE receita_id = %s ORDER BY data_upload DESC", (receita_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
                lista_fotos.append({
                    "id": foto[0],
                    "receita_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3]
                })

            receita_encontrada = {
                "id": dados_receita[0],
                "circulo_id": dados_receita[1],
                "nome": dados_receita[2],
                "nota": dados_receita[3],
                "provada": dados_receita[4],
                "caminho_imagem": dados_receita[5],
                "ingredientes": dados_receita[6],
                "modo_preparo": dados_receita[7],
                "comentario": dados_receita[8],
            }

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao carregar detalhes: {e}")

    if not receita_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Receita"},
            status_code=404
        )

    return templates.TemplateResponse(
        "receitas/receita_detalhes.html",
        {"request": request, "receita": receita_encontrada, "fotos": lista_fotos, "circulo_ativo": circulo_ativo, "user": user}
    )