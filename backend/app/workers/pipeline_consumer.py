"""
Worker consumidor da fila Kafka: processa evidências recém-criadas
(OCR, NLP, ALPR) e grava resultados/entidades no grafo Neo4j.
"""
import asyncio
import json

from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.services.nlp.extracao_entidades import extrair_entidades
from app.services.graph.custodia_service import registrar_evento_custodia
from app.models.evidencia import EtapaCustodia
from app.db.session import SessionLocal


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

            # TODO: buscar conteúdo real no MinIO, rotear por tipo (OCR/Whisper/ALPR)
            texto_extraido = evento.get("texto_ocr", "")
            entidades = extrair_entidades(texto_extraido)

            # TODO: persistir entidades como nós/relacionamentos no Neo4j

            db = SessionLocal()
            try:
                registrar_evento_custodia(
                    db=db,
                    evidencia_id=evidencia_id,
                    etapa=EtapaCustodia.processamento,
                    usuario="pipeline_ia",
                    hash_no_momento=evento.get("hash", ""),
                    acao="modificado",
                )
            finally:
                db.close()
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consumir_pipeline())
