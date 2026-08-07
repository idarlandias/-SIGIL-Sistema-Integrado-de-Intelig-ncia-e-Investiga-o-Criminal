import { useState, FormEvent } from 'react';
import apiClient from '../services/apiClient';

interface Segmento {
  inicio_segundos: number;
  fim_segundos: number;
  texto: string;
}

interface ResultadoTranscricao {
  texto_completo: string;
  idioma_detectado: string;
  segmentos: Segmento[];
}

function formatarTempo(segundos: number): string {
  const min = Math.floor(segundos / 60);
  const seg = Math.floor(segundos % 60);
  return `${min}:${seg.toString().padStart(2, '0')}`;
}

/**
 * Transcrição de depoimentos e escutas autorizadas via Whisper — consome
 * POST /v1/transcricao/audio, protegido por RBAC no backend (permissão
 * "evidencias:criar"). Exibe o texto completo e os segmentos
 * timestampados, úteis para apontar no laudo pericial o momento exato
 * de uma fala relevante.
 */
export default function TranscricaoAudioPage() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [idioma, setIdioma] = useState('pt');
  const [status, setStatus] = useState<'idle' | 'transcrevendo' | 'sucesso' | 'erro'>('idle');
  const [resultado, setResultado] = useState<ResultadoTranscricao | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!arquivo) return;

    setStatus('transcrevendo');
    setErro(null);
    setResultado(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', arquivo);

      const resposta = await apiClient.post('/transcricao/audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { idioma },
      });

      setResultado(resposta.data);
      setStatus('sucesso');
    } catch (err: any) {
      setStatus('erro');
      if (err.response?.status === 503) {
        setErro('Serviço de transcrição (Whisper) indisponível neste ambiente.');
      } else if (err.response?.status === 403) {
        setErro('Seu papel não tem permissão para transcrever áudio.');
      } else {
        setErro('Erro ao transcrever o áudio. Tente novamente.');
      }
    }
  }

  function copiarTextoCompleto() {
    if (resultado) {
      navigator.clipboard.writeText(resultado.texto_completo);
    }
  }

  return (
    <div className="transcricao-page">
      <h2>Transcrição de Depoimento / Escuta Autorizada</h2>
      <p className="upload-aviso">
        A transcrição é gerada via Whisper e não substitui a revisão humana
        antes de qualquer uso probatório. Segmentos timestampados permitem
        localizar o momento exato de uma fala no laudo pericial.
      </p>

      <form className="upload-form" onSubmit={handleSubmit}>
        <label>
          Arquivo de áudio
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
            required
          />
        </label>

        <label>
          Idioma
          <select value={idioma} onChange={(e) => setIdioma(e.target.value)}>
            <option value="pt">Português</option>
            <option value="en">Inglês</option>
            <option value="es">Espanhol</option>
          </select>
        </label>

        <button type="submit" disabled={status === 'transcrevendo'}>
          {status === 'transcrevendo' ? 'Transcrevendo...' : 'Transcrever Áudio'}
        </button>
      </form>

      {erro && <p className="erro">{erro}</p>}

      {resultado && (
        <div className="transcricao-resultado">
          <div className="transcricao-cabecalho">
            <h3>Transcrição completa (idioma detectado: {resultado.idioma_detectado})</h3>
            <button onClick={copiarTextoCompleto} className="transcricao-copiar">
              Copiar texto
            </button>
          </div>
          <p className="transcricao-texto-completo">{resultado.texto_completo}</p>

          <h3>Segmentos timestampados</h3>
          <table className="tabela-casos">
            <thead>
              <tr>
                <th>Início</th>
                <th>Fim</th>
                <th>Texto</th>
              </tr>
            </thead>
            <tbody>
              {resultado.segmentos.map((seg, idx) => (
                <tr key={idx}>
                  <td>{formatarTempo(seg.inicio_segundos)}</td>
                  <td>{formatarTempo(seg.fim_segundos)}</td>
                  <td>{seg.texto}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
