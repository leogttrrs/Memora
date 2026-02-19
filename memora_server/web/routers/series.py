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
    prefix="/series",
    tags=["series"]
)

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
    series_planejadas = []
    series_assistidas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM series ORDER BY id DESC")
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
    })


@router.post("/novo")
def criar_serie(request: Request, nome_serie: str = Form(...), qtd_temporadas: int = Form(...),
                imagem: UploadFile = File(None)):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                print(f"Arquivo rejeitado: {imagem.content_type}")
                return RedirectResponse(url="/series", status_code=303)

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
            "INSERT INTO series (nome, assistido_completo, imagem_capa) VALUES (%s, false, %s) RETURNING id",
            (nome_serie, caminho_imagem)
        )
        serie_id = cursor.fetchone()[0]

        for i in range(1, qtd_temporadas + 1):
            cursor.execute(
                """
                    INSERT INTO temporadas (serie_id, numero_temporada, assistido) 
                    VALUES (%s, %s, false)
                """,
                (serie_id, i)
            )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar série: {e}")

    return RedirectResponse(url="/series", status_code=303)


@router.post("/remove-serie/{serie_id}")
def remove_serie(request: Request, serie_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM series WHERE ID = %s", (serie_id,))
        conn.commit()
        cursor.close()
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
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                return RedirectResponse(url="/series?erro=tipo_invalido", status_code=303)

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

            cursor.execute("UPDATE series SET imagem_capa = %s WHERE id = %s", (caminho_imagem, serie_id))
            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa série: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)


@router.post("/{serie_id}/adicionar-foto")
def adicionar_foto_serie(serie_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/series/{serie_id}?erro=arquivo_invalido", status_code=303)

    try:
        extensao = arquivo.filename.split(".")[-1]
        nome_novo = f"{uuid.uuid4()}.{extensao}"
        caminho_relativo = f"uploads/{nome_novo}"

        caminho_absoluto = Path("static") / caminho_relativo
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)", (serie_id, caminho_relativo))
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
            caminho_relativo = row[0]
            serie_id = row[1]
            caminho_arquivo = Path("static") / caminho_relativo

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_serie WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_temporada WHERE caminho_foto = %s", (caminho_relativo,))
            conn.commit()
            conn.close()

            return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto série: {e}")
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
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}?erro=arquivo_invalido",
                                status_code=303)

    try:
        extensao = arquivo.filename.split(".")[-1]
        nome_novo = f"{uuid.uuid4()}.{extensao}"
        caminho_relativo = f"uploads/{nome_novo}"

        caminho_absoluto = Path("static") / caminho_relativo
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO fotos_temporada (temporada_id, caminho_foto) VALUES (%s, %s)",
                       (temporada_id, caminho_relativo))
        cursor.execute("INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)", (serie_id, caminho_relativo))
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)


@router.post("/temporadas/fotos/remover/{foto_id}")
def remover_foto_temporada(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, temporada_id FROM fotos_temporada WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_relativo = row[0]
            temporada_id = row[1]
            caminho_arquivo = Path("static") / caminho_relativo

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_temporada WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_serie WHERE caminho_foto = %s", (caminho_relativo,))
            conn.commit()

            cursor.execute("SELECT serie_id FROM temporadas WHERE id = %s", (temporada_id,))
            serie_id = cursor.fetchone()[0]

            conn.close()
            return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto temporada: {e}")
        return RedirectResponse(url="/series", status_code=303)

@router.get("/{serie_id}/temporada/{temporada_id}")
def read_temporada(request: Request, temporada_id: int, serie_id: int):
    temporada_encontrada = None
    serie_encontrada = None
    lista_fotos = []
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM temporadas WHERE id = %s", (temporada_id,))
        dados_temporada = cursor.fetchone()

        if dados_temporada:
            cursor.execute("SELECT * FROM fotos_temporada where temporada_id = %s ORDER BY data_upload DESC",
                           (temporada_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
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

            cursor.execute("SELECT * FROM series WHERE id = %s", (serie_id,))
            dados_serie = cursor.fetchone()

            serie_encontrada = {
                "id": serie_id,
                "nome": dados_serie[1],
                "nota": dados_serie[2],
                "assistido": dados_serie[3],
                "caminho_imagem": dados_serie[4],
                "comentarios": dados_serie[5],
            }

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao ler temporada: {e}")

    if not temporada_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Temporada"},
                                          status_code=404)

    return templates.TemplateResponse(
        "series/temporada_detalhes.html",
        {"request": request, "temporada": temporada_encontrada, "serie": serie_encontrada, "fotos": lista_fotos}
    )


@router.get("/{serie_id}")
def read_serie_detalhe(request: Request, serie_id: int):
    serie_encontrada = None
    lista_fotos = []
    lista_temporadas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM series WHERE id = %s", (serie_id,))
        dados_serie = cursor.fetchone()

        cursor.execute("SELECT * FROM temporadas WHERE serie_id = %s ORDER BY numero_temporada", (serie_id,))
        dados_temporadas = cursor.fetchall()

        if dados_serie:
            cursor.execute("SELECT * FROM fotos_serie where serie_id = %s ORDER BY data_upload DESC", (serie_id,))
            dados_fotos = cursor.fetchall()

            for foto in dados_fotos:
                lista_fotos.append({
                    "id": foto[0],
                    "serie_id": foto[1],
                    "caminho_foto": foto[2],
                    "data_upload": foto[3],
                })

            for temporada in dados_temporadas:
                lista_temporadas.append({
                    "id": temporada[0],
                    "serie_id": temporada[1],
                    "numero_temporada": temporada[2],
                    "nota": temporada[3],
                    "assistido": temporada[4],
                    "comentario": temporada[5],
                })

            serie_encontrada = {
                "id": dados_serie[0],
                "nome": dados_serie[1],
                "nota": dados_serie[2],
                "assistido": dados_serie[3],
                "caminho_imagem": dados_serie[4],
                "comentarios": dados_serie[5],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao ler detalhe da série: {e}")

    if not serie_encontrada:
        return templates.TemplateResponse("item_nao_encontrado.html", {"request": request, "item": "Série"},
                                          status_code=404)

    return templates.TemplateResponse(
        "series/serie_detalhes.html",
        {"request": request, "serie": serie_encontrada, "fotos": lista_fotos, "dados_temporadas": lista_temporadas},
    )