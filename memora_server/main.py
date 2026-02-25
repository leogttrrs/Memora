from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from core.database import get_connection
import random
import os

from web.routers import filmes, series, jogos, receitas, viagens, auth, circulos

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="uma-chave-muito-secreta-memora-2026")

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(auth.router)
app.include_router(circulos.router)
app.include_router(filmes.router)
app.include_router(series.router)
app.include_router(jogos.router)
app.include_router(receitas.router)
app.include_router(viagens.router)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user = request.session.get('user')
    lista_circulos = []
    lista_convites = []

    if user:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, c.nome, mc.papel, c.emoji 
                FROM circulos c
                JOIN membros_circulo mc ON c.id = mc.circulo_id
                WHERE mc.usuario_id = %s
                ORDER BY 
                    CASE WHEN mc.papel = 'admin' THEN 1 ELSE 2 END ASC, 
                    c.data_criacao ASC
            """, (user['id'],))
            for row in cursor.fetchall():
                lista_circulos.append({"id": row[0], "nome": row[1], "papel": row[2], "emoji": row[3] or '🪐'})

            cursor.execute("""
                SELECT conv.id, circ.nome, circ.emoji 
                FROM convites conv
                JOIN circulos circ ON conv.circulo_id = circ.id
                WHERE conv.email_convidado = %s
            """, (user['email'],))
            for row in cursor.fetchall():
                lista_convites.append({"id": row[0], "nome_circulo": row[1], "emoji": row[2]})

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao buscar dados do lobby: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "circulos": lista_circulos,
        "convites": lista_convites
    })


@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(request: Request):
    user = request.session.get('user')
    circulo_ativo = request.session.get('circulo_ativo')

    if not user or not circulo_ativo:
        return RedirectResponse(url="/")

    fotos_background = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            -- 1. FILMES (Capa e Galeria)
            SELECT imagem_capa FROM filmes WHERE circulo_id = %s AND imagem_capa IS NOT NULL
            UNION
            SELECT caminho_foto FROM fotos_filme ff JOIN filmes f ON f.id = ff.filme_id WHERE f.circulo_id = %s
            UNION

            -- 2. SÉRIES (Capa, Galeria Série e Galeria Temporada)
            SELECT imagem_capa FROM series WHERE circulo_id = %s AND imagem_capa IS NOT NULL
            UNION
            SELECT fs.caminho_foto FROM fotos_serie fs JOIN series s ON s.id = fs.serie_id WHERE s.circulo_id = %s
            UNION
            SELECT ft.caminho_foto FROM fotos_temporada ft 
                JOIN temporadas t ON t.id = ft.temporada_id 
                JOIN series s ON s.id = t.serie_id WHERE s.circulo_id = %s
            UNION

            -- 3. JOGOS (Capa e Galeria)
            SELECT imagem_capa FROM jogos WHERE circulo_id = %s AND imagem_capa IS NOT NULL
            UNION
            SELECT caminho_foto FROM fotos_jogo fj JOIN jogos j ON j.id = fj.jogo_id WHERE j.circulo_id = %s
            UNION

            -- 4. RECEITAS (Capa e Galeria)
            SELECT imagem_capa FROM receitas WHERE circulo_id = %s AND imagem_capa IS NOT NULL
            UNION
            SELECT caminho_foto FROM fotos_receita fr JOIN receitas r ON r.id = fr.receita_id WHERE r.circulo_id = %s
            UNION

            -- 5. VIAGENS (Capa, Galeria Viagem e Galeria Cidade)
            SELECT imagem_capa FROM viagens WHERE circulo_id = %s AND imagem_capa IS NOT NULL
            UNION
            SELECT fv.caminho_foto FROM fotos_viagem fv JOIN viagens v ON v.id = fv.viagem_id WHERE v.circulo_id = %s
            UNION
            SELECT fc.caminho_foto FROM fotos_cidade fc 
                JOIN cidades_x_viagem cv ON cv.id = fc.cidade_id 
                JOIN viagens v ON v.id = cv.viagem_id WHERE v.circulo_id = %s
        """

        cursor.execute(query, (circulo_ativo['id'],) * 12)
        rows = cursor.fetchall()

        for r in rows:
            url = r[0]
            imagens_para_ignorar = ['default_cover.png', 'default_city.png', 'default_cover_k7dlns.jpg']
            if any(padrao in url for padrao in imagens_para_ignorar):
                continue

            if not url.startswith('http'):
                url = f"/static/{url}"
            fotos_background.append(url)

        random.shuffle(fotos_background)
        conn.close()
    except Exception as e:
        print(f"Erro ao buscar fotos do dashboard: {e}")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "circulo_ativo": circulo_ativo,
        "fotos": fotos_background,
    })