"""
Dependencias FastAPI para autenticacao JWT e controle de acesso RBAC.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, tem_permissao
from app.db.session import get_db
from app.db.models import Usuario
from app.services.siem.wazuh_client import registrar_acesso_negado_siem

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """
    Decodifica o JWT, valida e retorna o usuario autenticado.
    Levanta 401 se o token for invalido/expirado ou o usuario estiver inativo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas ou expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        matricula: str = payload.get("sub")
        if matricula is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.query(Usuario).filter(Usuario.matricula == matricula).first()
    if usuario is None or not usuario.ativo:
        raise credentials_exception
    return usuario


def exigir_permissao(permissao: str):
    """
    Factory de dependencia: garante que o usuario autenticado tenha a
    permissao exigida pelo endpoint, de acordo com PERMISSOES_POR_PAPEL.
    Tentativas negadas sao espelhadas no SIEM - um padrao de multiplas
    negacoes do mesmo usuario pode indicar tentativa de escalonamento
    de privilegio (ver docs/RIPD.md, risco R-06).
    Uso: @router.get(..., dependencies=[Depends(exigir_permissao("grafo:ler"))])
    """
    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if not tem_permissao(usuario.papel, permissao):
            registrar_acesso_negado_siem(
                usuario=usuario.matricula, permissao_exigida=permissao, papel=usuario.papel
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Papel '{usuario.papel}' nao tem permissao '{permissao}'.",
            )
        return usuario
    return verificador
