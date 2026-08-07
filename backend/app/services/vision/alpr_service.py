"""
Serviço de leitura de placas veiculares (ALPR) em vídeos/imagens de câmeras.
Integração de referência com OpenALPR / fast-alpr.
"""
from typing import List, Dict


def processar_frame_alpr(caminho_imagem: str) -> List[Dict]:
    """
    Recebe caminho de um frame extraído de vídeo de câmera de segurança
    e retorna placas detectadas com score de confiança.

    TODO: integrar biblioteca real, ex.:
        from openalpr import Alpr
        alpr = Alpr("br", "openalpr.conf", "runtime_data")
        resultados = alpr.recognize_file(caminho_imagem)
    """
    raise NotImplementedError("Integrar OpenALPR/fast-alpr conforme docs/ARQUITETURA.md")


def extrair_metadados_exif(caminho_imagem: str) -> Dict:
    """
    Extrai metadados EXIF (geolocalização, timestamp, dispositivo) de uma imagem.
    TODO: integrar ExifTool ou biblioteca `exifread`.
    """
    raise NotImplementedError("Integrar ExifTool conforme docs/ARQUITETURA.md")
