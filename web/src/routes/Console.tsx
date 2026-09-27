import React, { useEffect, useState } from 'react';
import { DistrictDrawer } from '../components/DistrictDrawer';
import { DistrictInspector } from '../components/DistrictInspector';
import { LeftRail } from '../components/LeftRail';
import { MapComponent } from '../components/MapComponent';
import { fetchDistricts, fetchDistrictsGeoJSON, fetchGridLayer, fetchRegimes } from '../lib/api';
import { DistrictForecast, GridLayerResponse, RegimeProbabilityResponse, SystemMeta } from '../types';

interface ConsoleProps {
  meta: SystemMeta | null;
  theme: 'light' | 'dark';
}

export const Console: React.FC<ConsoleProps> = ({ meta, theme }) => {
  const [selectedRun, setSelectedRun] = useState<string>(meta?.latest_run || 'SYN_DEFAULT_DEMO');
  const [selectedLead, setSelectedLead] = useState<number>(1);
  const [selectedLayer, setSelectedLayer] = useState<string>('corrected');
  
  const [districts, setDistricts] = useState<DistrictForecast[]>([]);
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [gridData, setGridData] = useState<GridLayerResponse | null>(null);
  const [regimes, setRegimes] = useState<RegimeProbabilityResponse | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictForecast | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (meta?.latest_run && meta.latest_run !== 'NONE') {
      setSelectedRun(meta.latest_run);
    }
  }, [meta]);

  useEffect(() => {
    async function loadData() {
      if (!selectedRun) return;
      try {
        setLoading(true);
        const [dList, gJson, rProbs, gData] = await Promise.all([
          fetchDistricts(selectedRun, selectedLead).catch(() => []),
          fetchDistrictsGeoJSON(selectedRun).catch(() => null),
          fetchRegimes(selectedRun).catch(() => null),
          fetchGridLayer(selectedRun, selectedLead, selectedLayer).catch(() => null),
        ]);

        setDistricts(dList);
        setGeoJsonData(gJson);
        setRegimes(rProbs);
        setGridData(gData);

        if (dList.length > 0 && !selectedDistrict) {
          setSelectedDistrict(dList[0]);
        }
      } catch (err) {
        console.error('Error loading console data:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [selectedRun, selectedLead, selectedLayer]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 49px)' }}>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Rail */}
        <LeftRail
          meta={meta}
          selectedRun={selectedRun}
          onSelectRun={setSelectedRun}
          selectedLead={selectedLead}
          onSelectLead={setSelectedLead}
          selectedLayer={selectedLayer}
          onSelectLayer={setSelectedLayer}
          regimes={regimes}
        />

        {/* Center Map Cartography */}
        <main style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
          {loading && (
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              zIndex: 10,
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-hairline)',
              padding: '4px 10px',
              fontSize: '11px',
              fontWeight: 600,
            }}>
              Loading layer...
            </div>
          )}
          <MapComponent
            geoJsonData={geoJsonData}
            gridData={gridData}
            selectedDistrict={selectedDistrict}
            onSelectDistrict={setSelectedDistrict}
            selectedLayer={selectedLayer}
            theme={theme}
          />
        </main>

        {/* Right Inspector */}
        <DistrictInspector
          district={selectedDistrict}
          onClose={() => setSelectedDistrict(null)}
        />
      </div>

      {/* Bottom District Table Drawer */}
      <DistrictDrawer
        districts={districts}
        selectedDistrict={selectedDistrict}
        onSelectDistrict={setSelectedDistrict}
        runId={selectedRun}
      />
    </div>
  );
};
