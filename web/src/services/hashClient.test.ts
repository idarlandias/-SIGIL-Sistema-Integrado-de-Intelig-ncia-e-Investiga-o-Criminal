import { describe, it, expect } from 'vitest';
import { calcularHashArquivo } from './hashClient';

/**
 * Valida que o hash SHA-256 calculado no navegador (Web Crypto API) e
 * deterministico e sensivel a qualquer alteracao de conteudo - mesmo
 * principio de integridade usado no backend (evidencias.py) e no app
 * mobile (hashService.js). Este e o primeiro elo visivel ao operador
 * humano da cadeia de custodia digital.
 */
describe('calcularHashArquivo', () => {
  it('gera o mesmo hash para o mesmo conteudo (deterministico)', async () => {
    const arquivo1 = new File(['conteudo-de-teste'], 'evidencia.txt', { type: 'text/plain' });
    const arquivo2 = new File(['conteudo-de-teste'], 'evidencia.txt', { type: 'text/plain' });

    const hash1 = await calcularHashArquivo(arquivo1);
    const hash2 = await calcularHashArquivo(arquivo2);

    expect(hash1).toBe(hash2);
  });

  it('gera hashes diferentes para conteudos diferentes', async () => {
    const arquivoOriginal = new File(['conteudo-original'], 'evidencia.txt');
    const arquivoAdulterado = new File(['conteudo-adulterado'], 'evidencia.txt');

    const hashOriginal = await calcularHashArquivo(arquivoOriginal);
    const hashAdulterado = await calcularHashArquivo(arquivoAdulterado);

    expect(hashOriginal).not.toBe(hashAdulterado);
  });

  it('retorna uma string hexadecimal de 64 caracteres (SHA-256)', async () => {
    const arquivo = new File(['qualquer conteudo'], 'teste.txt');
    const hash = await calcularHashArquivo(arquivo);

    expect(hash).toMatch(/^[0-9a-f]{64}$/);
  });

  it('e sensivel ao nome do arquivo nao interferir no hash (so o conteudo importa)', async () => {
    const arquivoA = new File(['mesmo-conteudo'], 'nome_a.txt');
    const arquivoB = new File(['mesmo-conteudo'], 'nome_b.txt');

    const hashA = await calcularHashArquivo(arquivoA);
    const hashB = await calcularHashArquivo(arquivoB);

    expect(hashA).toBe(hashB);
  });
});
