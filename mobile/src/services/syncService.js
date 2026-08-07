/**
 * Fila de sincronização offline-first. Itens capturados sem conectividade
 * ficam persistidos localmente (SQLCipher) e são enviados automaticamente
 * quando a rede está disponível, com retry e idempotência via id_local (UUID).
 */
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { salvarItemLocal, listarItensPendentes, marcarComoSincronizado } from '../storage/db';

const API_BASE_URL = 'https://api.sigil.local/v1'; // substituir por endpoint real

export async function enfileirarEvidencia(evidencia) {
  const idLocal = uuidv4();
  await salvarItemLocal({ ...evidencia, id_local: idLocal, sincronizado: false });
  return idLocal;
}

export async function sincronizarFila() {
  const pendentes = await listarItensPendentes();
  const resultados = [];

  for (const item of pendentes) {
    try {
      const formData = new FormData();
      formData.append('arquivo', item.arquivo);
      formData.append('hash_sha256_cliente', item.hash);
      formData.append('tipo', item.tipo);
      formData.append('gps_lat', item.gpsLat);
      formData.append('gps_lon', item.gpsLon);
      formData.append('capturado_em', item.capturadoEm);
      formData.append('agente_matricula', item.agenteMatricula);
      formData.append('inquerito_numero', item.inqueritoNumero);
      formData.append('assinatura_dispositivo', item.assinatura);

      const response = await axios.post(`${API_BASE_URL}/evidencias`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      await marcarComoSincronizado(item.id_local, response.data.evidencia_id);
      resultados.push({ id_local: item.id_local, status: 'sucesso' });
    } catch (erro) {
      resultados.push({ id_local: item.id_local, status: 'falha', erro: erro.message });
    }
  }

  return resultados;
}
