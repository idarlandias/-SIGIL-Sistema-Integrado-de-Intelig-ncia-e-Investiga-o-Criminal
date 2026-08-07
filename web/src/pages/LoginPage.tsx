import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/apiClient';
import { useAuthStore } from '../store/authStore';

/**
 * Login em duas etapas: matrícula + senha, seguido do código TOTP de 6
 * dígitos (MFA obrigatório, sem opção de bypass — espelha a exigência do
 * endpoint POST /v1/auth/login no backend).
 */
export default function LoginPage() {
  const [matricula, setMatricula] = useState('');
  const [senha, setSenha] = useState('');
  const [codigoMfa, setCodigoMfa] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setCarregando(true);

    try {
      const resposta = await apiClient.post('/auth/login', {
        matricula,
        senha,
        codigo_mfa: codigoMfa,
      });

      const { access_token, refresh_token } = resposta.data;
      const payload = JSON.parse(atob(access_token.split('.')[1]));

      login(access_token, refresh_token, { matricula: payload.sub, papel: payload.papel });
      navigate('/casos');
    } catch (err: any) {
      if (err.response?.status === 428) {
        setErro('MFA não configurado para este usuário. Contate o administrador.');
      } else {
        setErro('Matrícula, senha ou código MFA inválidos.');
      }
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>SIGIL</h1>
        <p>Sistema Integrado de Inteligência e Investigação Criminal</p>

        <label>
          Matrícula
          <input value={matricula} onChange={(e) => setMatricula(e.target.value)} required autoFocus />
        </label>

        <label>
          Senha
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required />
        </label>

        <label>
          Código MFA (6 dígitos)
          <input
            value={codigoMfa}
            onChange={(e) => setCodigoMfa(e.target.value)}
            maxLength={6}
            pattern="[0-9]{6}"
            required
          />
        </label>

        {erro && <p className="login-erro">{erro}</p>}

        <button type="submit" disabled={carregando}>
          {carregando ? 'Autenticando...' : 'Entrar'}
        </button>
      </form>
    </div>
  );
}
