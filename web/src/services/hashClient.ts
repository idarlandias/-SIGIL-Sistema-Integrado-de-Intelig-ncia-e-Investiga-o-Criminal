/**
 * Cálculo de hash SHA-256 no navegador via Web Crypto API — mesmo
 * princípio do app mobile: o hash nunca é confiado ao servidor sem
 * validação, mas aqui serve para o operador confirmar visualmente a
 * integridade antes do envio (o app de campo é a fonte primária).
 */
export async function calcularHashArquivo(arquivo: File): Promise<string> {
  const buffer = await arquivo.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}
