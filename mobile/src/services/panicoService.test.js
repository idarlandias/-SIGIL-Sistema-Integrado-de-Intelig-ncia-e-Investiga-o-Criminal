import RNFS from 'react-native-fs';
import * as Keychain from 'react-native-keychain';
import { ativarModoPanico } from './panicoService';
import { apagarTodosOsDadosLocais } from '../storage/db';
import { apagarChaveDispositivo } from './keyStoreService';
import { logout } from './authService';

jest.mock('../storage/db');
jest.mock('./keyStoreService');
jest.mock('./authService');

/**
 * Valida o Modo Pânico — a funcionalidade de segurança mais crítica do
 * app mobile, usada quando um agente está em risco (abordagem, apreensão
 * do celular por terceiros). O requisito central é: mesmo que UM passo
 * de limpeza falhe, os DEMAIS passos devem continuar executando — nunca
 * interromper a limpeza por uma falha isolada.
 */
describe('panicoService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    RNFS.exists.mockResolvedValue(true);
    RNFS.unlink.mockResolvedValue();
  });

  it('executa todos os passos de limpeza com sucesso', async () => {
    apagarTodosOsDadosLocais.mockResolvedValue();
    apagarChaveDispositivo.mockResolvedValue();
    logout.mockResolvedValue();
    Keychain.resetGenericPassword.mockResolvedValue(true);

    const resultado = await ativarModoPanico();

    expect(resultado.banco).toBe(true);
    expect(resultado.chaveDispositivo).toBe(true);
    expect(resultado.chaveBanco).toBe(true);
    expect(resultado.sessaoAutenticacao).toBe(true);
    expect(resultado.arquivosCache).toBe(true);
    expect(RNFS.unlink).toHaveBeenCalled();
  });

  it('continua limpando os demais itens mesmo se apagar o banco falhar', async () => {
    apagarTodosOsDadosLocais.mockRejectedValue(new Error('falha no banco'));
    apagarChaveDispositivo.mockResolvedValue();
    logout.mockResolvedValue();
    Keychain.resetGenericPassword.mockResolvedValue(true);

    const resultado = await ativarModoPanico();

    expect(resultado.banco).toBe(false);
    expect(resultado.chaveDispositivo).toBe(true);
    expect(resultado.sessaoAutenticacao).toBe(true);
  });

  it('continua limpando os demais itens mesmo se o logout falhar', async () => {
    apagarTodosOsDadosLocais.mockResolvedValue();
    apagarChaveDispositivo.mockResolvedValue();
    logout.mockRejectedValue(new Error('falha no logout'));
    Keychain.resetGenericPassword.mockResolvedValue(true);

    const resultado = await ativarModoPanico();

    expect(resultado.sessaoAutenticacao).toBe(false);
    expect(resultado.banco).toBe(true);
    expect(resultado.chaveDispositivo).toBe(true);
  });

  it('nao tenta apagar cache se o diretorio nao existir', async () => {
    apagarTodosOsDadosLocais.mockResolvedValue();
    apagarChaveDispositivo.mockResolvedValue();
    logout.mockResolvedValue();
    Keychain.resetGenericPassword.mockResolvedValue(true);
    RNFS.exists.mockResolvedValue(false);

    const resultado = await ativarModoPanico();

    expect(RNFS.unlink).not.toHaveBeenCalled();
    expect(resultado.arquivosCache).toBe(true);
  });

  it('retorna todos os resultados como false quando tudo falha', async () => {
    apagarTodosOsDadosLocais.mockRejectedValue(new Error('falha'));
    apagarChaveDispositivo.mockRejectedValue(new Error('falha'));
    logout.mockRejectedValue(new Error('falha'));
    Keychain.resetGenericPassword.mockRejectedValue(new Error('falha'));
    RNFS.exists.mockRejectedValue(new Error('falha'));

    const resultado = await ativarModoPanico();

    expect(resultado.banco).toBe(false);
    expect(resultado.chaveDispositivo).toBe(false);
    expect(resultado.chaveBanco).toBe(false);
    expect(resultado.sessaoAutenticacao).toBe(false);
    expect(resultado.arquivosCache).toBe(false);
  });
});
