# Próximos Passos de Desenvolvimento

## Backend
- [x] Implementar persistência real (Postgres) nos endpoints de casos/evidências.
- [x] Integrar MinIO real (upload/download com Object Lock).
- [x] Implementar autenticação completa (login, refresh token, MFA obrigatório).
- [x] Enforcement de RBAC nos endpoints de grafo e custódia.
- [x] Migrar `custodia_service.py` de memória para a tabela `custodia_log` (Postgres).
- [x] Integrar spaCy (NER) e Presidio (anonimização) na extração de entidades.
- [x] Integrar Whisper para transcrição de áudio.
- [x] Integrar ALPR real (fast-alpr com fallback openalpr) + extração EXIF/GEOINT.
- [x] Integrar OCR real (PaddleOCR com fallback Tesseract).
- [x] Publicar evento real em Kafka ao registrar evidência.
- [x] Persistir entidades extraídas (NLP) como nós/relacionamentos no Neo4j.
- [x] Implementar fila de retry/dead-letter (DLT) para falhas de publicação no Kafka.
- [x] Escrever testes de integração com banco de dados real (testcontainers) — valida trigger append-only.

## Mobile
- [x] Implementar leitura de arquivo binário (`react-native-fs`) em `hashService.js`.
- [x] Implementar SQLCipher real em `storage/db.js`.
- [x] Implementar autenticação biométrica (`react-native-biometrics` + `keyStoreService.js`).
- [x] Implementar "modo pânico" (apagamento seguro via `panicoService.js`).
- [ ] Implementar captura real de foto/áudio/vídeo (hoje é placeholder de UI).
- [ ] Persistir refresh token do backend de forma segura no Keychain.

## Web (Painel de Inteligência)
- [x] Estrutura inicial React + Vite + TypeScript.
- [x] Autenticação com MFA (`LoginPage` consumindo `POST /v1/auth/login`).
- [x] Dashboard de inquéritos com filtros (`DashboardPage`).
- [x] Detalhe de caso + padrões similares entre inquéritos (`CasoDetalhePage`).
- [x] Visualização interativa do grafo de vínculos via Cytoscape.js (`GrafoVinculosPage`).
- [x] RBAC visual (esconde ações sem permissão) — RBAC real permanece no backend.
- [x] Tela de upload/captura de evidências (`UploadEvidenciaPage`).
- [x] Visualizador de trilha de custódia (`CustodiaEvidenciaPage`).
- [ ] Dashboard de heatmap GEOINT.
- [ ] Tela de transcrição de áudio (`POST /v1/transcricao/audio`).
- [ ] Testes com Vitest + React Testing Library.

## Infraestrutura
- [x] Criar manifests Kubernetes em `infra/k8s/` (Deployment, HPA, NetworkPolicy Zero Trust).
- [ ] Configurar HashiCorp Vault para gestão de segredos (substituir `secrets.example.yaml`).
- [ ] Configurar SIEM recebendo logs de auditoria.
- [ ] Configurar Ingress + cert-manager para TLS automatico.
- [ ] Adicionar Deployment/Service Kubernetes para o painel web.

## Documentação/Compliance
- [x] Elaborar RIPD completo (`docs/RIPD.md`) — 12 seções, 8 riscos mapeados, pendências claras.
- [ ] Diagrama C4 completo em Mermaid.
- [ ] Documentar RBAC/ABAC detalhado por papel em `docs/RBAC.md`.

## CI/CD
- [x] Corrigir separação de dependências core/IA no CI (causa raiz de 18 runs falhos).
- [x] Corrigir SyntaxError em test_alpr_service.py.
- [x] Adicionar job `integration-tests` separado (roda testcontainers com Docker).

## Como continuar no VS Code
1. Clone o repositorio: `git clone https://github.com/idarlandias/-SIGIL-Sistema-Integrado-de-Intelig-ncia-e-Investiga-o-Criminal.git`
2. Abra a pasta como workspace raiz.
3. Instale as extensões recomendadas: Python, ESLint, Docker.
4. Rode `docker compose -f infra/docker/docker-compose.yml up -d` para levantar a infra local.
5. Ative o ambiente virtual Python e instale `backend/requirements.txt` (core) ou `requirements-ai.txt` (com modelos de IA).
6. Rode `pytest -m "not integration"` para os testes unitários rápidos, ou `pytest -m integration` (requer Docker) para os de integração.
7. Para autenticar: crie um usuário direto no Postgres, chame `/v1/auth/mfa/setup`
   com um token temporário, escaneie o QR e depois use `/v1/auth/login`.
8. Para deploy em cluster real: `kubectl apply -f infra/k8s/` (ajuste `secrets.example.yaml` primeiro).
9. Para o painel web: `cd web && npm install && npm run dev` (ver `web/README.md`).
10. Antes de qualquer uso com dados reais: revisar `docs/RIPD.md` com o Encarregado (DPO) da instituição.
11. Comece pelos itens marcados `TODO` nos arquivos de serviço.
