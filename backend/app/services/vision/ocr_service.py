"""
Extração de texto via OCR (Tesseract/PaddleOCR) de documentos escaneados
e imagens de autos de inquérito. Prioriza PaddleOCR (melhor precisão em
português e layouts complexos); cai para Tesseract se indisponível.
"""
import tempfile
from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=1)
def _carregar_paddleocr():
    try:
        from paddleocr import PaddleOCR
        return PaddleOCR(use_angle_cls=True, lang="pt", show_log=False)
    except ImportError:
        return None


def _extrair_com_tesseract(caminho_imagem: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "Nem PaddleOCR nem pytesseract/Pillow estão instalados. "
            "Instale via `pip install pytesseract pillow` e o binário tesseract-ocr."
        )
    imagem = Image.open(caminho_imagem)
    return pytesseract.image_to_string(imagem, lang="por")


def extrair_texto_imagem(caminho_imagem: str) -> str:
    """
    Extrai texto de uma imagem (documento escaneado, print de conversa,
    página de auto de inquérito fotografada). Tenta PaddleOCR primeiro
    (melhor para português e documentos com layout tabular/misto).
    """
    motor = _carregar_paddleocr()
    if motor is not None:
        resultado = motor.ocr(caminho_imagem, cls=True)
        linhas = []
        for pagina in resultado:
            if not pagina:
                continue
            for linha in pagina:
                texto_linha = linha[1][0]
                linhas.append(texto_linha)
        return "\n".join(linhas)

    return _extrair_com_tesseract(caminho_imagem)


def extrair_texto_bytes(conteudo: bytes, extensao: str = ".jpg") -> str:
    """
    Variante para uso no pipeline assíncrono, onde a imagem chega como
    bytes vindos do MinIO em vez de um caminho local em disco.
    """
    with tempfile.NamedTemporaryFile(suffix=extensao, delete=True) as tmp:
        tmp.write(conteudo)
        tmp.flush()
        return extrair_texto_imagem(tmp.name)
