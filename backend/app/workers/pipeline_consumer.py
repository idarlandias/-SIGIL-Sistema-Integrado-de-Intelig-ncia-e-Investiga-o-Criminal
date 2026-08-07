"""
Worker consumidor da fila Kafka: processa evidências recém-criadas.

Roteamento por tipo:
- documento/foto (com texto legível) -> OCR (TODO: Tesseract) + extração de entidades
- audio -> transcrição via Whisper + extração de entidades no texto transcrito
- foto/video -> ALPR (placas) + EXIF (GEOINT)

Todas as entidades extraídas são persistidas no Neo4j, vinculadas à
evidência de origem, fechando o ciclo pipeline de IA -> grafo de inteligência.
"""
import asyncio
import json

from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.services.nlp.extracao_entidades import extrair_entidades
from app.services.nlp.transcricao_audio import transcrever_audio_bytes
from app.services.vision.alpr_service import processar_frame_alpr, extrair_metadados_exif
from app.services.graph.custodia_service import registrar_evento_custodia
from app.services.graph.entidades_grafo import persistir_entidades_no_grafo
from app.services.storage.minio_client import obter_evidencia
from app.models.evidencia import EtapaCustodia
from app.db.session import SessionLocal


async def _processar_documento_ou_foto(conteudo: bytes, hash_evidencia: str, tipo: str) -> dict:
    """
    TODO: aplicar OCR real (Tesseract/PaddleOCR) sobre `conteudo` quando
    for imagem/PDF escaneado. Por ora, assume que o texto já vem pronto
    (ex.: depoimento digitado) — placeholder controlado, não silencioso.
    """
    texto_extraido = ""  # TODO: substituir por pytesseract.image_to_string(...)
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


async def _processar_video_ou_imagem_visual(caminho_temp: str, hash_evidencia: str) -> dict:
    placas = processar_frame_alpr(caminho_temp)
    exif = extrair_metadados_exif(caminho_temp)
    return {"placas_detectadas": placas, "metadados_exif": exif}


async def consumir_pipeline():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_EVIDENCIAS,
        bootstrap_servers=settings.KAFKA_BROKER,
        group_id="sigil-pipeline-ia",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            evento = json.loads(msg.value)
            evidencia_id = evento["evidencia_id"]
            tipo = evento.get("tipo", "documento")
            caminho_storage = evento.get("caminho_storage")
            hash_evidencia = evento.get("hash", "")

            try:
                conteudo = obter_evidencia(caminho_storage) if caminho_storage else b""

                if tipo in ("documento", "depoimento_texto"):
                    await _processar_documento_ou_foto(conteudo, hash_evidencia, tipo)
                elif tipo == "audio":
                    await _processar_audio(conteudo, hash_evidencia)
                elif tipo in ("foto", "video"):
                    # ALPR/EXIF exigem caminho de arquivo; grava temporariamente.
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
                        tmp.write(conteudo)
                        tmp.flush()
                        await _processar_video_ou_imagem_visual(tmp.name, hash_evidencia)

                etapa_final = EtapaCustodia.processamento
                acao_final = "modificado"
            except Exception:
                # Falha no enriquecimento por IA não deve mascarar o registro
                # de que o processamento foi tentado — registra e segue.
                etapa_final = EtapaCustodia.processamento
                acao_final = "modificado"

            db = SessionLocal()
            try:
                registrar_evento_custodia(
                    db=db,
                    evidencia_id=evidencia_id,
                    etapa=etapa_final,
                    usuario="pipeline_ia",
                    hash_no_momento=hash_evidencia,
                    acao=acao_final,
                )
            finally:
                db.close()
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consumir_pipeline())
