import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

interface Ponto {
  lat: number;
  lon: number;
  tipo: string;
  capturado_em: string;
  evidencia_id: string;
}

interface Props {
  pontos: Ponto[];
}

/**
 * Renderiza o heatmap de manchas criminais usando Leaflet + leaflet.heat.
 * Cada ponto de evidência com GPS vira uma amostra de intensidade no mapa,
 * revelando áreas de maior concentração de ocorrências — insumo direto
 * para planejamento de policiamento e correlação de rotas de fuga.
 */
export default function HeatmapGeoint({ pontos }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const centroPadrao: [number, number] =
      pontos.length > 0 ? [pontos[0].lat, pontos[0].lon] : [-3.7327, -38.5267];

    const map = L.map(containerRef.current).setView(centroPadrao, 12);
    mapRef.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    const pontosHeat: [number, number, number][] = pontos.map((p) => [p.lat, p.lon, 0.6]);

    // @ts-expect-error - leaflet.heat estende L sem tipagem oficial completa
    const heatLayer = L.heatLayer(pontosHeat, { radius: 30, blur: 20, maxZoom: 17 });
    heatLayer.addTo(map);

    pontos.forEach((p) => {
      L.circleMarker([p.lat, p.lon], { radius: 3, color: '#8B0000', fillOpacity: 0.8 })
        .bindPopup(`<b>${p.tipo}</b><br/>${new Date(p.capturado_em).toLocaleString('pt-BR')}`)
        .addTo(map);
    });

    if (pontos.length > 1) {
      const bounds = L.latLngBounds(pontos.map((p) => [p.lat, p.lon]));
      map.fitBounds(bounds, { padding: [30, 30] });
    }

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [pontos]);

  return <div ref={containerRef} className="heatmap-canvas" style={{ width: '100%', height: '600px' }} />;
}
