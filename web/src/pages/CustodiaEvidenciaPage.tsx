import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../services/apiClient';

interface EventoCustodia {
  etapa: string;
  usuario: string;
  timestamp: string;
  hash_no_momento: string;
  acao: string;
}

const ETAPAS_ORDEM = [
  'reconhecimento', 'isolamento', 'fixacao', 'coleta', 'acondicionamento',
  'transporte', 'recebimento', 'processamento', 'armazenamento', 'descarte',
];

const LABEL_ETAPA: Record<string, string> = {
  reconhecimento: 'Reconhecimento',
  isolamento: 'Isolamento',
  fixacao: 'Fixação',
  coleta: 'Coleta',
  acondicionamento: 'Acondicionamento',
  transporte: 'Transporte',
  recebimento: 'Recebimento',
  processamento: 'Processamento',
  armazenamento: 'Armazenamento',
  descarte: 'Descarte',
};

const LABEL_ACAO: Record<string, string> = {
  criado: '➕ Criado',
  acessado: '👁 Acessado',
  modificado: '✏️ Modificado',
  exportado: '📤 Exportado',
};

/**
 * Visualizador da trilha de custódia de uma evidência — consome
 * GET /v1/custodia/{evidencia_id}, protegido por RBAC no backend
 * (permissão "custodia:ler"). Exibe a linha do tempo completa exigida
 * pelos arts. 158-A a 158-F do CPP (Lei 13.964/19).
 */
export default function CustodiaEvidenciaPage() {
  const { evidenciaId } = useParams<{ evidenciaId: string }>();
  const [eventos, setEventos] = useState<EventoCustodia[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!evidenciaId) return;

    apiClient
      .get(`/custodia/${evidenciaId}`)
      .then((resp) => setEventos(resp.data))
      .catch((err) => {
        if (err.response?.status === 403) {
          setErro('Seu papel não tem permissão para consultar a cadeia de custódia.');
        } else {
          setErro('Erro ao carregar a trilha de custódia.');
        }
      })
      .finally(() => setCarregando(false));
  }, [evidenciaId]);

  const etapasConcluidas = new Set(eventos.map((e) => e.etapa));

  if (carregando) return <p>Carregando trilha de custódia...</p>;
  if (erro) return <p className="erro">{erro}</p>;

  return (
    <div className="custodia-page">
      <h2>Cadeia de Custódia — Evidência {evidenciaId}</h2>
      <p className="upload-aviso">
        Trilha imutável conforme arts. 158-A a 158-F do CPP (Lei 13.964/19).
        Cada etapa abaixo foi registrada automaticamente pelo sistema.
      </p>

      <div className="custodia-progresso">
        {ETAPAS_ORDEM.map((etapa) => (
          <div
            key={etapa}
            className={`custodia-etapa-badge ${etapasConcluidas.has(etapa) ? 'concluida' : 'pendente'}`}
          >
            {LABEL_ETAPA[etapa]}
          </div>
        ))}
      </div>

      <table className="tabela-casos custodia-tabela">
        <thead>
          <tr>
            <th>Data/Hora</th>
            <th>Etapa</th>
            <th>Ação</th>
            <th>Usuário</th>
            <th>Hash no momento</th>
          </tr>
        </thead>
        <tbody>
          {eventos.map((evento, idx) => (
            <tr key={idx}>
              <td>{new Date(evento.timestamp).toLocaleString('pt-BR')}</td>
              <td>{LABEL_ETAPA[evento.etapa] ?? evento.etapa}</td>
              <td>{LABEL_ACAO[evento.acao] ?? evento.acao}</td>
              <td>{evento.usuario}</td>
              <td>
                <code className="hash-truncado" title={evento.hash_no_momento}>
                  {evento.hash_no_momento ? `${evento.hash_no_momento.slice(0, 12)}...` : '—'}
                </code>
              </td>
            </tr>
          ))}
          {eventos.length === 0 && (
            <tr>
              <td colSpan={5}>Nenhum evento de custódia registrado ainda.</td>
            </tr>
          )}
        </tbody>
      </table>

      <p className="custodia-voltar">
        <Link to="/casos">← Voltar aos inquéritos</Link>
      </p>
    </div>
  );
}
