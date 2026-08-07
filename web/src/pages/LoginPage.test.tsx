import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import apiClient from '../services/apiClient';
import { useAuthStore } from '../store/authStore';

vi.mock('../services/apiClient');

/**
 * Valida o fluxo de login em duas etapas (matricula+senha+codigo MFA),
 * espelhando a exigencia de MFA obrigatorio do endpoint real
 * POST /v1/auth/login no backend - sem opcao de bypass.
 */
function gerarJwtFalso(papel: string, matricula: string): string {
  const payload = btoa(JSON.stringify({ sub: matricula, papel }));
  return `header.${payload}.assinatura`;
}

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.getState().logout();
    vi.clearAllMocks();
  });

  it('renderiza os tres campos obrigatorios do login', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/matrícula/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/código mfa/i)).toBeInTheDocument();
  });

  it('autentica com sucesso e popula o authStore', async () => {
    const accessToken = gerarJwtFalso('investigador', 'MAT-001');
    (apiClient.post as any).mockResolvedValueOnce({
      data: { access_token: accessToken, refresh_token: 'refresh-abc' },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const usuario = userEvent.setup();
    await usuario.type(screen.getByLabelText(/matrícula/i), 'MAT-001');
    await usuario.type(screen.getByLabelText(/senha/i), 'senha-segura');
    await usuario.type(screen.getByLabelText(/código mfa/i), '123456');
    await usuario.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(useAuthStore.getState().autenticado).toBe(true);
    });
    expect(useAuthStore.getState().usuario?.papel).toBe('investigador');
  });

  it('exibe mensagem de erro quando o codigo MFA e invalido', async () => {
    (apiClient.post as any).mockRejectedValueOnce({ response: { status: 401 } });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const usuario = userEvent.setup();
    await usuario.type(screen.getByLabelText(/matrícula/i), 'MAT-001');
    await usuario.type(screen.getByLabelText(/senha/i), 'senha-errada');
    await usuario.type(screen.getByLabelText(/código mfa/i), '000000');
    await usuario.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(screen.getByText(/matrícula, senha ou código mfa inválidos/i)).toBeInTheDocument();
    });
    expect(useAuthStore.getState().autenticado).toBe(false);
  });

  it('avisa quando MFA nao esta configurado (HTTP 428)', async () => {
    (apiClient.post as any).mockRejectedValueOnce({ response: { status: 428 } });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const usuario = userEvent.setup();
    await usuario.type(screen.getByLabelText(/matrícula/i), 'MAT-002');
    await usuario.type(screen.getByLabelText(/senha/i), 'senha');
    await usuario.type(screen.getByLabelText(/código mfa/i), '111111');
    await usuario.click(screen.getByRole('button', { name: /entrar/i }));

    await waitFor(() => {
      expect(screen.getByText(/mfa não configurado/i)).toBeInTheDocument();
    });
  });
});
