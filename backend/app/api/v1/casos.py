"""
Endpoints de gestão de casos/inquéritos policiais — persistência real via PostgreSQL.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Inquerito

router = APIRouter()


@router.get("")
async def listar_casos(db: Session = Depends(get_db), status_filtro: str | None = None, delegacia: str | None = None):
    query = db.query(Inquerito)
    if status_filtro:
        query = query.filter(Inquerito.status == status_filtro)
    if delegacia:
        query = query.filter(Inquerito.delegacia == delegacia)

    inqueritos = query.order_by(Inquerito.data_abertura.desc()).all()
    return {
        "casos": [
            {
                "numero": i.numero,
                "delegacia": i.delegacia,
                "status": i.status,
                "data_abertura": i.data_abertura,
            }
            for i in inqueritos
        ]
    }


@router.get("/{numero}")
async def obter_caso(numero: str, db: Session = Depends(get_db)):
    inquerito = db.query(Inquerito).filter(Inquerito.numero == numero).first()
    if not inquerito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inquérito {numero} não encontrado.")

    return {
        "numero": inquerito.numero,
        "delegacia": inquerito.delegacia,
        "status": inquerito.status,
        "data_abertura": inquerito.data_abertura,
        "total_evidencias": len(inquerito.evidencias),
    }
