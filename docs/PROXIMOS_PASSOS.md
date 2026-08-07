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
- [x] Publicar evento real em Kafka ao registrar evidência.
- [ ] Escrever testes de integração com banco de dados real (testcontainers).
- [ ] Persistir entidades extraídas (NLP) como nós/relacionamentos no Neo4j (worker ainda tem TODO).
- [ ] Implementar fila de retry/dead-letter para falhas de publicação no Kafka.

## Mobile
- [x] Implementar leitura de arquivo binário (`react-native-fs`) em `hashService.js`.
- [x] Implementar SQLCipher real em `storage/db.js`.
- [x] Implementar autenticação biométrica (`react-native-biometrics` + `keyStoreService.js`).
- [x] Implementar "modo pânico" (apagamento seguro via `panicoService.js`).
- [ ] Implementar captura real de foto/áudio/vídeo (hoje é placeholder de UI).
- [ ] Persistir refresh token do backend de forma segura no Keychain.

## Web (Painel de Inteligência) — NOVO
- [x] Estrutura inicial React + Vite + TypeScript.
- [x] Autenticação com MFA (`LoginPage` consumindo `POST /v1/auth/login`).
- [x] Dashboard de inquéritos com filtros (`DashboardPage`).
- [x] Detalhe de caso + padrões similares entre inquéritos (`CasoDetalhePage`).
- [x] Visualização interativa do grafo de vínculos via Cytoscape.js (`GrafoVinculosPage`).
- [x] RBAC visual (esconde ações sem permissão) — RBAC real permanece no backend.
- [ ] Tela de upload/captura de evidências (`POST /v1/evidencias`).
- [ ] Visualizador de trilha de custódia (`GET /v1/custodia/{evidencia_id}`).
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
- [ ] Elaborar RIPD completo.
- [ ] Diagrama C4 completo em Mermaid.
- [ ] Documentar RBAC/ABAC detalhado por papel em `docs/RBAC.md`.

## Como continuar no VS Code
1. Clone o repositorio: `git clone https://github.com/idarlandias/-SIGIL-Sistema-Integrado-de-Intelig-ncia-e-Investiga-o-Criminal.git`
2. Abra a pasta como workspace raiz.
3. Instale as extensões recomendadas: Python, ESLint, Docker.
4. Rode `docker compose -f infra/docker/docker-compose.yml up -d` para levantar a infra local.
5. Ative o ambiente virtual Python e instale `backend/requirements.txt`.
6. Rode `pytest` em `backend/` para validar o esqueleto de testes.
7. Para autenticar: crie um usuário direto no Postgres, chame `/v1/auth/mfa/setup`
   com um token temporário, escaneie o QR e depois use `/v1/auth/login`.
8. Para deploy em cluster real: `kubectl apply -f infra/k8s/` (ajuste `secrets.example.yaml` primeiro).
9. Para modelos de IA reais, instale opcionalmente: `python -m spacy download pt_core_news_lg`,
   `pip install fast-alpr exifread` (Whisper e spaCy/Presidio já estão no requirements.txt).
10. Para o painel web: `cd web && npm install && npm run dev` (ver `web/README.md`).
11. Comece pelos itens marcados `TODO` nos arquivos de serviço.
