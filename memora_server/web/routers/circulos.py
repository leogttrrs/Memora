from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
import os
from fastapi.templating import Jinja2Templates
from core.database import get_connection
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

templates = Jinja2Templates(directory=BASE_DIR)

router = APIRouter(
    prefix="/circulos",
    tags=["circulos"]
)

EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_APP = os.getenv("SENHA_APP")

@router.get("/{circulo_id}/entrar")
def entrar_circulo(request: Request, circulo_id: int):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.nome, c.emoji FROM circulos c
            JOIN membros_circulo mc ON c.id = mc.circulo_id
            WHERE c.id = %s AND mc.usuario_id = %s
        """, (circulo_id, user['id']))

        resultado = cursor.fetchone()

        if resultado:
            request.session['circulo_ativo'] = {
                'id': circulo_id,
                'nome': resultado[0],
                'emoji': resultado[1] or '🪐'
            }

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao entrar no círculo: {e}")

    return RedirectResponse(url="/dashboard")


@router.post("/novo")
def criar_circulo(request: Request, nome_circulo: str = Form(...), emoji: str = Form("🪐")):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO circulos (nome, criador_id, emoji) VALUES (%s, %s, %s) RETURNING id",
            (nome_circulo, user['id'], emoji)
        )
        novo_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO membros_circulo (circulo_id, usuario_id, papel) VALUES (%s, %s, 'admin')",
            (novo_id, user['id'])
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar círculo: {e}")

    return RedirectResponse(url="/", status_code=303)


@router.get("/{circulo_id}/gerenciar")
def gerenciar_circulo(request: Request, circulo_id: int):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/")

    dados_circulo = None
    membros = []

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT papel FROM membros_circulo WHERE circulo_id = %s AND usuario_id = %s",
                       (circulo_id, user['id']))
        papel = cursor.fetchone()

        if not papel or papel[0] != 'admin':
            return RedirectResponse(url="/")

        cursor.execute("SELECT id, nome, emoji FROM circulos WHERE id = %s", (circulo_id,))
        row = cursor.fetchone()
        if row:
            dados_circulo = {"id": row[0], "nome": row[1], "emoji": row[2]}

        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.foto_url, mc.papel 
            FROM membros_circulo mc
            JOIN usuarios u ON mc.usuario_id = u.id
            WHERE mc.circulo_id = %s
        """, (circulo_id,))
        for m in cursor.fetchall():
            membros.append({"id": m[0], "nome": m[1], "email": m[2], "foto_url": m[3], "papel": m[4]})

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao carregar gerenciar: {e}")

    return templates.TemplateResponse("circulos/gerenciar_circulo.html", {
        "request": request, "user": user, "circulo": dados_circulo, "membros": membros
    })

@router.post("/{circulo_id}/editar")
def editar_circulo(request: Request, circulo_id: int, nome_circulo: str = Form(...), emoji: str = Form(...)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE circulos SET nome = %s, emoji = %s WHERE id = %s", (nome_circulo, emoji, circulo_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao editar: {e}")
    return RedirectResponse(url=f"/circulos/{circulo_id}/gerenciar", status_code=303)


@router.post("/{circulo_id}/convidar")
def enviar_convite(request: Request, circulo_id: int, email_convidado: str = Form(...)):
    user = request.session.get('user')
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM usuarios u JOIN membros_circulo mc ON u.id = mc.usuario_id WHERE u.email = %s AND mc.circulo_id = %s",
            (email_convidado, circulo_id))

        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO convites (circulo_id, email_convidado) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING id",
                (circulo_id, email_convidado))
            novo_convite = cursor.fetchone()

            if novo_convite:
                cursor.execute("SELECT nome FROM circulos WHERE id = %s", (circulo_id,))
                nome_circulo = cursor.fetchone()[0]

                disparar_email_convite(
                    email_destino=email_convidado,
                    nome_remetente=user['nome'],
                    nome_circulo=nome_circulo
                )

            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao convidar: {e}")

    return RedirectResponse(url=f"/circulos/{circulo_id}/gerenciar", status_code=303)

@router.post("/{circulo_id}/remover-membro/{membro_id}")
def remover_membro(request: Request, circulo_id: int, membro_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        user = request.session.get('user')
        if user['id'] != membro_id:
            cursor.execute("DELETE FROM membros_circulo WHERE circulo_id = %s AND usuario_id = %s", (circulo_id, membro_id))
            conn.commit()
        conn.close()
    except Exception as e:
        pass
    return RedirectResponse(url=f"/circulos/{circulo_id}/gerenciar", status_code=303)

@router.post("/convites/{convite_id}/aceitar")
def aceitar_convite(request: Request, convite_id: int):
    user = request.session.get('user')
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT circulo_id FROM convites WHERE id = %s AND email_convidado = %s", (convite_id, user['email']))
        row = cursor.fetchone()
        if row:
            circulo_id = row[0]

            cursor.execute("INSERT INTO membros_circulo (circulo_id, usuario_id, papel) VALUES (%s, %s, 'membro') ON CONFLICT DO NOTHING", (circulo_id, user['id']))
            cursor.execute("DELETE FROM convites WHERE id = %s", (convite_id,))
            conn.commit()
        conn.close()
    except Exception as e:
        pass
    return RedirectResponse(url="/", status_code=303)

@router.post("/convites/{convite_id}/recusar")
def recusar_convite(request: Request, convite_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM convites WHERE id = %s", (convite_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass
    return RedirectResponse(url="/", status_code=303)


def disparar_email_convite(email_destino, nome_remetente, nome_circulo):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email_destino
    msg['Subject'] = f"Convite para o Memora: {nome_circulo}"

    corpo = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; max-width: 500px;">
                <h2 style="color: #38bdf8; margin-top: 0;">Você recebeu um convite! 🪐</h2>
                <p>Olá!</p>
                <p><b>{nome_remetente}</b> acabou de convidar você para participar do círculo <b>"{nome_circulo}"</b> no Memora.</p>
                <p>Acesse o sistema para aceitar o convite e começar a compartilhar suas memórias.</p>
                <br>
                <a href="{BASE_URL}" style="background-color: #38bdf8; color: #0f172a; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Acessar o Memora</a>
            </div>
        </body>
    </html>
    """
    msg.attach(MIMEText(corpo, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_APP)
        server.send_message(msg)
        server.quit()
        print(f"E-mail de convite enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail via SMTP: {e}")


@router.post("/{circulo_id}/excluir")
def excluir_circulo(request: Request, circulo_id: int):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT papel FROM membros_circulo WHERE circulo_id = %s AND usuario_id = %s",
                       (circulo_id, user['id']))
        papel = cursor.fetchone()

        if papel and papel[0] == 'admin':
            cursor.execute("DELETE FROM circulos WHERE id = %s", (circulo_id,))
            conn.commit()

            if request.session.get('circulo_ativo') and request.session['circulo_ativo']['id'] == circulo_id:
                del request.session['circulo_ativo']

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao excluir círculo: {e}")

    return RedirectResponse(url="/", status_code=303)