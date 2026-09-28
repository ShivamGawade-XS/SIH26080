import React from 'react';
import { Link } from 'react-router-dom';
import { DistrictForecast } from '../types';

interface DistrictInspectorProps {
  district: DistrictForecast | null;
  onClose: () => void;
}

export const DistrictInspector: React.FC<DistrictInspectorProps> = ({ district, onClose }) => {
  if (!district) {
    return (
      <aside style={{
        width: '320px',
        borderLeft: '1px solid var(--border-hairline)',
        backgroundColor: 'var(--bg-surface)',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'var(--text-ink-muted)',
        textAlign: 'center',
        fontSize: '13px',
      }}>
        <p>Select or hover over a district on the map or table to inspect 5-day post-processed guidance.</p>
      </aside>
    );
  }

  const alertClass = `alert-${district.alert_level}`;

  return (
    <aside style={{
      width: '320px',
      borderLeft: '1px solid var(--border-hairline)',
      backgroundColor: 'var(--bg-surface)',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      overflowY: 'auto',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>
            {district.district_name}
          </h2>
          <span style={{ fontSize: '12px', color: 'var(--text-ink-2)' }}>
            {district.state}
          </span>
        </div>
        <button onClick={onClose} style={{ padding: '2px 6px', fontSize: '12px' }}>✕</button>
      </div>

      {district.is_subgrid && (
        <div style={{
          fontSize: '11px',
          background: 'var(--border-subtle)',
          padding: '4px 8px',
          borderRadius: '2px',
          color: 'var(--text-ink-2)',
        }}>
          ⚠️ <strong>Sub-Grid District:</strong> Area &lt; 1 grid cell. Using nearest grid centre.
        </div>
      )}

      {/* Alert Status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 12px',
        background: 'var(--bg-surface-elevated)',
        border: '1px solid var(--border-hairline)',
        borderRadius: 'var(--radius-sm)',
      }}>
        <div>
          <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-ink-muted)' }}>
            Indicative Alert Level
          </div>
          <div className={`alert-badge ${alertClass}`} style={{ marginTop: '2px' }}>
            <span>{district.alert_glyph}</span>
            <span>{district.alert_label} ({district.alert_action})</span>
          </div>
        </div>
        <span style={{ fontSize: '10px', color: 'var(--text-ink-muted)', textAlign: 'right' }}>
          Non-official<br />guidance
        </span>
      </div>

      {/* Precipitation Metrics */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
          Day-{district.lead_day} Rainfall Quantiles
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '6px',
          textAlign: 'center',
          background: 'var(--bg-surface-elevated)',
          padding: '10px',
          border: '1px solid var(--border-hairline)',
        }}>
          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-ink-muted)' }}>P10 (Min)</div>
            <div style={{ fontSize: '15px', fontWeight: 600 }} className="tabular-nums">
              {district.p10_mm} <span style={{ fontSize: '10px', fontWeight: 400 }}>mm</span>
            </div>
          </div>
          <div style={{ borderLeft: '1px solid var(--border-hairline)', borderRight: '1px solid var(--border-hairline)' }}>
            <div style={{ fontSize: '10px', color: 'var(--text-ink-2)', fontWeight: 600 }}>P50 (Median)</div>
            <div style={{ fontSize: '17px', fontWeight: 700, color: 'var(--accent-interactive)' }} className="tabular-nums">
              {district.corrected_p50_mm} <span style={{ fontSize: '10px', fontWeight: 400 }}>mm</span>
            </div>
          </div>
          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-ink-muted)' }}>P90 (Max)</div>
            <div style={{ fontSize: '15px', fontWeight: 600 }} className="tabular-nums">
              {district.p90_mm} <span style={{ fontSize: '10px', fontWeight: 400 }}>mm</span>
            </div>
          </div>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--text-ink-2)', display: 'flex', justifyContent: 'space-between' }}>
          <span>Raw NWP Mean: <strong className="tabular-nums">{district.raw_mean_mm} mm</strong></span>
          <span>Δ: <strong className="tabular-nums">{district.delta_mm > 0 ? `+${district.delta_mm}` : district.delta_mm} mm</strong></span>
        </div>
      </div>

      {/* Heavy Rain Exceedance */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
          Operational Exceedance Probabilities (D3)
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>P(Rain ≥ 64.5 mm / Heavy):</span>
            <strong className="tabular-nums">{Math.round(district.max_cell_prob_ge_64 * 100)}%</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>P(Rain ≥ 115.6 mm / Very Heavy):</span>
            <strong className="tabular-nums">{Math.round(district.max_cell_prob_ge_115 * 100)}%</strong>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Expected Area Fraction ≥ 64.5 mm:</span>
            <strong className="tabular-nums">{Math.round(district.expected_area_fraction_ge_64 * 100)}%</strong>
          </div>
        </div>
      </div>

      {/* TreeSHAP Feature Attributions Breakdown (FR-11 / Deliverable D2) */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
          TreeSHAP Physical Attributions (FR-11)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11px' }}>
          {[
            { key: 'moisture_instability', label: 'Moisture & CAPE' },
            { key: 'circulation_vorticity', label: 'Circulation & Vorticity' },
            { key: 'terrain_orography', label: 'Terrain & Orography' },
            { key: 'regime_conditioning', label: 'Regime Conditioning' },
            { key: 'nwp_baseline', label: 'NWP Baseline' },
          ].map((item) => {
            const rawVal = district.attributions?.[item.key as keyof typeof district.attributions];
            const val = typeof rawVal === 'number' ? rawVal : (item.key === 'nwp_baseline' ? district.raw_mean_mm : 0);
            const isPositive = val >= 0;
            const barWidth = Math.min(100, Math.round((Math.abs(val) / 30) * 100));
            return (
              <div
                key={item.key}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '3px',
                  background: 'var(--bg-surface-elevated)',
                  padding: '6px 8px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-hairline)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 500, color: 'var(--text-ink)' }}>{item.label}</span>
                  <span
                    className="tabular-nums"
                    style={{
                      fontWeight: 600,
                      color: isPositive ? 'var(--accent-interactive)' : '#C75100',
                    }}
                  >
                    {isPositive ? `+${val.toFixed(1)}` : val.toFixed(1)} mm
                  </span>
                </div>
                <div style={{ display: 'flex', height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${Math.max(4, barWidth)}%`,
                      background: isPositive ? 'var(--accent-interactive)' : '#C75100',
                      borderRadius: '2px',
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>


      {/* Action Link */}
      <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border-hairline)' }}>
        <Link
          to={`/d/${district.district_id}`}
          style={{
            display: 'block',
            textAlign: 'center',
            padding: '8px',
            background: 'var(--accent-interactive)',
            color: '#FFFFFF',
            textDecoration: 'none',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: 'var(--radius-sm)',
          }}
        >
          Open Printable District Brief (D4) →
        </Link>
      </div>
    </aside>
  );
};
