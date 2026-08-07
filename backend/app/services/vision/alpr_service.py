"""
Serviço de leitura de placas veiculares (ALPR) em vídeos/imagens de câmeras
de segurança, e extração de metadados EXIF de imagens.

Prioriza fast-alpr (mais moderno, baseado em modelos YOLO/OCR leves) e cai
para openalpr (biblioteca C++ clássica com binding Python) se disponível.
Se nenhuma das duas estiver instalada, opera em modo degradado retornando
lista vazia — o pipeline não quebra, apenas não enriquece com placas.
"""
from functools import lru_cache
from typing import List, Dict, Optional


@lru_cache(maxsize=1)
def _carregar_fast_alpr():
    try:
        from fast_alpr import ALPR
        return ALPR(detector_model="yolo-v9-t-384-license-plate-end2end",
                    ocr_model="cct-xs-v1-global-model")
    except ImportError:
        return None


@lru_cache(maxsize=1)
def _carregar_openalpr_legado():
    try:
        from openalpr import Alpr
        alpr = Alpr("br", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
        if not alpr.is_loaded():
            return None
        return alpr
    except ImportError:
        return None


def processar_frame_alpr(caminho_imagem: str) -> List[Dict]:
    """
    Recebe caminho de um frame extraído de vídeo de câmera de segurança
    e retorna placas detectadas com score de confiança e bounding box.
    Tenta fast-alpr primeiro; se indisponível, tenta openalpr legado.
    """
    motor = _carregar_fast_alpr()
    if motor is not None:
        resultados = motor.predict(caminho_imagem)
        return [
            {
                "placa": r.ocr.text,
                "confianca": round(r.ocr.confidence, 3),
                "bbox": {
                    "x1": r.detection.bounding_box.x1,
                    "y1": r.detection.bounding_box.y1,
                    "x2": r.detection.bounding_box.x2,
                    "y2": r.detection.bounding_box.y2,
                },
                "motor": "fast-alpr",
            }
            for r in resultados
        ]

    alpr_legado = _carregar_openalpr_legado()
    if alpr_legado is not None:
        resultados = alpr_legado.recognize_file(caminho_imagem)
        return [
            {
                "placa": p["plate"],
                "confianca": round(p["confidence"] / 100, 3),
                "bbox": None,
                "motor": "openalpr",
            }
            for p in resultados.get("results", [])
        ]

    return []


def extrair_metadados_exif(caminho_imagem: str) -> Dict:
    """
    Extrai metadados EXIF (geolocalização, timestamp, dispositivo) de uma
    imagem, usando a biblioteca `exifread` (pura Python, sem dependência de
    binário externo como o ExifTool). Retorna dict vazio se não houver EXIF.
    """
    try:
        import exifread
    except ImportError:
        raise RuntimeError(
            "exifread não está instalado. Instale via `pip install exifread`."
        )

    with open(caminho_imagem, "rb") as f:
        tags = exifread.process_file(f, details=False)

    if not tags:
        return {}

    resultado = {
        "dispositivo": str(tags.get("Image Model", "")) or None,
        "data_hora": str(tags.get("EXIF DateTimeOriginal", "")) or None,
        "orientacao": str(tags.get("Image Orientation", "")) or None,
    }

    gps_lat = _converter_gps(tags.get("GPS GPSLatitude"), tags.get("GPS GPSLatitudeRef"))
    gps_lon = _converter_gps(tags.get("GPS GPSLongitude"), tags.get("GPS GPSLongitudeRef"))
    if gps_lat is not None and gps_lon is not None:
        resultado["gps_lat"] = gps_lat
        resultado["gps_lon"] = gps_lon

    return resultado


def _converter_gps(valor, referencia) -> Optional[float]:
    """Converte coordenadas EXIF (graus, minutos, segundos) para decimal."""
    if valor is None:
        return None
    try:
        graus, minutos, segundos = [float(v.num) / float(v.den) for v in valor.values]
        decimal = graus + minutos / 60 + segundos / 3600
        if referencia and str(referencia) in ("S", "W"):
            decimal = -decimal
        return round(decimal, 6)
    except (AttributeError, ZeroDivisionError, ValueError):
        return None
