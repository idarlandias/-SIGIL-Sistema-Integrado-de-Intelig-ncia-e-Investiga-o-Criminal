"""
Cliente de acesso ao Neo4j — camada de abstração para queries de grafo.
"""
from neo4j import GraphDatabase
from app.core.config import settings

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    return _driver


def obter_rede_suspeito(cpf: str, profundidade: int = 2):
    """
    Encontra a rede de vínculos de um indivíduo até N graus,
    ordenada por soma de confiança dos relacionamentos.
    """
    query = f"""
    MATCH (p:Pessoa {{cpf: $cpf}})-[r*1..{profundidade}]-(alvo)
    WHERE p <> alvo
    RETURN alvo, reduce(s = 0, rel IN r | s + coalesce(rel.confianca, 0.5)) AS forca_vinculo
    ORDER BY forca_vinculo DESC
    LIMIT 50
    """
    with get_driver().session() as session:
        resultado = session.run(query, cpf=cpf)
        return [dict(record) for record in resultado]


def buscar_padroes_entre_inqueritos(numero_inquerito: str):
    """
    Retorna inquéritos conectados por relacionamento PADRAO_SIMILAR
    (gerado pelo motor de busca vetorial/NLP).
    """
    query = """
    MATCH (i1:Inquerito {numero: $numero})-[r:PADRAO_SIMILAR]-(i2:Inquerito)
    RETURN i2.numero AS inquerito_relacionado, r.criterio AS criterio, r.score_similaridade AS score
    ORDER BY r.score_similaridade DESC
    """
    with get_driver().session() as session:
        resultado = session.run(query, numero=numero_inquerito)
        return [dict(record) for record in resultado]
