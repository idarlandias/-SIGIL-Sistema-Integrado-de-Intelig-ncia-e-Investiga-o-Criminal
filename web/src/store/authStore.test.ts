import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from './authStore';

/**
 * Testa a logica de RBAC visual do frontend, que espelha
 * PERMISSOES_POR_PAPEL do backend (app/core/security.py). Este RBAC e
 * apenas cosmetico (esconde botoes/rotas) - o RBAC real e sempre
 * reforcado pelo backend em cada endpoint.
 */
describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('inicia deslogado por padrao', () => {
    const estado = useAuthStore.getState();
    expect(estado.autenticado).toBe(false);
    expect(estado.usuario).toBeNull();
    expect(estado.accessToken).toBeNull();
  });

  it('login popula o estado corretamente', () => {
    useAuthStore.getState().login('access-123', 'refresh-456', {
      matricula: 'MAT-001',
      papel: 'investigador',
    });

    const estado = useAuthStore.getState();
    expect(estado.autenticado).toBe(true);
    expect(estado.accessToken).toBe('access-123');
    expect(estado.refreshToken).toBe('refresh-456');
    expect(estado.usuario?.matricula).toBe('MAT-001');
  });

  it('logout limpa completamente o estado', () => {
    useAuthStore.getState().login('access-123', 'refresh-456', {
      matricula: 'MAT-001',
      papel: 'agente',
    });
    useAuthStore.getState().logout();

    const estado = useAuthStore.getState();
    expect(estado.autenticado).toBe(false);
    expect(estado.usuario).toBeNull();
    expect(estado.accessToken).toBeNull();
  });

  it('agente tem permissao de criar evidencia mas nao de ler grafo', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-001', papel: 'agente' });
    const { temPermissao } = useAuthStore.getState();

    expect(temPermissao('evidencias:criar')).toBe(true);
    expect(temPermissao('grafo:ler')).toBe(false);
  });

  it('investigador tem permissao de ler grafo mas nao de aprovar casos', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-002', papel: 'investigador' });
    const { temPermissao } = useAuthStore.getState();

    expect(temPermissao('grafo:ler')).toBe(true);
    expect(temPermissao('casos:aprovar')).toBe(false);
  });

  it('delegado tem permissao de aprovar casos e gerar relatorios', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-003', papel: 'delegado' });
    const { temPermissao } = useAuthStore.getState();

    expect(temPermissao('casos:aprovar')).toBe(true);
    expect(temPermissao('relatorios:gerar')).toBe(true);
  });

  it('administrador tem qualquer permissao (wildcard)', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-999', papel: 'administrador' });
    const { temPermissao } = useAuthStore.getState();

    expect(temPermissao('qualquer:coisa')).toBe(true);
    expect(temPermissao('custodia:registrar_etapa')).toBe(true);
  });

  it('usuario nao autenticado nunca tem permissao', () => {
    const { temPermissao } = useAuthStore.getState();
    expect(temPermissao('evidencias:ler')).toBe(false);
  });
});
