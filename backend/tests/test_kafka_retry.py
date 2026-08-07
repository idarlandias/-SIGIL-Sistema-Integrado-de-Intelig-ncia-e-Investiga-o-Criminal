"""
Testes do padrão retry-topic + dead-letter topic (DLT) do produtor Kafka.
Usa mock do AIOKafkaProducer — não depende de broker real em CI.
"""
from unittest.mock import patch, AsyncMock
import pytest

from app.services.messaging.kafka_producer import publicar_para_retry, MAX_TENTATIVAS_RETRY
from app.core.config import settings


@pytest.mark.asyncio
async def test_evento_dentro_do_limite_vai_para_retry_topic():
    producer_mock = AsyncMock()
    with patch("app.services.messaging.kafka_producer.get_producer", return_value=producer_mock):
        evento = {"evidencia_id": "abc", "tentativa": 1}
        await publicar_para_retry(evento, erro="Neo4j indisponível")

    args = producer_mock.send_and_wait.call_args
    assert args[0][0] == settings.KAFKA_TOPIC_RETRY
    assert args[0][1]["tentativa"] == 2


@pytest.mark.asyncio
async def test_evento_acima_do_limite_vai_para_dead_letter():
    producer_mock = AsyncMock()
    with patch("app.services.messaging.kafka_producer.get_producer", return_value=producer_mock):
        evento = {"evidencia_id": "abc", "tentativa": MAX_TENTATIVAS_RETRY}
        await publicar_para_retry(evento, erro="Falha persistente")

    args = producer_mock.send_and_wait.call_args
    assert args[0][0] == settings.KAFKA_TOPIC_DEAD_LETTER
    assert args[0][1]["tentativa"] == MAX_TENTATIVAS_RETRY + 1
    assert args[0][1]["ultimo_erro"] == "Falha persistente"
