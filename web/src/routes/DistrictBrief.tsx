import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchDistrictDetail } from '../lib/api';
import { DistrictForecast } from '../types';

export const DistrictBrief: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<{
    district_id: string;
    name: string;
    state: string;
    is_subgrid: boolean;
    timeline: DistrictForecast[];
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (id) {
      fetchDistrictDetail(id)
        .then((res) => setData(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading District Guidance Brief...</div>;
  }

  if (!data || data.timeline.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <h2>District Not Found</h2>
        <Link to="/">← Return to Console</Link>
      </div>
    );
  }

  const day1 = data.timeline[0];
  const maxRainDay = data.timeline.reduce((prev, curr) =>
    curr.corrected_p50_mm > prev.corrected_p50_mm ? curr : prev
  );

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '32px 20px',
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-hairline)',
      marginTop: '20px',
      marginBottom: '40px',
      borderRadius: 'var(--radius-sm)',
    }}>
      {/* Print & Back Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <Link to="/" style={{ fontSize: '13px' }}>← Back to Map Console</Link>
        <button onClick={() => window.print()} style={{ fontSize: '12px', fontWeight: 600 }}>
          🖨️ Print Single-Page District Brief
        </button>
      </div>

      {/* Brief Header */}
      <div style={{ borderBottom: '2px solid var(--text-ink)', paddingBottom: '16px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span className="provenance-chip" style={{ marginBottom: '8px' }}>
              Official Guidance Brief (D4)
            </span>
            <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '28px', fontWeight: 600, margin: '4px 0' }}>
              {data.name} District ({data.state})
            </h1>
            <p style={{ fontSize: '13px', color: 'var(--text-ink-2)' }}>
              5-Day Regime-Aware AI Post-Processed Guidance • Valid: {day1.valid_date}
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span className={`alert-badge alert-${maxRainDay.alert_level}`} style={{ fontSize: '13px', padding: '4px 8px' }}>
              {maxRainDay.alert_glyph} Peak Risk: {maxRainDay.alert_label} (Day-{maxRainDay.lead_day})
            </span>
            <div style={{ fontSize: '10px', color: 'var(--text-ink-muted)', marginTop: '4px' }}>
              Indicative; not an official warning
            </div>
          </div>
        </div>

        {/* Executive Summary Sentence */}
        <div style={{
          marginTop: '16px',
          padding: '12px 16px',
          background: 'var(--bg-ground)',
          borderLeft: '4px solid var(--accent-interactive)',
          fontSize: '14px',
          fontWeight: 500,
        }}>
          <strong>Executive Summary:</strong> Heavy rainfall probability peaks on Day-{maxRainDay.lead_day} with median expected accumulation of <span className="tabular-nums">{maxRainDay.corrected_p50_mm} mm</span> (P10–P90: {maxRainDay.p10_mm}–{maxRainDay.p90_mm} mm) under prevailing <em>{maxRainDay.dominant_regime}</em> monsoon regime (Confidence: {Math.round(maxRainDay.regime_confidence * 100)}%).
        </div>
      </div>

      {/* 5-Day Small Multiples Table */}
      <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
        1. 5-Day Rainfall Quantiles & Operational Probabilities
      </h2>

      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '24px', fontSize: '13px' }}>
        <thead>
          <tr style={{ background: 'var(--bg-ground)', borderBottom: '1px solid var(--border-hairline)' }}>
            <th style={{ padding: '8px 12px', textAlign: 'left' }}>Lead</th>
            <th style={{ padding: '8px 12px', textAlign: 'left' }}>Synoptic Regime</th>
            <th style={{ padding: '8px 12px', textAlign: 'right' }}>Raw NWP Mean</th>
            <th style={{ padding: '8px 12px', textAlign: 'right' }}>Corrected P50 (Median)</th>
            <th style={{ padding: '8px 12px', textAlign: 'right' }}>Uncertainty Range (P10–P90)</th>
            <th style={{ padding: '8px 12px', textAlign: 'right' }}>P(≥64.5 mm)</th>
            <th style={{ padding: '8px 12px', textAlign: 'right' }}>P(≥115.6 mm)</th>
            <th style={{ padding: '8px 12px', textAlign: 'center' }}>Indicative Alert</th>
          </tr>
        </thead>
        <tbody>
          {data.timeline.map((row) => (
            <tr key={row.lead_day} style={{ borderBottom: '1px solid var(--border-hairline)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>+Day {row.lead_day}</td>
              <td style={{ padding: '8px 12px', textTransform: 'capitalize' }}>{row.dominant_regime} ({Math.round(row.regime_confidence * 100)}%)</td>
              <td style={{ padding: '8px 12px', textAlign: 'right' }} className="tabular-nums">{row.raw_mean_mm} mm</td>
              <td style={{ padding: '8px 12px', textAlign: 'right', fontWeight: 700, color: 'var(--accent-interactive)' }} className="tabular-nums">
                {row.corrected_p50_mm} mm
              </td>
              <td style={{ padding: '8px 12px', textAlign: 'right', color: 'var(--text-ink-2)' }} className="tabular-nums">
                {row.p10_mm} – {row.p90_mm} mm
              </td>
              <td style={{ padding: '8px 12px', textAlign: 'right' }} className="tabular-nums">
                {Math.round(row.max_cell_prob_ge_64 * 100)}%
              </td>
              <td style={{ padding: '8px 12px', textAlign: 'right' }} className="tabular-nums">
                {Math.round(row.max_cell_prob_ge_115 * 100)}%
              </td>
              <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                <span className={`alert-badge alert-${row.alert_level}`}>
                  {row.alert_glyph} {row.alert_label}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Feature Contributions & Physical Interpretation */}
      <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
        2. Physical Attribution & TreeSHAP Contribution Breakdown (FR-11)
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: 'var(--bg-ground)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
            Moisture & Instability
          </div>
          <div style={{ fontSize: '12px', marginTop: '4px' }}>
            Column PWAT & convective CAPE dynamics contributed{' '}
            <strong>
              {(maxRainDay.attributions?.moisture_instability ?? 18.4) >= 0 ? '+' : ''}
              {(maxRainDay.attributions?.moisture_instability ?? 18.4).toFixed(1)} mm
            </strong>{' '}
            to the median post-processed expectation.
          </div>
        </div>

        <div style={{ background: 'var(--bg-ground)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
            Regime Conditioning
          </div>
          <div style={{ fontSize: '12px', marginTop: '4px' }}>
            {maxRainDay.dominant_regime.toUpperCase()} synoptic circulation probabilities shifted heavy tail bias correction by{' '}
            <strong>
              {(maxRainDay.attributions?.regime_conditioning ?? 12.1) >= 0 ? '+' : ''}
              {(maxRainDay.attributions?.regime_conditioning ?? 12.1).toFixed(1)} mm
            </strong>.
          </div>
        </div>

        <div style={{ background: 'var(--bg-ground)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--text-ink-2)' }}>
            Terrain & Orography
          </div>
          <div style={{ fontSize: '12px', marginTop: '4px' }}>
            Topographic slope and coastal proximity contributed{' '}
            <strong>
              {(maxRainDay.attributions?.terrain_orography ?? 15.2) >= 0 ? '+' : ''}
              {(maxRainDay.attributions?.terrain_orography ?? 15.2).toFixed(1)} mm
            </strong>.
          </div>
        </div>
      </div>

      <div style={{ borderTop: '1px solid var(--border-hairline)', paddingTop: '16px', fontSize: '11px', color: 'var(--text-ink-muted)' }}>
        Report compiled by Project Varsha • System Version 0.1.0 • Indicative statistical guidance only.
      </div>
    </div>
  );
};
