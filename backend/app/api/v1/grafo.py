"""
Endpoints de análise de vínculos (grafo de inteligência) via Neo4j.
Protegidos por RBAC: exigem permissão "grafo:ler".
"""
from fastapi import APIRouter, Query, Depends

from app.services.graph.neo4j_client import obter_rede_suspeito, buscar_padroes_entre_inqueritos
from app.core.deps import exigir_permissao

router = APIRouter()


@router.get("/pessoa/{cpf}/rede", dependencies=[Depends(exigir_permissao("grafo:ler"))])
async def rede_do_suspeito(cpf: str, profundidade: int = Query(2, ge=1, le=3)):
    """
    Retorna a rede de vínculos de um indivíduo até N graus de separação,
    ordenada por força/confiança do vínculo (estilo IBM i2 / Palantir Gotham).
    """
    return obter_rede_suspeito(cpf, profundidade)


@router.get("/inqueritos/padroes", dependencies=[Depends(exigir_permissao("grafo:ler"))])
async def padroes_entre_inqueritos(numero_inquerito: str):
    """
    Cruza o inquérito informado com a base histórica para identificar
    padrões similares (mesmo modus operandi, contas em comum, etc.).
    """
    return buscar_padroes_entre_inqueritos(numero_inquerito)
