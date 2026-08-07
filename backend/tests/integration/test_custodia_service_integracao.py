"""
Teste de integração do custodia_service.py com banco real — valida que
registrar_evento_custodia() e obter_trilha_custodia() funcionam de fato
contra PostgreSQL, não apenas contra o comportamento assumido em mocks.
"""
import uuid
import pytest
from sqlalchemy import text

from app.services.graph.custodia_service import registrar_evento_custodia, obter_trilha_custodia
from app.models.evidencia import EtapaCustodia


@pytest.mark.integration
def test_registrar_e_consultar_trilha_completa(db_session):
    usuario_id = uuid.uuid4()
    inquerito_id = uuid.uuid4()
    evidencia_id = uuid.uuid4()
    matricula = f"MAT-{usuario_id.hex[:6]}"

    db_session.execute(
        text(
            "INSERT INTO usuarios (id, matricula, nome, email, senha_hash, papel) "
            "VALUES (:id, :matricula, 'Investigador Teste', 'inv@sigil.local', 'hash', 'investigador')"
        ),
        {"id": usuario_id, "matricula": matricula},
    )
    db_session.execute(
        text(
            "INSERT INTO inqueritos (id, numero, delegacia, data_abertura) "
            "VALUES (:id, :numero, '5a DP', CURRENT_DATE)"
        ),
        {"id": inquerito_id, "numero": f"IP-TEST-{inquerito_id.hex[:6]}"},
    )
    db_session.execute(
        text(
            "INSERT INTO evidencias (id, hash_sha256, tipo, capturado_em, capturado_por, inquerito_id) "
            "VALUES (:id, :hash, 'foto', now(), :usuario_id, :inquerito_id)"
        ),
        {"id": evidencia_id, "hash": uuid.uuid4().hex + uuid.uuid4().hex[:24], "usuario_id": usuario_id, "inquerito_id": inquerito_id},
    )
    db_session.commit()

    registrar_evento_custodia(
        db=db_session,
        evidencia_id=str(evidencia_id),
        etapa=EtapaCustodia.coleta,
        usuario=matricula,
        hash_no_momento="hash-abc",
        acao="criado",
    )
    registrar_evento_custodia(
        db=db_session,
        evidencia_id=str(evidencia_id),
        etapa=EtapaCustodia.armazenamento,
        usuario=matricula,
        hash_no_momento="hash-abc",
        acao="acessado",
    )

    trilha = obter_trilha_custodia(db_session, str(evidencia_id))

    assert len(trilha) == 2
    assert trilha[0].etapa == EtapaCustodia.coleta
    assert trilha[0].acao.value == "criado"
    assert trilha[1].etapa == EtapaCustodia.armazenamento
    assert trilha[1].acao.value == "acessado"
    assert trilha[0].usuario == matricula


@pytest.mark.integration
def test_trilha_ordenada_cronologicamente(db_session):
    usuario_id = uuid.uuid4()
    inquerito_id = uuid.uuid4()
    evidencia_id = uuid.uuid4()
    matricula = f"MAT-{usuario_id.hex[:6]}"

    db_session.execute(
        text(
            "INSERT INTO usuarios (id, matricula, nome, email, senha_hash, papel) "
            "VALUES (:id, :matricula, 'Perito Teste', 'perito@sigil.local', 'hash', 'perito')"
        ),
        {"id": usuario_id, "matricula": matricula},
    )
    db_session.execute(
        text(
            "INSERT INTO inqueritos (id, numero, delegacia, data_abertura) "
            "VALUES (:id, :numero, '5a DP', CURRENT_DATE)"
        ),
        {"id": inquerito_id, "numero": f"IP-TEST-{inquerito_id.hex[:6]}"},
    )
    db_session.execute(
        text(
            "INSERT INTO evidencias (id, hash_sha256, tipo, capturado_em, capturado_por, inquerito_id) "
            "VALUES (:id, :hash, 'audio', now(), :usuario_id, :inquerito_id)"
        ),
        {"id": evidencia_id, "hash": uuid.uuid4().hex + uuid.uuid4().hex[:24], "usuario_id": usuario_id, "inquerito_id": inquerito_id},
    )
    db_session.commit()

    etapas_em_ordem = [
        EtapaCustodia.coleta,
        EtapaCustodia.transporte,
        EtapaCustodia.recebimento,
        EtapaCustodia.processamento,
    ]
    for etapa in etapas_em_ordem:
        registrar_evento_custodia(
            db=db_session,
            evidencia_id=str(evidencia_id),
            etapa=etapa,
            usuario=matricula,
            hash_no_momento="hash-xyz",
            acao="modificado",
        )

    trilha = obter_trilha_custodia(db_session, str(evidencia_id))
    etapas_retornadas = [e.etapa for e in trilha]
    assert etapas_retornadas == etapas_em_ordem
