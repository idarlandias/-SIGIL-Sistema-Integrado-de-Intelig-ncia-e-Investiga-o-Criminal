/**
 * Serviço de cálculo de hash SHA-256 no dispositivo, ANTES de qualquer
 * envio ao backend. Este é o primeiro elo da cadeia de custódia digital
 * (etapa "reconhecimento" — Lei 13.964/19).
 */
import RNFS from 'react-native-fs';
import { sha256 } from 'react-native-crypto';
import { Buffer } from 'buffer';

export async function calcularHashArquivo(caminhoArquivo) {
  const conteudo = await lerArquivoComoBuffer(caminhoArquivo);
  const hash = sha256(conteudo).toString('hex');
  return hash;
}

async function lerArquivoComoBuffer(caminho) {
  const base64 = await RNFS.readFile(caminho, 'base64');
  return Buffer.from(base64, 'base64');
}

export async function gerarAssinaturaDispositivo(payload, chaveDispositivo) {
  /**
   * Gera HMAC-SHA256 do payload usando a chave privada do dispositivo.
   * A chave é obtida do Keychain/Keystore (ver keyStoreService.js) — nunca
   * fica em texto plano em memória por mais tempo que o necessário.
   */
  const { createHmac } = await import('react-native-crypto');
  const payloadString = typeof payload === 'string' ? payload : JSON.stringify(payload);
  const hmac = createHmac('sha256', chaveDispositivo).update(payloadString).digest('hex');
  return hmac;
}
