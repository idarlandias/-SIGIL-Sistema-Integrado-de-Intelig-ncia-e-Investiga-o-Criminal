/**
 * Modo pânico: apaga com segurança todos os dados locais sensíveis do
 * dispositivo (banco SQLCipher, chaves do Keychain, cache de arquivos)
 * em caso de risco iminente ao agente (abordagem, apreensão do celular
 * por terceiros, etc.). Ação irreversível e silenciosa — não emite
 * confirmação sonora nem visual óbvia, para não expor o agente.
 */
import RNFS from 'react-native-fs';
import * as Keychain from 'react-native-keychain';
import { apagarTodosOsDadosLocais } from '../storage/db';
import { apagarChaveDispositivo } from './keyStoreService';

const DIRETORIO_CACHE_EVIDENCIAS = `${RNFS.CachesDirectoryPath}/sigil_evidencias`;

export async function ativarModoPanico() {
  const resultados = { banco: false, chaveDispositivo: false, chaveBanco: false, arquivosCache: false };

  try {
    await apagarTodosOsDadosLocais();
    resultados.banco = true;
  } catch (_) {
    // Falha ao apagar o banco não deve interromper a limpeza dos demais itens.
  }

  try {
    await apagarChaveDispositivo();
    resultados.chaveDispositivo = true;
  } catch (_) {}

  try {
    await Keychain.resetGenericPassword({ service: 'sigil.sqlcipher.db.key' });
    resultados.chaveBanco = true;
  } catch (_) {}

  try {
    const existe = await RNFS.exists(DIRETORIO_CACHE_EVIDENCIAS);
    if (existe) {
      await RNFS.unlink(DIRETORIO_CACHE_EVIDENCIAS);
    }
    resultados.arquivosCache = true;
  } catch (_) {}

  return resultados;
}
