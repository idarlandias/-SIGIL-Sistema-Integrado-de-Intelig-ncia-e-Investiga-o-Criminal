"""
Autenticação (JWT), MFA (TOTP) e controle de acesso RBAC/ABAC.
"""
from datetime import datetime, timedelta
from typing import Optional

import pyotp
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: str, papel: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Gera JWT contendo o papel funcional do usuário (agente, investigador,
    delegado, perito, administrador) para uso em RBAC.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES))
    payload = {"sub": subject, "papel": papel, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def gerar_segredo_mfa() -> str:
    return pyotp.random_base32()


def gerar_uri_mfa(segredo: str, usuario_email: str) -> str:
    return pyotp.totp.TOTP(segredo).provisioning_uri(
        name=usuario_email, issuer_name=settings.MFA_ISSUER_NAME
    )


def validar_codigo_mfa(segredo: str, codigo: str) -> bool:
    return pyotp.TOTP(segredo).verify(codigo)


# --- RBAC: mapa de permissões por papel funcional ---
PERMISSOES_POR_PAPEL = {
    "agente": {"evidencias:criar", "evidencias:ler_propria", "custodia:ler_propria"},
    "investigador": {"evidencias:criar", "evidencias:ler", "grafo:ler", "custodia:ler", "casos:ler", "casos:editar"},
    "delegado": {"evidencias:ler", "grafo:ler", "grafo:editar", "custodia:ler", "casos:ler", "casos:editar", "casos:aprovar", "relatorios:gerar"},
    "perito": {"evidencias:ler", "evidencias:processar", "custodia:ler", "custodia:registrar_etapa"},
    "administrador": {"*"},
}


def tem_permissao(papel: str, permissao: str) -> bool:
    permissoes = PERMISSOES_POR_PAPEL.get(papel, set())
    return "*" in permissoes or permissao in permissoes
