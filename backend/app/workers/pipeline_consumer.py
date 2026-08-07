"""
Worker consumidor da fila Kafka: processa evidências recém-criadas.

Roteamento por tipo:
- documento/foto (com texto legível) -> OCR (PaddleOCR/Tesseract) + extração de entidades
- audio -> transcrição via Whisper + extração de entidades no texto transcrito
- foto/video -> ALPR (placas) + EXIF (GEOINT), além do OCR quando aplicável

Resiliência: consome tanto o tópico principal quanto o tópico de retry.
Falhas de processamento (não a ausência de dados, mas exceções reais —
Neo4j fora do ar, MinIO indisponível, etc.) republicam o evento com
contador de tentativas incrementado; após MAX_TENTATIVAS_RETRY, o evento
vai para o dead-letter topic para investigação manual, em vez de ser
descartado silenciosamente ou reprocessado para sempre (ver padrão
retry-topic + DLT do Spring Kafka / Uber engineering).

Todas as entidades extraídas são persistidas no Neo4j, vinculadas à
evidência de origem, fechando o ciclo pipeline de IA -> grafo de inteligência.
"""
import asyncio
import json
import logging
import tempfile

from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.services.nlp.extracao_entidades import extrair_entidades
from app.services.nlp.transcricao_audio import transcrever_audio_bytes
from app.services.vision.alpr_service import processar_frame_alpr, extrair_metadados_exif
from app.services.vision.ocr_service import extrair_texto_bytes
from app.services.graph.custodia_service import registrar_evento_custodia
from app.services.graph.entidades_grafo import persistir_entidades_no_grafo
from app.services.storage.minio_client import obter_evidencia
from app.services.messaging.kafka_producer import publicar_para_retry
from app.models.evidencia import EtapaCustodia
from app.db.session import SessionLocal

logger = logging.getLogger("sigil.pipeline_consumer")


async def _processar_documento(conteudo: bytes, hash_evidencia: str, tipo: str) -> dict:
    if tipo == "depoimento_texto":
        texto_extraido = conteudo.decode("utf-8", errors="ignore")
    else:
        texto_extraido = extrair_texto_bytes(conteudo, extensao=".jpg")

    entidades = extrair_entidades(texto_extraido)
    resumo_grafo = persistir_entidades_no_grafo(entidades, hash_evidencia, tipo_evidencia=tipo)
    return {"entidades_extraidas": len(entidades), "resumo_grafo": resumo_grafo}


async def _processar_audio(conteudo: bytes, hash_evidencia: str) -> dict:
    resultado_transcricao = transcrever_audio_bytes(conteudo, extensao=".mp3")
    texto = resultado_transcricao["texto_completo"]
    entidades = extrair_entidades(texto)
    resumo_grafo = persistir_entidades_no_grafo(entidades, hash_evidencia, tipo_evidencia="audio")
    return {
        "transcricao": texto,
        "entidades_extraidas": len(entidades),
        "resumo_grafo": resumo_grafo,
    }


async def _processar_video_ou_imagem_visual(conteudo: bytes, hash_evidencia: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(conteudo)
        tmp.flush()
        placas = processar_frame_alpr(tmp.name)
        exif = extrair_metadados_exif(tmp.name)

    texto_ocr = extrair_texto_bytes(conteudo, extensao=".jpg")
    entidades = extrair_entidades(texto_ocr) if texto_ocr.strip() else []
    resumo_grafo = persistir_entidades_no_grafo(entidades, hash_evidencia, tipo_evidencia="foto")

    return {
        "placas_detectadas": placas,
        "metadados_exif": exif,
        "entidades_extraidas": len(entidades),
        "resumo_grafo": resumo_grafo,
    }


async def _processar_evento(evento: dict) -> None:
    """
    Roteia o evento por tipo e registra a etapa de custódia. Deixa
    exceções propagarem — quem chama decide entre retry/DLT/descarte.
    """
    evidencia_id = evento["evidencia_id"]
    tipo = evento.get("tipo", "documento")
    caminho_storage = evento.get("caminho_storage")
    hash_evidencia = evento.get("hash", "")

    conteudo = obter_evidencia(caminho_storage) if caminho_storage else b""

    if tipo in ("documento", "depoimento_texto"):
        await _processar_documento(conteudo, hash_evidencia, tipo)
    elif tipo == "audio":
        await _processar_audio(conteudo, hash_evidencia)
    elif tipo in ("foto", "video"):
        await _processar_video_ou_imagem_visual(conteudo, hash_evidencia)

    db = SessionLocal()
    try:
        registrar_evento_custodia(
            db=db,
            evidencia_id=evidencia_id,
            etapa=EtapaCustodia.processamento,
            usuario="pipeline_ia",
            hash_no_momento=hash_evidencia,
            acao="modificado",
        )
    finally:
        db.close()


async def consumir_pipeline():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_EVIDENCIAS,
        settings.KAFKA_TOPIC_RETRY,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="sigil-pipeline-ia",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            evento = json.loads(msg.value)
            tentativa = evento.get("tentativa", 0)

            try:
                await _processar_evento(evento)
            except Exception as e:
                logger.warning(
                    "Falha ao processar evidência %s (tentativa %d): %s",
                    evento.get("evidencia_id"), tentativa, e,
                )
                await publicar_para_retry(evento, erro=str(e))
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consumir_pipeline())
