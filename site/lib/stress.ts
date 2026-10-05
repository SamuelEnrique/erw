// Energy Research Warehouse (ERW) site, session 123: "How hard the system works" (/mix/stress, in review).
//
// The reading of the site's own copy of grid_stress_yearly (site/data/stress/<grid>.json, written by
// warehouse/derived/mix_stress.py --snapshot). Pure functions, no imports (Node runs this file as it is, for
// tests/test_session123.py). The page does no arithmetic of its own: every figure is a row of the table, picked here.
// A figure that is not held is null and is shown as not held, never as zero.

export const TABLE = "grid_stress_yearly";
export const GRIDS = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp"] as const;
export type Grid = (typeof GRIDS)[number];
export const FUEL_NAME: Record<string, string> = { natural_gas: "Natural gas", coal: "Coal", nuclear: "Nuclear", wind: "Wind", solar: "Solar", hydro: "Hydro", storage: "Storage",
  hydro_storage: "Hydro and storage together" };

type Vars = Record<string, number | string | undefined>;
export type GridFile = {
  grid: Grid; name: string; tz: string; built: string; join: string | null; fuels: string[]; all_years: string[]; together: string[]; from_year: number;
  tight: number; calm_pct: number; window: [number, number]; years: Record<string, Vars>;
};
export type Files = Record<Grid, GridFile>;

export const isGrid = (g: unknown): g is Grid => typeof g === "string" && (GRIDS as readonly string[]).includes(g);
export const yearsOf = (f: GridFile): string[] => Object.keys(f.years).sort();
/** One figure of a year, or null when the table does not hold it. */
export const get = (f: GridFile, y: string, k: string): number | null => {
  const v = f.years[y]?.[k];
  return typeof v === "number" && Number.isFinite(v) ? v : null;
};
/** The hour (UTC, its start) a record or a stretch begins at, or null. */
export const at = (f: GridFile, y: string, k: string): string | null => {
  const v = f.years[y]?.[`${k}_at`];
  return typeof v === "string" && v ? v : null;
};
/** A year is whole when the hours it was due are a whole year's (8,760 or 8,784): the newest year is not. */
export const wholeYear = (f: GridFile, y: string): boolean => (get(f, y, "hours_in_year") ?? 0) >= 8760;
/** The newest whole year, else the newest year; null when none. */
export function defaultYear(f: GridFile): string | null {
  const ys = yearsOf(f);
  const whole = ys.filter((y) => wholeYear(f, y));
  return whole.length ? whole[whole.length - 1] : ys.length ? ys[ys.length - 1] : null;
}

/** An hour as a reader sees it in the grid's own time: "19 January 2025, 16:00". */
export function when(iso: string | null, tz: string): string {
  if (!iso) return "not held";
  const d = new Date(iso);
  const day = d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: tz });
  const hour = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: tz });
  return `${day}, ${hour}`;
}
/** A stretch of n hours as days and hours: 38 as "1 day 14 hours". */
export function span(hours: number | null): string {
  if (hours === null) return "not held";
  const d = Math.floor(hours / 24), h = Math.round(hours - d * 24);
  const days = d ? `${d} day${d === 1 ? "" : "s"}` : "", hs = h || !d ? `${h} hour${h === 1 ? "" : "s"}` : "";
  return [days, hs].filter(Boolean).join(" ");
}

/** A fuel's line of the tightest hours: its mean output, its installed capacity and the share; null where not held. */
export type FuelRow = { fuel: string; name: string; mw: number | null; capacity: number | null; share: number | null; why: string | null };
export function fuelRows(f: GridFile, y: string): FuelRow[] {
  return f.fuels.map((fuel) => {
    const mw = get(f, y, `tight_${fuel}_mw`), capacity = get(f, y, `capacity_${fuel}_mw`), share = get(f, y, `tight_${fuel}_share_of_capacity_pct`);
    const why = mw === null ? "the source file does not report it for this year"
      : share !== null ? null
      : f.together.includes(fuel) ? "set against capacity with the other of the two, in the last line"
      : !f.all_years.includes(fuel) && Number(y) < f.from_year ? `installed capacity is held from ${f.from_year} only` : "no installed capacity is held";
    return { fuel, name: FUEL_NAME[fuel] ?? fuel, mw, capacity, share, why };
  });
}

export const whole = (v: number | null): string => (v === null ? "not held" : Math.round(v).toLocaleString("en-US"));
export const one = (v: number | null): string => (v === null ? "not held" : v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 }));
export const pct = (v: number | null, digits = 1): string => (v === null ? "not held" : `${v.toFixed(digits)}%`);
export const href = (grid: string, year?: string | null): string => `/mix/stress?grid=${grid}${year ? `&year=${year}` : ""}`;
