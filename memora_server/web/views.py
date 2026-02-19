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
FILMES_PATH = os.path.join(CURRENT_DIR, "filmes/filmes.html")
SERIES_PATH = os.path.join(CURRENT_DIR, "series/series.html")
JOGOS_PATH = os.path.join(CURRENT_DIR, "jogos/jogos.html")
RECEITAS_PATH = os.path.join(CURRENT_DIR, "receitas/receitas.html")
VIAGENS_PATH = os.path.join(CURRENT_DIR, "viagens/viagens.html")

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

    return templates.TemplateResponse("filmes/filmes.html", {
        "request": request,
        "filmes_planejados": filmes_planejados,
        "filmes_assistidos": filmes_assistidos
    })

@router.get("/receitas")
def read_receitas(request: Request):
    receitas_planejadas = []
    receitas_provadas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, nota FROM receitas ORDER BY id DESC")
        receitas_dados = cursor.fetchall()

        for item in receitas_dados:
            id_item = item[0]
            nome_item = item[1]
            nota = item[2]

            if nota is None:
                receitas_planejadas.append({"id": id_item, "nome": nome_item})
            else:
                receitas_provadas.append({"id": id_item, "nome": nome_item, "nota": nota})

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")

    return templates.TemplateResponse("receitas/receitas.html", {
        "request": request,
        "receitas_planejadas": receitas_planejadas,
        "receitas_provadas": receitas_provadas
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

@router.post("/jogos/novo")
def create_jogo(request: Request, nome_jogo: str = Form(...), imagem: UploadFile = File(None)):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:

            if imagem.content_type not in TIPOS_VALIDOS:
                print(f"Arquivo rejeitado: {imagem.content_type}")
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

        cursor.execute("INSERT INTO jogos (nome, imagem_capa) VALUES (%s, %s)", (nome_jogo, caminho_imagem))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/jogos", status_code=303)


@router.post("/receitas/novo")
def create_receita(
        request: Request,
        nome_receita: str = Form(...),
        ingredientes: str = Form(None),
        modo_preparo: str = Form(None),
        imagem: UploadFile = File(None)
):
    try:
        caminho_imagem = None
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                print(f"Arquivo rejeitado: {imagem.content_type}")
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
            INSERT INTO receitas (nome, ingredientes, modo_preparo, imagem_capa) 
            VALUES (%s, %s, %s, %s)
            """,
            (nome_receita, ingredientes, modo_preparo, caminho_imagem)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    # Redireciona para a página certa (estava indo para /jogos antes)
    return RedirectResponse(url="/receitas", status_code=303)


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

@router.post("/jogos/{jogo_id}/update-capa")
def update_jogo_capa(
        jogo_id: int,
        imagem: UploadFile = File(...)
):
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

@router.post("/series/{serie_id}/update-capa")
def update_serie_capa(
        serie_id: int,
        imagem: UploadFile = File(...)
):
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

            cursor.execute(
                "UPDATE series SET imagem_capa = %s WHERE id = %s",
                (caminho_imagem, serie_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/receitas/{receita_id}/update-capa")
def update_receita_capa(
        receita_id: int,
        imagem: UploadFile = File(...)
):
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

            cursor.execute(
                "UPDATE receitas SET imagem_capa = %s WHERE id = %s",
                (caminho_imagem, receita_id)
            )

            conn.commit()
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"Erro ao atualizar capa: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/filmes/update-comentario/{filme_id}")
def update_comentario_filme(filme_id:int, comentario: str = Form(default="")):
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

@router.post("/jogos/update-comentario/{jogo_id}")
def update_comentario_jogo(jogo_id:int, comentario: str = Form(default="")):
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

@router.post("/series/{serie_id}/temporadas/update-comentario/{temporada_id}")
def update_comentario_temporada(serie_id: int,temporada_id:int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE temporadas SET comentario = %s WHERE id = %s",
            (comentario, temporada_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.post("/series/update-comentario/{serie_id}")
def update_comentario_filme(serie_id:int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE series SET comentario = %s WHERE id = %s",
            (comentario, serie_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/receitas/update-comentario/{receita_id}")
def update_comentario_receitas(receita_id:int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE receitas SET comentario = %s WHERE id = %s",
            (comentario, receita_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/receitas/update-ingredientes/{receita_id}")
def update_ingredientes_receitas(receita_id:int, ingredientes: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE receitas SET ingredientes = %s WHERE id = %s",
            (ingredientes, receita_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar ingredientes: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/receitas/update-modo-preparo/{receita_id}")
def update_modo_preparo_receitas(receita_id:int, modo_preparo: str = Form(default="")):
    try:
        print(modo_preparo)
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE receitas SET modo_preparo = %s WHERE id = %s",
            (modo_preparo, receita_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar modo_preparo: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.get("/filmes/desmarcar-assistido/{filme_id}")
def desmarcar_assistido(filme_id:int):
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

@router.get("/receitas/desmarcar-provada/{receita_id}")
def desmarcar_provada(receita_id:int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE receitas SET provada = false, nota = null WHERE id = %s",
            (receita_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar provada: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.get("/jogos/desmarcar-finalizado/{jogo_id}")
def desmarcar_finalizado(jogo_id:int):
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

@router.get("/series/{serie_id}/temporadas/{temporada_id}/desmarcar-assistido")
def desmarcar_assistido_temporada(temporada_id:int, serie_id:int):
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
        print(f"Erro ao atualizar assistido: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.get("/filmes/{filme_id}")
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
        print(f"Erro ao salvar: {e}")

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

@router.get("/receitas/{receita_id}")
def read_receita_detalhe(request: Request, receita_id: int):
    receita_encontrada = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM receitas WHERE id = %s", (receita_id,))
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
                "nome": dados_receita[1],
                "nota": dados_receita[2],
                "provada": dados_receita[3],
                "caminho_imagem": dados_receita[4],
                "ingredientes": dados_receita[5],
                "modo_preparo": dados_receita[6],
                "comentario": dados_receita[7],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    if not receita_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Receita"},
            status_code=404
        )

    return templates.TemplateResponse(
        "receitas/receita_detalhes.html",
        {"request": request,"receita": receita_encontrada, "fotos": lista_fotos}
    )

@router.get("/jogos/{jogo_id}")
def read_jogo_detalhe(request: Request, jogo_id: int):
    jogo_encontrado = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jogos WHERE id = %s", (jogo_id,))
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
                "nome": dados_jogo[1],
                "nota": dados_jogo[2],
                "finalizado": dados_jogo[3],
                "caminho_imagem": dados_jogo[4],
                "comentarios": dados_jogo[5],
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    if not jogo_encontrado:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Jogo"},
            status_code=404
        )

    return templates.TemplateResponse(
        "jogos/jogo_detalhes.html",
        {"request": request,"jogo": jogo_encontrado, "fotos": lista_fotos}
    )

@router.post("/filmes/remove-filme/{filme_id}")
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

@router.post("/jogos/remove-jogo/{jogo_id}")
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

@router.post("/receitas/marcar-provada/{receita_id}")
def mark_as_watched_receita(request: Request, receita_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE receitas SET provada = true, nota = %s WHERE id = %s",
            (nota, receita_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/jogos/marcar-finalizado/{jogo_id}")
def marcar_finalizado_jogo(request: Request, jogo_id, nota: int = Form(...)):
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

@router.post("/series/{serie_id}/temporadas/{temporada_id}/marcar-assistido")
def mark_as_watched_temporada(request: Request,serie_id ,temporada_id, nota: int = Form(...)):
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
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.post("/filmes/alterar-nota/{filme_id}")
def alterar_nota_filme(request: Request, filme_id, nota: int = Form(...)):
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

@router.post("/receitas/alterar-nota/{receita_id}")
def alterar_nota_receita(request: Request, receita_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE receitas SET nota = %s where id = %s", (nota, receita_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/jogos/alterar-nota/{jogo_id}")
def alterar_nota_jogo(request: Request, jogo_id, nota: int = Form(...)):
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

@router.post("/series/{serie_id}/temporadas/alterar-nota/{temporada_id}")
def alterar_nota_temporada(request: Request,serie_id ,temporada_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE temporadas SET nota = %s where id = %s", (nota, temporada_id)
        )
        conn.commit()

        ler_temporadas_e_definir_nota_serie(conn, cursor, serie_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.post("/series/alterar-nota/{serie_id}")
def alterar_nota_filme(request: Request, serie_id, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE series SET nota_geral = %s where id = %s", (nota, serie_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)


@router.post("/filmes/{filme_id}/adicionar-foto")
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

@router.post("/jogos/{jogo_id}/adicionar-foto")
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

@router.post("/series/{serie_id}/temporadas/{temporada_id}/adicionar-foto")
def adicionar_foto_temporada(serie_id: int,temporada_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/temporadas/{temporada_id}?erro=arquivo_invalido", status_code=303)

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
            "INSERT INTO fotos_temporada (temporada_id, caminho_foto) VALUES (%s, %s)",
            (temporada_id, caminho_relativo)
        )
        cursor.execute(
            "INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)",
            (serie_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/series/{serie_id}/temporada/{temporada_id}", status_code=303)

@router.post("/series/{serie_id}/adicionar-foto")
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
        cursor.execute(
            "INSERT INTO fotos_serie (serie_id, caminho_foto) VALUES (%s, %s)",
            (serie_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.post("/receitas/{receita_id}/adicionar-foto")
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
        cursor.execute(
            "INSERT INTO fotos_receita (receita_id, caminho_foto) VALUES (%s, %s)",
            (receita_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

@router.post("/viagens/{viagem_id}/adicionar-foto")
def adicionar_foto_viagem(viagem_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/viagens/{viagem_id}?erro=arquivo_invalido", status_code=303)

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
            "INSERT INTO fotos_viagem (viagem_id, caminho_foto) VALUES (%s, %s)",
            (viagem_id, caminho_relativo)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)


@router.post("/filmes/fotos/remover/{foto_id}")
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
        return RedirectResponse(url="/series", status_code=303)

@router.post("/receitas/fotos/remover/{foto_id}")
def remover_foto_receita(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, receita_id FROM fotos_receita WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_arquivo = Path("static") / row[0]
            receita_id = row[1]

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_receita WHERE id = %s", (foto_id,))
            conn.commit()

            conn.close()
            return RedirectResponse(url=f"/receitas/{receita_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/series", status_code=303)

@router.post("/jogos/fotos/remover/{foto_id}")
def remover_foto_jogo(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, jogo_id FROM fotos_jogo WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_arquivo = Path("static") / row[0]
            jogo_id = row[1]

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            cursor.execute("DELETE FROM fotos_jogo WHERE id = %s", (foto_id,))
            conn.commit()

            conn.close()
            return RedirectResponse(url=f"/jogos/{jogo_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/series", status_code=303)


@router.post("/temporadas/fotos/remover/{foto_id}")
def remover_foto_temporada(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Descobrir o caminho e o ID da temporada
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
            conn.close()

            return RedirectResponse(url="/series", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/series", status_code=303)


@router.post("/series/fotos/remover/{foto_id}")
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
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/series", status_code=303)

@router.get("/series")
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
        print(f"Erro ao salvar: {e}")

    return templates.TemplateResponse("series/series.html", {
        "request": request,
        "series_planejadas": series_planejadas,
        "series_assistidas": series_assistidas,
    })

@router.post("/series/novo")
def criar_serie(request: Request, nome_serie: str = Form(...), qtd_temporadas: int = Form(...), imagem: UploadFile = File(None)):
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

@router.get("/series/{serie_id}/temporada/{temporada_id}")
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
            cursor.execute("SELECT * FROM fotos_temporada where temporada_id = %s ORDER BY data_upload DESC", (temporada_id,))
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

    except Exception as e:
        print(f"Erro ao ler temporada: {e}")

    if not temporada_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Temporada"},
            status_code=404
        )

    return templates.TemplateResponse(
        "series/temporada_detalhes.html",
        {"request": request, "temporada": temporada_encontrada, "serie": serie_encontrada,"fotos": lista_fotos}
    )



@router.post("/series/temporada/{temporada_id}/marcar-assistido")
def marcar_temporada(temporada_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE temporadas SET assistido = true, nota = %s WHERE id = %s RETURNING serie_id",
            (nota, temporada_id)
        )
        serie_id = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM temporadas WHERE serie_id = %s AND assistido = false",
            (serie_id,)
        )
        restantes = cursor.fetchone()[0]

        if restantes == 0:
            cursor.execute("UPDATE series SET assistido_completo = true WHERE id = %s", (serie_id,))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao atualizar temporada: {e}")

    return RedirectResponse(url=f"/series/{serie_id}", status_code=303)

@router.get("/series/{serie_id}")
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
        print(f"Erro ao salvar: {e}")

    if not serie_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Série"},
            status_code=404
        )

    return templates.TemplateResponse(
        "series/serie_detalhes.html",
        {"request": request, "serie": serie_encontrada, "fotos": lista_fotos, "dados_temporadas": lista_temporadas},
    )

@router.post("/series/remove-serie/{serie_id}")
def remove_serie(request: Request, serie_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM series WHERE ID = %s", (serie_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    return RedirectResponse(url="/series", status_code=303)

@router.post("/receitas/remove-receita/{receita_id}")
def remove_filme(request: Request, receita_id: int):
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

@router.get("/jogos", response_class=HTMLResponse)
def read_jogoss(request: Request):
    jogos_planejados = []
    jogos_finalizados = []

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, nota FROM jogos ORDER BY id DESC")
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
        "jogos_finalizados": jogos_finalizados
    })

@router.get("/viagens")
def read_viagens(request: Request):
    viagens_planejadas = []
    viagens_feitas = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM viagens ORDER BY id DESC")
        viagens_dados = cursor.fetchall()

        for item in viagens_dados:
            viagem_id = item[0]
            viagem_nome = item[1]
            nota = item[2]
            feita = item[3]

            cursor.execute("SELECT visitada FROM cidades_x_viagem WHERE viagem_id = %s", (viagem_id,))
            cidades_results = cursor.fetchall()

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
        print(f"Erro ao salvar: {e}")

    return templates.TemplateResponse("viagens/viagens.html", {
        "request": request,
        "viagens_planejadas": viagens_planejadas,
        "viagens_feitas": viagens_feitas,
    })

@router.get("/viagens/{viagem_id}")
def read_viagem_detalhe(request: Request, viagem_id: int):
    viagem_encontrada = None
    lista_fotos = []
    lista_cidades = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM viagens WHERE id = %s", (viagem_id,))
        dados_viagem = cursor.fetchone()

        print(dados_viagem)

        cursor.execute("SELECT * FROM cidades_x_viagem WHERE viagem_id = %s ORDER BY nome_cidade", (viagem_id,))
        dados_cidades = cursor.fetchall()

        if dados_viagem:
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
                "nome": dados_viagem[1],
                "nota": dados_viagem[2],
                "feita": dados_viagem[3],
                "caminho_imagem": dados_viagem[4],
                "comentarios": dados_viagem[5],
            }

        print(viagem_encontrada["caminho_imagem"])

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar: {e}")

    if not viagem_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Viagem"},
            status_code=404
        )

    return templates.TemplateResponse(
        "viagens/viagem_detalhes.html",
        {"request": request, "viagem": viagem_encontrada, "fotos": lista_fotos, "dados_cidades": lista_cidades},
    )


@router.post("/viagens/novo")
def create_viagem(
        request: Request,
        nome_viagem: str = Form(...),
        cidades: list[str] = Form(...),
        imagem: UploadFile = File(None)
):
    try:
        # 1. IMPORTANTE: Inicializar a variável antes de tudo!
        caminho_imagem = None

        # 2. Lógica para salvar a imagem no disco (se ela existir)
        TIPOS_VALIDOS = ["image/jpeg", "image/png", "image/webp", "image/jpg"]

        if imagem and imagem.filename:
            if imagem.content_type not in TIPOS_VALIDOS:
                print(f"Arquivo rejeitado: {imagem.content_type}")
                # Aqui você pode decidir se para tudo ou se continua sem imagem
            else:
                extensao = imagem.filename.split(".")[-1]
                nome_arquivo = f"{uuid.uuid4()}.{extensao}"

                pasta_destino = Path("static/uploads")
                pasta_destino.mkdir(parents=True, exist_ok=True)
                caminho_final = pasta_destino / nome_arquivo

                with open(caminho_final, "wb") as buffer:
                    shutil.copyfileobj(imagem.file, buffer)

                # Atualiza a variável com o caminho certo
                caminho_imagem = f"uploads/{nome_arquivo}"

        # 3. Lógica do Banco de Dados
        conn = get_connection()
        cursor = conn.cursor()

        # Cria a Viagem Principal (Agora 'caminho_imagem' existe, seja None ou o link do arquivo)
        cursor.execute(
            "INSERT INTO viagens (nome, imagem_capa) VALUES (%s, %s) RETURNING id",
            (nome_viagem, caminho_imagem)
        )
        viagem_id = cursor.fetchone()[0]

        # Cria as Cidades com base nos nomes da lista
        for nome_cidade in cidades:
            # Remove espaços em branco extras se houver (Ex: " Paris " vira "Paris")
            nome_limpo = nome_cidade.strip()

            if nome_limpo:  # Só salva se não estiver vazio
                cursor.execute(
                    """
                    INSERT INTO cidades_x_viagem (viagem_id, nome_cidade, caminho_foto, nota) 
                    VALUES (%s, %s, 'default_city.png', 0)
                    """,
                    (viagem_id, nome_limpo)
                )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao criar viagem: {e}")

    return RedirectResponse(url="/viagens", status_code=303)

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

    nota_geral_serie = round(nota_total / num_temporadas_contabilizadas)
    serie_assistida = num_temporadas_total == num_temporadas_contabilizadas
    print(f'Série assistida: {serie_assistida}')

    cursor.execute(
        "UPDATE series SET nota_geral = %s, assistido_completo = %s WHERE id = %s",
        (nota_geral_serie, serie_assistida, serie_id)
    )


    conn.commit()


def ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id):
    cursor.execute("SELECT visitada, nota FROM cidades_x_viagem WHERE viagem_id = %s", (viagem_id,))
    dados_cidades = cursor.fetchall()

    num_cidades_total = len(dados_cidades)
    num_cidades_visitadas = 0
    nota_total = 0

    for cidade in dados_cidades:
        if cidade[0]:  # Se visitada == True
            num_cidades_visitadas += 1
            if cidade[1]:  # Se tem nota
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


@router.get("/viagens/{viagem_id}/cidades/{cidade_id}")
def read_cidade_detalhe(request: Request, viagem_id: int, cidade_id: int):
    cidade_encontrada = None
    viagem_encontrada = None
    lista_fotos = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Busca a Viagem (para a capa de fundo e o título)
        cursor.execute("SELECT id, nome, imagem_capa FROM viagens WHERE id = %s", (viagem_id,))
        dados_viagem = cursor.fetchone()
        if dados_viagem:
            viagem_encontrada = {"id": dados_viagem[0], "nome": dados_viagem[1], "caminho_imagem": dados_viagem[2]}

        # Busca a Cidade Específica
        cursor.execute("SELECT * FROM cidades_x_viagem WHERE id = %s", (cidade_id,))
        dados_cidade = cursor.fetchone()

        if dados_cidade:
            # Busca as Fotos dessa cidade
            cursor.execute("SELECT * FROM fotos_cidade WHERE cidade_id = %s ORDER BY data_upload DESC", (cidade_id,))
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
                "comentario": dados_cidade[5],  # Usando índice 5 que é o comanterio no DB
            }

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Erro ao ler cidade: {e}")

    if not cidade_encontrada:
        return templates.TemplateResponse(
            "item_nao_encontrado.html",
            {"request": request, "item": "Cidade"},
            status_code=404
        )

    return templates.TemplateResponse(
        "viagens/cidade_detalhes.html",
        {"request": request, "cidade": cidade_encontrada, "viagem": viagem_encontrada, "fotos": lista_fotos}
    )


@router.post("/viagens/{viagem_id}/cidades/{cidade_id}/marcar-visitada")
def marcar_cidade_visitada(request: Request, viagem_id: int, cidade_id: int, nota: int = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE cidades_x_viagem SET visitada = true, nota = %s WHERE id = %s",
            (nota, cidade_id)
        )
        conn.commit()

        ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao marcar cidade como visitada: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)


@router.get("/viagens/{viagem_id}/cidades/{cidade_id}/desmarcar-visitada")
def desmarcar_visitada_cidade(viagem_id: int, cidade_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE cidades_x_viagem SET visitada = false, nota = null WHERE id = %s",
            (cidade_id,)
        )
        conn.commit()

        ler_cidades_e_definir_nota_viagem(conn, cursor, viagem_id)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao desmarcar cidade: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)


@router.post("/viagens/{viagem_id}/cidades/alterar-nota/{cidade_id}")
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


@router.post("/viagens/{viagem_id}/cidades/update-comentario/{cidade_id}")
def update_comentario_cidade(viagem_id: int, cidade_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Atenção ao typo no banco (comanterio)
        cursor.execute("UPDATE cidades_x_viagem SET comentario = %s WHERE id = %s", (comentario, cidade_id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)

@router.post("/viagens/update-comentario/{viagem_id}")
def update_comentario_viagem(viagem_id: int, comentario: str = Form(default="")):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE viagens SET comentario = %s WHERE id = %s",
            (comentario, viagem_id)
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao atualizar comentario da viagem: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}", status_code=303)


@router.post("/viagens/{viagem_id}/cidades/{cidade_id}/adicionar-foto")
def adicionar_foto_cidade(viagem_id: int, cidade_id: int, arquivo: UploadFile = File(...)):
    if arquivo.content_type not in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
        return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}?erro=arquivo_invalido", status_code=303)

    try:
        extensao = arquivo.filename.split(".")[-1]
        nome_novo = f"{uuid.uuid4()}.{extensao}"
        caminho_relativo = f"uploads/{nome_novo}"

        caminho_absoluto = Path("static") / caminho_relativo
        with open(caminho_absoluto, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)

        conn = get_connection()
        cursor = conn.cursor()

        # Insere na Cidade
        cursor.execute(
            "INSERT INTO fotos_cidade (cidade_id, caminho_foto) VALUES (%s, %s)",
            (cidade_id, caminho_relativo)
        )
        # Insere na Viagem (Para aparecer na galeria geral também!)
        cursor.execute(
            "INSERT INTO fotos_viagem (viagem_id, caminho_foto) VALUES (%s, %s)",
            (viagem_id, caminho_relativo)
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erro ao salvar foto: {e}")

    return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)


@router.post("/cidades/fotos/remover/{foto_id}")
def remover_foto_cidade(foto_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT caminho_foto, cidade_id FROM fotos_cidade WHERE id = %s", (foto_id,))
        row = cursor.fetchone()

        if row:
            caminho_relativo = row[0]
            cidade_id = row[1]
            caminho_arquivo = Path("static") / caminho_relativo

            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)

            # Apaga da tabela de cidades e da tabela geral de viagens (Fantasma)
            cursor.execute("DELETE FROM fotos_cidade WHERE id = %s", (foto_id,))
            cursor.execute("DELETE FROM fotos_viagem WHERE caminho_foto = %s", (caminho_relativo,))

            conn.commit()

            # Precisamos do id da viagem para redirecionar de volta.
            # Como a rota não recebe viagem_id, fazemos um JOIN rápido:
            cursor.execute("SELECT viagem_id FROM cidades_x_viagem WHERE id = %s", (cidade_id,))
            viagem_id = cursor.fetchone()[0]

            conn.close()
            return RedirectResponse(url=f"/viagens/{viagem_id}/cidades/{cidade_id}", status_code=303)

    except Exception as e:
        print(f"Erro ao deletar foto: {e}")
        return RedirectResponse(url="/viagens", status_code=303)