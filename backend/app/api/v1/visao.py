"""
Endpoints de visão computacional: leitura de placas (ALPR) em imagens de
câmeras de segurança e extração de metadados EXIF/GEOINT. Protegidos por
RBAC: exigem permissão "evidencias:processar".
"""
import tempfile

from fastapi import APIRouter, UploadFile, Depends

from app.services.vision.alpr_service import processar_frame_alpr, extrair_metadados_exif
from app.core.deps import exigir_permissao

router = APIRouter()


@router.post("/alpr", dependencies=[Depends(exigir_permissao("evidencias:processar"))])
async def ler_placas(arquivo: UploadFile):
    """
    Recebe um frame de imagem (extraído de vídeo de câmera de segurança)
    e retorna as placas detectadas com score de confiança.
    """
    conteudo = await arquivo.read()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(conteudo)
        tmp.flush()
        placas = processar_frame_alpr(tmp.name)

    return {"placas_detectadas": placas}


@router.post("/exif", dependencies=[Depends(exigir_permissao("evidencias:processar"))])
async def extrair_exif(arquivo: UploadFile):
    """
    Extrai metadados EXIF (geolocalização, data/hora, dispositivo) de uma
    imagem enviada por câmera/celular — útil para GEOINT e correlação de
    rota de fuga com evidências fotográficas de terceiros.
    """
    conteudo = await arquivo.read()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
        tmp.write(conteudo)
        tmp.flush()
        metadados = extrair_metadados_exif(tmp.name)

    return {"metadados_exif": metadados}
