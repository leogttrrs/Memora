from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import os
import shutil
import uuid
from pathlib import Path
from fastapi.templating import Jinja2Templates
from core.database import get_connection
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloudinary_url=os.getenv("CLOUDINARY_URL"),
    secure=True
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=BASE_DIR)

router = APIRouter(
    prefix="/receitas",
    tags=["receitas"]
)

def deletar_da_nuvem(url_completa: str):
    if not url_completa or "cloudinary" not in url_completa:
        return
    try:
        public_id = url_completa.split('upload/')[-1].split('.', 1)[0]
        if '/' in public_id and public_id.startswith('v'):
            public_id = public_id.split('/', 1)[1]
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Erro ao deletar arquivo no Cloudinary: {e}")

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
def create_receita(request: Request, nome_receita: str = Form(...), ingredientes: str = Form(None),
                   modo_preparo: str = Form(None), imagem: UploadFile = File(None)):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo: return RedirectResponse(url="/")

    try:
        url_imagem = None
        if imagem and imagem.filename:
            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_receitas")
            url_imagem = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO receitas (circulo_id, nome, ingredientes, modo_preparo, imagem_capa) VALUES (%s, %s, %s, %s, %s)",
            (circulo_ativo['id'], nome_receita, ingredientes, modo_preparo, url_imagem)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/receitas", status_code=303)

@router.post("/{receita_id}/update-capa")
def update_receita_capa(receita_id: int, imagem: UploadFile = File(...)):
    try:
        if imagem and imagem.filename:
            conn = get_connection()
            cursor = conn.cursor()

            # Deleta capa antiga
            cursor.execute("SELECT imagem_capa FROM receitas WHERE id = %s", (receita_id,))
            antiga = cursor.fetchone()
            if antiga and antiga[0]: deletar_da_nuvem(antiga[0])

            # Sobe nova
            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_receitas")
            nova_url = upload_result.get("secure_url")

            cursor.execute("UPDATE receitas SET imagem_capa = %s WHERE id = %s", (nova_url, receita_id))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")
    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/{receita_id}/adicionar-foto")
def adicionar_foto_receita(receita_id: int, arquivo: UploadFile = File(...)):
    try:
        upload_result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_receitas")
        url_foto = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_receita (receita_id, caminho_foto) VALUES (%s, %s)", (receita_id, url_foto))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto: {e}")
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

        cursor.execute("SELECT imagem_capa FROM receitas WHERE id = %s", (receita_id,))
        capa = cursor.fetchone()
        if capa and capa[0]: deletar_da_nuvem(capa[0])

        cursor.execute("SELECT caminho_foto FROM fotos_receita WHERE receita_id = %s", (receita_id,))
        for f in cursor.fetchall(): deletar_da_nuvem(f[0])

        cursor.execute("DELETE FROM receitas WHERE id = %s", (receita_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao remover: {e}")
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

@router.post("/fotos/remover/{foto_id}")
def remover_foto_receita(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, receita_id FROM fotos_receita WHERE id = %s", (foto_id,))
        row = cursor.fetchone()
        if row:
            url_foto, receita_id = row[0], row[1]
            deletar_da_nuvem(url_foto) # Remove da nuvem
            cursor.execute("DELETE FROM fotos_receita WHERE id = %s", (foto_id,))
            conn.commit()
        conn.close()
        return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar: {e}")
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