"""
Serviço de registro e consulta da cadeia de custódia digital.
Cada evento é imutável (append-only) — nunca se edita ou apaga um registro
já gravado, apenas se adicionam novos eventos.
"""
from datetime import datetime
from typing import List

from app.models.evidencia import EventoCustodia, EtapaCustodia

# NOTA: implementação de referência em memória.
# Em produção, gravar em tabela Postgres append-only (sem UPDATE/DELETE)
# e espelhar em log estruturado enviado ao SIEM.
_LOG_CUSTODIA: dict[str, List[EventoCustodia]] = {}


def registrar_evento_custodia(
    evidencia_id: str,
    etapa: EtapaCustodia,
    usuario: str,
    hash_no_momento: str,
    acao: str,
) -> EventoCustodia:
    evento = EventoCustodia(
        etapa=etapa,
        usuario=usuario,
        timestamp=datetime.utcnow(),
        hash_no_momento=hash_no_momento,
        acao=acao,
    )
    _LOG_CUSTODIA.setdefault(evidencia_id, []).append(evento)
    return evento


def obter_trilha_custodia(evidencia_id: str) -> List[EventoCustodia]:
    return _LOG_CUSTODIA.get(evidencia_id, [])
