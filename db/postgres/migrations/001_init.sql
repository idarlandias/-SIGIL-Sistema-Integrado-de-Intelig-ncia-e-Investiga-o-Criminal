-- SIGIL — Migration inicial (PostgreSQL)
-- Convenção: cadeia de custódia é append-only (sem UPDATE/DELETE em custodia_log)

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matricula VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    papel VARCHAR(30) NOT NULL CHECK (papel IN ('agente','investigador','delegado','perito','administrador')),
    mfa_secret VARCHAR(64),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inqueritos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero VARCHAR(30) UNIQUE NOT NULL,
    delegacia VARCHAR(100) NOT NULL,
    status VARCHAR(30) DEFAULT 'em_andamento',
    data_abertura DATE NOT NULL,
    criado_em TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidencias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hash_sha256 VARCHAR(64) UNIQUE NOT NULL,
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('foto','audio','video','documento','depoimento_texto')),
    gps_lat DOUBLE PRECISION,
    gps_lon DOUBLE PRECISION,
    capturado_em TIMESTAMPTZ NOT NULL,
    capturado_por UUID REFERENCES usuarios(id),
    inquerito_id UUID REFERENCES inqueritos(id),
    caminho_storage VARCHAR(500),
    criado_em TIMESTAMPTZ DEFAULT now()
);

-- Tabela append-only: nunca fazer UPDATE ou DELETE aqui.
CREATE TABLE IF NOT EXISTS custodia_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidencia_id UUID NOT NULL REFERENCES evidencias(id),
    etapa VARCHAR(30) NOT NULL CHECK (etapa IN (
        'reconhecimento','isolamento','fixacao','coleta','acondicionamento',
        'transporte','recebimento','processamento','armazenamento','descarte'
    )),
    usuario_id UUID REFERENCES usuarios(id),
    acao VARCHAR(20) NOT NULL CHECK (acao IN ('criado','acessado','modificado','exportado')),
    hash_no_momento VARCHAR(64),
    timestamp TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_custodia_evidencia ON custodia_log(evidencia_id);
CREATE INDEX IF NOT EXISTS idx_evidencias_inquerito ON evidencias(inquerito_id);

-- Trigger de proteção: impede UPDATE/DELETE em custodia_log (garante imutabilidade)
CREATE OR REPLACE FUNCTION bloquear_alteracao_custodia()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'custodia_log e append-only: UPDATE/DELETE nao permitido';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bloquear_update_custodia
    BEFORE UPDATE OR DELETE ON custodia_log
    FOR EACH ROW EXECUTE FUNCTION bloquear_alteracao_custodia();
