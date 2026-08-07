"""
Endpoint de consulta da trilha de auditoria (cadeia de custódia) de uma evidência.
Protegido por RBAC: exige permissão "custodia:ler". Persistência real via
tabela append-only `custodia_log` no PostgreSQL.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.evidencia import EventoCustodia
from app.services.graph.custodia_service import obter_trilha_custodia
from app.core.deps import exigir_permissao
from app.db.session import get_db

router = APIRouter()


@router.get(
    "/{evidencia_id}",
    response_model=List[EventoCustodia],
    dependencies=[Depends(exigir_permissao("custodia:ler"))],
)
async def consultar_custodia(evidencia_id: str, db: Session = Depends(get_db)):
    """
    Retorna a lista cronológica de eventos de custódia de uma evidência,
    conforme as dez etapas previstas nos arts. 158-A a 158-F do CPP.
    """
    return obter_trilha_custodia(db, evidencia_id)
