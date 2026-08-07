/**
 * Gestão da chave privada do dispositivo, usada para assinar (HMAC) o
 * payload de cada evidência antes do envio — prova que a requisição
 * partiu de um dispositivo autorizado, não de uma chamada direta à API.
 * Usa Keychain (iOS) / Keystore (Android) via react-native-keychain.
 */
import * as Keychain from 'react-native-keychain';
import { randomBytes } from 'react-native-crypto';

const SERVICE_NAME = 'sigil.device.signing.key';

export async function obterOuCriarChaveDispositivo() {
  const credenciais = await Keychain.getGenericPassword({ service: SERVICE_NAME });
  if (credenciais) {
    return credenciais.password;
  }

  const novaChave = randomBytes(32).toString('hex');
  await Keychain.setGenericPassword('sigil-device', novaChave, {
    service: SERVICE_NAME,
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
  return novaChave;
}

export async function apagarChaveDispositivo() {
  await Keychain.resetGenericPassword({ service: SERVICE_NAME });
}
