import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

interface Props {
  children: React.ReactNode;
  permissaoExigida?: string;
}

/**
 * Bloqueia acesso a rotas quando o usuário não está autenticado, e
 * opcionalmente exige uma permissão RBAC específica (ex.: "grafo:ler").
 */
export default function RotaProtegida({ children, permissaoExigida }: Props) {
  const { autenticado, temPermissao } = useAuthStore();

  if (!autenticado) {
    return <Navigate to="/login" replace />;
  }

  if (permissaoExigida && !temPermissao(permissaoExigida)) {
    return <div className="acesso-negado">Seu papel não tem permissão para acessar esta área.</div>;
  }

  return <>{children}</>;
}
