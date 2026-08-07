// SIGIL — Schema do Grafo de Inteligência (Neo4j)
// Execute este script no Neo4j Browser ou via cypher-shell após o primeiro start.

// ==================== CONSTRAINTS ====================
CREATE CONSTRAINT pessoa_cpf IF NOT EXISTS FOR (p:Pessoa) REQUIRE p.cpf IS UNIQUE;
CREATE CONSTRAINT veiculo_placa IF NOT EXISTS FOR (v:Veiculo) REQUIRE v.placa IS UNIQUE;
CREATE CONSTRAINT inquerito_numero IF NOT EXISTS FOR (i:Inquerito) REQUIRE i.numero IS UNIQUE;
CREATE CONSTRAINT evidencia_hash IF NOT EXISTS FOR (e:Evidencia) REQUIRE e.hash_sha256 IS UNIQUE;
CREATE CONSTRAINT conta_id IF NOT EXISTS FOR (c:ContaFinanceira) REQUIRE c.identificador IS UNIQUE;
CREATE CONSTRAINT faccao_nome IF NOT EXISTS FOR (f:Faccao) REQUIRE f.nome IS UNIQUE;

// ==================== ÍNDICES DE PERFORMANCE ====================
CREATE INDEX pessoa_nome IF NOT EXISTS FOR (p:Pessoa) ON (p.nome);
CREATE INDEX evidencia_capturado_em IF NOT EXISTS FOR (e:Evidencia) ON (e.capturado_em);

// ==================== SEEDS DE EXEMPLO (remover em produção) ====================
CREATE (p1:Pessoa {
  cpf: '000.000.000-00', nome: 'Fulano da Silva', alias: ['Fulaninho'],
  nivel_risco: 'alto', criado_em: datetime()
});

CREATE (p2:Pessoa {
  cpf: '111.111.111-11', nome: 'Ciclano de Souza', alias: [],
  nivel_risco: 'medio', criado_em: datetime()
});

CREATE (v1:Veiculo {placa: 'ABC1D23', modelo: 'Civic', cor: 'preto'});

CREATE (f1:Faccao {nome: 'Faccao XYZ', regiao_atuacao: 'Zona Norte'});

CREATE (i1:Inquerito {
  numero: 'IP-2026-0451', delegacia: '5a DP',
  status: 'em andamento', data_abertura: date('2026-08-01')
});

// Relacionamentos de exemplo
MATCH (p1:Pessoa {cpf: '000.000.000-00'}), (p2:Pessoa {cpf: '111.111.111-11'})
CREATE (p1)-[:RELACIONADO_COM {tipo_vinculo: 'associado', fonte: 'depoimento', confianca: 0.7, registrado_em: datetime()}]->(p2);

MATCH (p1:Pessoa {cpf: '000.000.000-00'}), (f1:Faccao {nome: 'Faccao XYZ'})
CREATE (p1)-[:PERTENCE_A {cargo: 'membro', fonte: 'inteligencia_osint', confianca: 0.6}]->(f1);

MATCH (p1:Pessoa {cpf: '000.000.000-00'}), (i1:Inquerito {numero: 'IP-2026-0451'})
CREATE (p1)-[:INVESTIGADO_EM {papel: 'suspeito', data_inclusao: date('2026-08-01')}]->(i1);

// ==================== QUERIES ANALÍTICAS DE REFERÊNCIA ====================

// Rede de 2o grau de um suspeito, ordenada por forca de vinculo
// MATCH (p:Pessoa {cpf: '000.000.000-00'})-[r1]-(intermediario)-[r2]-(alvo)
// WHERE p <> alvo
// RETURN alvo, r1.confianca + r2.confianca AS forca_vinculo
// ORDER BY forca_vinculo DESC
// LIMIT 25;

// Contas financeiras em comum entre suspeitos de inqueritos distintos
// MATCH (i1:Inquerito)<-[:INVESTIGADO_EM]-(p1:Pessoa)-[:TITULAR_DE]->(c:ContaFinanceira)
//       <-[:TITULAR_DE]-(p2:Pessoa)-[:INVESTIGADO_EM]->(i2:Inquerito)
// WHERE i1 <> i2
// RETURN i1.numero, i2.numero, p1.nome, p2.nome, c.identificador;
