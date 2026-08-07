"""
Cliente de integração com SpiderFoot (OSINT automation) via sua API REST.
https://github.com/smicallef/spiderfoot
"""
import httpx
from typing import Dict


SPIDERFOOT_BASE_URL = "http://localhost:5001"  # ajustar via settings em produção


async def disparar_scan_osint(alvo: str, modulos: list[str] | None = None) -> Dict:
    """
    Dispara um scan OSINT no SpiderFoot para o alvo informado (nome, e-mail,
    domínio, telefone) e retorna o ID do scan para consulta posterior.
    """
    payload = {"scanname": f"sigil_{alvo}", "scantarget": alvo, "modulelist": modulos or []}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{SPIDERFOOT_BASE_URL}/startscan", data=payload)
        resp.raise_for_status()
        return resp.json()


async def consultar_resultado_scan(scan_id: str) -> Dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{SPIDERFOOT_BASE_URL}/scanresults", params={"id": scan_id})
        resp.raise_for_status()
        return resp.json()
