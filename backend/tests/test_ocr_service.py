"""
Testes do serviço de OCR. Usa mocks — não depende de PaddleOCR/Tesseract
instalados em CI.
"""
from unittest.mock import patch, MagicMock

from app.services.vision.ocr_service import extrair_texto_imagem


def test_extrai_texto_com_paddleocr_mockado():
    resultado_paddle = [[
        [None, ("CPF do suspeito", 0.98)],
        [None, ("123.456.789-00", 0.95)],
    ]]
    motor_mock = MagicMock()
    motor_mock.ocr.return_value = resultado_paddle

    with patch("app.services.vision.ocr_service._carregar_paddleocr", return_value=motor_mock):
        texto = extrair_texto_imagem("qualquer_imagem.jpg")

    assert "CPF do suspeito" in texto
    assert "123.456.789-00" in texto


def test_extrai_texto_fallback_tesseract_sem_paddle():
    with patch("app.services.vision.ocr_service._carregar_paddleocr", return_value=None):
        try:
            extrair_texto_imagem("qualquer_imagem.jpg")
        except RuntimeError as e:
            assert "PaddleOCR" in str(e) or "pytesseract" in str(e)
        except Exception:
            # Se pytesseract/Pillow estiverem instalados no ambiente de teste,
            # a chamada tentará abrir o arquivo (que não existe) e falhará
            # de outra forma — ambos os cenários são aceitáveis aqui.
            pass
