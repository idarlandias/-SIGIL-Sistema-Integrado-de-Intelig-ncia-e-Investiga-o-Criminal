"""
Testes do módulo de extração de entidades (CPF, placas, telefones).
"""
from app.services.nlp.extracao_entidades import extrair_entidades


def test_extrai_cpf():
    texto = "O suspeito, CPF 123.456.789-00, foi visto no local."
    entidades = extrair_entidades(texto)
    tipos = [e["tipo"] for e in entidades]
    assert "CPF" in tipos


def test_extrai_placa():
    texto = "O veículo de placa ABC1D23 fugiu em direção ao centro."
    entidades = extrair_entidades(texto)
    tipos = [e["tipo"] for e in entidades]
    assert "PLACA" in tipos


def test_texto_sem_entidades():
    texto = "Nenhuma informação estruturada aqui."
    entidades = extrair_entidades(texto)
    assert entidades == []
