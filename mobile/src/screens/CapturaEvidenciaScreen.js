/**
 * Tela de captura de evidência em campo: foto/vídeo/áudio + geolocalização.
 * Exige biometria antes de habilitar a captura, calcula o hash localmente
 * (ver hashService.js) e assina o payload com a chave do dispositivo antes
 * de enfileirar para sincronização offline.
 */
import React, { useState, useEffect } from 'react';
import { View, Text, Button, Alert, TextInput, StyleSheet } from 'react-native';
import Geolocation from 'react-native-geolocation-service';
import { calcularHashArquivo, gerarAssinaturaDispositivo } from '../services/hashService';
import { enfileirarEvidencia } from '../services/syncService';
import { autenticarComBiometria, biometriaDisponivel } from '../services/biometriaService';
import { obterOuCriarChaveDispositivo } from '../services/keyStoreService';
import { ativarModoPanico } from '../services/panicoService';
import { capturarFoto, capturarVideo, iniciarGravacaoAudio } from '../services/captureService';

export default function CapturaEvidenciaScreen() {
  const [status, setStatus] = useState('pronto');
  const [autenticado, setAutenticado] = useState(false);
  const [inqueritoNumero, setInqueritoNumero] = useState('');
  const [agenteMatricula, setAgenteMatricula] = useState('');
  const [gravacaoAtiva, setGravacaoAtiva] = useState(null);
  const [segundosGravados, setSegundosGravados] = useState(0);

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

  function validarCamposObrigatorios() {
    if (!autenticado) {
      Alert.alert('Acesso bloqueado', 'Autentique-se com biometria antes de capturar evidências.');
      return false;
    }
    if (!inqueritoNumero || !agenteMatricula) {
      Alert.alert('Campos obrigatórios', 'Informe o número do inquérito e a matrícula do agente.');
      return false;
    }
    return true;
  }

  async function processarEEnfileirar(dadosCaptura) {
    setStatus('processando');
    try {
      const hash = await calcularHashArquivo(dadosCaptura.caminho);
      const posicao = await obterPosicaoAtual();
      const chaveDispositivo = await obterOuCriarChaveDispositivo();

      const payload = {
        hash,
        tipo: dadosCaptura.tipo,
        inqueritoNumero,
        agenteMatricula,
        capturadoEm: new Date().toISOString(),
      };
      const assinatura = await gerarAssinaturaDispositivo(payload, chaveDispositivo);

      const idLocal = await enfileirarEvidencia({
        arquivo: dadosCaptura.caminho,
        hash,
        tipo: dadosCaptura.tipo,
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

  async function handleCapturarFoto() {
    if (!validarCamposObrigatorios()) return;
    try {
      const foto = await capturarFoto();
      await processarEEnfileirar(foto);
    } catch (erro) {
      if (!erro.message?.includes('cancel')) {
        setStatus(`erro na captura: ${erro.message}`);
      }
    }
  }

  async function handleCapturarVideo() {
    if (!validarCamposObrigatorios()) return;
    try {
      const video = await capturarVideo();
      await processarEEnfileirar(video);
    } catch (erro) {
      if (!erro.message?.includes('cancel')) {
        setStatus(`erro na captura: ${erro.message}`);
      }
    }
  }

  async function handleIniciarAudio() {
    if (!validarCamposObrigatorios()) return;
    try {
      const gravacao = await iniciarGravacaoAudio();
      gravacao.onProgresso(({ segundosGravados }) => setSegundosGravados(segundosGravados));
      setGravacaoAtiva(gravacao);
      setStatus('gravando depoimento...');
    } catch (erro) {
      setStatus(`erro ao iniciar gravação: ${erro.message}`);
    }
  }

  async function handlePararAudio() {
    if (!gravacaoAtiva) return;
    try {
      const resultado = await gravacaoAtiva.parar();
      setGravacaoAtiva(null);
      setSegundosGravados(0);
      await processarEEnfileirar(resultado);
    } catch (erro) {
      setStatus(`erro ao finalizar gravação: ${erro.message}`);
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
    <View style={estilos.container}>
      <Text style={estilos.status}>Captura de Evidência — Status: {status}</Text>

      <TextInput
        style={estilos.input}
        placeholder="Número do inquérito (ex: IP-2026-0451)"
        value={inqueritoNumero}
        onChangeText={setInqueritoNumero}
      />
      <TextInput
        style={estilos.input}
        placeholder="Matrícula do agente"
        value={agenteMatricula}
        onChangeText={setAgenteMatricula}
      />

      <Button title="📷 Capturar Foto" onPress={handleCapturarFoto} disabled={!autenticado} />
      <Button title="🎥 Capturar Vídeo" onPress={handleCapturarVideo} disabled={!autenticado} />

      {!gravacaoAtiva ? (
        <Button title="🎙️ Iniciar Gravação de Depoimento" onPress={handleIniciarAudio} disabled={!autenticado} />
      ) : (
        <Button title={`⏹️ Parar Gravação (${segundosGravados}s)`} onPress={handlePararAudio} color="#8B0000" />
      )}

      <Button title="Modo Pânico" color="#8B0000" onPress={acionarModoPanico} />
    </View>
  );
}

const estilos = StyleSheet.create({
  container: { padding: 16, gap: 12 },
  status: { fontSize: 14, marginBottom: 8 },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    marginBottom: 8,
  },
});
