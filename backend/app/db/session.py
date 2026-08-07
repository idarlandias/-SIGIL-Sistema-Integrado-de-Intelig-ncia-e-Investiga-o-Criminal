"""
Gestão de conexão e sessão com PostgreSQL via SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

engine = create_engine(settings.postgres_dsn, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Session:
    """Dependency do FastAPI: fornece uma sessão de banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
