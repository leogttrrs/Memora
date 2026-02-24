import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from core.database import get_connection

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

router = APIRouter(tags=["auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, str(redirect_uri), prompt='select_account')


@router.get("/auth/callback", name="auth_callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        email = user_info.get('email')
        nome = user_info.get('name')
        foto_url = user_info.get('picture')

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario:
            usuario_id = usuario[0]
        else:
            cursor.execute(
                "INSERT INTO usuarios (email, nome, foto_url) VALUES (%s, %s, %s) RETURNING id",
                (email, nome, foto_url)
            )
            usuario_id = cursor.fetchone()[0]

            nome_circulo = f"Círculo de {nome.split(' ')[0]}"
            cursor.execute(
                "INSERT INTO circulos (nome, criador_id) VALUES (%s, %s) RETURNING id",
                (nome_circulo, usuario_id)
            )
            circulo_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO membros_circulo (circulo_id, usuario_id, papel) VALUES (%s, %s, 'admin')",
                (circulo_id, usuario_id)
            )

        conn.commit()
        cursor.close()
        conn.close()

        request.session['user'] = {
            'id': usuario_id,
            'email': email,
            'nome': nome,
            'foto_url': foto_url
        }

    except Exception as e:
        print(f"Erro no login: {e}")
        return RedirectResponse(url="/?erro=falha_login")

    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    request.session.pop('circulo_ativo_id', None)
    return RedirectResponse(url="/")