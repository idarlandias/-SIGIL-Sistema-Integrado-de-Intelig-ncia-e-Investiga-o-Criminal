import { useEffect, useState } from 'react';
import apiClient from '../services/apiClient';
import HeatmapGeoint from '../components/HeatmapGeoint';

interface Ponto {
  lat: number;
  lon: number;
  tipo: string;
  capturado_em: string;
  evidencia_id: string;
}

/**
 * Dashboard de heatmap GEOINT — consome GET /v1/geoint/pontos, protegido
 * por RBAC no backend (permissão "evidencias:ler"). Permite filtrar por
 * inquérito para visualizar a mancha criminal de um caso específico, ou
 * ver todos os pontos disponíveis quando nenhum filtro é aplicado.
 */
export default function HeatmapGeointPage() {
  const [pontos, setPontos] = useState<Ponto[]>([]);
  const [inqueritoNumero, setInqueritoNumero] = useState('');
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    buscarPontos();
  }, [inqueritoNumero]);

  async function buscarPontos() {
    setCarregando(true);
    setErro(null);
    try {
      const params = inqueritoNumero ? { inquerito_numero: inqueritoNumero } : {};
      const resposta = await apiClient.get('/geoint/pontos', { params });
      setPontos(resposta.data.pontos);
    } catch (err: any) {
      if (err.response?.status === 403) {
        setErro('Seu papel não tem permissão para consultar dados GEOINT.');
      } else {
        setErro('Erro ao carregar os pontos geográficos.');
      }
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="heatmap-page">
      <h2>Heatmap GEOINT — Manchas Criminais</h2>
      <p className="upload-aviso">
        Concentração espacial das evidências coletadas em campo. Filtre por
        inquérito para analisar a mancha criminal de um caso específico.
      </p>

      <div className="heatmap-filtros">
        <input
          className="upload-form-input"
          placeholder="Filtrar por número de inquérito (opcional)"
          value={inqueritoNumero}
          onChange={(e) => setInqueritoNumero(e.target.value)}
        />
      </div>

      {erro && <p className="erro">{erro}</p>}
      {carregando && <p>Carregando pontos...</p>}

      {!carregando && !erro && (
        <>
          <p>{pontos.length} ponto(s) com geolocalização encontrado(s).</p>
          <HeatmapGeoint pontos={pontos} />
        </>
      )}
    </div>
  );
}
