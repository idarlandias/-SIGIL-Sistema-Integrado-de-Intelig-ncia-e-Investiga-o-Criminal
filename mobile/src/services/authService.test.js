import axios from 'axios';
import * as Keychain from 'react-native-keychain';
import { login, obterTokensSalvos, renovarSessao, obterAccessTokenValido, logout } from './authService';

/**
 * Valida o fluxo de autenticação do app mobile: login com MFA,
 * persistência segura no Keychain (nunca AsyncStorage), e renovação
 * automática de sessão via refresh token — espelha o comportamento
 * exigido pelo backend (POST /v1/auth/login, sem bypass de MFA).
 */
describe('authService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  function gerarJwtFalso(payloadObj) {
    const payloadBase64 = Buffer.from(JSON.stringify(payloadObj)).toString('base64');
    return `header.${payloadBase64}.assinatura`;
  }

  it('login persiste os tokens no Keychain apos sucesso', async () => {
    const expiraEm = Math.floor(Date.now() / 1000) + 3600;
    const accessToken = gerarJwtFalso({ sub: 'MAT-001', papel: 'investigador', exp: expiraEm });

    axios.post.mockResolvedValueOnce({
      data: { access_token: accessToken, refresh_token: 'refresh-abc' },
    });

    const resultado = await login('MAT-001', 'senha123', '123456');

    expect(axios.post).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login'),
      { matricula: 'MAT-001', senha: 'senha123', codigo_mfa: '123456' }
    );
    expect(Keychain.setGenericPassword).toHaveBeenCalled();
    expect(resultado.accessToken).toBe(accessToken);
  });

  it('obterTokensSalvos retorna null quando nao ha sessao salva', async () => {
    Keychain.getGenericPassword.mockResolvedValueOnce(false);
    const tokens = await obterTokensSalvos();
    expect(tokens).toBeNull();
  });

  it('renovarSessao lanca erro quando nao ha refresh token salvo', async () => {
    Keychain.getGenericPassword.mockResolvedValueOnce(false);
    await expect(renovarSessao()).rejects.toThrow('Nenhuma sessão salva');
  });

  it('obterAccessTokenValido lanca erro quando usuario nao autenticado', async () => {
    Keychain.getGenericPassword.mockResolvedValueOnce(false);
    await expect(obterAccessTokenValido()).rejects.toThrow('não autenticado');
  });

  it('obterAccessTokenValido renova automaticamente quando o token esta expirado', async () => {
    const expirado = Math.floor(Date.now() / 1000) - 100;
    const tokenExpirado = gerarJwtFalso({ sub: 'MAT-001', papel: 'agente', exp: expirado });

    Keychain.getGenericPassword.mockResolvedValueOnce({
      password: JSON.stringify({ accessToken: tokenExpirado, refreshToken: 'refresh-antigo' }),
    });

    const novoExpiraEm = Math.floor(Date.now() / 1000) + 3600;
    const novoAccessToken = gerarJwtFalso({ sub: 'MAT-001', papel: 'agente', exp: novoExpiraEm });
    axios.post.mockResolvedValueOnce({
      data: { access_token: novoAccessToken, refresh_token: 'refresh-novo' },
    });

    const tokenValido = await obterAccessTokenValido();

    expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/auth/refresh'), null, expect.anything());
    expect(tokenValido).toBe(novoAccessToken);
  });

  it('logout remove os tokens do Keychain', async () => {
    await logout();
    expect(Keychain.resetGenericPassword).toHaveBeenCalled();
  });
});
