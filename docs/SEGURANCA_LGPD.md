# Segurança, LGPD e Validade Jurídica das Provas

## Cadeia de Custódia (Lei 13.964/19 — arts. 158-A a 158-F do CPP)

Dez etapas obrigatórias, cada uma registrada automaticamente pelo sistema:

1. Reconhecimento
2. Isolamento
3. Fixação
4. Coleta
5. Acondicionamento
6. Transporte
7. Recebimento
8. Processamento
9. Armazenamento
10. Descarte

Implementação: tabela `custodia_log` (Postgres) é **append-only**, protegida por
trigger que bloqueia `UPDATE`/`DELETE` (ver `db/postgres/migrations/001_init.sql`).
Toda leitura de evidência (`GET /v1/evidencias/{id}`) também gera um evento
`acessado`, conforme exigência de auditoria completa.

## LGPD (Lei 13.709/18)

- **Base legal:** art. 23 — tratamento de dados por autoridades de segurança
  pública e persecução penal.
- **Minimização:** uso de Microsoft Presidio para mascarar CPFs e dados
  sensíveis fora do escopo direto do inquérito antes de exibição/exportação.
- **Retenção:** definir prazo de retenção por tipo de dado e automatizar
  anonimização/descarte ao final do prazo legal.
- **RIPD:** produzir Relatório de Impacto à Proteção de Dados antes do deploy
  em produção, submetido ao DPO da instituição.

## Requisitos Técnicos de Segurança

- MFA obrigatório (TOTP) para todos os perfis — ver `app/core/security.py`.
- RBAC por papel funcional (agente, investigador, delegado, perito, administrador)
  — ver `PERMISSOES_POR_PAPEL` em `app/core/security.py`.
- TLS 1.3 em trânsito; AES-256 em repouso (MinIO server-side encryption).
- Arquitetura Zero Trust: segmentação de rede entre serviços no Kubernetes.
- SAST no pipeline CI (Bandit) — ver `.github/workflows/ci.yml`.
- Auditoria centralizada: encaminhar `custodia_log` e logs de acesso para SIEM.

## Checklist Pré-Produção

- [ ] Pentest completo da API e do app mobile.
- [ ] Revisão jurídica do fluxo de cadeia de custódia por perito criminal.
- [ ] RIPD aprovado pelo DPO.
- [ ] Rotação de segredos via vault (ex.: HashiCorp Vault).
- [ ] Testes de carga no pipeline Kafka/workers.
- [ ] Plano de resposta a incidentes e backup/disaster recovery testado.
