"""
SIGIL Backend — Ponto de entrada da API FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import evidencias, custodia, grafo, casos, auth, transcricao

app = FastAPI(
    title="SIGIL API",
    description="API de inteligência e investigação criminal",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/v1/auth", tags=["Autenticação"])
app.include_router(evidencias.router, prefix="/v1/evidencias", tags=["Evidências"])
app.include_router(custodia.router, prefix="/v1/custodia", tags=["Cadeia de Custódia"])
app.include_router(grafo.router, prefix="/v1/grafo", tags=["Análise de Vínculos"])
app.include_router(casos.router, prefix="/v1/casos", tags=["Inquéritos"])
app.include_router(transcricao.router, prefix="/v1/transcricao", tags=["Transcrição de Áudio"])


@app.get("/health", tags=["Infra"])
async def health_check():
    return {"status": "ok", "service": "SIGIL API"}
