/**
 * Tela de captura de evidência em campo: foto/vídeo/áudio + geolocalização.
 * Exige biometria antes de habilitar a captura, calcula o hash localmente
 * (ver hashService.js) e assina o payload com a chave do dispositivo antes
 * de enfileirar para sincronização offline.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import Geolocation from 'react-native-geolocation-service';
import { calcularHashArquivo, gerarAssinaturaDispositivo } from '../services/hashService';
import { enfileirarEvidencia } from '../services/syncService';
import { autenticarComBiometria, biometriaDisponivel } from '../services/biometriaService';
import { obterOuCriarChaveDispositivo } from '../services/keyStoreService';
import { ativarModoPanico } from '../services/panicoService';

export default function CapturaEvidenciaScreen() {
  const [status, setStatus] = useState('pronto');
  const [autenticado, setAutenticado] = useState(false);

  useEffect(() => {
    verificarBiometriaEAutenticar();
  }, []);

  async function verificarBiometriaEAutenticar() {
    const { available } = await biometriaDisponivel();
    if (!available) {
      setStatus('biometria indisponível — usando MFA do backend apenas');
      setAutenticado(true);
      return;
    }
    try {
      await autenticarComBiometria();
      setAutenticado(true);
      setStatus('pronto');
    } catch (erro) {
      setStatus(`autenticação biométrica falhou: ${erro.message}`);
    }
  }

  async function capturarEEnfileirar(caminhoArquivo, tipo, inqueritoNumero, agenteMatricula) {
    if (!autenticado) {
      Alert.alert('Acesso bloqueado', 'Autentique-se com biometria antes de capturar evidências.');
      return;
    }

    setStatus('processando');
    try {
      const hash = await calcularHashArquivo(caminhoArquivo);
      const posicao = await obterPosicaoAtual();
      const chaveDispositivo = await obterOuCriarChaveDispositivo();

      const payload = { hash, tipo, inqueritoNumero, agenteMatricula, capturadoEm: new Date().toISOString() };
      const assinatura = await gerarAssinaturaDispositivo(payload, chaveDispositivo);

      const idLocal = await enfileirarEvidencia({
        arquivo: caminhoArquivo,
        hash,
        tipo,
        gpsLat: posicao.latitude,
        gpsLon: posicao.longitude,
        capturadoEm: payload.capturadoEm,
        agenteMatricula,
        inqueritoNumero,
        assinatura,
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

  async function acionarModoPanico() {
    Alert.alert(
      'Confirmar ação',
      'Isso apagará todos os dados locais não sincronizados. Continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Confirmar',
          style: 'destructive',
          onPress: async () => {
            await ativarModoPanico();
            setStatus('dados locais apagados');
          },
        },
      ]
    );
  }

  return (
    <View>
      <Text>Captura de Evidência — Status: {status}</Text>
      {/* TODO: componentes de câmera/microfone (react-native-image-crop-picker, etc.) */}
      <Button title="Simular Captura" onPress={() => {}} disabled={!autenticado} />
      <Button title="Modo Pânico" color="#8B0000" onPress={acionarModoPanico} />
    </View>
  );
}
