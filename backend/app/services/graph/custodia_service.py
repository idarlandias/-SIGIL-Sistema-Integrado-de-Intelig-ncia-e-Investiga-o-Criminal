"""
Servico de registro e consulta da cadeia de custodia digital.
Persistencia real em PostgreSQL, na tabela `custodia_log` - que e
append-only por trigger de banco (trg_bloquear_update_custodia), garantindo
que nenhuma modificacao seja possivel mesmo com acesso direto ao banco.

Cada evento tambem e espelhado no SIEM (Wazuh) para correlacao de
anomalias - ver app/services/siem/wazuh_client.py.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.evidencia import EventoCustodia, EtapaCustodia, AcaoAuditoria
from app.db.models import CustodiaLog, Usuario, Evidencia
from app.services.siem.wazuh_client import registrar_evento_custodia_siem


def registrar_evento_custodia(
    db: Session,
    evidencia_id: str,
    etapa: EtapaCustodia,
    usuario: str,
    hash_no_momento: str,
    acao: str,
) -> EventoCustodia:
    """
    Grava um novo evento na cadeia de custodia. Nunca faz UPDATE/DELETE -
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

    registrar_evento_custodia_siem(
        evidencia_id=evidencia_id,
        etapa=registro.etapa,
        usuario=usuario,
        acao=acao,
    )

    return EventoCustodia(
        etapa=EtapaCustodia(registro.etapa),
        usuario=usuario,
        timestamp=registro.timestamp,
        hash_no_momento=registro.hash_no_momento or "",
        acao=AcaoAuditoria(registro.acao),
    )


def obter_trilha_custodia(db: Session, evidencia_id: str) -> List[EventoCustodia]:
    """
    Retorna a trilha cronologica completa de eventos de uma evidencia,
    ordenada por timestamp - a sequencia exata exigida em juizo para
    comprovar a integridade da cadeia de custodia.
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
