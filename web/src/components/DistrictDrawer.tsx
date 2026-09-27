import React, { useState } from 'react';
import { DistrictForecast } from '../types';

interface DistrictDrawerProps {
  districts: DistrictForecast[];
  selectedDistrict: DistrictForecast | null;
  onSelectDistrict: (d: DistrictForecast) => void;
  runId: string;
}

export const DistrictDrawer: React.FC<DistrictDrawerProps> = ({
  districts,
  selectedDistrict,
  onSelectDistrict,
  runId,
}) => {
  const [search, setSearch] = useState('');
  const [alertFilter, setAlertFilter] = useState('all');
  const [isExpanded, setIsExpanded] = useState(true);

  const filtered = districts.filter((d) => {
    const matchSearch =
      d.district_name.toLowerCase().includes(search.toLowerCase()) ||
      d.state.toLowerCase().includes(search.toLowerCase());
    const matchAlert = alertFilter === 'all' || d.alert_level === alertFilter;
    return matchSearch && matchAlert;
  });

  return (
    <section style={{
      borderTop: '1px solid var(--border-hairline)',
      backgroundColor: 'var(--bg-surface)',
      height: isExpanded ? '280px' : '40px',
      display: 'flex',
      flexDirection: 'column',
      transition: 'height 180ms ease-out',
    }}>
      {/* Drawer Control Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '6px 16px',
        borderBottom: isExpanded ? '1px solid var(--border-hairline)' : 'none',
        backgroundColor: 'var(--bg-surface-elevated)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            style={{ padding: '2px 8px', fontSize: '11px', fontWeight: 600 }}
          >
            {isExpanded ? '▼ Collapse District Table' : '▲ Expand District Table'}
          </button>

          <span style={{ fontSize: '12px', fontWeight: 600 }}>
            District Guidance Table (D4) — {filtered.length} of {districts.length} Districts
          </span>
        </div>

        {isExpanded && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <input
              type="text"
              placeholder="Search district or state..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '180px' }}
            />

            <select value={alertFilter} onChange={(e) => setAlertFilter(e.target.value)}>
              <option value="all">All Alerts</option>
              <option value="red">Red (Warning)</option>
              <option value="orange">Orange (Alert)</option>
              <option value="yellow">Yellow (Watch)</option>
              <option value="green">Green (No Warning)</option>
            </select>

            <a
              href={`/api/v1/runs/${runId}/districts.csv`}
              download
              style={{
                fontSize: '12px',
                padding: '4px 8px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-hairline)',
                borderRadius: '2px',
                color: 'var(--text-ink)',
                textDecoration: 'none',
                fontWeight: 500,
              }}
            >
              📥 Export CSV
            </a>
          </div>
        )}
      </div>

      {/* Table Content */}
      {isExpanded && (
        <div style={{ flex: 1, overflow: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--bg-surface)', borderBottom: '1px solid var(--border-hairline)' }}>
              <tr>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>District</th>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>State</th>
                <th style={{ padding: '8px 12px', textAlign: 'center' }}>Indicative Alert</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>Raw Mean</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>Corrected P50</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>P10–P90 Range</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>P(≥64.5 mm)</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>Area Frac ≥64.5</th>
                <th style={{ padding: '8px 12px', textAlign: 'left' }}>Regime</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => {
                const isSelected = selectedDistrict?.district_id === d.district_id;
                return (
                  <tr
                    key={d.district_id}
                    onClick={() => onSelectDistrict(d)}
                    style={{
                      cursor: 'pointer',
                      backgroundColor: isSelected ? 'var(--bg-surface-elevated)' : 'transparent',
                      borderBottom: '1px solid var(--border-subtle)',
                      outline: isSelected ? '1px solid var(--accent-interactive)' : 'none',
                    }}
                  >
                    <td style={{ padding: '6px 12px', fontWeight: 600 }}>
                      {d.district_name} {d.is_subgrid && <span style={{ fontSize: '10px', color: 'var(--text-ink-muted)' }}>(sub-grid)</span>}
                    </td>
                    <td style={{ padding: '6px 12px', color: 'var(--text-ink-2)' }}>{d.state}</td>
                    <td style={{ padding: '6px 12px', textAlign: 'center' }}>
                      <span className={`alert-badge alert-${d.alert_level}`}>
                        {d.alert_glyph} {d.alert_label}
                      </span>
                    </td>
                    <td style={{ padding: '6px 12px', textAlign: 'right' }} className="tabular-nums">{d.raw_mean_mm} mm</td>
                    <td style={{ padding: '6px 12px', textAlign: 'right', fontWeight: 600, color: 'var(--accent-interactive)' }} className="tabular-nums">
                      {d.corrected_p50_mm} mm
                    </td>
                    <td style={{ padding: '6px 12px', textAlign: 'right', color: 'var(--text-ink-2)' }} className="tabular-nums">
                      {d.p10_mm} – {d.p90_mm} mm
                    </td>
                    <td style={{ padding: '6px 12px', textAlign: 'right' }} className="tabular-nums">
                      {Math.round(d.max_cell_prob_ge_64 * 100)}%
                    </td>
                    <td style={{ padding: '6px 12px', textAlign: 'right' }} className="tabular-nums">
                      {Math.round(d.expected_area_fraction_ge_64 * 100)}%
                    </td>
                    <td style={{ padding: '6px 12px', textTransform: 'capitalize' }}>{d.dominant_regime}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
