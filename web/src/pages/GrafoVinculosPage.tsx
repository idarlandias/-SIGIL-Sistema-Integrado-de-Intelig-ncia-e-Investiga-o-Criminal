import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../services/apiClient';
import GrafoVinculosCanvas from '../components/GrafoVinculosCanvas';

/**
 * Página de análise de vínculos — consome GET /v1/grafo/pessoa/{cpf}/rede,
 * protegido por RBAC no backend (permissão "grafo:ler"). Permite ajustar
 * a profundidade da busca (1 a 3 graus de separação).
 */
export default function GrafoVinculosPage() {
  const { cpf } = useParams<{ cpf: string }>();
  const [dadosRede, setDadosRede] = useState<any[]>([]);
  const [profundidade, setProfundidade] = useState(2);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!cpf) return;
    buscarRede();
  }, [cpf, profundidade]);

  async function buscarRede() {
    setCarregando(true);
    setErro(null);
    try {
      const resposta = await apiClient.get(`/grafo/pessoa/${cpf}/rede`, {
        params: { profundidade },
      });
      setDadosRede(resposta.data);
    } catch (err: any) {
      if (err.response?.status === 403) {
        setErro('Seu papel não tem permissão para consultar o grafo de vínculos.');
      } else {
        setErro('Erro ao carregar a rede de vínculos.');
      }
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="grafo-vinculos-page">
      <h2>Rede de Vínculos — CPF {cpf}</h2>

      <label>
        Profundidade (graus de separação):
        <select value={profundidade} onChange={(e) => setProfundidade(Number(e.target.value))}>
          <option value={1}>1</option>
          <option value={2}>2</option>
          <option value={3}>3</option>
        </select>
      </label>

      {erro && <p className="erro">{erro}</p>}
      {carregando && <p>Carregando rede...</p>}

      {!carregando && !erro && cpf && (
        <GrafoVinculosCanvas cpfCentral={cpf} dadosRede={dadosRede} />
      )}
    </div>
  );
}
