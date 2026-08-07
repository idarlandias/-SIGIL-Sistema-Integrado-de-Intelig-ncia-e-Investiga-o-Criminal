"""
Testes do módulo de persistência de entidades no grafo Neo4j.
Usa mock do driver — não depende de instância real do Neo4j em CI.
"""
from unittest.mock import patch, MagicMock

from app.services.graph.entidades_grafo import persistir_entidades_no_grafo


def test_persistir_entidades_vazio_nao_chama_driver():
    with patch("app.services.graph.entidades_grafo.get_driver") as driver_mock:
        resultado = persistir_entidades_no_grafo([], "hash123")
    assert resultado == {}
    driver_mock.assert_not_called()


def test_persistir_entidades_cpf_e_placa():
    session_mock = MagicMock()
    driver_mock = MagicMock()
    driver_mock.session.return_value.__enter__.return_value = session_mock

    entidades = [
        {"tipo": "CPF", "valor": "123.456.789-00", "posicao": 0},
        {"tipo": "PLACA", "valor": "ABC1D23", "posicao": 20},
    ]

    with patch("app.services.graph.entidades_grafo.get_driver", return_value=driver_mock):
        resumo = persistir_entidades_no_grafo(entidades, "hash123", tipo_evidencia="documento")

    assert resumo == {"CPF": 1, "PLACA": 1}
    assert session_mock.run.call_count >= 2


def test_persistir_entidades_tipo_nao_mapeado_e_ignorado():
    session_mock = MagicMock()
    driver_mock = MagicMock()
    driver_mock.session.return_value.__enter__.return_value = session_mock

    entidades = [{"tipo": "EMAIL_PIX", "valor": "teste@exemplo.com", "posicao": 0}]

    with patch("app.services.graph.entidades_grafo.get_driver", return_value=driver_mock):
        resumo = persistir_entidades_no_grafo(entidades, "hash123")

    assert resumo == {}
