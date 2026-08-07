"""
Endpoints de autenticacao: login (com MFA obrigatorio), refresh token e
configuracao de MFA para novos usuarios.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    gerar_segredo_mfa,
    gerar_uri_mfa,
    validar_codigo_mfa,
)
from app.core.deps import get_current_user
from app.db.session import get_db
from app.db.models import Usuario
from app.services.siem.wazuh_client import registrar_evento_autenticacao_siem

router = APIRouter()


class LoginComMFARequest(BaseModel):
    matricula: str
    senha: str
    codigo_mfa: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MfaSetupResponse(BaseModel):
    segredo: str
    uri_provisionamento: str


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginComMFARequest, db: Session = Depends(get_db)):
    """
    Login com MFA obrigatorio: senha + codigo TOTP de 6 digitos.
    Sem os dois fatores, o acesso e negado - nao ha bypass de MFA.
    Cada tentativa (sucesso ou falha) e registrada no SIEM para deteccao
    de forca bruta ou comprometimento de credenciais.
    """
    usuario = db.query(Usuario).filter(Usuario.matricula == payload.matricula).first()
    erro_generico = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Matricula, senha ou codigo MFA invalidos."
    )

    if not usuario or not usuario.ativo:
        registrar_evento_autenticacao_siem(payload.matricula, "falha_senha", motivo="usuario_inexistente_ou_inativo")
        raise erro_generico
    if not verify_password(payload.senha, usuario.senha_hash):
        registrar_evento_autenticacao_siem(payload.matricula, "falha_senha")
        raise erro_generico
    if not usuario.mfa_secret:
        registrar_evento_autenticacao_siem(payload.matricula, "mfa_nao_configurado")
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="MFA nao configurado para este usuario. Chame /v1/auth/mfa/setup primeiro.",
        )
    if not validar_codigo_mfa(usuario.mfa_secret, payload.codigo_mfa):
        registrar_evento_autenticacao_siem(payload.matricula, "falha_mfa")
        raise erro_generico

    registrar_evento_autenticacao_siem(payload.matricula, "sucesso")

    access_token = create_access_token(subject=usuario.matricula, papel=usuario.papel)
    refresh_token = create_access_token(
        subject=usuario.matricula, papel=usuario.papel, expires_delta=timedelta(days=7)
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    """
    Emite um novo access token a partir de um refresh token valido,
    sem exigir novo MFA (o refresh token ja prova posse continua da sessao).
    """
    try:
        payload = decode_access_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalido ou expirado.")

    usuario = db.query(Usuario).filter(Usuario.matricula == payload.get("sub")).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido ou inativo.")

    novo_access = create_access_token(subject=usuario.matricula, papel=usuario.papel)
    novo_refresh = create_access_token(
        subject=usuario.matricula, papel=usuario.papel, expires_delta=timedelta(days=7)
    )
    return TokenResponse(access_token=novo_access, refresh_token=novo_refresh)


@router.post("/mfa/setup", response_model=MfaSetupResponse)
async def configurar_mfa(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Gera um novo segredo TOTP para o usuario autenticado e retorna a URI
    de provisionamento (para exibir como QR code em app tipo Google Authenticator).
    Sobrescreve qualquer segredo MFA anterior.
    """
    segredo = gerar_segredo_mfa()
    usuario.mfa_secret = segredo
    db.add(usuario)
    db.commit()

    uri = gerar_uri_mfa(segredo, usuario.email)
    return MfaSetupResponse(segredo=segredo, uri_provisionamento=uri)
