"""
Fixtures de integração: sobe um PostgreSQL real via testcontainers,
aplica o schema oficial (db/postgres/migrations/001_init.sql) — incluindo
a trigger que bloqueia UPDATE/DELETE em custodia_log — e fornece uma
sessão SQLAlchemy real para os testes.

Marcados com @pytest.mark.integration; rodam em job separado no CI que
tem Docker disponível (ver .github/workflows/ci.yml).

IMPORTANTE: a importação de `testcontainers` é feita dentro da fixture,
não no topo do módulo — assim o job de testes unitários (que não instala
requirements-test.txt) consegue coletar este arquivo sem ImportError,
mesmo sem rodar os testes de integração de fato.

IMPORTANTE 2: a migration SQL é executada de UMA VEZ via cursor DBAPI
puro, e não dividida por ";" — a função PL/pgSQL usa dollar-quoting
($$ ... $$) que contém ";" internamente (ex.: `RAISE EXCEPTION '...';`).
Dividir o texto por ";" corta esse bloco no meio e gera
"unterminated dollar-quoted string". O driver psycopg2 já sabe
interpretar múltiplos statements com dollar-quoting corretamente quando
recebe o SQL completo.
"""
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

MIGRATION_PATH = Path(__file__).resolve().parents[3] / "db" / "postgres" / "migrations" / "001_init.sql"


@pytest.fixture(scope="session")
def postgres_container():
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url, pool_pre_ping=True)

    sql_migration = MIGRATION_PATH.read_text(encoding="utf-8")

    raw_conn = engine.raw_connection()
    try:
        cursor = raw_conn.cursor()
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
        # Envia o arquivo de migration inteiro em uma única chamada —
        # psycopg2/libpq processam corretamente múltiplos statements com
        # dollar-quoting quando o SQL não é pré-dividido por nós.
        cursor.execute(sql_migration)
        raw_conn.commit()
        cursor.close()
    finally:
        raw_conn.close()

    return engine


@pytest.fixture()
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
