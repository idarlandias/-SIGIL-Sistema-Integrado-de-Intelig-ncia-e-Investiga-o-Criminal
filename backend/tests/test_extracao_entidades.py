"""
Testes do módulo de extração de entidades (CPF, placas, telefones) e anonimização.
"""
from app.services.nlp.extracao_entidades import extrair_entidades, anonimizar_texto, sumarizar_depoimento


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


def test_extrai_email():
    texto = "Contato via suspeito@exemplo.com foi identificado."
    entidades = extrair_entidades(texto)
    tipos = [e["tipo"] for e in entidades]
    assert "EMAIL_PIX" in tipos


def test_texto_sem_entidades():
    texto = "Nenhuma informação estruturada aqui."
    entidades = extrair_entidades(texto)
    assert entidades == []


def test_anonimizar_mascara_cpf_modo_degradado():
    texto = "CPF do suspeito: 123.456.789-00"
    resultado = anonimizar_texto(texto)
    assert "123.456.789-00" not in resultado


def test_sumarizar_depoimento_curto_retorna_integro():
    texto = "Frase um. Frase dois. Frase tres."
    resultado = sumarizar_depoimento(texto, max_sentencas=5)
    assert "Frase um" in resultado
    assert "Frase tres" in resultado


def test_sumarizar_depoimento_longo_reduz_tamanho():
    texto = ". ".join([f"Esta e a frase numero {i} do depoimento" for i in range(10)])
    resultado = sumarizar_depoimento(texto, max_sentencas=3)
    assert len(resultado.split(". ")) <= 3
