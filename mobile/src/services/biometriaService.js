/**
 * Autenticação biométrica (Face ID / Touch ID / impressão digital Android)
 * como segundo fator local antes de liberar acesso ao app ou à fila de
 * evidências offline, mesmo sem conectividade com o backend.
 */
import ReactNativeBiometrics, { BiometryTypes } from 'react-native-biometrics';

const rnBiometrics = new ReactNativeBiometrics({ allowDeviceCredentials: true });

export async function biometriaDisponivel() {
  const { available, biometryType } = await rnBiometrics.isSensorAvailable();
  return { available, biometryType };
}

export async function autenticarComBiometria(promptMessage = 'Confirme sua identidade para acessar o SIGIL') {
  const { success, error } = await rnBiometrics.simplePrompt({ promptMessage });
  if (!success) {
    throw new Error(error || 'Autenticação biométrica falhou ou foi cancelada.');
  }
  return true;
}

export async function registrarChaveBiometrica(payload) {
  /**
   * Cria um par de chaves protegido por biometria (Secure Enclave/StrongBox)
   * e assina o payload — usado para provar que o login foi autorizado
   * pelo titular do dispositivo, complementando o MFA do backend.
   */
  const { publicKey } = await rnBiometrics.createKeys();
  const { success, signature } = await rnBiometrics.createSignature({
    promptMessage: 'Autorize o acesso ao SIGIL',
    payload,
  });
  if (!success) {
    throw new Error('Falha ao gerar assinatura biométrica.');
  }
  return { publicKey, signature };
}
