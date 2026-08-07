import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RotaProtegida from './RotaProtegida';
import { useAuthStore } from '../store/authStore';

/**
 * Valida o comportamento de RotaProtegida: bloqueia navegacao para
 * usuarios nao autenticados (redireciona para /login) e para usuarios
 * sem a permissao RBAC exigida (exibe mensagem de acesso negado), sem
 * jamais expor o conteudo protegido nesses dois casos.
 */
function renderComRota(permissaoExigida?: string) {
  return render(
    <MemoryRouter initialEntries={['/area-restrita']}>
      <Routes>
        <Route path="/login" element={<div>Página de Login</div>} />
        <Route
          path="/area-restrita"
          element={
            <RotaProtegida permissaoExigida={permissaoExigida}>
              <div>Conteúdo Protegido</div>
            </RotaProtegida>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

describe('RotaProtegida', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
  });

  it('redireciona para /login quando o usuario nao esta autenticado', () => {
    renderComRota();
    expect(screen.getByText('Página de Login')).toBeInTheDocument();
    expect(screen.queryByText('Conteúdo Protegido')).not.toBeInTheDocument();
  });

  it('exibe o conteudo quando autenticado e sem restricao de permissao', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-001', papel: 'agente' });
    renderComRota();
    expect(screen.getByText('Conteúdo Protegido')).toBeInTheDocument();
  });

  it('bloqueia acesso quando autenticado mas sem a permissao exigida', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-001', papel: 'agente' });
    renderComRota('grafo:ler');
    expect(screen.queryByText('Conteúdo Protegido')).not.toBeInTheDocument();
    expect(screen.getByText(/não tem permissão/i)).toBeInTheDocument();
  });

  it('permite acesso quando autenticado e com a permissao exigida', () => {
    useAuthStore.getState().login('t', 'r', { matricula: 'MAT-001', papel: 'delegado' });
    renderComRota('grafo:ler');
    expect(screen.getByText('Conteúdo Protegido')).toBeInTheDocument();
  });
});
