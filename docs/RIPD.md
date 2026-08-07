# Relatório de Impacto à Proteção de Dados Pessoais (RIPD)
## Sistema SIGIL — Sistema Integrado de Inteligência e Investigação Criminal

**Versão:** 1.0 — Rascunho para revisão jurídica e aprovação do Encarregado (DPO)
**Base normativa:** Lei nº 13.709/2018 (LGPD), arts. 5º, XVII e 38; Lei nº 13.964/2019 (Pacote Anticrime), arts. 158-A a 158-F do CPP.
**Status:** Documento de referência técnica — requer validação por profissional jurídico e aprovação formal do Encarregado antes de qualquer operação em produção.

---

## 1. Identificação dos Agentes de Tratamento e do Encarregado

| Papel | Responsável |
|---|---|
| Controlador | Órgão de Polícia Civil operador do sistema (a ser definido pela instituição) |
| Operador | Equipe técnica responsável pela infraestrutura (backend, banco de dados, nuvem/on-premise) |
| Encarregado (DPO) | A ser formalmente designado pela instituição antes do go-live |
| Desenvolvedor/Arquitetura de referência | Documentação técnica elaborada como estudo de arquitetura GovTech |

> **Pendência crítica:** este RIPD é um modelo de referência. A instituição que for operacionalizar o SIGIL deve designar formalmente seu Encarregado e preencher esta seção com os dados reais antes de submeter à ANPD ou a qualquer auditoria.

---

## 2. Partes Interessadas Consultadas

- Delegados, investigadores, peritos e agentes (usuários finais do sistema, papéis definidos em RBAC).
- Titulares dos dados: suspeitos, vítimas, testemunhas e terceiros mencionados em inquéritos.
- Encarregado de Dados (DPO) da instituição.
- Corregedoria/Controle interno da Polícia Civil.
- Ministério Público (fiscal externo da persecução penal).

> Recomenda-se consulta formal a cada uma dessas partes antes da aprovação final deste relatório, com atas registradas.

---

## 3. Justificativa da Necessidade de Elaboração do Relatório

O SIGIL realiza tratamento de dados pessoais em larga escala, incluindo **dados sensíveis** (art. 5º, II da LGPD) — biométricos (login com biometria), dados de investigação criminal que podem revelar opinião política, filiação, ou informações de saúde mencionadas em depoimentos — e utiliza **novas tecnologias com impacto relevante** sobre os titulares: inteligência artificial (NLP, reconhecimento facial-adjacente via biometria, análise de vínculos em grafo, reconhecimento de padrões entre investigados).

Conforme orientação da ANPD, essas três condições — dados sensíveis, biometria e novas tecnologias de alto impacto — tornam a elaboração do RIPD **obrigatória antes da operação em produção**, não apenas recomendável.

---

## 4. Escopo do Relatório de Impacto

Este relatório cobre:
- O **backend** (API FastAPI, banco PostgreSQL, grafo Neo4j, armazenamento MinIO).
- O **aplicativo móvel** de campo (captura de evidências, biometria local, sincronização offline).
- O **painel web** de inteligência (análise de vínculos, upload de evidências, consulta de custódia).
- O **pipeline de IA** (OCR, transcrição de áudio, extração de entidades, reconhecimento de placas).

Não cobre integrações externas ainda não implementadas (ex.: SpiderFoot/OSINT em produção, Vault, SIEM) — estas exigirão adendo a este RIPD quando forem efetivamente conectadas a dados reais.

---

## 5. Finalidades do Tratamento

| Finalidade | Base no sistema |
|---|---|
| Investigação criminal e produção de prova | Módulo de evidências, cadeia de custódia |
| Análise de vínculos entre pessoas, veículos, contas e organizações | Grafo Neo4j |
| Identificação de padrões entre inquéritos distintos | Busca vetorial + grafo |
| Autenticação segura de agentes/investigadores | MFA, biometria, RBAC |
| Transcrição e sumarização de depoimentos/escutas autorizadas | Whisper, spaCy |
| Geolocalização de evidências e rotas | GPS do app + EXIF de imagens |

Todas as finalidades estão vinculadas à persecução penal e à segurança pública, conforme art. 4º, III, "b" da LGPD (tratamento realizado para fins exclusivos de segurança pública, defesa nacional, segurança do Estado ou atividades de investigação e repressão de infrações penais).

---

## 6. Natureza dos Dados Tratados

| Categoria | Exemplos no SIGIL | Sensibilidade |
|---|---|---|
| Identificação | Nome, CPF, matrícula funcional | Pessoal comum |
| Biométricos | Login por Face ID/Touch ID/impressão digital (app mobile) | **Sensível** (art. 5º, II) |
| Localização | GPS de evidências, EXIF de imagens | Pessoal comum, mas revela padrões de deslocamento |
| Comunicações | Transcrições de depoimentos e escutas autorizadas | Pode conter dados sensíveis incidentais (saúde, opinião política, orientação) |
| Financeiros | Contas/chaves PIX mencionadas em investigações | Pessoal comum, alto risco reputacional |
| Veiculares | Placas detectadas via ALPR | Pessoal comum, vinculável a movimentação |
| Metadados de acesso | Logs de custódia (quem acessou, quando, o quê) | Pessoal comum, mas crítico para auditoria |

**Dados de terceiros não investigados:** o sistema pode capturar incidentalmente dados de pessoas mencionadas em depoimentos ou fotografadas em evidências sem serem o foco da investigação. Isso exige atenção redobrada de minimização (Seção 9).

---

## 7. Descrição do Tratamento

### 7.1 Ciclo de vida do dado

1. **Coleta**: agente captura evidência em campo (foto/áudio/vídeo/documento) via app mobile, ou upload no painel web.
2. **Trânsito**: dados são transmitidos via TLS/mTLS ao backend.
3. **Processamento**: pipeline assíncrono (Kafka) aciona OCR, transcrição (Whisper), extração de entidades (spaCy/regex), ALPR e EXIF.
4. **Armazenamento**: metadados em PostgreSQL; binários em MinIO com Object Lock (WORM, retenção de 5 anos); relações em Neo4j.
5. **Acesso**: investigadores/delegados/peritos consultam via API, sujeitos a RBAC e MFA.
6. **Auditoria**: toda leitura/escrita gera registro imutável em `custodia_log` (append-only, protegido por trigger de banco).
7. **Retenção e descarte**: **pendente de definição formal** — ver Seção 10, risco R-05.

### 7.2 Fluxo de dados (referência)

App Mobile → API Gateway (TLS/mTLS) → Backend FastAPI → PostgreSQL/MinIO/Neo4j → Pipeline Kafka (IA) → Painel Web.

---

## 8. Base Legal do Tratamento

| Base legal | Artigo LGPD | Aplicação no SIGIL |
|---|---|---|
| Cumprimento de obrigação legal/regulatória pelo controlador | Art. 7º, II | Dever legal de investigação criminal |
| Execução de políticas públicas de segurança pública | Art. 23 | Atividade típica de persecução penal |
| Tratamento de dados sensíveis para cumprimento de obrigação legal | Art. 11, II, "a" | Biometria para autenticação de agentes |
| Proteção da vida ou incolumidade física do titular ou terceiro | Art. 11, II, "e" | Justifica tratamento de dados sensíveis incidentais em investigações |

> **Importante:** o art. 4º, III da LGPD estabelece regime específico (não a LGPD integralmente) para tratamento por autoridades de segurança pública com finalidade exclusiva de investigação e repressão de infrações penais — mas isso **não dispensa** a adoção de medidas de segurança, governança e boas práticas, que devem ser objeto de legislação específica (ainda pendente de regulamentação detalhada no Brasil). Este RIPD adota, por precaução, os padrões da LGPD geral como piso mínimo.

---

## 9. Avaliação Principiológica e Demais Requisitos Legais

| Princípio (art. 6º LGPD) | Avaliação no SIGIL |
|---|---|
| Finalidade | ✅ Finalidades específicas documentadas (Seção 5) |
| Adequação | ✅ Tratamento compatível com finalidade de investigação criminal |
| Necessidade | ⚠️ **Requer revisão**: captura de EXIF/GPS pode coletar mais dados que o estritamente necessário — avaliar limitação de campos coletados |
| Livre acesso | ⚠️ Direitos do titular (acesso, correção) **não implementados** — ver risco R-01 |
| Qualidade dos dados | ✅ Hash SHA-256 garante integridade; validação de schema via Pydantic |
| Transparência | ⚠️ Não há aviso de privacidade voltado a titulares de investigação (esperado, dado o sigilo processual, mas deve constar de política institucional) |
| Segurança | ✅ MFA, RBAC, TLS, criptografia em repouso, cadeia de custódia imutável |
| Prevenção | ✅ Object Lock/WORM previne alteração; trigger de banco previne adulteração de logs |
| Não discriminação | ⚠️ **Requer avaliação**: uso de IA (NLP, ALPR) para inferências sobre indivíduos deve ser auditado periodicamente para viés algorítmico |
| Responsabilização e prestação de contas | ⚠️ Depende da designação formal do Encarregado (Seção 1) |

---

## 10. Inventário e Análise de Riscos

| ID | Risco | Probabilidade | Impacto | Mitigação proposta |
|---|---|---|---|---|
| R-01 | Ausência de mecanismo formal de atendimento a direitos do titular (mesmo que restritos em investigação em curso) | Média | Alto | Definir procedimento institucional de resposta a solicitações, compatível com sigilo processual |
| R-02 | Vazamento de dados sensíveis (biometria, depoimentos) por comprometimento de credenciais | Média | Crítico | MFA já mitiga parcialmente; recomenda-se rotação de credenciais e monitoramento de anomalias (SIEM — pendente) |
| R-03 | Retenção indefinida de dados de pessoas não indiciadas mencionadas incidentalmente | Alta | Alto | Definir política de retenção e expurgo automatizado (pendente de implementação) |
| R-04 | Viés algorítmico em NLP/ALPR gerando falsos positivos que impactam pessoas inocentes | Média | Alto | Revisão humana obrigatória antes de qualquer ação com base em inferência automatizada; auditoria periódica de acurácia por perfil demográfico |
| R-05 | Ausência de política formal de descarte de evidências (etapa "descarte" da cadeia de custódia existe no schema, mas não há processo automatizado) | Alta | Médio | Implementar rotina de expurgo conforme prazo legal de guarda de inquéritos |
| R-06 | Uso de dados do sistema para finalidade distinta da investigação original (function creep) | Baixa | Alto | RBAC já restringe por papel; recomenda-se auditoria periódica de acessos via `custodia_log` |
| R-07 | Exposição de dados sensíveis em logs de aplicação (ex.: stack traces com PII) | Média | Médio | Revisar logging para garantir mascaramento (Presidio já implementado para exibição, mas não para logs de erro) |
| R-08 | Dependência de infraestrutura de terceiros (nuvem) sem contrato de operador formalizado | A definir | Alto | Formalizar contrato de operador de dados com qualquer provedor de nuvem utilizado |

---

## 11. Medidas, Salvaguardas e Mecanismos de Mitigação de Risco

### 11.1 Medidas já implementadas na arquitetura

- **Autenticação multifator obrigatória** (TOTP) para todos os perfis de acesso.
- **RBAC/ABAC** por papel funcional (agente, investigador, delegado, perito, administrador), com permissões granulares por endpoint.
- **Criptografia em trânsito** (TLS/mTLS) e **em repouso** (AES-256 no MinIO; SQLCipher no app mobile).
- **Cadeia de custódia imutável**: tabela `custodia_log` protegida por trigger de banco que bloqueia `UPDATE`/`DELETE`, validado por teste de integração automatizado.
- **Anonimização/mascaramento**: Microsoft Presidio disponível para mascarar CPF/e-mail/telefone antes de exibição ou exportação (modo degradado com regex quando Presidio não está instalado).
- **Hash de integridade**: SHA-256 calculado na origem (dispositivo/navegador), validado no servidor — rejeita divergências automaticamente.
- **Retenção técnica**: MinIO com Object Lock em modo GOVERNANCE (5 anos), mas **sem processo formal de descarte pós-prazo** (ver R-05).
- **Modo pânico** no app mobile: apagamento seguro de dados locais em caso de risco ao agente.

### 11.2 Medidas pendentes de implementação (recomendadas antes do go-live)

- [ ] Designação formal do Encarregado (DPO) — Seção 1.
- [ ] Política institucional de atendimento a direitos do titular, compatível com sigilo processual.
- [ ] Rotina automatizada de expurgo/descarte conforme prazo legal.
- [ ] SIEM para detecção de acesso anômalo (mencionado no roadmap técnico, não implementado).
- [ ] HashiCorp Vault para segredos (hoje em `.env`/Secrets do Kubernetes, sem rotação automatizada).
- [ ] Auditoria periódica de viés algorítmico nos modelos de NLP/ALPR.
- [ ] Contrato formal de operador de dados com qualquer provedor de infraestrutura terceirizada.
- [ ] Revisão de logging para evitar exposição de PII em mensagens de erro/stack trace.

---

## 12. Aprovação

| Papel | Nome | Assinatura | Data |
|---|---|---|---|
| Encarregado de Dados (DPO) | _A definir_ | | |
| Responsável Técnico | _A definir_ | | |
| Autoridade Máxima do Órgão | _A definir_ | | |

**Este documento não substitui análise jurídica formal.** Deve ser revisado por profissional habilitado e pelo Encarregado de Dados da instituição antes de qualquer submissão à ANPD ou uso como evidência de conformidade em auditoria.

---

## Anexo: Checklist de Pré-Produção (cruzado com docs/SEGURANCA_LGPD.md)

- [ ] Pentest completo da API e do app mobile.
- [ ] Revisão jurídica do fluxo de cadeia de custódia por perito criminal.
- [ ] Este RIPD aprovado pelo DPO.
- [ ] Rotação de segredos via vault.
- [ ] Testes de carga no pipeline Kafka/workers.
- [ ] Plano de resposta a incidentes e backup/disaster recovery testado.
