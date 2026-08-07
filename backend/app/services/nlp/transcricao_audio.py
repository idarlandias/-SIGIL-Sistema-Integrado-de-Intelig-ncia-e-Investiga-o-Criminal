"""
Transcrição de depoimentos e escutas telefônicas autorizadas via OpenAI Whisper.

O modelo é carregado de forma lazy e mantido em cache de processo, pois o
carregamento inicial é custoso (~1-2s para o modelo "base", mais para
modelos maiores). Suporta arquivos locais (path) e bytes em memória.
"""
import io
import tempfile
from functools import lru_cache
from typing import Dict, Optional

from app.core.config import settings


@lru_cache(maxsize=1)
def _carregar_modelo_whisper():
    """
    Carrega o modelo Whisper definido em WHISPER_MODEL (ex.: "base", "small",
    "medium"). Retorna None se a biblioteca não estiver instalada, permitindo
    que o restante do pipeline continue operando em modo degradado.
    """
    try:
        import whisper
        return whisper.load_model(settings.WHISPER_MODEL)
    except ImportError:
        return None


def transcrever_audio(caminho_arquivo: str, idioma: str = "pt") -> Dict:
    """
    Transcreve um arquivo de áudio (depoimento ou escuta autorizada) e
    retorna o texto completo com segmentos timestampados — úteis para
    apontar no laudo pericial o momento exato de uma fala relevante.
    """
    modelo = _carregar_modelo_whisper()
    if modelo is None:
        raise RuntimeError(
            "Whisper não está instalado neste ambiente. "
            "Instale via `pip install openai-whisper` (ver requirements.txt)."
        )

    resultado = modelo.transcribe(caminho_arquivo, language=idioma, verbose=False)

    return {
        "texto_completo": resultado["text"].strip(),
        "idioma_detectado": resultado.get("language", idioma),
        "segmentos": [
            {
                "inicio_segundos": round(seg["start"], 2),
                "fim_segundos": round(seg["end"], 2),
                "texto": seg["text"].strip(),
            }
            for seg in resultado.get("segments", [])
        ],
    }


def transcrever_audio_bytes(conteudo: bytes, extensao: str = ".mp3", idioma: str = "pt") -> Dict:
    """
    Variante para uso no pipeline assíncrono (worker Kafka), onde o áudio
    chega como bytes vindos do MinIO em vez de um caminho local. Grava em
    arquivo temporário pois o Whisper opera sobre caminhos de arquivo.
    """
    with tempfile.NamedTemporaryFile(suffix=extensao, delete=True) as tmp:
        tmp.write(conteudo)
        tmp.flush()
        return transcrever_audio(tmp.name, idioma=idioma)
