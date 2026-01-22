# memora_server/api/endpoints.py
from fastapi import APIRouter

# Criamos um "mini-app" apenas para rotas da API
router = APIRouter()

@router.get("/status")
def api_status():
    return {"status": "online", "sistema": "Memora API", "versao": "1.0"}