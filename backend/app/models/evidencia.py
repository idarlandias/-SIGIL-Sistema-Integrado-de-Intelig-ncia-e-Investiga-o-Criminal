"""
Modelos Pydantic relacionados a evidências e cadeia de custódia.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TipoEvidencia(str, Enum):
    foto = "foto"
    audio = "audio"
    video = "video"
    documento = "documento"
    depoimento_texto = "depoimento_texto"


class EtapaCustodia(str, Enum):
    reconhecimento = "reconhecimento"
    isolamento = "isolamento"
    fixacao = "fixacao"
    coleta = "coleta"
    acondicionamento = "acondicionamento"
    transporte = "transporte"
    recebimento = "recebimento"
    processamento = "processamento"
    armazenamento = "armazenamento"
    descarte = "descarte"


class AcaoAuditoria(str, Enum):
    criado = "criado"
    acessado = "acessado"
    modificado = "modificado"
    exportado = "exportado"


class EvidenciaCreate(BaseModel):
    hash_sha256_cliente: str = Field(..., description="Hash calculado no dispositivo antes do envio")
    tipo: TipoEvidencia
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    capturado_em: datetime
    agente_matricula: str
    inquerito_numero: str
    assinatura_dispositivo: str = Field(..., description="HMAC do payload gerado com chave do dispositivo")


class EvidenciaResponse(BaseModel):
    evidencia_id: str
    hash_confirmado: bool
    etapa_custodia: EtapaCustodia


class EventoCustodia(BaseModel):
    etapa: EtapaCustodia
    usuario: str
    timestamp: datetime
    hash_no_momento: str
    acao: AcaoAuditoria
