"""
Endpoints de registro e consulta de evidências digitais.
O hash é calculado no dispositivo; este endpoint apenas valida.
Persistência real: metadados em PostgreSQL, binário em MinIO (WORM),
cadeia de custódia na tabela append-only `custodia_log`.
"""
import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, UploadFile, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.evidencia import EvidenciaResponse, EtapaCustodia
from app.db.session import get_db
from app.db.models import Evidencia, Usuario, Inquerito
from app.services.graph.custodia_service import registrar_evento_custodia
from app.services.storage.minio_client import salvar_evidencia, gerar_url_temporaria

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
    db: Session = Depends(get_db),
):
    """
    Recebe uma evidência coletada em campo, recalcula o hash SHA-256 e
    rejeita em caso de divergência (possível adulteração em trânsito).
    Persiste metadados no Postgres e o binário no MinIO (Object Lock/WORM).
    """
    conteudo = await arquivo.read()
    hash_servidor = _calcular_hash(conteudo)

    if hash_servidor != hash_sha256_cliente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Divergência de hash: possível adulteração da evidência.",
        )

    agente = db.query(Usuario).filter(Usuario.matricula == agente_matricula).first()
    inquerito = db.query(Inquerito).filter(Inquerito.numero == inquerito_numero).first()
    if not inquerito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquérito {inquerito_numero} não encontrado.",
        )

    evidencia_id = uuid.uuid4()
    caminho_storage = salvar_evidencia(str(evidencia_id), conteudo, arquivo.content_type)

    nova_evidencia = Evidencia(
        id=evidencia_id,
        hash_sha256=hash_servidor,
        tipo=tipo,
        gps_lat=gps_lat,
        gps_lon=gps_lon,
        capturado_em=capturado_em,
        capturado_por=agente.id if agente else None,
        inquerito_id=inquerito.id,
        caminho_storage=caminho_storage,
    )
    db.add(nova_evidencia)
    db.commit()

    # TODO: publicar evento em Kafka para o pipeline de OCR/NLP/ALPR

    registrar_evento_custodia(
        db=db,
        evidencia_id=str(evidencia_id),
        etapa=EtapaCustodia.coleta,
        usuario=agente_matricula,
        hash_no_momento=hash_servidor,
        acao="criado",
    )

    return EvidenciaResponse(
        evidencia_id=str(evidencia_id),
        hash_confirmado=True,
        etapa_custodia=EtapaCustodia.coleta,
    )


@router.get("/{evidencia_id}")
async def obter_evidencia(evidencia_id: str, usuario_matricula: str = "usuario_autenticado", db: Session = Depends(get_db)):
    """
    Toda leitura gera automaticamente um evento 'acessado' na cadeia de
    custódia, conforme exigência de auditoria completa. Retorna metadados
    e uma URL temporária (15 min) para visualização do binário.
    """
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()
    if not evidencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidência não encontrada.")

    registrar_evento_custodia(
        db=db,
        evidencia_id=evidencia_id,
        etapa=EtapaCustodia.armazenamento,
        usuario=usuario_matricula,  # TODO: substituir por Depends(get_current_user).matricula
        hash_no_momento=evidencia.hash_sha256,
        acao="acessado",
    )

    url_temporaria = gerar_url_temporaria(evidencia.caminho_storage)

    return {
        "evidencia_id": str(evidencia.id),
        "tipo": evidencia.tipo,
        "hash_sha256": evidencia.hash_sha256,
        "capturado_em": evidencia.capturado_em,
        "gps_lat": evidencia.gps_lat,
        "gps_lon": evidencia.gps_lon,
        "url_visualizacao": url_temporaria,
    }
