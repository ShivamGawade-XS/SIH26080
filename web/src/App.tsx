import React, { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Header } from './components/Header';
import { fetchSystemMeta } from './lib/api';
import { Console } from './routes/Console';
import { DistrictBrief } from './routes/DistrictBrief';
import { Method } from './routes/Method';
import { Regimes } from './routes/Regimes';
import { Verification } from './routes/Verification';
import { SystemMeta } from './types';

export const App: React.FC = () => {
  const [meta, setMeta] = useState<SystemMeta | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    fetchSystemMeta()
      .then((m) => setMeta(m))
      .catch((err) => console.error('Could not fetch meta:', err));
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  };

  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Header meta={meta} theme={theme} onToggleTheme={toggleTheme} />
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Console meta={meta} theme={theme} />} />
            <Route path="/d/:id" element={<DistrictBrief />} />
            <Route path="/verification" element={<Verification meta={meta} />} />
            <Route path="/regimes" element={<Regimes />} />
            <Route path="/method" element={<Method />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
};
