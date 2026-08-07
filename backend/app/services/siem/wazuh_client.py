"""
Cliente de envio de eventos de seguranca/auditoria ao SIEM (Wazuh) via
syslog UDP. Cobre os dois tipos de evento mais criticos para deteccao de
anomalias: (1) eventos da cadeia de custodia - acesso, modificacao e
exportacao de evidencias - e (2) eventos de autenticacao - login
bem-sucedido, falha de MFA, acesso negado por RBAC.

Falhas no envio ao SIEM NUNCA devem impedir a operacao principal do
sistema (registrar evidencia, autenticar usuario) - o SIEM e observador,
nao bloqueador. Por isso todo envio e best-effort com timeout curto.
"""
import json
import logging
import socket
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("sigil.siem")

_TIMEOUT_SEGUNDOS = 1.0


def _enviar_evento_syslog(evento: dict) -> None:
    """
    Envia um evento estruturado (JSON) via syslog UDP ao Wazuh Manager.
    Best-effort: qualquer falha e logada localmente e silenciada - nunca
    propaga excecao que interrompa o fluxo principal da aplicacao.
    """
    try:
        mensagem = json.dumps(evento, default=str).encode("utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(_TIMEOUT_SEGUNDOS)
        sock.sendto(mensagem, (settings.SIEM_HOST, settings.SIEM_SYSLOG_PORT))
        sock.close()
    except Exception as e:
        logger.warning("Falha ao enviar evento ao SIEM (nao bloqueante): %s", e)


def registrar_evento_custodia_siem(
    evidencia_id: str,
    etapa: str,
    usuario: str,
    acao: str,
) -> None:
    """
    Espelha no SIEM cada evento ja persistido na tabela append-only
    `custodia_log`, permitindo correlacao de anomalias (ex.: mesmo
    usuario acessando um volume incomum de evidencias em curto espaco
    de tempo - indicio de exfiltracao de dados).
    """
    evento = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sigil_event_type": "custodia",
        "evidencia_id": evidencia_id,
        "etapa": etapa,
        "usuario": usuario,
        "acao": acao,
    }
    _enviar_evento_syslog(evento)


def registrar_evento_autenticacao_siem(
    usuario: str,
    resultado: str,
    motivo: Optional[str] = None,
    ip_origem: Optional[str] = None,
) -> None:
    """
    Registra tentativas de autenticacao (sucesso/falha de senha/falha de
    MFA) no SIEM - essencial para detectar tentativas de forca bruta ou
    comprometimento de credenciais (risco R-02 do RIPD, docs/RIPD.md).
    """
    evento = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sigil_event_type": "autenticacao",
        "usuario": usuario,
        "resultado": resultado,  # "sucesso", "falha_senha", "falha_mfa", "mfa_nao_configurado"
        "motivo": motivo,
        "ip_origem": ip_origem,
    }
    _enviar_evento_syslog(evento)


def registrar_acesso_negado_siem(usuario: str, permissao_exigida: str, papel: str) -> None:
    """
    Registra tentativas de acesso bloqueadas por RBAC - um padrao de
    multiplas tentativas negadas do mesmo usuario pode indicar tentativa
    de escalonamento de privilegio ou uso indevido de credenciais.
    """
    evento = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sigil_event_type": "acesso_negado",
        "usuario": usuario,
        "permissao_exigida": permissao_exigida,
        "papel_atual": papel,
    }
    _enviar_evento_syslog(evento)
