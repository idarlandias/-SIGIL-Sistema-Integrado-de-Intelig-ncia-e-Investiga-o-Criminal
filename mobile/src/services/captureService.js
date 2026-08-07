/**
 * Captura real de mídia em campo: foto/vídeo via câmera nativa e
 * gravação de áudio (depoimentos). Cada captura retorna o caminho local
 * do arquivo, que segue para hashService.js (hash SHA-256) antes de
 * qualquer envio — nunca se assume integridade sem essa validação.
 */
import ImagePicker from 'react-native-image-crop-picker';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import { PermissionsAndroid, Platform } from 'react-native';

const audioRecorderPlayer = new AudioRecorderPlayer();

async function solicitarPermissaoAudio() {
  if (Platform.OS !== 'android') return true;
  const resultado = await PermissionsAndroid.request(
    PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
    {
      title: 'Permissão de microfone',
      message: 'O SIGIL precisa acessar o microfone para gravar depoimentos em campo.',
      buttonPositive: 'Permitir',
    }
  );
  return resultado === PermissionsAndroid.RESULTS.GRANTED;
}

/**
 * Abre a câmera nativa para capturar uma foto. Retorna o caminho local
 * do arquivo e metadados básicos (dimensões, tamanho, mimetype).
 */
export async function capturarFoto() {
  const imagem = await ImagePicker.openCamera({
    width: 1600,
    height: 1200,
    cropping: false,
    includeExif: true,
    mediaType: 'photo',
    compressImageQuality: 0.9,
  });

  return {
    caminho: imagem.path,
    tipo: 'foto',
    mimeType: imagem.mime,
    tamanhoBytes: imagem.size,
    largura: imagem.width,
    altura: imagem.height,
  };
}

/**
 * Abre a câmera nativa em modo vídeo. Sem compressão agressiva — a
 * qualidade da evidência prevalece sobre o tamanho do arquivo.
 */
export async function capturarVideo() {
  const video = await ImagePicker.openCamera({
    mediaType: 'video',
  });

  return {
    caminho: video.path,
    tipo: 'video',
    mimeType: video.mime,
    tamanhoBytes: video.size,
    duracaoSegundos: video.duration ? video.duration / 1000 : null,
  };
}

/**
 * Inicia a gravação de áudio (depoimento). Retorna uma função `parar()`
 * que finaliza a gravação e resolve com o caminho do arquivo gravado.
 */
export async function iniciarGravacaoAudio() {
  const permitido = await solicitarPermissaoAudio();
  if (!permitido) {
    throw new Error('Permissão de microfone negada pelo usuário.');
  }

  const nomeArquivo = `depoimento_${Date.now()}.m4a`;
  const caminhoGravacao = await audioRecorderPlayer.startRecorder(nomeArquivo);

  return {
    parar: async () => {
      const caminhoFinal = await audioRecorderPlayer.stopRecorder();
      audioRecorderPlayer.removeRecordBackListener();
      return {
        caminho: caminhoFinal || caminhoGravacao,
        tipo: 'audio',
        mimeType: 'audio/m4a',
      };
    },
    onProgresso: (callback) => {
      audioRecorderPlayer.addRecordBackListener((evento) => {
        callback({
          segundosGravados: Math.floor(evento.currentPosition / 1000),
        });
      });
    },
  };
}
