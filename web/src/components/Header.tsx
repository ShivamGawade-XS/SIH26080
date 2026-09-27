import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { SystemMeta } from '../types';

interface HeaderProps {
  meta: SystemMeta | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({ meta, theme, onToggleTheme }) => {
  const location = useLocation();
  const validTimeUtc = meta?.manifest?.valid_time_utc || '2026-07-15 03:00 UTC';
  const dataMode = meta?.data_mode || 'synthetic';

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 20px',
      borderBottom: '1px solid var(--border-hairline)',
      backgroundColor: 'var(--bg-surface)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <span style={{
            fontFamily: 'var(--font-serif)',
            fontSize: '20px',
            fontWeight: 600,
            letterSpacing: '1px',
          }}>
            VARSHA
          </span>
        </Link>

        <span className={`provenance-chip ${dataMode}`}>
          {dataMode === 'synthetic' ? '● SYNTHETIC DEMO' : '● REAL NWP+IMD'}
        </span>

        <span style={{ fontSize: '12px', color: 'var(--text-ink-2)', fontVariantNumeric: 'tabular-nums' }}>
          Valid: <strong>{validTimeUtc}</strong> (08:30 IST)
        </span>
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <Link
          to="/"
          style={{
            fontSize: '13px',
            fontWeight: location.pathname === '/' ? 600 : 400,
            color: location.pathname === '/' ? 'var(--accent-interactive)' : 'var(--text-ink)',
            textDecoration: location.pathname === '/' ? 'underline' : 'none',
          }}
        >
          Console
        </Link>
        <Link
          to="/verification"
          style={{
            fontSize: '13px',
            fontWeight: location.pathname === '/verification' ? 600 : 400,
            color: location.pathname === '/verification' ? 'var(--accent-interactive)' : 'var(--text-ink)',
            textDecoration: location.pathname === '/verification' ? 'underline' : 'none',
          }}
        >
          Verification (D5)
        </Link>
        <Link
          to="/regimes"
          style={{
            fontSize: '13px',
            fontWeight: location.pathname === '/regimes' ? 600 : 400,
            color: location.pathname === '/regimes' ? 'var(--accent-interactive)' : 'var(--text-ink)',
            textDecoration: location.pathname === '/regimes' ? 'underline' : 'none',
          }}
        >
          Regimes (D1)
        </Link>
        <Link
          to="/method"
          style={{
            fontSize: '13px',
            fontWeight: location.pathname === '/method' ? 600 : 400,
            color: location.pathname === '/method' ? 'var(--accent-interactive)' : 'var(--text-ink)',
            textDecoration: location.pathname === '/method' ? 'underline' : 'none',
          }}
        >
          Method & Limits
        </Link>

        <button
          onClick={onToggleTheme}
          title="Toggle Light / Dark theme"
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            fontWeight: 500,
          }}
        >
          {theme === 'light' ? 'Dark Theme' : 'Light Theme'}
        </button>
      </nav>
    </header>
  );
};
