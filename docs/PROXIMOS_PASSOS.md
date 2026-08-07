# Próximos Passos de Desenvolvimento

## Backend
- [x] Implementar persistência real (Postgres) nos endpoints de casos/evidências.
- [x] Integrar MinIO real (upload/download com Object Lock).
- [x] Implementar autenticação completa (login, refresh token, MFA obrigatório).
- [x] Enforcement de RBAC nos endpoints de grafo e custódia.
- [ ] Integrar spaCy (modelo `pt_core_news_lg`) e Presidio na extração de entidades.
- [ ] Integrar Whisper para transcrição de áudio.
- [ ] Integrar OpenALPR/fast-alpr real no `alpr_service.py`.
- [ ] Publicar evento real em Kafka ao registrar evidência (hoje é TODO em `evidencias.py`).
- [ ] Escrever testes de integração com banco de dados real (testcontainers).
- [ ] Migrar `custodia_service.py` de memória para a tabela `custodia_log` (Postgres).

## Mobile
- [ ] Implementar leitura de arquivo binário (`react-native-fs`) em `hashService.js`.
- [ ] Implementar SQLCipher real em `storage/db.js`.
- [ ] Implementar tela de login com biometria (`react-native-biometrics`).
- [ ] Implementar captura real de foto/áudio/vídeo.
- [ ] Implementar "modo pânico" (apagamento seguro de dados locais).

## Infraestrutura
- [x] Criar manifests Kubernetes em `infra/k8s/` (Deployment, HPA, NetworkPolicy Zero Trust).
- [ ] Configurar HashiCorp Vault para gestão de segredos (substituir `secrets.example.yaml`).
- [ ] Configurar SIEM recebendo logs de auditoria.
- [ ] Configurar Ingress + cert-manager para TLS automatico.

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
9. Comece pelos itens marcados `TODO` nos arquivos de serviço.
