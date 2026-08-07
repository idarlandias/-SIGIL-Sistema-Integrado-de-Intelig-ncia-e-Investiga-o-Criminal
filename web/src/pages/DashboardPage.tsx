import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../services/apiClient';

interface Caso {
  numero: string;
  delegacia: string;
  status: string;
  data_abertura: string;
}

/**
 * Lista de inquéritos, consumindo GET /v1/casos com filtros opcionais
 * por status e delegacia — espelha os query params do endpoint real.
 */
export default function DashboardPage() {
  const [casos, setCasos] = useState<Caso[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [filtroStatus, setFiltroStatus] = useState('');

  useEffect(() => {
    buscarCasos();
  }, [filtroStatus]);

  async function buscarCasos() {
    setCarregando(true);
    try {
      const params = filtroStatus ? { status_filtro: filtroStatus } : {};
      const resposta = await apiClient.get('/casos', { params });
      setCasos(resposta.data.casos);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="dashboard-page">
      <h2>Inquéritos</h2>

      <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)}>
        <option value="">Todos os status</option>
        <option value="em_andamento">Em andamento</option>
        <option value="concluido">Concluído</option>
        <option value="arquivado">Arquivado</option>
      </select>

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <table className="tabela-casos">
          <thead>
            <tr>
              <th>Número</th>
              <th>Delegacia</th>
              <th>Status</th>
              <th>Abertura</th>
            </tr>
          </thead>
          <tbody>
            {casos.map((caso) => (
              <tr key={caso.numero}>
                <td>
                  <Link to={`/casos/${caso.numero}`}>{caso.numero}</Link>
                </td>
                <td>{caso.delegacia}</td>
                <td>{caso.status}</td>
                <td>{new Date(caso.data_abertura).toLocaleDateString('pt-BR')}</td>
              </tr>
            ))}
            {casos.length === 0 && (
              <tr>
                <td colSpan={4}>Nenhum inquérito encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
