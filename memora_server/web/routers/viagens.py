from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
import os
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
    prefix="/viagens",
    tags=["viagens"]
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

def ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id):
    cursor.execute("SELECT visitada, nota FROM cidades_x_viagem WHERE viagem_id = %s", (viagem_id,))
    dados_cidades = cursor.fetchall()

    num_cidades_total = len(dados_cidades)
    num_cidades_visitadas = 0
    nota_total = 0

    for cidade in dados_cidades:
        if cidade[0]:
            num_cidades_visitadas += 1
            if cidade[1]:
                nota_total += cidade[1]

    nota_geral_viagem = None
    if num_cidades_visitadas > 0:
        nota_geral_viagem = round(nota_total / num_cidades_visitadas)

    viagem_feita = (num_cidades_total == num_cidades_visitadas) and num_cidades_total > 0

    cursor.execute(
        "UPDATE viagens SET nota = %s, feita = %s WHERE id = %s",
        (nota_geral_viagem, viagem_feita, viagem_id)
    )
    conn.commit()


@router.get("/")
def read_viagens(request: Request):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    viagens_planejadas = []
    viagens_feitas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, nota, feita FROM viagens WHERE circulo_id = %s ORDER BY id DESC", (circulo_ativo['id'],))
        viagens_dados = cursor.fetchall()

        for item in viagens_dados:
            viagem_id = item[0]
            viagem_nome = item[1]
            nota = item[2]
            feita = item[3]

            viagem_obj = {
                "id": viagem_id,
                "nome": viagem_nome,
                "nota": nota,
            }

            if not feita:
                viagens_planejadas.append(viagem_obj)
            else:
                viagens_feitas.append(viagem_obj)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao ler viagens: {e}")

    return templates.TemplateResponse("viagens/viagens.html", {
        "request": request,
        "viagens_planejadas": viagens_planejadas,
        "viagens_feitas": viagens_feitas,
        "circulo_ativo": circulo_ativo,
        "user": user
    })

@router.post("/novo")
def create_viagem(request: Request, nome_viagem: str = Form(...), cidades: list[str] = Form(...), imagem: UploadFile = File(None)):
    circulo_ativo = request.session.get('circulo_ativo')
    URL_PADRAO_CIDADE = "https://res.cloudinary.com/dcj3ttx9j/image/upload/v1771983520/default_cover_k7dlns.jpg"
    if not circulo_ativo:
        return RedirectResponse(url="/")

    try:
        url_imagem = None
        if imagem and imagem.filename:
            upload_result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_viagens")
            url_imagem = upload_result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO viagens (circulo_id, nome, imagem_capa) VALUES (%s, %s, %s) RETURNING id",
            (circulo_ativo['id'], nome_viagem, url_imagem)
        )
        viagem_id = cursor.fetchone()[0]

        for nome_cidade in cidades:
            nome_limpo = nome_cidade.strip()
            if nome_limpo:
                cursor.execute(
                    "INSERT INTO cidades_x_viagem (viagem_id, nome_cidade, caminho_foto, nota) VALUES (%s, %s, %s, 0)",
                    (viagem_id, nome_limpo, URL_PADRAO_CIDADE)
                )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar viagem: {e}")

    return RedirectResponse(url="/viagens", status_code=303)

@router.post("/remove-viagem/{viagem_id}")
def remove_viagem(request: Request, viagem_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT imagem_capa FROM viagens WHERE id = %s", (viagem_id,))
        capa = cursor.fetchone()
        if capa and capa[0]:
            deletar_da_nuvem(capa[0])

        cursor.execute("SELECT caminho_foto FROM fotos_viagem WHERE viagem_id = %s", (viagem_id,))
        for f in cursor.fetchall():
            deletar_da_nuvem(f[0])

        cursor.execute("DELETE FROM viagens WHERE id = %s", (viagem_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao remover viagem: {e}")
    return RedirectResponse(url="/viagens", status_code=303)


@router.post("/{viagem_id}/update-capa")
def update_viagem_capa(viagem_id: int, imagem: UploadFile = File(...)):
    try:
        if imagem and imagem.filename:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT imagem_capa FROM viagens WHERE id = %s", (viagem_id,))
            antiga = cursor.fetchone()
            if antiga and antiga[0]:
                deletar_da_nuvem(antiga[0])

            upload_result = cloudinary.uploader.upload(
                imagem.file,
                folder="memora/capas_viagens"
            )
            nova_url = upload_result.get("secure_url")

            cursor.execute(
                "UPDATE viagens SET imagem_capa = %s WHERE id = %s",
                (nova_url, viagem_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa da viagem no Cloudinary: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)

@router.post("/update-comentario/{viagem_id}")
def update_comentario_viagem(viagem_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE viagens SET comentario = %s WHERE id = %s", (comentario, viagem_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario da viagem: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)

@router.post("/{viagem_id}/adicionar-foto")
def adicionar_foto_viagem(viagem_id: int, arquivo: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_viagens")
        url_foto = result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_viagem (viagem_id, caminho_foto) VALUES (%s, %s)", (viagem_id, url_foto))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto: {e}")
    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)

@router.post("/fotos/remover/{foto_id}")
def remover_foto_viagem(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, viagem_id FROM fotos_viagem WHERE id = %s", (foto_id,))
        row = cursor.fetchone()
        if row:
            url_foto, viagem_id = row[0], row[1]
            deletar_da_nuvem(url_foto)
            cursor.execute("DELETE FROM fotos_viagem WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_cidade WHERE caminho_foto = %s", (url_foto,))
            conn.commit()
        conn.close()
        return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return RedirectResponse(url="/viagens", status_code=303)

@router.get("/{viagem_id}/cidades/{cidade_id}")
def read_cidade_detalhe(request: Request, viagem_id: int, cidade_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    cidade_encontrada = None
    viagem_encontrada = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, imagem_capa FROM viagens WHERE id = %s AND circulo_id = %s",
                       (viagem_id, circulo_ativo['id']))
        dados_viagem = cursor.fetchone()

        if dados_viagem:
            viagem_encontrada = {"id": dados_viagem[0], "nome": dados_viagem[1], "caminho_imagem": dados_viagem[2]}

            cursor.execute("SELECT * FROM cidades_x_viagem WHERE id = %s AND viagem_id = %s", (cidade_id, viagem_id))
            dados_cidade = cursor.fetchone()

            if dados_cidade:
                cursor.execute("SELECT * FROM fotos_cidade WHERE cidade_id = %s ORDER BY data_upload DESC",
                               (cidade_id,))
                dados_fotos = cursor.fetchall()
                for foto in dados_fotos:
                    lista_fotos.append({
                        "id": foto[0], "cidade_id": foto[1], "caminho_foto": foto[2], "data_upload": foto[3]
                    })

                cidade_encontrada = {
                    "id": dados_cidade[0],
                    "viagem_id": viagem_id,
                    "nome_cidade": dados_cidade[2],
                    "visitada": dados_cidade[3],
                    "nota": dados_cidade[4],
                    "comentario": dados_cidade[5],
                }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao ler cidade: {e}")

    if not cidade_encontrada or not viagem_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Cidade"},
                                          status_code=404)

    return templates.TemplateResponse(
        "viagens/cidade_detalhes.html",
        {"request": request, "cidade": cidade_encontrada, "viagem": viagem_encontrada, "fotos": lista_fotos,
         "circulo_ativo": circulo_ativo, "user": user}
    )


@router.post("/{viagem_id}/cidades/{cidade_id}/marcar-visitada")
def marcar_cidade_visitada(request: Request, viagem_id: int, cidade_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE cidades_x_viagem SET visitada = true, nota = %s WHERE id = %s", (nota, cidade_id))
        conn.commit()

        ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao marcar cidade como visitada: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)


@router.get("/{viagem_id}/cidades/{cidade_id}/desmarcar-visitada")
def desmarcar_visitada_cidade(viagem_id: int, cidade_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE cidades_x_viagem SET visitada = false, nota = null WHERE id = %s", (cidade_id,))
        conn.commit()

        ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao desmarcar cidade: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)


@router.post("/{viagem_id}/cidades/alterar-nota/{cidade_id}")
def alterar_nota_cidade(request: Request, viagem_id: int, cidade_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE cidades_x_viagem SET nota = %s WHERE id = %s", (nota, cidade_id))
        conn.commit()

        ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao alterar nota cidade: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)


@router.post("/{viagem_id}/cidades/update-comentario/{cidade_id}")
def update_comentario_cidade(viagem_id: int, cidade_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE cidades_x_viagem SET comentario = %s WHERE id = %s", (comentario, cidade_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)

@router.post("/{viagem_id}/cidades/{cidade_id}/adicionar-foto")
def adicionar_foto_cidade(viagem_id: int, cidade_id: int, arquivo: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_cidades")
        url_foto = result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_cidade (cidade_id, caminho_foto) VALUES (%s, %s)", (cidade_id, url_foto))
        cursor.execute("INSERT INTO fotos_viagem (viagem_id, caminho_foto) VALUES (%s, %s)", (viagem_id, url_foto))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto cidade: {e}")
    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)


@router.post("/cidades/fotos/remover/{foto_id}")
def remover_foto_cidade(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, cidade_id FROM fotos_cidade WHERE id = %s", (foto_id,))
        row = cursor.fetchone()
        if row:
            url_foto, cidade_id = row[0], row[1]
            deletar_da_nuvem(url_foto)
            cursor.execute("DELETE FROM fotos_cidade WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_viagem WHERE caminho_foto = %s", (url_foto,))
            conn.commit()

            cursor.execute("SELECT viagem_id FROM cidades_x_viagem WHERE id = %s", (cidade_id,))
            viagem_id = cursor.fetchone()[0]
            conn.close()
            return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return RedirectResponse(url="/viagens", status_code=303)

@router.get("/{viagem_id}")
def read_viagem_detalhe(request: Request, viagem_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    viagem_encontrada = None
    lista_fotos = []
    lista_cidades = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM viagens WHERE id = %s AND circulo_id = %s", (viagem_id, circulo_ativo['id']))
        dados_viagem = cursor.fetchone()

        if dados_viagem:
            cursor.execute("SELECT * FROM cidades_x_viagem WHERE viagem_id = %s ORDER BY nome_cidade", (viagem_id,))
            dados_cidades = cursor.fetchall()

            cursor.execute("SELECT * FROM fotos_viagem where viagem_id = %s ORDER BY data_upload DESC", (viagem_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
                lista_fotos.append({
                    "id": foto[0],
                    "viagem_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3],
                })

            for cidade in dados_cidades:
                lista_cidades.append({
                    "id": cidade[0],
                    "viagem_id": cidade[1],
                    "nome_cidade": cidade[2],
                    "visitada": cidade[3],
                    "nota": cidade[4],
                    "comentario": cidade[5],
                })

            viagem_encontrada = {
                "id": dados_viagem[0],
                "circulo_id": dados_viagem[1],
                "nome": dados_viagem[2],
                "nota": dados_viagem[3],
                "feita": dados_viagem[4],
                "caminho_imagem": dados_viagem[5],
                "comentarios": dados_viagem[6],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao buscar detalhes da viagem: {e}")

    if not viagem_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Viagem"}, status_code=404)

    return templates.TemplateResponse(
        "viagens/viagem_detalhes.html",
        {"request": request, "viagem": viagem_encontrada, "fotos": lista_fotos, "dados_cidades": lista_cidades, "circulo_ativo": circulo_ativo, "user": user},
    )