"""
Testes do fluxo de registro de evidências e validação de hash.
"""
import hashlib
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hash_sha256_consistente():
    conteudo = b"conteudo-de-teste-da-evidencia"
    hash1 = hashlib.sha256(conteudo).hexdigest()
    hash2 = hashlib.sha256(conteudo).hexdigest()
    assert hash1 == hash2


def test_hash_diverge_com_conteudo_alterado():
    original = hashlib.sha256(b"conteudo-original").hexdigest()
    adulterado = hashlib.sha256(b"conteudo-adulterado").hexdigest()
    assert original != adulterado
