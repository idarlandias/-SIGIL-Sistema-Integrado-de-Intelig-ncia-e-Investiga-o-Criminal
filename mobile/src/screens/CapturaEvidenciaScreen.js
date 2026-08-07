/**
 * Tela de captura de evidência em campo: foto/vídeo/áudio + geolocalização.
 * O hash é calculado localmente antes de qualquer envio (ver hashService.js).
 */
import React, { useState } from 'react';
import { View, Text, Button } from 'react-native';
import Geolocation from 'react-native-geolocation-service';
import { calcularHashArquivo } from '../services/hashService';
import { enfileirarEvidencia } from '../services/syncService';

export default function CapturaEvidenciaScreen() {
  const [status, setStatus] = useState('pronto');

  async function capturarEEnfileirar(caminhoArquivo, tipo, inqueritoNumero, agenteMatricula) {
    setStatus('processando');
    try {
      const hash = await calcularHashArquivo(caminhoArquivo);
      const posicao = await obterPosicaoAtual();

      const idLocal = await enfileirarEvidencia({
        arquivo: caminhoArquivo,
        hash,
        tipo,
        gpsLat: posicao.latitude,
        gpsLon: posicao.longitude,
        capturadoEm: new Date().toISOString(),
        agenteMatricula,
        inqueritoNumero,
      });

      setStatus(`enfileirado: ${idLocal}`);
    } catch (erro) {
      setStatus(`erro: ${erro.message}`);
    }
  }

  function obterPosicaoAtual() {
    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        (pos) => resolve(pos.coords),
        (err) => reject(err),
        { enableHighAccuracy: true, timeout: 15000 }
      );
    });
  }

  return (
    <View>
      <Text>Captura de Evidência — Status: {status}</Text>
      {/* TODO: componentes de câmera/microfone (react-native-image-crop-picker, etc.) */}
      <Button title="Simular Captura" onPress={() => {}} />
    </View>
  );
}
