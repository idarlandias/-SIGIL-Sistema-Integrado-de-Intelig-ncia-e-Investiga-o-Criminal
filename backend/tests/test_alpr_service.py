"""
Testes do serviço de ALPR e EXIF. Não depende de modelos reais instalados —
usa mocks para validar o comportamento de fallback e a estrutura de retorno.
"""
from unittest.mock import patch, MagicMock

from app.services.vision.alpr_service import processar_frame_alpr, _converter_gps


def test_processar_frame_sem_motores_retorna_lista_vazia():
    with patch("app.services.vision.alpr_service._carregar_fast_alpr", return_value=None), \\
         patch("app.services.vision.alpr_service._carregar_openalpr_legado", return_value=None):
        resultado = processar_frame_alpr("qualquer_imagem.jpg")
    assert resultado == []


def test_processar_frame_com_fast_alpr_mockado():
    deteccao_mock = MagicMock()
    deteccao_mock.ocr.text = "ABC1D23"
    deteccao_mock.ocr.confidence = 0.95
    deteccao_mock.detection.bounding_box.x1 = 10
    deteccao_mock.detection.bounding_box.y1 = 20
    deteccao_mock.detection.bounding_box.x2 = 100
    deteccao_mock.detection.bounding_box.y2 = 60

    motor_mock = MagicMock()
    motor_mock.predict.return_value = [deteccao_mock]

    with patch("app.services.vision.alpr_service._carregar_fast_alpr", return_value=motor_mock):
        resultado = processar_frame_alpr("qualquer_imagem.jpg")

    assert len(resultado) == 1
    assert resultado[0]["placa"] == "ABC1D23"
    assert resultado[0]["motor"] == "fast-alpr"


def test_converter_gps_sem_valor_retorna_none():
    assert _converter_gps(None, None) is None
