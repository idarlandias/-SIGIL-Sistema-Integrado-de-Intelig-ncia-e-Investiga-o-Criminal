"""
Endpoint GEOINT: retorna pontos geograficos (lat/lon) das evidencias de um
inquerito, ou de todos os inqueritos de uma delegacia, para renderizacao
de heatmap de manchas criminais e rotas de fuga no painel web.
Protegido por RBAC: exige permissao "evidencias:ler".
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Evidencia, Inquerito
from app.core.deps import exigir_permissao

router = APIRouter()


@router.get("/pontos", dependencies=[Depends(exigir_permissao("evidencias:ler"))])
async def listar_pontos_geograficos(
    inquerito_numero: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Retorna as coordenadas GPS de evidencias que possuem geolocalizacao,
    opcionalmente filtradas por inquerito. Cada ponto inclui tipo de
    evidencia e timestamp - insumo direto para o heatmap de manchas
    criminais e para a reconstrucao de rotas de fuga no painel web.
    """
    query = db.query(Evidencia).filter(
        Evidencia.gps_lat.isnot(None), Evidencia.gps_lon.isnot(None)
    )

    if inquerito_numero:
        inquerito = db.query(Inquerito).filter(Inquerito.numero == inquerito_numero).first()
        if not inquerito:
            return {"pontos": []}
        query = query.filter(Evidencia.inquerito_id == inquerito.id)

    evidencias = query.all()

    return {
        "pontos": [
            {
                "lat": e.gps_lat,
                "lon": e.gps_lon,
                "tipo": e.tipo,
                "capturado_em": e.capturado_em,
                "evidencia_id": str(e.id),
            }
            for e in evidencias
        ]
    }
