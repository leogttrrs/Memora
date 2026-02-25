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
    prefix="/series",
    tags=["series"]
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

def ler_temporadas_e_definir_nota_serie(conn, cursor, serie_id):
    cursor.execute(
        "SELECT * FROM temporadas WHERE serie_id = %s", (serie_id,)
    )

    dados_temporadas_serie = cursor.fetchall()
    num_temporadas_total = len(dados_temporadas_serie)
    num_temporadas_contabilizadas = 0
    nota_total = 0

    for temporada in dados_temporadas_serie:
        if temporada[3]:
            num_temporadas_contabilizadas += 1
            nota_total += temporada[3]

    nota_geral_serie = None
    if num_temporadas_contabilizadas > 0:
        nota_geral_serie = round(nota_total / num_temporadas_contabilizadas)

    serie_assistida = num_temporadas_total == num_temporadas_contabilizadas

    cursor.execute(
        "UPDATE series SET nota_geral = %s, assistido_completo = %s WHERE id = %s",
        (nota_geral_serie, serie_assistida, serie_id)
    )
    conn.commit()


@router.get("/")
def read_series(request: Request):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    series_planejadas = []
    series_assistidas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, nome, nota_geral, assistido_completo FROM series WHERE circulo_id = %s ORDER BY id DESC",
            (circulo_ativo['id'],)
        )
        series_dados = cursor.fetchall()

        for item in series_dados:
            serie_id = item[0]
            serie_nome = item[1]
            nota = item[2]
            assistida = item[3]

            cursor.execute("SELECT assistido FROM temporadas WHERE serie_id = %s", (serie_id,))
            temporadas_results = cursor.fetchall()

            total_temporadas = len(temporadas_results)
            assistidas_count = sum(1 for t in temporadas_results if t[0] is True)
            porcentagem_str = "0%"

            if total_temporadas > 0:
                calculo = int((assistidas_count / total_temporadas) * 100)
                porcentagem_str = f"{calculo}%"

            serie_obj = {
                "id": serie_id,
                "nome": serie_nome,
                "nota": nota,
                "porcentagem": porcentagem_str
            }

            if not assistida:
                series_planejadas.append(serie_obj)
            else:
                serie_obj["porcentagem"] = "100%"
                series_assistidas.append(serie_obj)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao ler séries: {e}")

    return templates.TemplateResponse("series/series.html", {
        "request": request,
        "series_planejadas": series_planejadas,
        "series_assistidas": series_assistidas,
        "circulo_ativo": circulo_ativo,
        "user": user
    })

@router.post("/novo")
def criar_serie(request: Request, nome_serie: str = Form(...), qtd_temporadas: int = Form(...),
                imagem: UploadFile = File(None)):
    circulo_ativo = request.session.get('circulo_ativo')
    if not circulo_ativo: return RedirectResponse(url="/")

    try:
        url_imagem = None
        if imagem and imagem.filename:
            result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_series")
            url_imagem = result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO series (circulo_id, nome, assistido_completo, imagem_capa) VALUES (%s, %s, false, %s) RETURNING id",
            (circulo_ativo['id'], nome_serie, url_imagem)
        )
        serie_id = cursor.fetchone()[0]

        for i in range(1, qtd_temporadas + 1):
            cursor.execute(
                "INSERT INTO temporadas (serie_id, numero_temporada, assistido) VALUES (%s, %s, false)",
                (serie_id, i)
            )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar série: {e}")

    return RedirectResponse(url="/series", status_code=303)

@router.post("/remove-serie/{serie_id}")
def remove_serie(request: Request, serie_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT imagem_capa FROM series WHERE id = %s", (serie_id,))
        capa = cursor.fetchone()
        if capa and capa[0]: deletar_da_nuvem(capa[0])

        cursor.execute("SELECT caminho_foto FROM fotos_serie WHERE serie_id = %s", (serie_id,))
        fotos = cursor.fetchall()
        for f in fotos: deletar_da_nuvem(f[0])

        cursor.execute("DELETE FROM series WHERE id = %s", (serie_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao remover série: {e}")

    return RedirectResponse(url="/series", status_code=303)

@router.post("/alterar-nota/{serie_id}")
def alterar_nota_serie(request: Request, serie_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE series SET nota_geral = %s where id = %s", (nota, serie_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao alterar nota série: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)


@router.post("/update-comentario/{serie_id}")
def update_comentario_serie(serie_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE series SET comentario = %s WHERE id = %s", (comentario, serie_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario série: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/{serie_id}/update-capa")
def update_serie_capa(serie_id: int, imagem: UploadFile = File(...)):
    try:
        if imagem and imagem.filename:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT imagem_capa FROM series WHERE id = %s", (serie_id,))
            antiga = cursor.fetchone()
            if antiga and antiga[0]: deletar_da_nuvem(antiga[0])

            result = cloudinary.uploader.upload(imagem.file, folder="memora/capas_series")
            nova_url = result.get("secure_url")

            cursor.execute("UPDATE series SET imagem_capa = %s WHERE id = %s", (nova_url, serie_id))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")
    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/{serie_id}/adicionar-foto")
def adicionar_foto_serie(serie_id: int, arquivo: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_series")
        url_foto = result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)", (serie_id, url_foto))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto série: {e}")
    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/fotos/remover/{foto_id}")
def remover_foto_serie(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_foto, serie_id FROM fotos_serie WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            url_foto, serie_id = row[0], row[1]
            deletar_da_nuvem(url_foto)

            cursor.execute("DELETE FROM fotos_serie WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_temporada WHERE caminho_foto = %s", (url_foto,))
            conn.commit()
        conn.close()
        return RedirectResponse(url=f"/series/{serie_id}", status_code=303)
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return RedirectResponse(url="/series", status_code=303)

@router.post("/{serie_id}/temporadas/{temporada_id}/marcar-assistido")
def marcar_temporada(request: Request, serie_id: int, temporada_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE temporadas SET assistido = true, nota = %s WHERE id = %s",
            (nota, temporada_id)
        )
        conn.commit()

        ler_temporadas_e_definir_nota_serie(conn, cursor, serie_id)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao marcar temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)


@router.get("/{serie_id}/temporadas/{temporada_id}/desmarcar-assistido")
def desmarcar_assistido_temporada(temporada_id: int, serie_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE temporadas SET assistido = false, nota = null WHERE id = %s",
            (temporada_id,)
        )
        conn.commit()

        ler_temporadas_e_definir_nota_serie(conn, cursor, serie_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao desmarcar temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)


@router.post("/{serie_id}/temporadas/alterar-nota/{temporada_id}")
def alterar_nota_temporada(request: Request, serie_id: int, temporada_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE temporadas SET nota = %s where id = %s", (nota, temporada_id))
        conn.commit()

        ler_temporadas_e_definir_nota_serie(conn, cursor, serie_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao alterar nota temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)


@router.post("/{serie_id}/temporadas/update-comentario/{temporada_id}")
def update_comentario_temporada(serie_id: int, temporada_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE temporadas SET comentario = %s WHERE id = %s", (comentario, temporada_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.post("/{serie_id}/temporadas/{temporada_id}/adicionar-foto")
def adicionar_foto_temporada(serie_id: int, temporada_id: int, arquivo: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(arquivo.file, folder="memora/galeria_temporadas")
        url_foto = result.get("secure_url")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_temporada (temporada_id, caminho_foto) VALUES (%s, %s)", (temporada_id, url_foto))
        cursor.execute("INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)", (serie_id, url_foto))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar foto: {e}")
    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)


@router.post("/{serie_id}/temporadas/{temporada_id}/fotos/remover/{foto_id}")
def remover_foto_temporada(serie_id: int, temporada_id: int, foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto FROM fotos_temporada WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            url_foto = row[0]

            deletar_da_nuvem(url_foto)

            cursor.execute("DELETE FROM fotos_temporada WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_serie WHERE caminho_foto = %s", (url_foto,))

            conn.commit()

        cursor.execute("SELECT serie_id FROM temporadas WHERE id = %s", (temporada_id,))
        serie_id_db = cursor.fetchone()
        final_serie_id = serie_id_db[0] if serie_id_db else serie_id

        conn.close()
        return RedirectResponse(url=f"/series/{final_serie_id}/temporada/{temporada_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto temporada: {e}")
        return RedirectResponse(url="/series", status_code=303)

@router.get("/{serie_id}/temporada/{temporada_id}")
def read_temporada(request: Request, temporada_id: int, serie_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    temporada_encontrada = None
    serie_encontrada = None
    lista_fotos = []
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM temporadas WHERE id = %s", (temporada_id,))
        dados_temporada = cursor.fetchone()

        if dados_temporada:
            cursor.execute("SELECT id, temporada_id, caminho_foto, data_upload FROM fotos_temporada where temporada_id = %s ORDER BY data_upload DESC",
                           (temporada_id,))
            for foto in cursor.fetchall():
                lista_fotos.append({
                    "id": foto[0],
                    "temporada_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3],
                })

            temporada_encontrada = {
                "id": dados_temporada[0],
                "serie_id": serie_id,
                "numero_temporada": dados_temporada[2],
                "nota": dados_temporada[3],
                "assistido": dados_temporada[4],
                "comentario": dados_temporada[5],
            }

            cursor.execute("SELECT * FROM series WHERE id = %s AND circulo_id = %s", (serie_id, circulo_ativo['id']))
            dados_serie = cursor.fetchone()

            if dados_serie:
                serie_encontrada = {
                    "id": serie_id,
                    "circulo_id": dados_serie[1],
                    "nome": dados_serie[2],
                    "nota": dados_serie[3],
                    "assistido": dados_serie[4],
                    "caminho_imagem": dados_serie[5],
                    "comentarios": dados_serie[6],
                }

        conn.close()
    except Exception as e:
        print(f"Erro ao ler temporada: {e}")

    if not temporada_encontrada or not serie_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html",
                                          {"request": request, "item": "Temporada ou Série"},
                                          status_code=404)

    return templates.TemplateResponse(
        "series/temporada_detalhes.html",
        {"request": request, "temporada": temporada_encontrada, "serie": serie_encontrada, "fotos": lista_fotos,
         "circulo_ativo": circulo_ativo, "user": user}
    )

@router.get("/{serie_id}")
def read_serie_detalhe(request: Request, serie_id: int):
    circulo_ativo = request.session.get('circulo_ativo')
    user = request.session.get('user')
    if not circulo_ativo:
        return RedirectResponse(url="/")

    serie_encontrada = None
    lista_fotos = []
    lista_temporadas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM series WHERE id = %s AND circulo_id = %s", (serie_id, circulo_ativo['id']))
        dados_serie = cursor.fetchone()

        if dados_serie:
            cursor.execute("SELECT * FROM temporadas WHERE serie_id = %s ORDER BY numero_temporada", (serie_id,))
            for temporada in cursor.fetchall():
                lista_temporadas.append({
                    "id": temporada[0],
                    "serie_id": temporada[1],
                    "numero_temporada": temporada[2],
                    "nota": temporada[3],
                    "assistido": temporada[4],
                    "comentario": temporada[5],
                })

            cursor.execute("SELECT id, serie_id, caminho_foto, data_upload FROM fotos_serie where serie_id = %s ORDER BY data_upload DESC", (serie_id,))
            for foto in cursor.fetchall():
                lista_fotos.append({
                    "id": foto[0],
                    "serie_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3],
                })

            serie_encontrada = {
                "id": dados_serie[0],
                "circulo_id": dados_serie[1],
                "nome": dados_serie[2],
                "nota": dados_serie[3],
                "assistido": dados_serie[4],
                "caminho_imagem": dados_serie[5],
                "comentarios": dados_serie[6],
            }

        conn.close()
    except Exception as e:
        print(f"Erro ao ler detalhe da série: {e}")

    if not serie_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Série"},
                                          status_code=404)

    return templates.TemplateResponse(
        "series/serie_detalhes.html",
        {"request": request, "serie": serie_encontrada, "fotos": lista_fotos, "dados_temporadas": lista_temporadas,
         "circulo_ativo": circulo_ativo, "user": user},
    )