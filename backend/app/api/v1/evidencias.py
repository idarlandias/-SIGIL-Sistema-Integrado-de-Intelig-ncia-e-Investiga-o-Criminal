"""
Endpoints de registro e consulta de evidências digitais.
O hash é calculado no dispositivo; este endpoint apenas valida.
"""
import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, Form, HTTPException, status

from app.models.evidencia import EvidenciaResponse, EtapaCustodia
from app.services.graph.custodia_service import registrar_evento_custodia

router = APIRouter()


def _calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


@router.post("", response_model=EvidenciaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_evidencia(
    arquivo: UploadFile,
    hash_sha256_cliente: str = Form(...),
    tipo: str = Form(...),
    gps_lat: float = Form(None),
    gps_lon: float = Form(None),
    capturado_em: datetime = Form(...),
    agente_matricula: str = Form(...),
    inquerito_numero: str = Form(...),
    assinatura_dispositivo: str = Form(...),
):
    """
    Recebe uma evidência coletada em campo, recalcula o hash SHA-256 e
    rejeita em caso de divergência (possível adulteração em trânsito).
    """
    conteudo = await arquivo.read()
    hash_servidor = _calcular_hash(conteudo)

    if hash_servidor != hash_sha256_cliente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Divergência de hash: possível adulteração da evidência.",
        )

    evidencia_id = str(uuid.uuid4())

    # TODO: gravar `conteudo` em armazenamento WORM (MinIO com Object Lock)
    # TODO: publicar evento em Kafka para o pipeline de OCR/NLP/ALPR

    registrar_evento_custodia(
        evidencia_id=evidencia_id,
        etapa=EtapaCustodia.coleta,
        usuario=agente_matricula,
        hash_no_momento=hash_servidor,
        acao="criado",
    )

    return EvidenciaResponse(
        evidencia_id=evidencia_id,
        hash_confirmado=True,
        etapa_custodia=EtapaCustodia.coleta,
    )


@router.get("/{evidencia_id}")
async def obter_evidencia(evidencia_id: str):
    """
    Toda leitura gera automaticamente um evento 'acessado' na cadeia de
    custódia, conforme exigência de auditoria completa.
    """
    registrar_evento_custodia(
        evidencia_id=evidencia_id,
        etapa=EtapaCustodia.armazenamento,
        usuario="usuario_autenticado",  # substituir por dependência de auth
        hash_no_momento="",
        acao="acessado",
    )
    # TODO: buscar metadados reais no Postgres e conteúdo no MinIO
    return {"evidencia_id": evidencia_id, "status": "implementar_busca_real"}
