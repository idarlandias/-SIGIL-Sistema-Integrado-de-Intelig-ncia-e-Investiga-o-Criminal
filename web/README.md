# SIGIL Web — Painel de Inteligência

Painel do analista/delegado/perito: gestão de inquéritos e análise de vínculos
via grafo interativo (Cytoscape.js), consumindo a API FastAPI em `backend/`.

## Stack

- React 18 + TypeScript + Vite
- React Router para navegação
- Zustand para estado de autenticação (tokens mantidos em memória, nunca em localStorage)
- Cytoscape.js para renderização do grafo de vínculos
- Axios com interceptor de JWT e logout automático em 401

## Como rodar

```bash
cd web
npm install
cp .env.example .env
npm run dev
```

A aplicação abre em `http://localhost:5173` e faz proxy de `/v1/*` para o
backend em `http://localhost:8000` (configurado em `vite.config.ts`).

## Estrutura

```
web/src/
├── components/    # RotaProtegida, Layout, GrafoVinculosCanvas
├── pages/         # LoginPage, DashboardPage, CasoDetalhePage, GrafoVinculosPage
├── services/      # apiClient (axios com interceptors)
├── store/         # authStore (Zustand)
└── styles/        # CSS global
```

## Fluxo de autenticação

1. `LoginPage` envia matrícula + senha + código MFA para `POST /v1/auth/login`.
2. O `access_token` (JWT) é decodificado no cliente para extrair `papel` e
   popular o `authStore` — usado para RBAC visual (esconder botões/rotas).
3. O RBAC **real** continua sendo aplicado no backend; o frontend apenas
   evita mostrar ações que o usuário não teria permissão de executar.
4. `RotaProtegida` bloqueia acesso a rotas sem autenticação ou sem a
   permissão exigida.

## Próximos passos

- [ ] Tela de captura/upload de evidências (consumindo `POST /v1/evidencias`).
- [ ] Visualizador de trilha de custódia (`GET /v1/custodia/{evidencia_id}`).
- [ ] Dashboard de heatmap GEOINT (manchas criminais, rotas de fuga).
- [ ] Integração com endpoint de transcrição (`POST /v1/transcricao/audio`).
- [ ] Testes com Vitest + React Testing Library.
