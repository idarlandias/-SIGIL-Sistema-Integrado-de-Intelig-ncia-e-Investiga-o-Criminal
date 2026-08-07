/**
 * Autenticação do app mobile contra o backend SIGIL: login com MFA
 * obrigatório, persistência segura de tokens no Keychain/Keystore
 * (nunca em AsyncStorage, que não é criptografado por padrão), e
 * renovação automática via refresh token quando o access token expira.
 */
import axios from 'axios';
import * as Keychain from 'react-native-keychain';

const API_BASE_URL = 'https://api.sigil.local/v1'; // substituir por endpoint real
const TOKEN_SERVICE = 'sigil.auth.tokens';

/**
 * Realiza login com matrícula + senha + código MFA (TOTP). Em caso de
 * sucesso, persiste access e refresh tokens no Keychain/Keystore.
 */
export async function login(matricula, senha, codigoMfa) {
  const resposta = await axios.post(`${API_BASE_URL}/auth/login`, {
    matricula,
    senha,
    codigo_mfa: codigoMfa,
  });

  const { access_token, refresh_token } = resposta.data;
  await salvarTokens(access_token, refresh_token);
  return { accessToken: access_token, refreshToken: refresh_token };
}

/**
 * Persiste os tokens de forma segura. O Keychain (iOS) e o Keystore
 * (Android) usam armazenamento protegido por hardware quando disponível
 * — muito mais seguro que AsyncStorage para dados de autenticação.
 */
async function salvarTokens(accessToken, refreshToken) {
  await Keychain.setGenericPassword(
    'sigil-tokens',
    JSON.stringify({ accessToken, refreshToken, salvoEm: Date.now() }),
    {
      service: TOKEN_SERVICE,
      accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    }
  );
}

export async function obterTokensSalvos() {
  const credenciais = await Keychain.getGenericPassword({ service: TOKEN_SERVICE });
  if (!credenciais) return null;
  try {
    return JSON.parse(credenciais.password);
  } catch (_) {
    return null;
  }
}

/**
 * Usa o refresh token salvo para obter um novo access token, sem exigir
 * novo MFA — espelha o comportamento do endpoint POST /v1/auth/refresh.
 */
export async function renovarSessao() {
  const tokensSalvos = await obterTokensSalvos();
  if (!tokensSalvos?.refreshToken) {
    throw new Error('Nenhuma sessão salva para renovar.');
  }

  const resposta = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
    params: { refresh_token: tokensSalvos.refreshToken },
  });

  const { access_token, refresh_token } = resposta.data;
  await salvarTokens(access_token, refresh_token);
  return { accessToken: access_token, refreshToken: refresh_token };
}

/**
 * Retorna um access token válido, renovando automaticamente via refresh
 * token se necessário. Usado como interceptor antes de qualquer chamada
 * autenticada à API.
 */
export async function obterAccessTokenValido() {
  const tokensSalvos = await obterTokensSalvos();
  if (!tokensSalvos) {
    throw new Error('Usuário não autenticado.');
  }

  const payload = decodificarPayloadJWT(tokensSalvos.accessToken);
  const expiraEm = payload?.exp ? payload.exp * 1000 : 0;
  const margemSeguranca = 30_000; // renova 30s antes de expirar

  if (Date.now() >= expiraEm - margemSeguranca) {
    const novosTokens = await renovarSessao();
    return novosTokens.accessToken;
  }

  return tokensSalvos.accessToken;
}

function decodificarPayloadJWT(token) {
  try {
    const [, payloadBase64] = token.split('.');
    const payloadJson = global.atob
      ? global.atob(payloadBase64)
      : Buffer.from(payloadBase64, 'base64').toString('utf-8');
    return JSON.parse(payloadJson);
  } catch (_) {
    return null;
  }
}

/**
 * Logout: remove os tokens do Keychain. Chamado explicitamente pelo
 * usuário ou automaticamente pelo modo pânico (ver panicoService.js).
 */
export async function logout() {
  await Keychain.resetGenericPassword({ service: TOKEN_SERVICE });
}
