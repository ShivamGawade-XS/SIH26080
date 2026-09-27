import React from 'react';

export const Regimes: React.FC = () => {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 20px' }}>
      <div style={{ borderBottom: '1px solid var(--border-hairline)', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '28px', fontWeight: 600 }}>
          Weather Regime Classifier & Compound Taxonomy (Deliverable D1)
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-ink-2)' }}>
          Objective meteorological definitions, compound key formulation, and forecast-side classifier performance.
        </p>
      </div>

      {/* Synoptic Regimes Matrix */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '16px', color: 'var(--text-ink-2)' }}>
          1. Synoptic Weather Regimes (Domain Scale)
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ padding: '12px', background: 'var(--bg-ground)', borderLeft: '4px solid #1B4B74' }}>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>Active Monsoon (`active`)</div>
            <div style={{ fontSize: '12px', color: 'var(--text-ink-2)', marginTop: '2px' }}>
              <strong>Objective Rule:</strong> Core Monsoon Zone (CMZ: 18°N–28°N, 73°E–86°E) standardized precipitation anomaly ≥ +0.7σ with low-level westerly jet (u850 ≥ 15 m/s), sustained ≥ 3 consecutive days.
            </div>
          </div>

          <div style={{ padding: '12px', background: 'var(--bg-ground)', borderLeft: '4px solid #B85D19' }}>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>Break Monsoon (`break`)</div>
            <div style={{ fontSize: '12px', color: 'var(--text-ink-2)', marginTop: '2px' }}>
              <strong>Objective Rule:</strong> CMZ standardized precipitation anomaly ≤ -0.7σ with monsoon trough shifted to the foothills of the Himalayas, sustained ≥ 3 consecutive days.
            </div>
          </div>

          <div style={{ padding: '12px', background: 'var(--bg-ground)', borderLeft: '4px solid #6B2D5C' }}>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>Monsoon Low / Depression (`depression`)</div>
            <div style={{ fontSize: '12px', color: 'var(--text-ink-2)', marginTop: '2px' }}>
              <strong>Objective Rule:</strong> Relative vorticity at 850 hPa ≥ 3.0 × 10⁻⁵ s⁻¹ with closed MSLP depression ≥ 2.0 hPa below environmental mean, sustained ≥ 2 days.
            </div>
          </div>

          <div style={{ padding: '12px', background: 'var(--bg-ground)', borderLeft: '4px solid #555B63' }}>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>Normal / Transition (`normal`)</div>
            <div style={{ fontSize: '12px', color: 'var(--text-ink-2)', marginTop: '2px' }}>
              <strong>Objective Rule:</strong> Baseline background circulation without active/break extremes or closed vortex.
            </div>
          </div>
        </div>
      </section>

      {/* Compound Key Architecture */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '16px', color: 'var(--text-ink-2)' }}>
          2. Compound Key: Synoptic State × Geographic Forcing
        </h2>
        <p style={{ fontSize: '13px', lineHeight: 1.6, marginBottom: '16px' }}>
          Rainfall biases over India arise from the non-linear interaction between large-scale synoptic state and local geographic forcing. Varsha pairs every cell-day with a compound tuple:
          <code style={{ display: 'block', padding: '8px', background: 'var(--bg-ground)', margin: '8px 0' }}>
            RegimeKey = (SynopticRegime, GeographicZone)
          </code>
        </p>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr style={{ background: 'var(--bg-ground)', borderBottom: '1px solid var(--border-hairline)' }}>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Geographic Zone</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Physical Criteria</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Dominant Bias Characteristic</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>Western Ghats Orographic</td>
              <td style={{ padding: '8px 12px' }}>Elevation &gt; 400m, Lon &le; 76.5°E, Lat 8°N–21°N, u850 ≥ 5 m/s</td>
              <td style={{ padding: '8px 12px' }}>Ridge-line smoothing & peak displacement</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>West Coast Maritime</td>
              <td style={{ padding: '8px 12px' }}>Distance to coast &le; 50 km, Lat 8°N–23°N</td>
              <td style={{ padding: '8px 12px' }}>Offshore convective timing offset</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>Northeast Hills</td>
              <td style={{ padding: '8px 12px' }}>Elevation &gt; 300m, Lon &ge; 88°E, Lat &ge; 22°N</td>
              <td style={{ padding: '8px 12px' }}>Funneling and valley under-estimation</td>
            </tr>
            <tr>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>Continental Interior</td>
              <td style={{ padding: '8px 12px' }}>Default continental land area</td>
              <td style={{ padding: '8px 12px' }}>Spurious break drizzle / active under-forecast</td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* Sensitivity Analysis */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
          3. Threshold Sensitivity Analysis (Section 6.6)
        </h2>
        <p style={{ fontSize: '13px', lineHeight: 1.6, color: 'var(--text-ink-2)' }}>
          Perturbing CMZ anomaly thresholds by ±0.25σ and spell lengths by ±1 day confirms that the downstream Model B4 skill advantage remains robust (ETS difference variation &lt; 0.03), validating rule robustness against threshold boundary shifts.
        </p>
      </section>
    </div>
  );
};
