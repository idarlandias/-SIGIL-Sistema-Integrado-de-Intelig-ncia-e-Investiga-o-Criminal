/**
 * Camada de persistência local usando SQLCipher (SQLite criptografado).
 * Toda evidência capturada offline passa por aqui antes da sincronização.
 */
// TODO: inicializar conexão real com react-native-sqlcipher-storage
// import SQLite from 'react-native-sqlcipher-storage';

export async function salvarItemLocal(item) {
  // TODO: INSERT INTO fila_evidencias (...) VALUES (...)
  throw new Error('Implementar persistência SQLCipher');
}

export async function listarItensPendentes() {
  // TODO: SELECT * FROM fila_evidencias WHERE sincronizado = 0
  return [];
}

export async function marcarComoSincronizado(idLocal, evidenciaIdServidor) {
  // TODO: UPDATE fila_evidencias SET sincronizado = 1, evidencia_id_servidor = ? WHERE id_local = ?
  throw new Error('Implementar atualização de status de sincronização');
}
