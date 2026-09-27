import React from 'react';
import { RegimeProbabilityResponse, SystemMeta } from '../types';

interface LeftRailProps {
  meta: SystemMeta | null;
  selectedRun: string;
  onSelectRun: (run: string) => void;
  selectedLead: number;
  onSelectLead: (lead: number) => void;
  selectedLayer: string;
  onSelectLayer: (layer: string) => void;
  regimes: RegimeProbabilityResponse | null;
}

const LAYERS = [
  { id: 'corrected', label: 'Corrected Rain (B4 P50)' },
  { id: 'raw', label: 'Raw NWP (B0)' },
  { id: 'delta', label: 'Correction Δ (B4 − B0)' },
  { id: 'p64', label: 'Prob ≥ 64.5 mm (Heavy)' },
  { id: 'p115', label: 'Prob ≥ 115.6 mm (Very Heavy)' },
  { id: 'alert', label: 'Indicative Alert (IMD 4-Tier)' },
];


export const LeftRail: React.FC<LeftRailProps> = ({
  meta,
  selectedRun,
  onSelectRun,
  selectedLead,
  onSelectLead,
  selectedLayer,
  onSelectLayer,
  regimes,
}) => {
  const leadRegimes = regimes?.[String(selectedLead)] || {
    active: 0.70,
    break: 0.05,
    normal: 0.20,
    depression: 0.05,
  };

  return (
    <aside style={{
      width: '260px',
      borderRight: '1px solid var(--border-hairline)',
      backgroundColor: 'var(--bg-surface)',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
      overflowY: 'auto',
    }}>
      {/* Run Selector */}
      <div>
        <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)', marginBottom: '6px' }}>
          Forecast Run
        </label>
        <select
          value={selectedRun}
          onChange={(e) => onSelectRun(e.target.value)}
          style={{ width: '100%', fontSize: '12px' }}
        >
          {meta?.available_runs?.map((r) => (
            <option key={r} value={r}>{r}</option>
          )) || <option value={selectedRun}>{selectedRun}</option>}
        </select>
      </div>

      {/* Lead Day Selector */}
      <div>
        <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)', marginBottom: '6px' }}>
          Forecast Lead Time
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '4px' }}>
          {[1, 2, 3, 4, 5].map((d) => (
            <button
              key={d}
              onClick={() => onSelectLead(d)}
              style={{
                padding: '8px 4px',
                fontSize: '12px',
                fontWeight: selectedLead === d ? 700 : 400,
                backgroundColor: selectedLead === d ? 'var(--accent-interactive)' : 'var(--bg-surface-elevated)',
                color: selectedLead === d ? '#FFFFFF' : 'var(--text-ink)',
                borderColor: selectedLead === d ? 'var(--accent-interactive)' : 'var(--border-hairline)',
              }}
            >
              +D{d}
            </button>
          ))}
        </div>
      </div>

      {/* Layer Selector */}
      <div>
        <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)', marginBottom: '6px' }}>
          Cartographic Layer
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {LAYERS.map((layer) => (
            <button
              key={layer.id}
              onClick={() => onSelectLayer(layer.id)}
              style={{
                textAlign: 'left',
                padding: '8px 10px',
                fontSize: '12px',
                fontWeight: selectedLayer === layer.id ? 600 : 400,
                backgroundColor: selectedLayer === layer.id ? 'var(--bg-surface-elevated)' : 'transparent',
                borderColor: selectedLayer === layer.id ? 'var(--accent-interactive)' : 'var(--border-subtle)',
              }}
            >
              {layer.label}
            </button>
          ))}
        </div>
      </div>

      {/* Regime Probability Distribution */}
      <div style={{ borderTop: '1px solid var(--border-hairline)', paddingTop: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
            Day-{selectedLead} Synoptic Regime (D1)
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
          {Object.entries(leadRegimes).map(([regime, prob]) => (
            <div key={regime}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                <span style={{ textTransform: 'capitalize' }}>{regime}</span>
                <span style={{ fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>
                  {Math.round(prob * 100)}%
                </span>
              </div>
              <div style={{ width: '100%', height: '4px', background: 'var(--border-subtle)', borderRadius: '1px' }}>
                <div style={{
                  width: `${Math.round(prob * 100)}%`,
                  height: '100%',
                  background: regime === 'active' ? '#1B4B74' : regime === 'break' ? '#B85D19' : regime === 'depression' ? '#6B2D5C' : '#555B63',
                }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
