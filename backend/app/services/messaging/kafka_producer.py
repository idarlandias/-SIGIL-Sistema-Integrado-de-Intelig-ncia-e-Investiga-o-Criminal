"""
Produtor Kafka para publicação de eventos assíncronos — hoje usado para
notificar o pipeline de IA (OCR/NLP/ALPR/Whisper) sobre novas evidências.

O produtor é inicializado de forma lazy e reutilizado entre requisições
(uma única conexão AIOKafkaProducer por processo), evitando o custo de
abrir/fechar conexão TCP em cada chamada.
"""
import json
from typing import Optional

from aiokafka import AIOKafkaProducer

from app.core.config import settings

_producer: Optional[AIOKafkaProducer] = None


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await _producer.start()
    return _producer


async def publicar_evidencia_criada(evidencia_id: str, tipo: str, caminho_storage: str, hash_sha256: str) -> None:
    """
    Publica um evento no tópico de evidências recém-criadas, disparando o
    pipeline assíncrono (OCR para documentos, Whisper para áudio, ALPR/EXIF
    para imagens) sem bloquear a resposta HTTP ao cliente que fez o upload.
    """
    producer = await get_producer()
    evento = {
        "evidencia_id": evidencia_id,
        "tipo": tipo,
        "caminho_storage": caminho_storage,
        "hash": hash_sha256,
    }
    await producer.send_and_wait(settings.KAFKA_TOPIC_EVIDENCIAS, evento)


async def encerrar_producer() -> None:
    """Chamado no shutdown da aplicação (evento `shutdown` do FastAPI)."""
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
