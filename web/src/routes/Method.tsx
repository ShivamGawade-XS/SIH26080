import React from 'react';

export const Method: React.FC = () => {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 20px' }}>
      <div style={{ borderBottom: '1px solid var(--border-hairline)', paddingBottom: '16px', marginBottom: '24px' }}>
        <h1 style={{ fontFamily: 'var(--font-serif)', fontSize: '28px', fontWeight: 600 }}>
          Scientific Methodology & Limitations
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--text-ink-2)' }}>
          Detailed alignment specifications, leakage safeguards, data sources, and operational caveats.
        </p>
      </div>

      {/* Accumulation Window Alignment */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
          1. 24-Hour Accumulation Window Alignment
        </h2>
        <p style={{ fontSize: '13px', lineHeight: 1.6, color: 'var(--text-ink-2)', marginBottom: '12px' }}>
          India Meteorological Department (IMD) daily gridded rainfall observations are defined over the 24-hour accumulation window from <strong>03:00 UTC to 03:00 UTC</strong> (08:30 IST to 08:30 IST).
        </p>
        <p style={{ fontSize: '13px', lineHeight: 1.6, color: 'var(--text-ink-2)' }}>
          NWP raw forecasts (e.g. GFS sub-daily buckets) are de-accumulated and summed to precisely align with this 03–03 UTC window for Day-1 (+24h to +48h) through Day-5 (+120h to +144h).
        </p>
      </section>

      {/* Strict Leakage Prevention */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
          2. Leakage Guard Architecture (N4)
        </h2>
        <ul style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: 1.8, color: 'var(--text-ink-2)' }}>
          <li><strong>Feature Registry:</strong> Asserts that every feature availability timestamp satisfies <code>t_avail ≤ t_init</code>. Observations at or after initialisation are strictly rejected.</li>
          <li><strong>Year-Based Splits:</strong> Leave-One-Season-Out (LOSO) cross-validation across training years prevents intra-season autocorrelation leakage.</li>
          <li><strong>Out-of-Fold Regime Conditioning:</strong> Model B4 is trained on nested out-of-fold regime probabilities from cross-validation folds, eliminating target leakage.</li>
        </ul>
      </section>

      {/* Data Sources and Licensing */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
          3. External Data Sources & Licences (N6)
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr style={{ background: 'var(--bg-ground)', borderBottom: '1px solid var(--border-hairline)' }}>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Source</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Provider</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Licence</th>
              <th style={{ padding: '8px 12px', textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>Synthetic Monsoon World</td>
              <td style={{ padding: '8px 12px' }}>Project Varsha</td>
              <td style={{ padding: '8px 12px' }}>MIT / Apache-2.0</td>
              <td style={{ padding: '8px 12px', color: 'green', fontWeight: 600 }}>VERIFIED</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>NOAA GFS Forecasts</td>
              <td style={{ padding: '8px 12px' }}>NOAA Open Data (AWS S3)</td>
              <td style={{ padding: '8px 12px' }}>Public Domain (CC0)</td>
              <td style={{ padding: '8px 12px' }}>UNVERIFIED (Network)</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>IMD Gridded Daily Rainfall</td>
              <td style={{ padding: '8px 12px' }}>IMD Pune</td>
              <td style={{ padding: '8px 12px' }}>Academic / Research Fair Use</td>
              <td style={{ padding: '8px 12px' }}>UNVERIFIED (Portal)</td>
            </tr>
            <tr>
              <td style={{ padding: '8px 12px', fontWeight: 600 }}>Indian Administrative Boundaries</td>
              <td style={{ padding: '8px 12px' }}>DataMeet / GeoBoundaries</td>
              <td style={{ padding: '8px 12px' }}>ODbL / CC-BY 4.0</td>
              <td style={{ padding: '8px 12px' }}>UNVERIFIED (Human Signoff)</td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* Top 5 Known Limitations */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-hairline)',
        padding: '20px',
        borderRadius: 'var(--radius-sm)',
      }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, textTransform: 'uppercase', marginBottom: '12px', color: 'var(--text-ink-2)' }}>
          4. Known Limitations (N1 / N2 / N5)
        </h2>
        <ol style={{ paddingLeft: '20px', fontSize: '13px', lineHeight: 1.8, color: 'var(--text-ink-2)' }}>
          <li><strong>Synthetic vs Real Skill:</strong> Synthetic verification validates pipeline recovery of known physical structures and must never be cited as real atmospheric forecast skill.</li>
          <li><strong>Sub-Grid Districts:</strong> Districts smaller than grid resolution use a nearest-cell assignment fallback and are badged `sub-grid`.</li>
          <li><strong>Season Scope:</strong> MVP is tuned exclusively for Southwest Monsoon (JJAS); winter Western Disturbances are out of scope.</li>
          <li><strong>Extremely Heavy Rain Rarity:</strong> For events ≥ 204.5 mm, sample sparsity requires cautious interpretation of upper quantiles.</li>
          <li><strong>Indicative Alerts:</strong> Alert levels represent statistical guidance and do not replace official statutory IMD bulletins.</li>
        </ol>
      </section>
    </div>
  );
};
