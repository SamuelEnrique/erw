// The project map's categories (session 16), shared by the server page and the client map.

export const KINDS = [
  { id: "operating", label: "Operating (EIA-860M)" },
  { id: "planned", label: "Planned (EIA-860M)" },
  { id: "queue", label: "Queue positions (six ISOs)" },
  { id: "datacenter", label: "Datacenters (from the news)" },
] as const;

// Technology groups of energy_projects, in the order of the site's eight fuel colors
// (app/tokens.css, validated in session 15). Past the seventh, groups share "other":
// a ninth hue is never generated.
export const TECH_GROUPS = [
  { id: "natural_gas", label: "Natural gas", color: "gas" },
  { id: "coal", label: "Coal", color: "coal" },
  { id: "nuclear", label: "Nuclear", color: "nuclear" },
  { id: "wind", label: "Wind", color: "wind" },
  { id: "solar", label: "Solar", color: "solar" },
  { id: "hydro", label: "Hydro", color: "hydro" },
  { id: "storage", label: "Storage", color: "storage" },
  { id: "hybrid", label: "Hybrid", color: "other" },
  { id: "petroleum", label: "Petroleum", color: "other" },
  { id: "biomass", label: "Biomass", color: "other" },
  { id: "geothermal", label: "Geothermal", color: "other" },
  { id: "transmission", label: "Transmission", color: "other" },
  { id: "other", label: "Other", color: "other" },
  { id: "unknown", label: "Not stated", color: "other" },
] as const;

export const COLOR_OF: Record<string, string> = {
  gas: "--color-fuel-gas",
  coal: "--color-fuel-coal",
  nuclear: "--color-fuel-nuclear",
  wind: "--color-fuel-wind",
  solar: "--color-fuel-solar",
  hydro: "--color-fuel-hydro",
  storage: "--color-fuel-storage",
  other: "--color-fuel-other",
};

export const COLOR_LEGEND = [
  { color: "gas", label: "Natural gas" },
  { color: "coal", label: "Coal" },
  { color: "nuclear", label: "Nuclear" },
  { color: "wind", label: "Wind" },
  { color: "solar", label: "Solar" },
  { color: "hydro", label: "Hydro" },
  { color: "storage", label: "Storage" },
  { color: "other", label: "Other, hybrid, not stated" },
];

/** What the server page hands the client map: parallel arrays, one entry per drawn point. */
export type MapData = {
  width: number;
  height: number;
  statesPath: string; // inner state borders, projected
  nation: string; // the national outline, projected
  statesGeo: unknown; // session 22: the states as a GeoJSON FeatureCollection, projected (the ECharts map)
  stateCodes: string[];
  statuses: string[];
  x: number[];
  y: number[];
  mw: number[];
  kind: number[];
  tech: number[];
  state: number[];
  status: number[];
  county: number[]; // 1: a county point (a ring), 0: exact coordinates (a dot)
  table: number[]; // 0: energy_projects, 1: datacenter_projects
  id: string[];
  offMap: number;
  unplaced: number;
};
