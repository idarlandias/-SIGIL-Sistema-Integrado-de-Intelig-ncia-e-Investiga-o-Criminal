"""
Endpoints de registro e consulta de evidencias digitais.
O hash e calculado no dispositivo; este endpoint apenas valida.
Persistencia real: metadados em PostgreSQL, binario em MinIO (WORM),
cadeia de custodia na tabela append-only `custodia_log`, e disparo
assincrono do pipeline de IA via Kafka.

Protegido por RBAC: POST exige "evidencias:criar"; GET exige
"evidencias:ler" (acesso amplo) - ver docs/RBAC.md para o gap conhecido
sobre filtro por "evidencias:ler_propria" ainda pendente de implementacao.
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
from app.services.messaging.kafka_producer import publicar_evidencia_criada
from app.core.deps import exigir_permissao, get_current_user

router = APIRouter()


def _calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


@router.post(
    "",
    response_model=EvidenciaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_permissao("evidencias:criar"))],
)
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
    Recebe uma evidencia coletada em campo, recalcula o hash SHA-256 e
    rejeita em caso de divergencia (possivel adulteracao em transito).
    Persiste metadados no Postgres, o binario no MinIO (Object Lock/WORM),
    e publica evento no Kafka para o pipeline assincrono de IA processar
    (OCR, NLP, transcricao Whisper, ALPR/EXIF) sem bloquear esta resposta.
    """
    conteudo = await arquivo.read()
    hash_servidor = _calcular_hash(conteudo)

    if hash_servidor != hash_sha256_cliente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Divergencia de hash: possivel adulteracao da evidencia.",
        )

    agente = db.query(Usuario).filter(Usuario.matricula == agente_matricula).first()
    inquerito = db.query(Inquerito).filter(Inquerito.numero == inquerito_numero).first()
    if not inquerito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inquerito {inquerito_numero} nao encontrado.",
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

    registrar_evento_custodia(
        db=db,
        evidencia_id=str(evidencia_id),
        etapa=EtapaCustodia.coleta,
        usuario=agente_matricula,
        hash_no_momento=hash_servidor,
        acao="criado",
    )

    try:
        await publicar_evidencia_criada(
            evidencia_id=str(evidencia_id),
            tipo=tipo,
            caminho_storage=caminho_storage,
            hash_sha256=hash_servidor,
        )
    except Exception:
        # Falha ao publicar no Kafka nao deve impedir o registro da evidencia
        # (ja persistida e com hash validado) - apenas o enriquecimento por
        # IA fica pendente. TODO: registrar em fila de retry/dead-letter.
        pass

    return EvidenciaResponse(
        evidencia_id=str(evidencia_id),
        hash_confirmado=True,
        etapa_custodia=EtapaCustodia.coleta,
    )


@router.get("/{evidencia_id}", dependencies=[Depends(exigir_permissao("evidencias:ler"))])
async def obter_evidencia(
    evidencia_id: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Toda leitura gera automaticamente um evento 'acessado' na cadeia de
    custodia, conforme exigencia de auditoria completa. Retorna metadados
    e uma URL temporaria (15 min) para visualizacao do binario.

    Protegido por "evidencias:ler" - GAP CONHECIDO (ver docs/RBAC.md):
    esta permissao nao distingue "ler propria" (agente) de "ler todas"
    (investigador/delegado/perito); um agente autenticado como tal
    recebera 403 aqui ate que o filtro por `capturado_por` seja
    implementado como alternativa via "evidencias:ler_propria".
    """
    evidencia = db.query(Evidencia).filter(Evidencia.id == evidencia_id).first()
    if not evidencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidencia nao encontrada.")

    registrar_evento_custodia(
        db=db,
        evidencia_id=evidencia_id,
        etapa=EtapaCustodia.armazenamento,
        usuario=usuario.matricula,
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
