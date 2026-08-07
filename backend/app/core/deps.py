"""
Dependências FastAPI para autenticação JWT e controle de acesso RBAC.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, tem_permissao
from app.db.session import get_db
from app.db.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """
    Decodifica o JWT, valida e retorna o usuário autenticado.
    Levanta 401 se o token for inválido/expirado ou o usuário estiver inativo.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas.",
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
    Factory de dependência: garante que o usuário autenticado tenha a
    permissão exigida pelo endpoint, de acordo com PERMISSOES_POR_PAPEL.
    Uso: @router.get(..., dependencies=[Depends(exigir_permissao("grafo:ler"))])
    """
    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if not tem_permissao(usuario.papel, permissao):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Papel '{usuario.papel}' não tem permissão '{permissao}'.",
            )
        return usuario
    return verificador
