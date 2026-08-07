"""
Modelos ORM (SQLAlchemy) — espelham o schema em db/postgres/migrations/001_init.sql.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Date, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matricula = Column(String(20), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    papel = Column(String(30), nullable=False)  # agente, investigador, delegado, perito, administrador
    mfa_secret = Column(String(64), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)


class Inquerito(Base):
    __tablename__ = "inqueritos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero = Column(String(30), unique=True, nullable=False)
    delegacia = Column(String(100), nullable=False)
    status = Column(String(30), default="em_andamento")
    data_abertura = Column(Date, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    evidencias = relationship("Evidencia", back_populates="inquerito")


class Evidencia(Base):
    __tablename__ = "evidencias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash_sha256 = Column(String(64), unique=True, nullable=False)
    tipo = Column(String(30), nullable=False)
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    capturado_em = Column(DateTime, nullable=False)
    capturado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    inquerito_id = Column(UUID(as_uuid=True), ForeignKey("inqueritos.id"), nullable=True)
    caminho_storage = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    inquerito = relationship("Inquerito", back_populates="evidencias")
    eventos_custodia = relationship("CustodiaLog", back_populates="evidencia")


class CustodiaLog(Base):
    """
    Tabela append-only: a trigger `trg_bloquear_update_custodia` no banco
    impede UPDATE/DELETE, mesmo que este ORM tente executá-los.
    """
    __tablename__ = "custodia_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidencia_id = Column(UUID(as_uuid=True), ForeignKey("evidencias.id"), nullable=False)
    etapa = Column(String(30), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    acao = Column(String(20), nullable=False)
    hash_no_momento = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    evidencia = relationship("Evidencia", back_populates="eventos_custodia")
