export interface SystemMeta {
  system_name: string;
  version: string;
  data_mode: 'synthetic' | 'real';
  latest_run: string;
  available_runs: string[];
  leads: number[];
  profile: string;
  grid_resolution: number;
  manifest?: {
    valid_time_utc?: string;
    config_hash?: string;
    provenance_statement?: string;
    controls?: Record<string, string>;
  };
}

export interface DistrictForecast {
  district_id: string;
  district_name: string;
  state: string;
  lead_day: number;
  valid_date: string;
  raw_mean_mm: number;
  corrected_p50_mm: number;
  p10_mm: number;
  p90_mm: number;
  delta_mm: number;
  expected_area_fraction_ge_64: number;
  expected_area_fraction_ge_115: number;
  max_cell_prob_ge_64: number;
  max_cell_prob_ge_115: number;
  dominant_regime: string;
  regime_confidence: number;
  alert_level: 'green' | 'yellow' | 'orange' | 'red';
  alert_label: string;
  alert_action: string;
  alert_glyph: string;
  is_subgrid: boolean;
  centroid_lat: number;
  centroid_lon: number;
  attributions?: {
    moisture_instability: number;
    circulation_vorticity: number;
    terrain_orography: number;
    regime_conditioning: number;
    nwp_baseline: number;
  };
}


export interface GridLayerResponse {
  lats: number[];
  lons: number[];
  lead: number;
  layer: string;
  values: number[][];
}

export interface RegimeProbabilityResponse {
  [lead: string]: {
    [regime: string]: number;
  };
}

export interface VerificationSummary {
  ladder: {
    [model: string]: {
      rmse: number;
      mae: number;
      ets_64: number;
      fss_64_scale3: number;
    };
  };
  paired_differences?: Record<string, { mean: number; ci_95_low: number; ci_95_high: number }>;
  controls?: Record<string, string>;
}
