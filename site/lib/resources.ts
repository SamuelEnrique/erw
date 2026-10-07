// Energy Research Warehouse (ERW) site, session 146: "Where the resources are" (/resources, in review).
//
// The pure part of the page: the contract with the data side (data/resources/manifest.json), how a grid file is
// decoded, which cell a longitude and latitude fall in, which level of a grid's pyramid is drawn at a zoom, the plane
// the map is drawn on, the address that holds the view, and whether a point is inside a shape. No imports: Node runs
// this file as it is (site/scripts/test-resources.mjs, site/scripts/check-resources.mjs) and the browser runs the same
// functions. Nothing here makes a number: every value shown is a stored value of a layer's file, times its own scale.

// ---------------------------------------------------------------------------------------------------------------------
// The manifest: one entry a layer. The page has one renderer a kind and reads everything else from the entry.

export type Level = { file: string; cell_deg: number; ncols?: number; nrows?: number; bytes?: number };
export type Legend = { min: number; max: number; stops?: number[] };
/** A part of a grid layer kept in files of its own (Alaska, Hawaii), with its own pyramid and box. */
export type Extent = { extent: string; levels: Level[]; legend?: Legend; grid?: { west: number; north: number; east: number; south: number } };
export type Layer = {
  id: string; group: string; title: string; kind: "grid" | "shapes" | "points";
  unit?: string; value_label?: string; publisher?: string; source_title?: string; source_url?: string; terms_url?: string;
  terms_quote?: string; terms_quotes?: string[]; terms_notice?: string; terms_in_file?: string; credit?: string; acknowledgment?: string;
  vintage?: string; retrieved_at_utc?: string; extent?: string; source_resolution?: string; reduction?: string;
  levels?: Level[]; other_extents?: Extent[]; file?: string; files?: (string | { file: string })[]; bytes?: number;
  legend?: Legend; classes?: { value: number; label: string }[]; notes_for_method?: string;
  point_spacing_km?: number; columns_meaning?: Record<string, string>;
};
export type Missing = { id?: string; group?: string; title?: string; reason?: string; why?: string };
export type Manifest = { built_at_utc?: string; layers: Layer[]; missing?: Missing[] };

/** Every file a layer names, in the manifest's order: a grid's levels, or the one file of its shapes or points. */
export function filesOf(l: Layer): string[] {
  const out: string[] = [];
  for (const v of l.levels ?? []) if (v && typeof v.file === "string") out.push(v.file);
  for (const x of l.other_extents ?? []) for (const v of x.levels ?? []) if (v && typeof v.file === "string") out.push(v.file);
  if (typeof l.file === "string") out.push(l.file);
  for (const f of l.files ?? []) out.push(typeof f === "string" ? f : f.file);
  return [...new Set(out.filter(Boolean))];
}
/** A file's name in the page's address for it: its extension dropped, so the release gate sees the request
 *  (the gate lets any address ending in an extension through; lib/release.ts). */
export const stemOf = (file: string) => file.replace(/\.[A-Za-z0-9]+$/, "");
export const layerHref = (file: string) => `/resources/layer/${encodeURIComponent(stemOf(file))}`;

// ---------------------------------------------------------------------------------------------------------------------
// The toggles: the groups in the owner's order, and the layers the owner expects in each. A layer the manifest does
// not hold is a greyed toggle with its reason; a layer the manifest holds and this list does not expect is still shown.

export const GROUPS = [
  { id: "wind", label: "Wind", color: "--color-fuel-wind" },
  { id: "solar", label: "Solar", color: "--color-fuel-solar" },
  { id: "geothermal", label: "Geothermal", color: "--color-fuel-other" },
  { id: "oil_gas", label: "Oil and gas", color: "--color-fuel-gas" },
  { id: "hydropower", label: "Hydropower", color: "--color-fuel-hydro" },
  { id: "biomass", label: "Biomass", color: "--color-fuel-nuclear" },
  { id: "offshore_wind", label: "Offshore wind", color: "--color-fuel-storage" },
] as const;
const OTHER_COLOR = "--color-fuel-coal";

/** A group as the manifest writes it, as one of the page's groups ("Oil and gas", "oil_and_gas" and "oilgas" are one). */
export function groupId(written: string): string {
  const g = (written ?? "").toLowerCase().replace(/[^a-z]+/g, "_").replace(/^_|_$/g, "");
  if (/offshore/.test(g)) return "offshore_wind";
  if (/oil|gas|basin|play|petroleum/.test(g)) return "oil_gas";
  if (/hydro(?!thermal)/.test(g)) return "hydropower";
  if (/geotherm|hydrothermal/.test(g)) return "geothermal";
  if (/bio/.test(g)) return "biomass";
  if (/solar|irradi/.test(g)) return "solar";
  if (/wind/.test(g)) return "wind";
  return g || "other";
}
export const groupColor = (group: string) => GROUPS.find((g) => g.id === group)?.color ?? OTHER_COLOR;

export const EXPECTED: { group: string; label: string; match: RegExp }[] = [
  { group: "wind", label: "Wind speed at 100 m", match: /speed/ },
  { group: "wind", label: "Gross capacity factor", match: /capacity.?factor|(^|[^a-z])cf([^a-z]|$)/ },
  { group: "solar", label: "Global horizontal irradiance", match: /ghi|global.?horizontal/ },
  { group: "solar", label: "Direct normal irradiance", match: /dni|direct.?normal/ },
  { group: "geothermal", label: "Hydrothermal", match: /hydrothermal/ },
  { group: "geothermal", label: "Enhanced geothermal", match: /egs|enhanced/ },
  { group: "oil_gas", label: "Sedimentary basins", match: /basin/ },
  { group: "oil_gas", label: "Tight oil and shale gas plays", match: /play/ },
  { group: "hydropower", label: "Hydropower potential", match: /hydro/ },
  { group: "biomass", label: "Biomass", match: /bio|billion/ },
  { group: "offshore_wind", label: "Lease areas", match: /lease/ },
  { group: "offshore_wind", label: "Planning areas", match: /planning/ },
];
export const NOT_HELD = "not held";
const NO_REASON = "This layer is not among the resource layers the warehouse holds yet.";

export type Toggle = { held: true; layer: Layer } | { held: false; key: string; label: string; reason: string };
export type ToggleGroup = { id: string; label: string; color: string; items: Toggle[] };

/** The toggles of the page, in groups: every layer held, then what is expected or named as missing and not held. */
export function toggleGroups(m: Manifest): ToggleGroup[] {
  const words = (x: { id?: string; title?: string }) => `${x.id ?? ""} ${x.title ?? ""}`.toLowerCase();
  const ids: string[] = GROUPS.map((g) => g.id);
  for (const l of m.layers) if (!ids.includes(groupId(l.group))) ids.push(groupId(l.group));
  for (const x of m.missing ?? []) if (x.group && !ids.includes(groupId(x.group))) ids.push(groupId(x.group));
  return ids.map((id) => {
    const known = GROUPS.find((g) => g.id === id);
    const held = m.layers.filter((l) => groupId(l.group) === id);
    const missing = (m.missing ?? []).filter((x) => groupId(x.group ?? words(x)) === id);
    const items: Toggle[] = held.map((layer) => ({ held: true, layer }));
    const used = new Set<Missing>();
    for (const e of EXPECTED.filter((x) => x.group === id)) {
      if (held.some((l) => e.match.test(words(l)))) continue;
      const said = missing.find((x) => !used.has(x) && e.match.test(words(x)));
      if (said) used.add(said);
      items.push({ held: false, key: `${id}:${e.label}`, label: said?.title ?? e.label, reason: said?.reason ?? said?.why ?? NO_REASON });
    }
    for (const x of missing) {
      if (used.has(x) || held.some((l) => l.id === x.id)) continue;
      items.push({ held: false, key: `${id}:${x.id ?? x.title ?? "missing"}`, label: x.title ?? x.id ?? "A layer", reason: x.reason ?? x.why ?? NO_REASON });
    }
    return { id, label: known?.label ?? id.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()), color: known?.color ?? OTHER_COLOR, items };
  }).filter((g) => g.items.length > 0);
}

// ---------------------------------------------------------------------------------------------------------------------
// A grid file: a regular longitude and latitude grid, north to south, row-major, unsigned 16-bit little-endian in
// base64. value = stored * scale + offset, in the source's own unit; the stored value `nodata` is an empty cell.

export type GridFile = {
  lon0: number; lat0: number; dlon: number; dlat: number; ncols: number; nrows: number; scale: number; offset: number;
  nodata: number; encoding: string; values: string;
};
export type Grid = Omit<GridFile, "values" | "encoding"> & { data: Uint16Array };

export function decodeGrid(f: GridFile): Grid {
  if (f.encoding !== "uint16-le-base64") throw new Error(`a grid encoded as ${f.encoding}: this page reads uint16-le-base64`);
  const bin = atob(f.values);
  const n = f.ncols * f.nrows;
  if (bin.length !== 2 * n) throw new Error(`a grid of ${f.ncols} by ${f.nrows} cells holds ${bin.length} bytes, not ${2 * n}`);
  const data = new Uint16Array(n);
  for (let i = 0; i < n; i++) data[i] = bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8);
  return { lon0: f.lon0, lat0: f.lat0, dlon: Math.abs(f.dlon), dlat: Math.abs(f.dlat), ncols: f.ncols, nrows: f.nrows, scale: f.scale, offset: f.offset ?? 0, nodata: f.nodata ?? 65535, data };
}

/** The cell a longitude and latitude fall in: lon0 is the west edge and lat0 the north edge; null outside the grid. */
export function cellOf(g: Pick<Grid, "lon0" | "lat0" | "dlon" | "dlat" | "ncols" | "nrows">, lon: number, lat: number): { col: number; row: number } | null {
  const col = Math.floor((lon - g.lon0) / g.dlon), row = Math.floor((g.lat0 - lat) / g.dlat);
  if (!Number.isFinite(col) || !Number.isFinite(row) || col < 0 || row < 0 || col >= g.ncols || row >= g.nrows) return null;
  return { col, row };
}
/** The grid's value at a place, in the source's unit; null where the cell is empty or the place is outside the grid. */
export function valueAt(g: Grid, lon: number, lat: number): number | null {
  const c = cellOf(g, lon, lat);
  if (!c) return null;
  const s = g.data[c.row * g.ncols + c.col];
  return s === g.nodata ? null : s * g.scale + g.offset;
}
/** The decimals a grid's values are stored to (its scale): what the hover and the legend print, no more. */
export function decimalsOf(scale: number): number {
  if (!(scale > 0) || scale >= 1) return 0;
  return Math.min(4, Math.ceil(-Math.log10(scale) - 1e-9));
}
export const show = (v: number, decimals: number) => v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

// The level of a pyramid drawn at a zoom: the finest whose cells are at least MIN_CELL_PX wide on the screen, since a
// finer one would put several cells under one pixel and the pointer could not tell them apart; when even the coarsest
// is finer than that, the coarsest. FINEST_DEG is the finest cell the page draws at all (0: no floor): the measured
// frame time on the session's laptop decides it (site/scripts/check-resources.mjs --frames; the session's report).
export const MIN_CELL_PX = 0.75;
export const FINEST_DEG = 0;
export function levelFor(levels: Level[], pxPerDegLon: number, minCellPx = MIN_CELL_PX, finestDeg = FINEST_DEG): Level | null {
  const coarseFirst = [...levels].filter((l) => l.cell_deg > 0).sort((a, b) => b.cell_deg - a.cell_deg);
  if (!coarseFirst.length) return null;
  let pick = coarseFirst[0];
  for (const l of coarseFirst) if (l.cell_deg * pxPerDegLon >= minCellPx && l.cell_deg >= finestDeg - 1e-12) pick = l;
  return pick;
}

/** The pyramids of a grid layer: its own, then one for each part kept in files of its own. A part's box, where the
 *  manifest gives it, lets the page leave its files unread until the map shows that part of the world. */
export type Pyramid = { key: string; extent: string; levels: Level[]; box: [number, number, number, number] | null };
export function pyramidsOf(l: Layer): Pyramid[] {
  const out: Pyramid[] = [{ key: l.id, extent: "", levels: l.levels ?? [], box: null }];
  for (const x of l.other_extents ?? []) {
    if (!x || !Array.isArray(x.levels) || !x.levels.length) continue;
    const g = x.grid;
    out.push({ key: `${l.id}:${x.extent}`, extent: x.extent, levels: x.levels, box: g && [g.west, g.south, g.east, g.north].every(Number.isFinite) ? [g.west, g.south, g.east, g.north] : null });
  }
  return out;
}
/** The one legend of a layer: its own range widened to hold every part's range, with its own stops, so that one scale
 *  is true wherever the map is. Null when the manifest gives no range. */
export function legendOf(l: Layer): Legend | null {
  const ok = (g: Legend | undefined): g is Legend => !!g && typeof g === "object" && typeof g.min === "number" && typeof g.max === "number" && g.max > g.min;
  if (!ok(l.legend)) return null;
  let min = l.legend.min, max = l.legend.max;
  for (const x of l.other_extents ?? []) if (ok(x.legend)) { min = Math.min(min, x.legend.min); max = Math.max(max, x.legend.max); }
  return { min, max, stops: (l.legend.stops ?? []).filter((s) => typeof s === "number") };
}
/** Where each class of a layer sits on its ramp (0 light, 1 dark), in the manifest's order; null for a class that is
 *  no step of the scale (not assessed, no data), which is drawn in a neutral grey. A scale whose first class is named
 *  the most and whose last the least runs the other way, so that darker always reads as more. */
export function classTones(classes: { value: number; label: string }[]): (number | null)[] {
  const off = (c: { label: string }) => /not assessed|no data|not available|unknown/i.test(c.label);
  const steps = classes.filter((c) => !off(c));
  const down = steps.length > 1 && /most|highest/i.test(steps[0].label) && /least|lowest/i.test(steps[steps.length - 1].label);
  return classes.map((c) => {
    if (off(c)) return null;
    const i = steps.indexOf(c), t = steps.length > 1 ? i / (steps.length - 1) : 0.5;
    return 0.06 + 0.94 * (down ? 1 - t : t);
  });
}
/** A number of a legend or a hover, as the source's precision allows: no more than four decimals, thousands apart. */
export const plainNumber = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: Math.abs(v) >= 1000 ? 1 : 4 });
/** A legend's tick: short for a large range, with the decimals a small one needs. */
export function tickLabel(v: number, lg: Legend): string {
  const range = lg.max - lg.min;
  if (range >= 100000) return v === 0 ? "0" : v.toLocaleString("en-US", { notation: "compact", maximumFractionDigits: 1 });
  return show(v, range >= 50 ? (Number.isInteger(v) || Math.abs(v) >= 100 ? 0 : 1) : range >= 5 ? 1 : 2);
}

// ---------------------------------------------------------------------------------------------------------------------
// The plane. Longitude and latitude are drawn straight: x grows with longitude, squeezed by the cosine of 37.5 degrees
// north (the middle of the contiguous states), y with latitude. A cell of a grid is then a rectangle on the screen, so
// a grid is drawn as it is stored, cell for cell, and the pointer's place is read back exactly.

export const KX = Math.cos((37.5 * Math.PI) / 180);
export const HOME = { lon: -95.75, lat: 37.25, spanLon: 60, spanLat: 27.5 } as const;   // the contiguous states, with a margin
export const PLACES = [
  { id: "conus", label: "Contiguous states", lon: HOME.lon, lat: HOME.lat, z: 1 },
  { id: "alaska", label: "Alaska", lon: -152, lat: 63, z: 1.15 },
  { id: "hawaii", label: "Hawaii", lon: -157.5, lat: 20.5, z: 5 },
] as const;
export const Z_MIN = 0.35, Z_MAX = 96;

export type View = { z: number; lon: number; lat: number };
/** Pixels a degree of latitude at zoom 1: the contiguous states fill the map's box. */
export const fitK = (w: number, h: number) => Math.min(w / (HOME.spanLon * KX), h / HOME.spanLat);
export function toScreen(v: View, w: number, h: number, lon: number, lat: number): [number, number] {
  const k = fitK(w, h) * v.z;
  return [(lon - v.lon) * KX * k + w / 2, (v.lat - lat) * k + h / 2];
}
export function toPlace(v: View, w: number, h: number, x: number, y: number): [number, number] {
  const k = fitK(w, h) * v.z;
  return [v.lon + (x - w / 2) / (KX * k), v.lat - (y - h / 2) / k];
}
export const clampView = (v: View): View => ({
  z: Math.min(Z_MAX, Math.max(Z_MIN, v.z)), lon: Math.min(-60, Math.max(-180, v.lon)), lat: Math.min(73, Math.max(15, v.lat)),
});
/** Zoom by a factor about a point of the screen: the place under that point stays under it. */
export function zoomAbout(v: View, w: number, h: number, x: number, y: number, factor: number): View {
  const [lon, lat] = toPlace(v, w, h, x, y);
  const z = Math.min(Z_MAX, Math.max(Z_MIN, v.z * factor));
  const k = fitK(w, h) * z;
  return clampView({ z, lon: lon - (x - w / 2) / (KX * k), lat: lat + (y - h / 2) / k });
}

// ---------------------------------------------------------------------------------------------------------------------
// The address holds the view: ?on=<layers and overlays, comma separated>&z=<zoom>&c=<longitude>,<latitude>, and
// &fuel=<the plants' fuels shown> when not all are. /resources alone is the contiguous states with one layer on.

export const OVERLAYS = [
  { id: "plants_operating", label: "Plants, operating", source: "plants" },
  { id: "plants_planned", label: "Plants, planned or under construction", source: "plants" },
  { id: "queue", label: "Interconnection queue, by county", source: "queue" },
  { id: "datacenters", label: "Datacenters", source: "datacenters" },
] as const;
export type OverlayId = (typeof OVERLAYS)[number]["id"];
export type Shown = { on: string[]; view: View; fuel: string[] | null };

/** The layer a bare address opens with: wind speed where it is held, else the first layer held. */
export function firstLayer(layers: Pick<Layer, "id" | "title" | "group">[]): string | null {
  const wind = layers.find((l) => groupId(l.group) === "wind" && /speed/.test(`${l.id} ${l.title}`.toLowerCase()));
  return (wind ?? layers[0])?.id ?? null;
}
export function parseShown(search: string, layers: Pick<Layer, "id" | "title" | "group">[]): Shown {
  const q = new URLSearchParams(search);
  const known = new Set<string>([...layers.map((l) => l.id), ...OVERLAYS.map((o) => o.id)]);
  const first = firstLayer(layers);
  const on = q.has("on") ? [...new Set((q.get("on") ?? "").split(",").map((s) => s.trim()).filter((s) => known.has(s)))] : first ? [first] : [];
  const num = (s: string | undefined) => (s !== undefined && s.trim() !== "" && Number.isFinite(Number(s)) ? Number(s) : null);
  const z = num(q.get("z") ?? undefined);
  const c = (q.get("c") ?? "").split(",");
  const lon = num(c[0]), lat = num(c[1]);
  const view = clampView({ z: z !== null && z > 0 ? z : 1, lon: lon ?? HOME.lon, lat: lat ?? HOME.lat });
  const fuel = q.has("fuel") ? (q.get("fuel") ?? "").split(",").map((s) => s.trim()).filter(Boolean) : null;
  return { on, view, fuel };
}
const trim = (v: number, d: number) => String(Number(v.toFixed(d)));
export function shownQuery(s: Shown): string {
  const parts = [`on=${s.on.map(encodeURIComponent).join(",")}`, `z=${trim(s.view.z, 3)}`, `c=${trim(s.view.lon, 4)},${trim(s.view.lat, 4)}`];
  if (s.fuel) parts.push(`fuel=${s.fuel.map(encodeURIComponent).join(",")}`);
  return `?${parts.join("&")}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// Shapes and color.

export type Geometry = { type: string; coordinates?: unknown; geometries?: Geometry[] };
type Ring = number[][];
function inRings(rings: Ring[], lon: number, lat: number): boolean {
  let inside = false;
  for (const ring of rings) {
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
      if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
    }
  }
  return inside;
}
/** Whether a place is inside a polygon or multipolygon (its holes are outside). Lines and points have no inside. */
export function inGeometry(g: Geometry | null | undefined, lon: number, lat: number): boolean {
  if (!g) return false;
  if (g.type === "Polygon") return inRings(g.coordinates as Ring[], lon, lat);
  if (g.type === "MultiPolygon") return (g.coordinates as Ring[][]).some((p) => inRings(p, lon, lat));
  if (g.type === "GeometryCollection") return (g.geometries ?? []).some((x) => inGeometry(x, lon, lat));
  return false;
}
/** The box of a geometry: [west, south, east, north]; null for one with no coordinates. */
export function boxOf(g: Geometry | null | undefined): [number, number, number, number] | null {
  let w = Infinity, s = Infinity, e = -Infinity, n = -Infinity;
  const walk = (c: unknown) => {
    if (!Array.isArray(c)) return;
    if (typeof c[0] === "number" && typeof c[1] === "number") { w = Math.min(w, c[0]); e = Math.max(e, c[0]); s = Math.min(s, c[1]); n = Math.max(n, c[1]); return; }
    for (const x of c) walk(x);
  };
  const each = (x: Geometry | null | undefined) => { if (!x) return; if (x.type === "GeometryCollection") (x.geometries ?? []).forEach(each); else walk(x.coordinates); };
  each(g);
  return Number.isFinite(w) ? [w, s, e, n] : null;
}

export type Rgb = [number, number, number];
export function rgbOf(hex: string): Rgb {
  const h = hex.trim().replace(/^#/, "");
  const f = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  return [parseInt(f.slice(0, 2), 16), parseInt(f.slice(2, 4), 16), parseInt(f.slice(4, 6), 16)];
}
export const mix = (a: Rgb, b: Rgb, t: number): Rgb => [0, 1, 2].map((i) => Math.round(a[i] + (b[i] - a[i]) * t)) as Rgb;
/** A sequential scale of one hue, light to dark: two tints of the hue, the hue, and the hue darkened twice with the
 *  text color. TINTS and SHADES are the share of white, then of the text color, mixed in at each step. */
const TINTS = [0.72, 0.36], SHADES = [0.45, 0.82];
export const rampOf = (hue: Rgb, ink: Rgb): Rgb[] => [...TINTS.map((t) => mix(hue, [255, 255, 255], t)), hue, ...SHADES.map((t) => mix(hue, ink, t))];
/** The same five steps as CSS, from a color token's name, for a legend: the browser mixes them as rampOf does. */
export function rampCss(token: string): string[] {
  const pct = (t: number) => `${Math.round((1 - t) * 100)}%`;
  return [...TINTS.map((t) => `color-mix(in srgb, var(${token}) ${pct(t)}, #ffffff)`), `var(${token})`, ...SHADES.map((t) => `color-mix(in srgb, var(${token}) ${pct(t)}, var(--color-ink))`)];
}
/** The color at t along a token's ramp, as CSS. */
export function alongCss(token: string, t: number): string {
  const steps = rampCss(token), x = Math.min(1, Math.max(0, Number.isFinite(t) ? t : 0)) * (steps.length - 1), i = Math.min(steps.length - 2, Math.floor(x));
  return `color-mix(in srgb, ${steps[i]} ${Math.round((1 - (x - i)) * 100)}%, ${steps[i + 1]})`;
}
/** The color at t (0 to 1) along a ramp. */
export function along(ramp: Rgb[], t: number): Rgb {
  const x = Math.min(1, Math.max(0, Number.isFinite(t) ? t : 0)) * (ramp.length - 1);
  const i = Math.min(ramp.length - 2, Math.floor(x));
  return mix(ramp[i], ramp[i + 1], x - i);
}
/** Where a value sits on a legend, 0 at its minimum and 1 at its maximum. Where the legend gives stops, the minimum,
 *  the stops and the maximum are spaced evenly and a value sits in proportion between the two it lies between: the
 *  manifest's stops mark where the layer's values crowd, and the color follows them. */
export function position(v: number, lg: Legend): number {
  if (!(lg.max > lg.min)) return 0.5;
  const knots = [lg.min, ...(lg.stops ?? []).filter((s) => s > lg.min && s < lg.max).sort((a, b) => a - b), lg.max].filter((s, i, a) => i === 0 || s > a[i - 1]);
  if (v <= knots[0]) return 0;
  for (let i = 1; i < knots.length; i++) if (v <= knots[i]) return (i - 1 + (v - knots[i - 1]) / (knots[i] - knots[i - 1])) / (knots.length - 1);
  return 1;
}
export const css = (c: Rgb, a = 1) => (a >= 1 ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`);
