"""
Endpoints de gestão de casos/inquéritos policiais.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def listar_casos():
    # TODO: implementar listagem paginada com filtros por status/delegacia
    return {"casos": []}


@router.get("/{numero}")
async def obter_caso(numero: str):
    # TODO: implementar busca real no Postgres
    return {"numero": numero, "status": "implementar"}
