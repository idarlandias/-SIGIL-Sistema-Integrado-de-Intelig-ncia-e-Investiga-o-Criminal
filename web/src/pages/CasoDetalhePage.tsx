import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../services/apiClient';

interface DetalheCaso {
  numero: string;
  delegacia: string;
  status: string;
  data_abertura: string;
  total_evidencias: number;
}

interface PadraoRelacionado {
  inquerito_relacionado: string;
  criterio: string;
  score: number;
}

/**
 * Detalhe de um inquérito: metadados + inquéritos com padrão similar
 * (GET /v1/casos/{numero} e GET /v1/grafo/inqueritos/padroes).
 */
export default function CasoDetalhePage() {
  const { numero } = useParams<{ numero: string }>();
  const [caso, setCaso] = useState<DetalheCaso | null>(null);
  const [padroes, setPadroes] = useState<PadraoRelacionado[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!numero) return;

    apiClient
      .get(`/casos/${numero}`)
      .then((resp) => setCaso(resp.data))
      .catch(() => setErro('Inquérito não encontrado.'));

    apiClient
      .get('/grafo/inqueritos/padroes', { params: { numero_inquerito: numero } })
      .then((resp) => setPadroes(resp.data))
      .catch(() => setPadroes([]));
  }, [numero]);

  if (erro) return <p className="erro">{erro}</p>;
  if (!caso) return <p>Carregando...</p>;

  return (
    <div className="caso-detalhe-page">
      <h2>Inquérito {caso.numero}</h2>
      <dl>
        <dt>Delegacia</dt>
        <dd>{caso.delegacia}</dd>
        <dt>Status</dt>
        <dd>{caso.status}</dd>
        <dt>Data de abertura</dt>
        <dd>{new Date(caso.data_abertura).toLocaleDateString('pt-BR')}</dd>
        <dt>Total de evidências</dt>
        <dd>{caso.total_evidencias}</dd>
      </dl>

      <h3>Padrões similares detectados</h3>
      {padroes.length === 0 ? (
        <p>Nenhum padrão similar encontrado com outros inquéritos.</p>
      ) : (
        <ul className="lista-padroes">
          {padroes.map((p) => (
            <li key={p.inquerito_relacionado}>
              <Link to={`/casos/${p.inquerito_relacionado}`}>{p.inquerito_relacionado}</Link>
              {' — '}
              {p.criterio} (score: {p.score.toFixed(2)})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
