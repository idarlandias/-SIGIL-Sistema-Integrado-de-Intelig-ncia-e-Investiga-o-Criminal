"""
Serviço de registro e consulta da cadeia de custódia digital.
Persistência real em PostgreSQL, na tabela `custodia_log` — que é
append-only por trigger de banco (trg_bloquear_update_custodia), garantindo
que nenhuma modificação seja possível mesmo com acesso direto ao banco.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.evidencia import EventoCustodia, EtapaCustodia, AcaoAuditoria
from app.db.models import CustodiaLog, Usuario, Evidencia


def registrar_evento_custodia(
    db: Session,
    evidencia_id: str,
    etapa: EtapaCustodia,
    usuario: str,
    hash_no_momento: str,
    acao: str,
) -> EventoCustodia:
    """
    Grava um novo evento na cadeia de custódia. Nunca faz UPDATE/DELETE —
    apenas INSERT, respeitando a trilha de auditoria exigida pela
    Lei 13.964/19 (arts. 158-A a 158-F do CPP).
    """
    usuario_obj = db.query(Usuario).filter(Usuario.matricula == usuario).first()

    registro = CustodiaLog(
        evidencia_id=evidencia_id,
        etapa=etapa.value if isinstance(etapa, EtapaCustodia) else etapa,
        usuario_id=usuario_obj.id if usuario_obj else None,
        acao=acao,
        hash_no_momento=hash_no_momento,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)

    return EventoCustodia(
        etapa=EtapaCustodia(registro.etapa),
        usuario=usuario,
        timestamp=registro.timestamp,
        hash_no_momento=registro.hash_no_momento or "",
        acao=AcaoAuditoria(registro.acao),
    )


def obter_trilha_custodia(db: Session, evidencia_id: str) -> List[EventoCustodia]:
    """
    Retorna a trilha cronológica completa de eventos de uma evidência,
    ordenada por timestamp — a sequência exata exigida em juízo para
    comprovar a integridade da cadeia de custódia.
    """
    registros = (
        db.query(CustodiaLog)
        .filter(CustodiaLog.evidencia_id == evidencia_id)
        .order_by(CustodiaLog.timestamp.asc())
        .all()
    )

    resultado = []
    for r in registros:
        usuario_matricula = r.usuario.matricula if r.usuario else "desconhecido"
        resultado.append(
            EventoCustodia(
                etapa=EtapaCustodia(r.etapa),
                usuario=usuario_matricula,
                timestamp=r.timestamp,
                hash_no_momento=r.hash_no_momento or "",
                acao=AcaoAuditoria(r.acao),
            )
        )
    return resultado
