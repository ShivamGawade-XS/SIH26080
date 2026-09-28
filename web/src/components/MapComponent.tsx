import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import { DistrictForecast, GridLayerResponse } from '../types';

interface MapComponentProps {
  geoJsonData: any;
  gridData: GridLayerResponse | null;
  selectedDistrict: DistrictForecast | null;
  onSelectDistrict: (d: DistrictForecast | null) => void;
  selectedLayer: string;
  theme: 'light' | 'dark';
}

const IMD_RAIN_LEGEND = [
  { label: '< 2.5 mm (Dry)', color: '#EBE8E0' },
  { label: '2.5 – 15.6 mm (Light)', color: '#B5D3CE' },
  { label: '15.6 – 35.5 mm (Moderate)', color: '#6CA2B3' },
  { label: '35.5 – 64.5 mm (Rather Heavy)', color: '#367794' },
  { label: '64.5 – 115.6 mm (Heavy)', color: '#1B4B74' },
  { label: '115.6 – 204.5 mm (Very Heavy)', color: '#102652' },
  { label: '≥ 204.5 mm (Extreme)', color: '#380C3D' },
];

const DELTA_LEGEND = [
  { label: '< -15 mm (Drying)', color: '#8C510A' },
  { label: '-15 to -5 mm', color: '#D8B365' },
  { label: '-5 to -1 mm', color: '#F6E8C3' },
  { label: 'Neutral (-1 to +1 mm)', color: '#F5F5F5' },
  { label: '+1 to +5 mm', color: '#C7EAE5' },
  { label: '+5 to +15 mm', color: '#5AB4AC' },
  { label: '> +15 mm (Wetting)', color: '#01665E' },
];

const PROB_64_LEGEND = [
  { label: '< 10% (Low Risk)', color: '#E8F5E9' },
  { label: '10% – 25% (Elevated)', color: '#A5D6A7' },
  { label: '25% – 50% (Moderate)', color: '#FFF59D' },
  { label: '50% – 75% (High)', color: '#FFB74D' },
  { label: '≥ 75% (Extreme)', color: '#D32F2F' },
];

const PROB_115_LEGEND = [
  { label: '< 5% (Low Risk)', color: '#E8F5E9' },
  { label: '5% – 15% (Guarded)', color: '#FFF59D' },
  { label: '15% – 35% (Significant)', color: '#FFB74D' },
  { label: '35% – 60% (Dangerous)', color: '#D32F2F' },
  { label: '≥ 60% (Catastrophic)', color: '#4A148C' },
];

const ALERT_LEGEND = [
  { label: 'Green (No Warning / Normal)', color: '#2E7D32' },
  { label: 'Yellow (Watch / Be Updated)', color: '#9A6A00' },
  { label: 'Orange (Alert / Be Prepared)', color: '#C75100' },
  { label: 'Red (Warning / Take Action)', color: '#B71C1C' },
];

function getChoroplethPaint(layer: string): any {
  switch (layer) {
    case 'raw':
      return [
        'step',
        ['coalesce', ['get', 'raw_mean_mm'], 0],
        '#EBE8E0', 2.5,
        '#B5D3CE', 15.6,
        '#6CA2B3', 35.5,
        '#367794', 64.5,
        '#1B4B74', 115.6,
        '#102652', 204.5,
        '#380C3D',
      ];
    case 'delta':
      return [
        'step',
        ['coalesce', ['get', 'delta_mm'], 0],
        '#8C510A', -15.0,
        '#D8B365', -5.0,
        '#F6E8C3', -1.0,
        '#F5F5F5', 1.0,
        '#C7EAE5', 5.0,
        '#5AB4AC', 15.0,
        '#01665E',
      ];
    case 'p64':
      return [
        'step',
        ['coalesce', ['get', 'max_cell_prob_ge_64'], 0],
        '#E8F5E9', 0.1,
        '#A5D6A7', 0.25,
        '#FFF59D', 0.5,
        '#FFB74D', 0.75,
        '#D32F2F',
      ];
    case 'p115':
      return [
        'step',
        ['coalesce', ['get', 'max_cell_prob_ge_115'], 0],
        '#E8F5E9', 0.05,
        '#FFF59D', 0.15,
        '#FFB74D', 0.35,
        '#D32F2F', 0.6,
        '#4A148C',
      ];
    case 'alert':
      return [
        'match',
        ['get', 'alert_level'],
        'red', '#B71C1C',
        'orange', '#C75100',
        'yellow', '#9A6A00',
        '#2E7D32',
      ];
    case 'corrected':
    default:
      return [
        'step',
        ['coalesce', ['get', 'corrected_p50_mm'], 0],
        '#EBE8E0', 2.5,
        '#B5D3CE', 15.6,
        '#6CA2B3', 35.5,
        '#367794', 64.5,
        '#1B4B74', 115.6,
        '#102652', 204.5,
        '#380C3D',
      ];
  }
}

export const MapComponent: React.FC<MapComponentProps> = ({
  geoJsonData,
  selectedDistrict,
  onSelectDistrict,
  selectedLayer,
  theme,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  const bgColor = theme === 'dark' ? '#0F1418' : '#F4F2ED';
  const boundaryColor = theme === 'dark' ? '#2A323A' : '#D8D4CA';

  useEffect(() => {
    if (mapRef.current && selectedDistrict?.centroid_lat && selectedDistrict?.centroid_lon) {
      mapRef.current.flyTo({
        center: [selectedDistrict.centroid_lon, selectedDistrict.centroid_lat],
        zoom: 6.0,
        speed: 1.2,
      });
    }
  }, [selectedDistrict]);

  useEffect(() => {
    if (!mapContainer.current) return;

    // Initialize MapLibre with local inline style (ADR 004 - Zero external tile server)
    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: { 'background-color': bgColor },
          },
        ],
      },
      center: [78.9629, 22.5937], // Central India
      zoom: 4.2,
      maxZoom: 9,
      minZoom: 3,
      attributionControl: false,
    });

    mapRef.current = map;

    map.on('load', () => {
      // Add district source if geoJsonData available
      if (geoJsonData) {
        map.addSource('districts-source', {
          type: 'geojson',
          data: geoJsonData,
        });

        // Fill layer with dynamic thematic choropleth coloring
        map.addLayer({
          id: 'districts-fill',
          type: 'fill',
          source: 'districts-source',
          paint: {
            'fill-color': getChoroplethPaint(selectedLayer),
            'fill-opacity': 0.70,
          },
        });

        // Boundary outline layer
        map.addLayer({
          id: 'districts-line',
          type: 'line',
          source: 'districts-source',
          paint: {
            'line-color': boundaryColor,
            'line-width': 1.2,
          },
        });

        // Hover & Click interaction
        map.on('click', 'districts-fill', (e: any) => {
          if (e.features && e.features[0]) {
            const props = e.features[0].properties as any;
            onSelectDistrict(props);
          }
        });

        map.on('mouseenter', 'districts-fill', () => {
          map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', 'districts-fill', () => {
          map.getCanvas().style.cursor = '';
        });
      }
    });

    return () => {
      map.remove();
    };
  }, [bgColor, boundaryColor]);

  // Update GeoJSON source data when prop changes
  useEffect(() => {
    if (mapRef.current && mapRef.current.isStyleLoaded() && geoJsonData) {
      const src = mapRef.current.getSource('districts-source') as maplibregl.GeoJSONSource;
      if (src) {
        src.setData(geoJsonData);
      }
    }
  }, [geoJsonData]);

  // Dynamically update choropleth fill-color when selectedLayer changes
  useEffect(() => {
    if (mapRef.current && mapRef.current.isStyleLoaded() && mapRef.current.getLayer('districts-fill')) {
      const paintExpr = getChoroplethPaint(selectedLayer);
      mapRef.current.setPaintProperty('districts-fill', 'fill-color', paintExpr);
    }
  }, [selectedLayer]);

  // Get active legend based on selected layer
  let legendTitle = 'Precipitation (mm/day)';
  let legendItems = IMD_RAIN_LEGEND;
  if (selectedLayer === 'delta') {
    legendTitle = 'NWP Bias Correction Δ (mm)';
    legendItems = DELTA_LEGEND;
  } else if (selectedLayer === 'p64') {
    legendTitle = 'Heavy Rain Prob P(≥64.5 mm)';
    legendItems = PROB_64_LEGEND;
  } else if (selectedLayer === 'p115') {
    legendTitle = 'Very Heavy Rain Prob P(≥115.6 mm)';
    legendItems = PROB_115_LEGEND;
  } else if (selectedLayer === 'alert') {
    legendTitle = 'Indicative Alert Level';
    legendItems = ALERT_LEGEND;
  }

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />

      {/* Dynamic Cartographic Legend */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '16px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '10px 14px',
        borderRadius: 'var(--radius-sm)',
        fontSize: '11px',
        boxShadow: '0 2px 6px rgba(0,0,0,0.08)',
        zIndex: 5,
        maxWidth: '240px',
      }}>
        <div style={{ fontWeight: 600, textTransform: 'uppercase', marginBottom: '6px', color: 'var(--text-ink-2)' }}>
          {legendTitle}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
          {legendItems.map((item) => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '14px', height: '10px', backgroundColor: item.color, border: '1px solid rgba(0,0,0,0.15)', flexShrink: 0 }} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
        <div style={{ marginTop: '8px', fontSize: '10px', color: 'var(--text-ink-muted)' }}>
          Graticule 5° interval • Dynamic Thematic Engine
        </div>
      </div>
    </div>
  );
};
