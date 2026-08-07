/**
 * Camada de persistência local usando SQLCipher (SQLite criptografado).
 * Toda evidência capturada offline passa por aqui antes da sincronização.
 * A chave de criptografia do banco é obtida do Keychain/Keystore, nunca
 * hardcoded, e é distinta da chave de assinatura de dispositivo.
 */
import SQLite from 'react-native-sqlcipher-storage';
import * as Keychain from 'react-native-keychain';
import { randomBytes } from 'react-native-crypto';

SQLite.DEBUG(false);
SQLite.enablePromise(true);

const DB_NAME = 'sigil_offline.db';
const DB_KEY_SERVICE = 'sigil.sqlcipher.db.key';

let dbInstance = null;

async function obterChaveDoBanco() {
  const credenciais = await Keychain.getGenericPassword({ service: DB_KEY_SERVICE });
  if (credenciais) return credenciais.password;

  const novaChave = randomBytes(32).toString('hex');
  await Keychain.setGenericPassword('sigil-db', novaChave, {
    service: DB_KEY_SERVICE,
    accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
  });
  return novaChave;
}

async function getDb() {
  if (dbInstance) return dbInstance;

  const chave = await obterChaveDoBanco();
  dbInstance = await SQLite.openDatabase({ name: DB_NAME, key: chave, location: 'default' });

  await dbInstance.executeSql(`
    CREATE TABLE IF NOT EXISTS fila_evidencias (
      id_local TEXT PRIMARY KEY,
      arquivo_path TEXT NOT NULL,
      hash TEXT NOT NULL,
      tipo TEXT NOT NULL,
      gps_lat REAL,
      gps_lon REAL,
      capturado_em TEXT NOT NULL,
      agente_matricula TEXT NOT NULL,
      inquerito_numero TEXT NOT NULL,
      assinatura TEXT,
      sincronizado INTEGER DEFAULT 0,
      evidencia_id_servidor TEXT,
      criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    );
  `);

  return dbInstance;
}

export async function salvarItemLocal(item) {
  const db = await getDb();
  await db.executeSql(
    `INSERT INTO fila_evidencias
      (id_local, arquivo_path, hash, tipo, gps_lat, gps_lon, capturado_em, agente_matricula, inquerito_numero, assinatura, sincronizado)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)`,
    [
      item.id_local,
      item.arquivo,
      item.hash,
      item.tipo,
      item.gpsLat ?? null,
      item.gpsLon ?? null,
      item.capturadoEm,
      item.agenteMatricula,
      item.inqueritoNumero,
      item.assinatura ?? null,
    ]
  );
  return item.id_local;
}

export async function listarItensPendentes() {
  const db = await getDb();
  const [resultado] = await db.executeSql(
    'SELECT * FROM fila_evidencias WHERE sincronizado = 0 ORDER BY criado_em ASC'
  );

  const itens = [];
  for (let i = 0; i < resultado.rows.length; i++) {
    const row = resultado.rows.item(i);
    itens.push({
      id_local: row.id_local,
      arquivo: row.arquivo_path,
      hash: row.hash,
      tipo: row.tipo,
      gpsLat: row.gps_lat,
      gpsLon: row.gps_lon,
      capturadoEm: row.capturado_em,
      agenteMatricula: row.agente_matricula,
      inqueritoNumero: row.inquerito_numero,
      assinatura: row.assinatura,
    });
  }
  return itens;
}

export async function marcarComoSincronizado(idLocal, evidenciaIdServidor) {
  const db = await getDb();
  await db.executeSql(
    'UPDATE fila_evidencias SET sincronizado = 1, evidencia_id_servidor = ? WHERE id_local = ?',
    [evidenciaIdServidor, idLocal]
  );
}

export async function apagarTodosOsDadosLocais() {
  /**
   * Usado exclusivamente pelo modo pânico (panicoService.js). Derruba o
   * banco inteiro — não há como recuperar itens não sincronizados após
   * esta chamada, por design.
   */
  const db = await getDb();
  await db.executeSql('DROP TABLE IF EXISTS fila_evidencias;');
  dbInstance = null;
}
