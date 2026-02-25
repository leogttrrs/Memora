from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import os
import cloudinary
import cloudinary.uploader
from fastapi.templating import Jinja2Templates
from core.database import get_connection

cloudinary.config(
    cloudinary_url=os.getenv("CLOUDINARY_URL"),
    secure=True
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=BASE_DIR)

router = APIRouter(
    prefix="/filmes",
    tags=["filmes"]
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
def read_filmes(request: Request):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    filmes_planejados = []
    filmes_assistidos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, nota FROM filmes WHERE circulo_id = %s ORDER BY id DESC",
            (circulo_ativo['id'],)
        )
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
        "filmes_assistidos": filmes_assistidos,
        "circulo_ativo": circulo_ativo,
        "user": user,
    })


@router.post("/novo")
def create_filme(request: Request, nome_filme: str = Form(...), imagem: UploadFile = File(None)):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo: return RedirectResponse(url="/")

    try:
        url_imagem = None
        if imagem and imagem.filename:
            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_filmes")
            url_imagem = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO filmes (circulo_id, nome, imagem_capa) VALUES (%s, %s, %s)",
            (circulo_ativo['id'], nome_filme, url_imagem)
        )
        conn.commit()
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

        cursor.execute("SELECT imagem_capa FROM filmes WHERE id = %s", (filme_id,))
        capa = cursor.fetchone()
        if capa and capa[0]: deletar_da_nuvem(capa[0])

        cursor.execute("SELECT caminho_foto FROM fotos_filme WHERE filme_id = %s", (filme_id,))
        fotos = cursor.fetchall()
        for f in fotos: deletar_da_nuvem(f[0])

        cursor.execute("DELETE FROM filmes WHERE id = %s", (filme_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao remover filme: {e}")

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
def update_filme_capa(filme_id: int, imagem: UploadFile = File(...)):
    try:
        if imagem and imagem.filename:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT imagem_capa FROM filmes WHERE id = %s", (filme_id,))
            antiga = cursor.fetchone()
            if antiga and antiga[0]:
                deletar_da_nuvem(antiga[0])

            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_filmes")
            nova_url = upload_result.get("secure_url")

            cursor.execute("UPDATE filmes SET imagem_capa = %s WHERE id = %s", (nova_url, filme_id))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")
    return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)

@router.post("/{filme_id}/adicionar-foto")
def adicionar_foto_filme(filme_id: int, arquivo: UploadFile = File(...)):
    try:
        upload_result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_filmes")
        url_foto = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_filme (filme_id, caminho_foto) VALUES (%s, %s)", (filme_id, url_foto))
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
            url_foto, filme_id = row[0], row[1]
            deletar_da_nuvem(url_foto)
            cursor.execute("DELETE FROM fotos_filme WHERE id = %s", (foto_id,))
            conn.commit()
        conn.close()
        return RedirectResponse(url=f"/filmes/{filme_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/filmes", status_code=303)

@router.get("/{filme_id}")
def read_filme_detalhe(request: Request, filme_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo: return RedirectResponse(url="/")

    filme_encontrado = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filmes WHERE id = %s AND circulo_id = %s", (filme_id, circulo_ativo['id']))
        dados_filme = cursor.fetchone()

        if dados_filme:
            cursor.execute("SELECT id, filme_id, caminho_foto, data_upload FROM fotos_filme WHERE filme_id = %s ORDER BY data_upload DESC", (filme_id,))
            for foto in cursor.fetchall():
                lista_fotos.append({"id": foto[0], "filme_id": foto[1], "caminho_foto": foto[2], "data_upload": foto[3]})

            filme_encontrado = {
                "id": dados_filme[0], "circulo_id": dados_filme[1], "nome": dados_filme[2],
                "nota": dados_filme[3], "assistido": dados_filme[4], "caminho_imagem": dados_filme[5], "comentarios": dados_filme[6],
            }
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar detalhes: {e}")

    if not filme_encontrado:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Filme"}, status_code=404)

    return templates.TemplateResponse("filmes/filme_detalhes.html", {
        "request": request, "filme": filme_encontrado, "fotos": lista_fotos,
        "circulo_ativo": circulo_ativo, "user": request.session.get('user')
    })