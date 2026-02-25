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
    prefix="/jogos",
    tags=["jogos"]
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
    if not circulo_ativo: return RedirectResponse(url="/")

    try:
        url_imagem = None
        if imagem and imagem.filename:
            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_jogos")
            url_imagem = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jogos (circulo_id, nome, imagem_capa) VALUES (%s, %s, %s)",
            (circulo_ativo['id'], nome_jogo, url_imagem)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/jogos", status_code=303)


@router.post("/remove-jogo/{jogo_id}")
def remove_jogo(request: Request, jogo_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT imagem_capa FROM jogos WHERE id = %s", (jogo_id,))
        capa = cursor.fetchone()
        if capa and capa[0]:
            deletar_da_nuvem(capa[0])

        cursor.execute("SELECT caminho_foto FROM fotos_jogo WHERE jogo_id = %s", (jogo_id,))
        fotos = cursor.fetchall()
        for f in fotos:
            deletar_da_nuvem(f[0])

        cursor.execute("DELETE FROM jogos WHERE id = %s", (jogo_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao remover: {e}")

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
        if imagem and imagem.filename:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT imagem_capa FROM jogos WHERE id = %s", (jogo_id,))
            antiga = cursor.fetchone()
            if antiga and antiga[0]:
                deletar_da_nuvem(antiga[0])

            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_jogos")
            nova_url = upload_result.get("secure_url")

            cursor.execute("UPDATE jogos SET imagem_capa = %s WHERE id = %s", (nova_url, jogo_id))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")
    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)

@router.post("/{jogo_id}/adicionar-foto")
def adicionar_foto_jogo(jogo_id: int, arquivo: UploadFile = File(...)):
    try:
        upload_result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_jogos")
        url_foto = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_jogo (jogo_id, caminho_foto) VALUES (%s, %s)", (jogo_id, url_foto))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao adicionar foto: {e}")
    return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)

@router.post("/fotos/remover/{foto_id}")
def remover_foto_jogo(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, jogo_id FROM fotos_jogo WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            url_foto, jogo_id = row[0], row[1]
            deletar_da_nuvem(url_foto)
            cursor.execute("DELETE FROM fotos_jogo WHERE id = %s", (foto_id,))
            conn.commit()
        conn.close()
        return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao remover foto: {e}")
        return RedirectResponse(url="/jogos", status_code=303)

@router.get("/{jogo_id}")
def read_jogo_detalhe(request: Request, jogo_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
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
            cursor.execute("SELECT id, jogo_id, caminho_foto, data_upload FROM fotos_jogo WHERE jogo_id = %s ORDER BY data_upload DESC", (jogo_id,))
            for foto in cursor.fetchall():
                lista_fotos.append({"id": foto[0], "jogo_id": foto[1], "caminho_foto": foto[2], "data_upload": foto[3]})

            jogo_encontrado = {
                "id": dados_jogo[0], "circulo_id": dados_jogo[1], "nome": dados_jogo[2],
                "nota": dados_jogo[3], "finalizado": dados_jogo[4], "caminho_imagem": dados_jogo[5], "comentarios": dados_jogo[6],
            }
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar: {e}")

    if not jogo_encontrado:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Jogo"}, status_code=404)

    return templates.TemplateResponse("jogos/jogo_detalhes.html", {
        "request": request, "jogo": jogo_encontrado, "fotos": lista_fotos,
        "circulo_ativo": circulo_ativo, "user": request.session.get('user')
    })