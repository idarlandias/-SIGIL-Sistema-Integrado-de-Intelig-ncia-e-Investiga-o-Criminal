"""
Teste de integração CRÍTICO: valida que a tabela custodia_log é
verdadeiramente append-only no PostgreSQL real — a trigger
`trg_bloquear_update_custodia` deve impedir UPDATE e DELETE, mesmo com
uma conexão de superusuário. Isso é o núcleo da garantia jurídica de
integridade exigida pela Lei 13.964/19 e não pode ser validado por mock.
"""
import uuid
import pytest
from sqlalchemy.exc import DatabaseError
from sqlalchemy import text


@pytest.mark.integration
def test_update_em_custodia_log_e_bloqueado(db_session):
    usuario_id = uuid.uuid4()
    inquerito_id = uuid.uuid4()
    evidencia_id = uuid.uuid4()
    custodia_id = uuid.uuid4()

    db_session.execute(
        text(
            "INSERT INTO usuarios (id, matricula, nome, email, senha_hash, papel) "
            "VALUES (:id, :matricula, 'Teste', 'teste@sigil.local', 'hash', 'agente')"
        ),
        {"id": usuario_id, "matricula": f"MAT-{usuario_id.hex[:6]}"},
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
            "VALUES (:id, :hash, 'documento', now(), :usuario_id, :inquerito_id)"
        ),
        {"id": evidencia_id, "hash": uuid.uuid4().hex + uuid.uuid4().hex[:24], "usuario_id": usuario_id, "inquerito_id": inquerito_id},
    )
    db_session.execute(
        text(
            "INSERT INTO custodia_log (id, evidencia_id, etapa, usuario_id, acao) "
            "VALUES (:id, :evidencia_id, 'coleta', :usuario_id, 'criado')"
        ),
        {"id": custodia_id, "evidencia_id": evidencia_id, "usuario_id": usuario_id},
    )
    db_session.commit()

    with pytest.raises(DatabaseError, match="append-only"):
        db_session.execute(
            text("UPDATE custodia_log SET acao = 'modificado' WHERE id = :id"),
            {"id": custodia_id},
        )
        db_session.commit()

    db_session.rollback()


@pytest.mark.integration
def test_delete_em_custodia_log_e_bloqueado(db_session):
    usuario_id = uuid.uuid4()
    inquerito_id = uuid.uuid4()
    evidencia_id = uuid.uuid4()
    custodia_id = uuid.uuid4()

    db_session.execute(
        text(
            "INSERT INTO usuarios (id, matricula, nome, email, senha_hash, papel) "
            "VALUES (:id, :matricula, 'Teste2', 'teste2@sigil.local', 'hash', 'agente')"
        ),
        {"id": usuario_id, "matricula": f"MAT-{usuario_id.hex[:6]}"},
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
            "VALUES (:id, :hash, 'documento', now(), :usuario_id, :inquerito_id)"
        ),
        {"id": evidencia_id, "hash": uuid.uuid4().hex + uuid.uuid4().hex[:24], "usuario_id": usuario_id, "inquerito_id": inquerito_id},
    )
    db_session.execute(
        text(
            "INSERT INTO custodia_log (id, evidencia_id, etapa, usuario_id, acao) "
            "VALUES (:id, :evidencia_id, 'coleta', :usuario_id, 'criado')"
        ),
        {"id": custodia_id, "evidencia_id": evidencia_id, "usuario_id": usuario_id},
    )
    db_session.commit()

    with pytest.raises(DatabaseError, match="append-only"):
        db_session.execute(text("DELETE FROM custodia_log WHERE id = :id"), {"id": custodia_id})
        db_session.commit()

    db_session.rollback()


@pytest.mark.integration
def test_insert_em_custodia_log_funciona_normalmente(db_session):
    """Confirma que a trigger bloqueia apenas UPDATE/DELETE, não INSERT."""
    usuario_id = uuid.uuid4()
    inquerito_id = uuid.uuid4()
    evidencia_id = uuid.uuid4()

    db_session.execute(
        text(
            "INSERT INTO usuarios (id, matricula, nome, email, senha_hash, papel) "
            "VALUES (:id, :matricula, 'Teste3', 'teste3@sigil.local', 'hash', 'agente')"
        ),
        {"id": usuario_id, "matricula": f"MAT-{usuario_id.hex[:6]}"},
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
            "VALUES (:id, :hash, 'documento', now(), :usuario_id, :inquerito_id)"
        ),
        {"id": evidencia_id, "hash": uuid.uuid4().hex + uuid.uuid4().hex[:24], "usuario_id": usuario_id, "inquerito_id": inquerito_id},
    )
    db_session.execute(
        text(
            "INSERT INTO custodia_log (evidencia_id, etapa, usuario_id, acao) "
            "VALUES (:evidencia_id, 'coleta', :usuario_id, 'criado')"
        ),
        {"evidencia_id": evidencia_id, "usuario_id": usuario_id},
    )
    db_session.commit()

    total = db_session.execute(
        text("SELECT COUNT(*) FROM custodia_log WHERE evidencia_id = :evidencia_id"),
        {"evidencia_id": evidencia_id},
    ).scalar()
    assert total == 1
