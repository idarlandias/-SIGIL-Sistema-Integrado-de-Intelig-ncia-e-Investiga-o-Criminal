"""
Endpoint de consulta da trilha de auditoria (cadeia de custódia) de uma evidência.
"""
from typing import List
from fastapi import APIRouter

from app.models.evidencia import EventoCustodia
from app.services.graph.custodia_service import obter_trilha_custodia

router = APIRouter()


@router.get("/{evidencia_id}", response_model=List[EventoCustodia])
async def consultar_custodia(evidencia_id: str):
    """
    Retorna a lista cronológica de eventos de custódia de uma evidência,
    conforme as dez etapas previstas nos arts. 158-A a 158-F do CPP.
    """
    return obter_trilha_custodia(evidencia_id)
