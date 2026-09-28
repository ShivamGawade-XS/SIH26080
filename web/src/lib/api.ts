import { DistrictForecast, GridLayerResponse, RegimeProbabilityResponse, SystemMeta, VerificationSummary } from '../types';

const API_BASE = '/api/v1';

export async function fetchSystemMeta(): Promise<SystemMeta> {
  const res = await fetch(`${API_BASE}/meta`);
  if (!res.ok) throw new Error('Failed to fetch system meta');
  return res.json();
}

export async function fetchDistricts(runId: string, lead: number): Promise<DistrictForecast[]> {
  const res = await fetch(`${API_BASE}/runs/${runId}/districts?lead=${lead}`);
  if (!res.ok) throw new Error('Failed to fetch district forecast table');
  return res.json();
}

export async function fetchDistrictsGeoJSON(runId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/runs/${runId}/districts.geojson`);
  if (!res.ok) throw new Error('Failed to fetch district GeoJSON');
  return res.json();
}

export async function fetchGridLayer(runId: string, lead: number, layer: string): Promise<GridLayerResponse> {
  const res = await fetch(`${API_BASE}/runs/${runId}/grid?lead=${lead}&layer=${layer}`);
  if (!res.ok) throw new Error(`Failed to fetch grid layer ${layer}`);
  return res.json();
}

export async function fetchRegimes(runId: string): Promise<RegimeProbabilityResponse> {
  const res = await fetch(`${API_BASE}/runs/${runId}/regime`);
  if (!res.ok) throw new Error('Failed to fetch regime probabilities');
  return res.json();
}

export async function fetchDistrictDetail(districtId: string, runId: string = 'latest'): Promise<{
  district_id: string;
  name: string;
  state: string;
  is_subgrid: boolean;
  timeline: DistrictForecast[];
}> {
  const res = await fetch(`${API_BASE}/districts/${districtId}?run=${runId}`);
  if (!res.ok) throw new Error(`Failed to fetch district detail for ${districtId}`);
  return res.json();
}

export async function fetchVerificationSummary(runId: string = 'latest'): Promise<VerificationSummary> {
  const res = await fetch(`${API_BASE}/verification/summary?run=${runId}`);
  if (!res.ok) throw new Error('Failed to fetch verification summary');
  return res.json();
}
