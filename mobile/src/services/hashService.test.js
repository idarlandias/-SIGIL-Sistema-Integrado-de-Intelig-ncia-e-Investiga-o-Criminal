import { calcularHashArquivo, gerarAssinaturaDispositivo } from './hashService';
import RNFS from 'react-native-fs';

/**
 * Valida o serviço de hash SHA-256 do app mobile — o primeiro elo da
 * cadeia de custódia digital (etapa "reconhecimento", Lei 13.964/19).
 * Usa mocks de RNFS/react-native-crypto (ver jest.setup.js) — não
 * depende de arquivo real em disco.
 */
describe('hashService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('calcularHashArquivo le o arquivo e retorna um hash', async () => {
    const hash = await calcularHashArquivo('/caminho/qualquer/evidencia.jpg');

    expect(RNFS.readFile).toHaveBeenCalledWith(
      '/caminho/qualquer/evidencia.jpg',
      'base64'
    );
    expect(hash).toBeTruthy();
    expect(typeof hash).toBe('string');
  });

  it('gerarAssinaturaDispositivo retorna uma assinatura para o payload', async () => {
    const payload = { hash: 'abc123', tipo: 'foto' };
    const assinatura = await gerarAssinaturaDispositivo(payload, 'chave-mock');

    expect(assinatura).toBeTruthy();
  });

  it('gerarAssinaturaDispositivo aceita payload como string', async () => {
    const assinatura = await gerarAssinaturaDispositivo('payload-em-texto', 'chave-mock');
    expect(assinatura).toBeTruthy();
  });
});
