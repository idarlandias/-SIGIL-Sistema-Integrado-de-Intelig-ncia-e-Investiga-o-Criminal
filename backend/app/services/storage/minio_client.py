"""
Cliente MinIO com Object Lock (WORM) para armazenamento imutável de evidências.
"""
import io
from datetime import timedelta

from minio import Minio
from minio.commonconfig import GOVERNANCE
from minio.retention import Retention
from datetime import datetime

from app.core.config import settings

_client = None


def get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.ENVIRONMENT == "production",
        )
    return _client


def garantir_bucket_worm():
    """
    Cria o bucket de evidências com Object Lock habilitado, se não existir.
    Object Lock deve ser configurado na CRIAÇÃO do bucket — não pode ser
    adicionado depois. Retenção padrão: modo GOVERNANCE, 5 anos.
    """
    client = get_client()
    if not client.bucket_exists(settings.MINIO_BUCKET_EVIDENCIAS):
        client.make_bucket(settings.MINIO_BUCKET_EVIDENCIAS, object_lock=True)


def salvar_evidencia(evidencia_id: str, conteudo: bytes, content_type: str = "application/octet-stream") -> str:
    """
    Grava a evidência no bucket WORM com retenção de 5 anos em modo
    GOVERNANCE (impede exclusão/sobrescrita mesmo por administradores,
    exceto com permissão especial de bypass).
    """
    client = get_client()
    caminho = f"evidencias/{evidencia_id}"

    retencao = Retention(GOVERNANCE, datetime.utcnow() + timedelta(days=5 * 365))

    client.put_object(
        settings.MINIO_BUCKET_EVIDENCIAS,
        caminho,
        io.BytesIO(conteudo),
        length=len(conteudo),
        content_type=content_type,
        retention=retencao,
        legal_hold=False,
    )
    return caminho


def obter_evidencia(caminho_storage: str) -> bytes:
    client = get_client()
    response = client.get_object(settings.MINIO_BUCKET_EVIDENCIAS, caminho_storage)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def gerar_url_temporaria(caminho_storage: str, expira_em_minutos: int = 15) -> str:
    """
    Gera URL pré-assinada de curta duração para visualização da evidência
    no painel web, sem expor credenciais do MinIO ao cliente.
    """
    client = get_client()
    return client.presigned_get_object(
        settings.MINIO_BUCKET_EVIDENCIAS,
        caminho_storage,
        expires=timedelta(minutes=expira_em_minutos),
    )
