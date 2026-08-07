"""
Extração de entidades nomeadas (CPF, placas, endereços, chaves PIX, pessoas,
locais e organizações) em documentos de inquérito, usando spaCy + regex para
padrões estruturados brasileiros, e Microsoft Presidio para anonimização.

O modelo spaCy é carregado de forma lazy (sob demanda) para não pesar o
tempo de boot da API quando o endpoint de NLP não é usado.
"""
import re
from functools import lru_cache
from typing import List, Dict

from app.core.config import settings

PADRAO_CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
PADRAO_PLACA = re.compile(r"[A-Z]{3}\d[A-Z0-9]\d{2}")
PADRAO_PIX_TELEFONE = re.compile(r"\(\d{2}\)\s?\d{4,5}-?\d{4}")
PADRAO_PIX_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PADRAO_CEP = re.compile(r"\d{5}-?\d{3}")


@lru_cache(maxsize=1)
def _carregar_modelo_spacy():
    """
    Carrega o modelo spaCy em português apenas na primeira chamada e mantém
    em cache de processo. Se o modelo não estiver instalado, retorna None
    e o sistema opera apenas com os padrões regex (modo degradado).
    """
    try:
        import spacy
        return spacy.load(settings.SPACY_MODEL)
    except (ImportError, OSError):
        return None


def extrair_entidades(texto: str) -> List[Dict[str, str]]:
    """
    Extrai entidades estruturadas (regex) e entidades nomeadas (spaCy NER,
    se o modelo estiver disponível) de um texto — depoimento transcrito ou
    conteúdo extraído de PDF via OCR.
    """
    entidades = []

    for match in PADRAO_CPF.finditer(texto):
        entidades.append({"tipo": "CPF", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_PLACA.finditer(texto):
        entidades.append({"tipo": "PLACA", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_PIX_TELEFONE.finditer(texto):
        entidades.append({"tipo": "TELEFONE_PIX", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_PIX_EMAIL.finditer(texto):
        entidades.append({"tipo": "EMAIL_PIX", "valor": match.group(), "posicao": match.start()})
    for match in PADRAO_CEP.finditer(texto):
        entidades.append({"tipo": "CEP", "valor": match.group(), "posicao": match.start()})

    nlp = _carregar_modelo_spacy()
    if nlp is not None:
        doc = nlp(texto)
        mapa_labels = {"PER": "PESSOA", "LOC": "LOCAL", "ORG": "ORGANIZACAO", "GPE": "LOCAL"}
        for ent in doc.ents:
            tipo = mapa_labels.get(ent.label_, ent.label_)
            entidades.append({"tipo": tipo, "valor": ent.text, "posicao": ent.start_char})

    return sorted(entidades, key=lambda e: e["posicao"])


@lru_cache(maxsize=1)
def _carregar_presidio():
    """
    Carrega o AnalyzerEngine e AnonymizerEngine do Presidio. Retorna
    (None, None) se a biblioteca não estiver instalada — o chamador deve
    tratar esse caso como "anonimização indisponível neste ambiente".
    """
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        return AnalyzerEngine(), AnonymizerEngine()
    except ImportError:
        return None, None


def anonimizar_texto(texto: str, entidades_permitidas: List[str] | None = None) -> str:
    """
    Mascara dados pessoais sensíveis (CPF, e-mail, telefone, etc.) fora do
    escopo direto do inquérito, conforme princípio de minimização da LGPD
    (art. 6º, III). Usado antes de exibir/exportar documentos a terceiros
    ou de indexar conteúdo em sistemas de busca menos restritos.
    """
    analyzer, anonymizer = _carregar_presidio()
    if analyzer is None:
        # Modo degradado: aplica mascaramento simples via regex nos padrões
        # brasileiros já capturados por extrair_entidades.
        texto_mascarado = texto
        for match in PADRAO_CPF.finditer(texto):
            texto_mascarado = texto_mascarado.replace(match.group(), "***.***.***-**")
        for match in PADRAO_PIX_EMAIL.finditer(texto):
            texto_mascarado = texto_mascarado.replace(match.group(), "[EMAIL REDACTED]")
        return texto_mascarado

    resultados = analyzer.analyze(text=texto, language="pt", entities=entidades_permitidas)
    anonimizado = anonymizer.anonymize(text=texto, analyzer_results=resultados)
    return anonimizado.text


def sumarizar_depoimento(texto: str, max_sentencas: int = 5) -> str:
    """
    Sumarização extrativa simples baseada em posição e comprimento de frase
    (proxy leve para relevância). Para IA generativa completa (LLM),
    substituir por chamada a modelo local ou API segura respeitando LGPD
    — nunca enviar depoimentos brutos a APIs externas sem anonimização prévia.
    """
    sentencas = [s.strip() for s in texto.split(". ") if s.strip()]
    if len(sentencas) <= max_sentencas:
        return ". ".join(sentencas)

    sentencas_pontuadas = sorted(
        enumerate(sentencas), key=lambda item: len(item[1]), reverse=True
    )[:max_sentencas]
    sentencas_pontuadas.sort(key=lambda item: item[0])
    return ". ".join(s for _, s in sentencas_pontuadas)
