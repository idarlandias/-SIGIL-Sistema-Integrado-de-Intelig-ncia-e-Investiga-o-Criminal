import '@testing-library/jest-dom';

// jsdom nem sempre expoe crypto.subtle (Web Crypto API) nativamente.
// Como o calculo de hash SHA-256 (hashClient.ts) depende dela para
// validar a integridade das evidencias no navegador, garantimos aqui
// que o ambiente de teste tenha o mesmo comportamento de um browser real,
// usando o webcrypto nativo do Node como polyfill quando necessario.
if (typeof globalThis.crypto === 'undefined' || !globalThis.crypto.subtle) {
  const { webcrypto } = await import('node:crypto');
  // @ts-expect-error - atribuicao de polyfill em ambiente de teste
  globalThis.crypto = webcrypto;
}
