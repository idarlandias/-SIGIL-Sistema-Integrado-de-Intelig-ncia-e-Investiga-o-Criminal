"""
Extração de entidades nomeadas (CPF, placas, endereços, chaves PIX) em
documentos de inquérito, usando spaCy + Microsoft Presidio.
"""
import re
from typing import List, Dict

# TODO: carregar modelo real -> import spacy; nlp = spacy.load(settings.SPACY_MODEL)

PADRAO_CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
PADRAO_PLACA = re.compile(r"[A-Z]{3}\d[A-Z0-9]\d{2}")
PADRAO_PIX_TELEFONE = re.compile(r"\(\d{2}\)\s?\d{4,5}-?\d{4}")


def extrair_entidades(texto: str) -> List[Dict[str, str]]:
    """
    Extrai entidades estruturadas de um texto (ex.: transcrição de depoimento
    ou texto extraído de PDF via OCR). Retorna lista de {tipo, valor, posicao}.
    """
    entidades = []
    for match in PADRAO_CPF.finditer(texto):
        entidades.append({"tipo": "CPF", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_PLACA.finditer(texto):
        entidades.append({"tipo": "PLACA", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_PIX_TELEFONE.finditer(texto):
        entidades.append({"tipo": "TELEFONE_PIX", "valor": match.group(), "posicao": match.start()})

    # TODO: integrar spaCy NER para PESSOA, LOCAL, ORGANIZACAO
    # TODO: integrar Presidio para anonimização automática de dados sensíveis fora do escopo do IP
    return entidades


def sumarizar_depoimento(texto: str, max_sentencas: int = 5) -> str:
    """
    Placeholder de sumarização extrativa. Substituir por chamada a modelo
    de IA generativa (ex.: LLM local ou API segura, respeitando LGPD).
    """
    sentencas = texto.split(". ")
    return ". ".join(sentencas[:max_sentencas])
