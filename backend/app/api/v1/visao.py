"""
Endpoints de visão computacional: leitura de placas (ALPR), OCR de
documentos escaneados, e extração de metadados EXIF/GEOINT. Protegidos
por RBAC: exigem permissão "evidencias:processar".
"""
import tempfile

from fastapi import APIRouter, UploadFile, Depends

from app.services.vision.alpr_service import processar_frame_alpr, extrair_metadados_exif
from app.services.vision.ocr_service import extrair_texto_bytes
from app.services.nlp.extracao_entidades import extrair_entidades
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


@router.post("/ocr", dependencies=[Depends(exigir_permissao("evidencias:processar"))])
async def extrair_texto_documento(arquivo: UploadFile, extrair_entidades_automaticamente: bool = True):
    """
    Executa OCR (PaddleOCR/Tesseract) sobre um documento escaneado ou
    imagem fotografada, e opcionalmente já extrai entidades estruturadas
    (CPF, placas, etc.) do texto reconhecido em uma única chamada.
    """
    conteudo = await arquivo.read()
    extensao = "." + (arquivo.filename.split(".")[-1] if arquivo.filename and "." in arquivo.filename else "jpg")

    texto = extrair_texto_bytes(conteudo, extensao=extensao)

    resposta = {"texto_extraido": texto}
    if extrair_entidades_automaticamente:
        resposta["entidades"] = extrair_entidades(texto)

    return resposta
