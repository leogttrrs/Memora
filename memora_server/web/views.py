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
            "filmes/filme_nao_encontrado.html",
            {"request": request},
            status_code=404
        )

    return templates.TemplateResponse(
        "filmes/filme_detalhes.html",
        {"request": request,"filme": filme_encontrado, "fotos": lista_fotos}
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
            "jogos/jogo_nao_encontrado.html",
            {"request": request},
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
def adicionar_foto(serie_id: int, arquivo: UploadFile = File(...)):
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
            "filmes/filme_nao_encontrado.html",
            {"request": request},
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
            "filmes/filme_nao_encontrado.html",
            {"request": request},
            status_code=404
        )

    return templates.TemplateResponse(
        "series/serie_detalhes.html",
        {"request": request, "serie": serie_encontrada, "fotos": lista_fotos, "dados_temporadas": lista_temporadas},
    )

@router.post("/series/remove-serie/{serie_id}")
def remove_filme(request: Request, serie_id: int):
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



@router.get("/receitas", response_class=HTMLResponse)
def read_receitas():
    try:
        with open(RECEITAS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>receitas.html não encontrado!</h1>"

@router.get("/viagens", response_class=HTMLResponse)
def read_viagens():
    try:
        with open(VIAGENS_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>viagens.html não encontrado!</h1>"

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