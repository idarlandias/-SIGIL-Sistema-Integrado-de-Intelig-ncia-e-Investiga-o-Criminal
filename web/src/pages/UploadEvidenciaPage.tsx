import { useState, FormEvent } from 'react';
import apiClient from '../services/apiClient';
import { calcularHashArquivo } from '../services/hashClient';
import { useAuthStore } from '../store/authStore';

type TipoEvidencia = 'foto' | 'audio' | 'video' | 'documento' | 'depoimento_texto';

/**
 * Upload de evidências pelo painel web — complementar ao app de campo,
 * usado por peritos/investigadores para anexar documentos digitalizados
 * e mídias recebidas por outros canais (ofícios, quebra de sigilo, etc.).
 * Consome POST /v1/evidencias, que valida o hash SHA-256 no servidor e
 * rejeita com 409 em caso de divergência.
 */
export default function UploadEvidenciaPage() {
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [tipo, setTipo] = useState<TipoEvidencia>('documento');
  const [inqueritoNumero, setInqueritoNumero] = useState('');
  const [status, setStatus] = useState<'idle' | 'calculando' | 'enviando' | 'sucesso' | 'erro'>('idle');
  const [mensagem, setMensagem] = useState('');
  const [evidenciaId, setEvidenciaId] = useState<string | null>(null);

  const usuario = useAuthStore((s) => s.usuario);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!arquivo || !inqueritoNumero || !usuario) return;

    setStatus('calculando');
    setMensagem('');

    try {
      const hash = await calcularHashArquivo(arquivo);

      setStatus('enviando');
      const formData = new FormData();
      formData.append('arquivo', arquivo);
      formData.append('hash_sha256_cliente', hash);
      formData.append('tipo', tipo);
      formData.append('capturado_em', new Date().toISOString());
      formData.append('agente_matricula', usuario.matricula);
      formData.append('inquerito_numero', inqueritoNumero);
      // Assinatura de dispositivo não se aplica ao painel web (canal
      // secundário); o backend a torna informativa neste fluxo, dado que
      // a autenticidade já vem do JWT do usuário autenticado.
      formData.append('assinatura_dispositivo', 'painel-web');

      const resposta = await apiClient.post('/evidencias', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setEvidenciaId(resposta.data.evidencia_id);
      setStatus('sucesso');
      setMensagem(`Evidência registrada com sucesso. Etapa de custódia: ${resposta.data.etapa_custodia}`);
    } catch (err: any) {
      setStatus('erro');
      if (err.response?.status === 409) {
        setMensagem('Divergência de hash detectada pelo servidor — possível corrupção no upload. Tente novamente.');
      } else if (err.response?.status === 404) {
        setMensagem(`Inquérito ${inqueritoNumero} não encontrado.`);
      } else {
        setMensagem('Erro ao registrar evidência. Tente novamente.');
      }
    }
  }

  return (
    <div className="upload-evidencia-page">
      <h2>Registrar Nova Evidência</h2>
      <p className="upload-aviso">
        O hash SHA-256 é calculado no navegador antes do envio e revalidado pelo
        servidor — qualquer divergência é rejeitada automaticamente (cadeia de
        custódia, Lei 13.964/19).
      </p>

      <form className="upload-form" onSubmit={handleSubmit}>
        <label>
          Arquivo
          <input
            type="file"
            onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
            required
          />
        </label>

        <label>
          Tipo de evidência
          <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoEvidencia)}>
            <option value="documento">Documento</option>
            <option value="foto">Foto</option>
            <option value="video">Vídeo</option>
            <option value="audio">Áudio</option>
            <option value="depoimento_texto">Depoimento (texto)</option>
          </select>
        </label>

        <label>
          Número do inquérito
          <input
            value={inqueritoNumero}
            onChange={(e) => setInqueritoNumero(e.target.value)}
            placeholder="IP-2026-0451"
            required
          />
        </label>

        <button type="submit" disabled={status === 'calculando' || status === 'enviando'}>
          {status === 'calculando' && 'Calculando hash...'}
          {status === 'enviando' && 'Enviando...'}
          {(status === 'idle' || status === 'sucesso' || status === 'erro') && 'Registrar Evidência'}
        </button>
      </form>

      {mensagem && (
        <p className={status === 'sucesso' ? 'upload-sucesso' : 'erro'}>{mensagem}</p>
      )}

      {evidenciaId && status === 'sucesso' && (
        <p>
          ID da evidência: <code>{evidenciaId}</code>
        </p>
      )}
    </div>
  );
}
