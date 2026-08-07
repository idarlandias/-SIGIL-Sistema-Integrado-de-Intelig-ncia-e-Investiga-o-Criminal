import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Ponto de entrada para consultar a cadeia de custódia de uma evidência
 * pelo seu ID (UUID retornado no registro). Redireciona para a página
 * de detalhe da trilha (CustodiaEvidenciaPage).
 */
export default function BuscarCustodiaPage() {
  const [evidenciaId, setEvidenciaId] = useState('');
  const navigate = useNavigate();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (evidenciaId.trim()) {
      navigate(`/custodia/${evidenciaId.trim()}`);
    }
  }

  return (
    <div className="buscar-custodia-page">
      <h2>Consultar Cadeia de Custódia</h2>
      <form className="upload-form" onSubmit={handleSubmit}>
        <label>
          ID da evidência
          <input
            value={evidenciaId}
            onChange={(e) => setEvidenciaId(e.target.value)}
            placeholder="UUID retornado no registro da evidência"
            required
          />
        </label>
        <button type="submit">Consultar Trilha</button>
      </form>
    </div>
  );
}
