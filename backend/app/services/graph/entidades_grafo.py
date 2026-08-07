"""
Persistência de entidades extraídas via NLP (CPF, placas, pessoas, locais,
organizações) como nós e relacionamentos no grafo Neo4j, vinculando-as ao
documento/evidência de origem — fecha o ciclo entre o pipeline de IA e a
análise de vínculos.
"""
from datetime import datetime
from typing import List, Dict

from app.services.graph.neo4j_client import get_driver


_MERGE_POR_TIPO = {
    "CPF": """
        MERGE (p:Pessoa {cpf: $valor})
        ON CREATE SET p.criado_em = datetime(), p.nivel_risco = 'nao_avaliado'
        WITH p
        MATCH (e:Evidencia {hash_sha256: $hash_evidencia})
        MERGE (p)-[r:MENCIONADO_EM]->(e)
        ON CREATE SET r.metodo_extracao = $metodo, r.confianca = $confianca, r.registrado_em = datetime()
    """,
    "PLACA": """
        MERGE (v:Veiculo {placa: $valor})
        WITH v
        MATCH (e:Evidencia {hash_sha256: $hash_evidencia})
        MERGE (v)-[r:DETECTADO_EM]->(e)
        ON CREATE SET r.metodo_extracao = $metodo, r.confianca = $confianca, r.registrado_em = datetime()
    """,
    "PESSOA": """
        MERGE (p:PessoaMencionada {nome: $valor})
        ON CREATE SET p.criado_em = datetime()
        WITH p
        MATCH (e:Evidencia {hash_sha256: $hash_evidencia})
        MERGE (p)-[r:MENCIONADO_EM]->(e)
        ON CREATE SET r.metodo_extracao = $metodo, r.confianca = $confianca, r.registrado_em = datetime()
    """,
    "LOCAL": """
        MERGE (l:Local {nome: $valor})
        WITH l
        MATCH (e:Evidencia {hash_sha256: $hash_evidencia})
        MERGE (l)-[r:MENCIONADO_EM]->(e)
        ON CREATE SET r.metodo_extracao = $metodo, r.confianca = $confianca, r.registrado_em = datetime()
    """,
    "ORGANIZACAO": """
        MERGE (o:Organizacao {nome: $valor})
        WITH o
        MATCH (e:Evidencia {hash_sha256: $hash_evidencia})
        MERGE (o)-[r:MENCIONADO_EM]->(e)
        ON CREATE SET r.metodo_extracao = $metodo, r.confianca = $confianca, r.registrado_em = datetime()
    """,
}

_METODO_POR_TIPO = {
    "CPF": "regex_cpf",
    "PLACA": "regex_placa",
    "PESSOA": "spacy_ner",
    "LOCAL": "spacy_ner",
    "ORGANIZACAO": "spacy_ner",
}

_CONFIANCA_POR_METODO = {
    "regex_cpf": 0.95,
    "regex_placa": 0.9,
    "spacy_ner": 0.75,
}


def garantir_nodo_evidencia(hash_evidencia: str, tipo: str) -> None:
    """
    Cria o nó :Evidencia no Neo4j caso ainda não exista (idempotente via
    MERGE). A evidência "canônica" vive no Postgres; este nó é uma
    referência leve para permitir vínculos no grafo de inteligência.
    """
    query = """
        MERGE (e:Evidencia {hash_sha256: $hash_evidencia})
        ON CREATE SET e.tipo = $tipo, e.capturado_em = datetime()
    """
    with get_driver().session() as session:
        session.run(query, hash_evidencia=hash_evidencia, tipo=tipo)


def persistir_entidades_no_grafo(entidades: List[Dict], hash_evidencia: str, tipo_evidencia: str = "documento") -> Dict[str, int]:
    """
    Recebe a lista de entidades retornada por `extrair_entidades()` e cria
    os nós/relacionamentos correspondentes no Neo4j, vinculando cada um à
    evidência de origem (via hash SHA-256, que já é único no grafo).

    Retorna um resumo de quantas entidades de cada tipo foram persistidas,
    útil para logging e para o painel exibir o que o pipeline extraiu.
    """
    if not entidades:
        return {}

    garantir_nodo_evidencia(hash_evidencia, tipo_evidencia)

    resumo: Dict[str, int] = {}

    with get_driver().session() as session:
        for entidade in entidades:
            tipo = entidade.get("tipo")
            query = _MERGE_POR_TIPO.get(tipo)
            if query is None:
                # Tipos não mapeados (EMAIL_PIX, TELEFONE_PIX, CEP) ainda não
                # têm um label de nó definido no schema — ignorados por ora.
                continue

            metodo = _METODO_POR_TIPO.get(tipo, "desconhecido")
            confianca = _CONFIANCA_POR_METODO.get(metodo, 0.5)

            session.run(
                query,
                valor=entidade["valor"],
                hash_evidencia=hash_evidencia,
                metodo=metodo,
                confianca=confianca,
            )
            resumo[tipo] = resumo.get(tipo, 0) + 1

    return resumo
