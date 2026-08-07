# Arquitetura SIGIL — Referência Completa

## Módulos Funcionais

### App de Campo (Mobile, offline-first)
- Captura de evidências (foto/vídeo/áudio) com hash SHA-256 local, GPS e timestamp.
- Fila de sincronização criptografada (SQLCipher) com retry e idempotência.
- Transcrição assistida de depoimentos em campo.
- Etiquetagem física-digital via QR code para lacres de evidências.
- Login biométrico + MFA, com token local temporário para uso offline.
- Modo pânico: ocultao/apagamento seguro de dados locais sensíveis.

### Painel Web (Inteligência)
- Análise de vínculos: grafo interativo de pessoas, contas, veículos, facções.
- OSINT: consolidação de dados públicos, vazamentos e perfis de risco.
- NLP/IA generativa: sumarização de depoimentos, extração de entidades,
  cruzamento semântico entre inquéritos.
- Visão computacional & GEOINT: ALPR, heatmaps de manchas criminais, EXIF.
- Cadeia de custódia digital: hash imutável + trilha de auditoria completa.
- Gestão de casos e geração de relatórios finais assinados digitalmente.

## Benchmark Internacional
Inspirado em Palantir Gotham, IBM i2 Analyst's Notebook, Cellebrite e SpiderFoot.

## Stack Tecnológica
- **Backend:** FastAPI (Python), Kafka para mensageria assíncrona.
- **Dados:** PostgreSQL (relacional), Neo4j (grafo), Qdrant (vetorial),
  Elasticsearch (busca textual), MinIO (objetos WORM).
- **Mobile:** React Native, SQLite + SQLCipher.
- **IA:** spaCy, Microsoft Presidio, Whisper, YOLOv8, OpenALPR, Tesseract/PaddleOCR.
- **Infra:** Docker, Kubernetes, Zero Trust, MFA, RBAC/ABAC.

## Diagrama de Containers (texto, para conversão em Mermaid/C4)

- **App Mobile (React Native)** → comunica via HTTPS/mTLS com o **API Gateway**.
- **API Gateway** → roteia para **Backend FastAPI** (evidências, custódia, casos).
- **Backend** → grava metadados em **PostgreSQL**, publica eventos em **Kafka**.
- **Workers (Kafka Consumers)** → processam OCR/NLP/ALPR, gravam entidades no
  **Neo4j**, indexam texto no **Elasticsearch**, geram embeddings no **Qdrant**.
- **Evidências binárias** → armazenadas no **MinIO** com Object Lock (WORM).
- **Painel Web (React/Next.js)** → consome a mesma API, renderiza grafo via
  Cytoscape.js/Sigma.js.

## Próximos Diagramas Recomendados
1. C4 Nível 2 (Containers) em Mermaid.
2. C4 Nível 3 (Componentes) do módulo de Cadeia de Custódia.
3. Diagrama de fluxo de dados (DFD) para o RIPD/LGPD.
