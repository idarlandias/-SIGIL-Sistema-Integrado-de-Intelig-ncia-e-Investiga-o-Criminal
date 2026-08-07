/**
 * Serviço de cálculo de hash SHA-256 no dispositivo, ANTES de qualquer
 * envio ao backend. Este é o primeiro elo da cadeia de custódia digital
 * (etapa "reconhecimento" — Lei 13.964/19).
 */
import { sha256 } from 'react-native-crypto';

export async function calcularHashArquivo(caminhoArquivo) {
  const conteudo = await lerArquivoComoBuffer(caminhoArquivo);
  const hash = sha256(conteudo).toString('hex');
  return hash;
}

async function lerArquivoComoBuffer(caminho) {
  // TODO: implementar leitura via react-native-fs
  throw new Error('Implementar leitura de arquivo binário (react-native-fs)');
}

export function gerarAssinaturaDispositivo(payload, chaveDispositivo) {
  // TODO: implementar HMAC-SHA256 do payload usando a chave privada
  // armazenada de forma segura (Keychain/Keystore) no dispositivo.
  throw new Error('Implementar assinatura HMAC do payload');
}
