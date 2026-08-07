/**
 * Store de autenticação (Zustand). Persiste tokens em memória — nunca em
 * localStorage, para reduzir superfície de ataque via XSS. Ao recarregar
 * a página, o usuário precisa autenticar novamente (aceitável para um
 * painel de inteligência policial, onde sessões longas são um risco).
 */
import { create } from 'zustand';

interface Usuario {
  matricula: string;
  papel: 'agente' | 'investigador' | 'delegado' | 'perito' | 'administrador';
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  usuario: Usuario | null;
  autenticado: boolean;
  login: (accessToken: string, refreshToken: string, usuario: Usuario) => void;
  logout: () => void;
  temPermissao: (permissao: string) => boolean;
}

const PERMISSOES_POR_PAPEL: Record<string, string[]> = {
  agente: ['evidencias:criar', 'evidencias:ler_propria', 'custodia:ler_propria'],
  investigador: ['evidencias:criar', 'evidencias:ler', 'grafo:ler', 'custodia:ler', 'casos:ler', 'casos:editar'],
  delegado: ['evidencias:ler', 'grafo:ler', 'grafo:editar', 'custodia:ler', 'casos:ler', 'casos:editar', 'casos:aprovar', 'relatorios:gerar'],
  perito: ['evidencias:ler', 'evidencias:processar', 'custodia:ler', 'custodia:registrar_etapa'],
  administrador: ['*'],
};

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,
  usuario: null,
  autenticado: false,

  login: (accessToken, refreshToken, usuario) =>
    set({ accessToken, refreshToken, usuario, autenticado: true }),

  logout: () => set({ accessToken: null, refreshToken: null, usuario: null, autenticado: false }),

  temPermissao: (permissao: string) => {
    const papel = get().usuario?.papel;
    if (!papel) return false;
    const permissoes = PERMISSOES_POR_PAPEL[papel] ?? [];
    return permissoes.includes('*') || permissoes.includes(permissao);
  },
}));
