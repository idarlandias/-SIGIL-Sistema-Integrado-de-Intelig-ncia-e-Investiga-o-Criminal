import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Layout() {
  const { usuario, logout, temPermissao } = useAuthStore();
  const navigate = useNavigate();

  function sair() {
    logout();
    navigate('/login');
  }

  return (
    <div className="layout">
      <header className="layout-header">
        <h1>SIGIL</h1>
        <nav>
          <Link to="/casos">Inquéritos</Link>
          {(temPermissao('evidencias:criar') || temPermissao('evidencias:ler_propria')) && (
            <Link to="/evidencias/nova">Nova Evidência</Link>
          )}
          {temPermissao('custodia:ler') && <Link to="/custodia">Cadeia de Custódia</Link>}
          {temPermissao('evidencias:ler') && <Link to="/geoint">GEOINT</Link>}
          {temPermissao('evidencias:criar') && <Link to="/transcricao">Transcrição</Link>}
        </nav>
        <div className="layout-usuario">
          <span>{usuario?.matricula} ({usuario?.papel})</span>
          <button onClick={sair}>Sair</button>
        </div>
      </header>
      <main className="layout-conteudo">
        <Outlet />
      </main>
    </div>
  );
}
