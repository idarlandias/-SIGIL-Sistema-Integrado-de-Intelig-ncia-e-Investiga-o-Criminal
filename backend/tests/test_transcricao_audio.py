"""
Testes do módulo de transcrição de áudio. O modelo Whisper real não é
carregado em CI (evita download pesado); testamos o comportamento de
fallback e a estrutura de retorno via mock.
"""
from unittest.mock import patch, MagicMock

from app.services.nlp.transcricao_audio import transcrever_audio, _carregar_modelo_whisper


def test_transcrever_audio_sem_modelo_levanta_erro():
    _carregar_modelo_whisper.cache_clear()
    with patch("app.services.nlp.transcricao_audio._carregar_modelo_whisper", return_value=None):
        try:
            transcrever_audio("arquivo_inexistente.mp3")
            assert False, "Deveria ter levantado RuntimeError"
        except RuntimeError as e:
            assert "Whisper não está instalado" in str(e)


def test_transcrever_audio_com_modelo_mockado():
    modelo_mock = MagicMock()
    modelo_mock.transcribe.return_value = {
        "text": "Isso é um depoimento de teste.",
        "language": "pt",
        "segments": [{"start": 0.0, "end": 2.5, "text": "Isso é um depoimento de teste."}],
    }
    with patch(
        "app.services.nlp.transcricao_audio._carregar_modelo_whisper",
        return_value=modelo_mock,
    ):
        resultado = transcrever_audio("qualquer_caminho.mp3")

    assert resultado["texto_completo"] == "Isso é um depoimento de teste."
    assert resultado["idioma_detectado"] == "pt"
    assert len(resultado["segmentos"]) == 1
    assert resultado["segmentos"][0]["inicio_segundos"] == 0.0
