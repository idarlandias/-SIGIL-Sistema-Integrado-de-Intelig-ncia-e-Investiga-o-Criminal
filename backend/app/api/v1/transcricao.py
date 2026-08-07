"""
Endpoint de transcrição de depoimentos/escutas autorizadas via Whisper.
Protegido por RBAC: exige permissão "evidencias:processar" (perito) ou
"evidencias:criar" (agente/investigador enviando depoimento em campo).
"""
from fastapi import APIRouter, UploadFile, HTTPException, status, Depends

from app.services.nlp.transcricao_audio import transcrever_audio_bytes
from app.core.deps import exigir_permissao

router = APIRouter()


@router.post("/audio", dependencies=[Depends(exigir_permissao("evidencias:criar"))])
async def transcrever_audio_endpoint(arquivo: UploadFile, idioma: str = "pt"):
    """
    Recebe um arquivo de áudio (depoimento gravado em campo ou escuta
    autorizada) e retorna a transcrição completa com segmentos timestampados.
    """
    conteudo = await arquivo.read()
    extensao = "." + (arquivo.filename.split(".")[-1] if "." in arquivo.filename else "mp3")

    try:
        resultado = transcrever_audio_bytes(conteudo, extensao=extensao, idioma=idioma)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    return resultado
