# Próximos Passos de Desenvolvimento

## Backend
- [ ] Implementar persistência real (Postgres) nos endpoints de casos/evidências.
- [ ] Integrar MinIO real (upload/download com Object Lock).
- [ ] Implementar autenticação completa (login, refresh token, MFA obrigatório).
- [ ] Integrar spaCy (modelo `pt_core_news_lg`) e Presidio na extração de entidades.
- [ ] Integrar Whisper para transcrição de áudio.
- [ ] Integrar OpenALPR/fast-alpr real no `alpr_service.py`.
- [ ] Escrever testes de integração com banco de dados real (testcontainers).

## Mobile
- [ ] Implementar leitura de arquivo binário (`react-native-fs`) em `hashService.js`.
- [ ] Implementar SQLCipher real em `storage/db.js`.
- [ ] Implementar tela de login com biometria (`react-native-biometrics`).
- [ ] Implementar captura real de foto/áudio/vídeo.
- [ ] Implementar "modo pânico" (apagamento seguro de dados locais).

## Infraestrutura
- [ ] Criar manifests Kubernetes em `infra/k8s/`.
- [ ] Configurar HashiCorp Vault para gestão de segredos.
- [ ] Configurar SIEM recebendo logs de auditoria.

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
7. Comece pelos itens marcados `TODO` nos arquivos de serviço.
