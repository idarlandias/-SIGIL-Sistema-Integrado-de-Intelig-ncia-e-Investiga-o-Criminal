import { useEffect, useRef } from 'react';
import cytoscape, { Core, ElementDefinition } from 'cytoscape';

interface NoRede {
  cpf?: string;
  nome?: string;
  [key: string]: unknown;
}

interface ResultadoRede {
  alvo: NoRede;
  forca_vinculo: number;
}

interface Props {
  cpfCentral: string;
  dadosRede: ResultadoRede[];
}

/**
 * Renderiza o grafo de vínculos usando Cytoscape.js. A espessura e cor
 * das arestas refletem `forca_vinculo` (soma de confiança dos
 * relacionamentos), replicando visualmente o conceito de confiabilidade
 * de inteligência usado no schema Neo4j (ver db/neo4j/schema.cypher).
 */
export default function GrafoVinculosCanvas({ cpfCentral, dadosRede }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const elementos: ElementDefinition[] = [
      { data: { id: cpfCentral, label: 'Suspeito Central' }, classes: 'no-central' },
    ];

    dadosRede.forEach((item, idx) => {
      const idAlvo = (item.alvo.cpf as string) || `no-${idx}`;
      const label = (item.alvo.nome as string) || idAlvo;

      elementos.push({ data: { id: idAlvo, label } });
      elementos.push({
        data: {
          id: `${cpfCentral}-${idAlvo}`,
          source: cpfCentral,
          target: idAlvo,
          forca: item.forca_vinculo,
        },
      });
    });

    const cy = cytoscape({
      container: containerRef.current,
      elements: elementos,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#003366',
            label: 'data(label)',
            color: '#fff',
            'font-size': 11,
            'text-valign': 'bottom',
            'text-margin-y': 6,
          },
        },
        {
          selector: '.no-central',
          style: { 'background-color': '#8B0000', width: 40, height: 40 },
        },
        {
          selector: 'edge',
          style: {
            width: 'mapData(forca, 0, 3, 1, 8)',
            'line-color': '#666',
            'curve-style': 'bezier',
            label: 'data(forca)',
            'font-size': 9,
          },
        },
      ],
      layout: { name: 'concentric', concentric: (node) => (node.hasClass('no-central') ? 2 : 1) },
    });

    cyRef.current = cy;
    return () => cy.destroy();
  }, [cpfCentral, dadosRede]);

  return <div ref={containerRef} className="grafo-canvas" style={{ width: '100%', height: '600px' }} />;
}
