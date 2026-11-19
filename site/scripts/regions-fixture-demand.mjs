// Energy Research Warehouse (ERW) site, session 8420 (chain 503, part C): fixtures in the form of the data machine's
// page files of demand for the whole country (docs/state/page_files_regions.md, sections 2 and 3: index.json,
// demand/<region>.json, demand/ba/<code>.json), for tests only. Every value here is made by a rule a test can recompute
// (a place's number times a round figure), is not data, and is never shown on the site: each file says so in its
// `fixture` line, and the site's reader (lib/countryfiles.ts readRegionFile) refuses a fixture in the site's own
// folder. The real files are written by the data machine from EIA's Form EIA-930. The names of the regions and of the
// balancing authorities are EIA's; nothing else here is anyone's figure.
import fs from "node:fs";
import path from "node:path";

export const CODES = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"];
export const NAMES = { CAL: "California", CAR: "Carolinas", CENT: "Central", FLA: "Florida", MIDA: "Mid-Atlantic", MIDW: "Midwest", NE: "New England", NW: "Northwest", NY: "New York", SE: "Southeast", SW: "Southwest", TEN: "Tennessee", TEX: "Texas" };
const TZ = { CAL: "America/Los_Angeles", CAR: "America/New_York", CENT: "America/Chicago", FLA: "America/New_York", MIDA: "America/New_York", MIDW: "America/Chicago", NE: "America/New_York", NW: "America/Los_Angeles", NY: "America/New_York", SE: "America/Chicago", SW: "America/Phoenix", TEN: "America/Chicago", TEX: "America/Chicago" };
const GRIDS = { CAL: ["CISO"], CENT: ["SWPP"], MIDA: ["PJM"], MIDW: ["MISO"], NE: ["ISNE"], NY: ["NYIS"], TEX: ["ERCO"] };
/** The balancing authorities of the fixture's index: number, region, the grid it is, generation only, retired, the first year held. */
export const BAS = {
  TVA: { n: 21, name: "Tennessee Valley Authority", region: "TEN" },
  DUK: { n: 22, name: "Duke Energy Carolinas", region: "CAR" },
  CPLE: { n: 23, name: "Duke Energy Progress East", region: "CAR" },
  ERCO: { n: 24, name: "Electric Reliability Council of Texas, Inc.", region: "TEX", grid: "ERCO" },
  SOCO: { n: 25, name: "Southern Company Services, Inc. - Trans", region: "SE" },
  SEPA: { n: 26, name: "Southeastern Power Administration", region: "SE", generation_only: true },
  AEC: { n: 27, name: "PowerSouth Energy Cooperative", region: "SE", retired: "2021-09-01", active: false },
  GRID: { n: 28, name: "Gridforce Energy Management, LLC", region: "NW", first_year: 2022 },
};
/** The pairs the contract names: a region that covers nearly the ground of one of the seven grids. */
export const ALIKE = { TEX: "ERCO", NY: "NYIS", NE: "ISNE", MIDA: "PJM" };
/** Written as the data machine's builder writes its own (warehouse/derived/regions_pages.py): a clause with no capital
 *  and no full stop. The view sets it as a sentence and changes none of its words. */
export const WHY = "a clause made for a test: the region is EIA's sum of its authorities and the grid is one of them";
const FIXTURE = "made by a rule for a test (site/scripts/regions-fixture-demand.mjs); not data";
const BUILT = "2026-11-19T12:00:00Z";
const r2 = (v) => Math.round(v * 100) / 100;
const pad = (n) => String(n).padStart(2, "0");
/** The number of a place: 1 to 13 for the regions in EIA's order, 21 and up for the fixture's balancing authorities. */
export const numberOf = (code, level = "region") => (level === "region" ? CODES.indexOf(code) + 1 : BAS[code].n);

/** index.json: the thirteen regions and the fixture's eight balancing authorities. */
export function indexFixture() {
  return {
    fixture: FIXTURE, built: BUILT, tables: ["eia930_ba_demand_hourly", "eia930_region_hourly"], method: "docs/methods/demand_growth.md", license: "public",
    regions: CODES.map((code) => ({
      code, name: NAMES[code], tz: TZ[code], bas: Object.keys(BAS).filter((b) => BAS[b].region === code), grids: GRIDS[code] ?? [],
      first_hour: "2018-07-01T05:00:00Z", last_hour: "2026-11-17T05:00:00Z",
    })),
    bas: Object.entries(BAS).map(([code, b]) => ({
      code, name: b.name, region: b.region, tz: TZ[b.region], grid: b.grid ?? null, region_grids: GRIDS[b.region] ?? [], generation_only: !!b.generation_only,
      active: b.active ?? true, retired: b.retired ?? null, first_hour: `${b.first_year ?? 2018}-07-01T05:00:00Z`, last_hour: b.retired ? "2021-09-01T04:00:00Z" : "2026-11-17T05:00:00Z",
      files: b.generation_only ? ["mix"] : ["demand"],
    })),
  };
}

/** The average demand the rule gives place number i in year y: 1000 i + 100 (y - 2019) MW. The peak is twice it. */
export const avgOf = (i, y) => 1000 * i + 100 * (y - 2019);

/** One place's file. Place number i (numberOf), `n` local days from `first`.
 *  daily: day d (from 0) has 24 hours, a demand of 24 (1000 i + 10 d) MWh and a highest hour of 1000 i + 10 d + 500 MW at
 *  22:00 UTC; day 3 holds 20 of its hours, so its demand and its highest hour are null.
 *  growth: base 2019, last whole year 2025, the year so far to 2026-10; year y averages avgOf(i, y) MW with a peak of
 *  twice that on 15 August at 21:00 UTC; the year so far averages 50 MW more; each growth is the plain percent of those,
 *  to two decimals. Month m (1 to 12) and hour h (0 to 23) of 2025: growth_mw m + h and growth_pct m - 6 + h / 10; the
 *  cell of February at 03:00 is absent. A place whose first year is after 2019 has no figure since 2019.
 *  weather (regions only): fitted on 2019 to 2021 (`train`); years 2022 to 2026, four figures each: growth i + (y - 2021)
 *  percent, of which the weather explains 1, with a give or take of 2; 2026 stops on 6 November; the winter peak of 2022
 *  is null. holdout 2019 to 2021.
 *  alike (TEX, NY, NE, MIDA): the grid's average is 100 MW under the region's each year. */
export function demandFixture(code, { level = "region", first = "2024-12-25", n = 17, license = "public", weather = true, tables } = {}) {
  const i = numberOf(code, level);
  const ba = level === "ba" ? BAS[code] : null;
  const firstYear = ba?.first_year ?? 2019;
  const t0 = Date.parse(`${first}T00:00:00Z`);
  const days = Array.from({ length: n }, (_, d) => new Date(t0 + d * 86_400_000).toISOString().slice(0, 10));
  const daily = {
    days,
    demand_mwh: days.map((_, d) => (d === 3 ? null : 24 * (1000 * i + 10 * d))),
    peak_mw: days.map((_, d) => (d === 3 ? null : 1000 * i + 10 * d + 500)),
    peak_at: days.map((day, d) => (d === 3 ? null : `${day}T22:00:00Z`)),
    hours: days.map((_, d) => (d === 3 ? 20 : 24)),
  };
  const years = {}, at = {};
  for (let y = firstYear; y <= 2025; y++) {
    const avg = avgOf(i, y), leap = y % 4 === 0;
    const row = { avg_demand_mw: avg, hours_used: leap ? 8784 : 8760, hours_in_year: leap ? 8784 : 8760, peak_demand_mw: 2 * avg, ytd_avg_demand_mw: avg + 50, ytd_hours_used: 7295, ytd_hours_in_window: 7295, ytd_peak_demand_mw: 2 * avg };
    if (firstYear === 2019 && y > 2019) {
      row.avg_demand_growth_since_2019_pct = r2(((avg - avgOf(i, 2019)) / avgOf(i, 2019)) * 100);
      row.peak_demand_growth_since_2019_pct = row.avg_demand_growth_since_2019_pct;
      row.ytd_avg_demand_growth_since_2019_pct = r2(((avg - avgOf(i, 2019)) / (avgOf(i, 2019) + 50)) * 100);
      row.ytd_peak_demand_growth_since_2019_pct = row.avg_demand_growth_since_2019_pct;
    }
    if (y > firstYear) row.avg_demand_growth_yoy_pct = r2((100 / avgOf(i, y - 1)) * 100);
    if (y === 2025 && firstYear === 2019) {
      for (let m = 1; m <= 12; m++) {
        row[`growth_mw_m${pad(m)}`] = m; row[`growth_pct_m${pad(m)}`] = m - 6;
        for (let h = 0; h < 24; h++) {
          if (m === 2 && h === 3) continue;
          row[`growth_mw_m${pad(m)}_h${pad(h)}`] = m + h; row[`growth_pct_m${pad(m)}_h${pad(h)}`] = r2(m - 6 + h / 10);
        }
      }
      for (let h = 0; h < 24; h++) { row[`growth_mw_h${pad(h)}`] = h; row[`growth_pct_h${pad(h)}`] = r2(h / 10); }
    }
    years[String(y)] = row;
    at[String(y)] = { peak_demand_mw: `${y}-08-15T21:00:00Z`, ytd_peak_demand_mw: `${y}-08-15T21:00:00Z` };
  }
  const ytd = avgOf(i, 2026) + 50;
  years["2026"] = { ytd_avg_demand_mw: ytd, ytd_hours_used: 7295, ytd_hours_in_window: 7295, ytd_peak_demand_mw: 2 * avgOf(i, 2026) };
  if (firstYear === 2019) {
    years["2026"].ytd_avg_demand_growth_since_2019_pct = r2(((ytd - (avgOf(i, 2019) + 50)) / (avgOf(i, 2019) + 50)) * 100);
    years["2026"].ytd_peak_demand_growth_since_2019_pct = r2(((avgOf(i, 2026) - avgOf(i, 2019)) / avgOf(i, 2019)) * 100);
  }
  at["2026"] = { ytd_peak_demand_mw: "2026-07-22T22:00:00Z" };
  const file = {
    fixture: FIXTURE, built: BUILT, tables: tables ?? (level === "region" ? ["eia930_region_hourly"] : ["eia930_ba_demand_hourly"]), method: "docs/methods/demand_growth.md", license,
    code, name: level === "region" ? NAMES[code] : ba.name, tz: TZ[level === "region" ? code : ba.region], level,
    basis: level === "region" ? "region_sum" : "ba",
    screened: { blank: i, not_positive: 0, jumps: 2 * i },
    daily,
    growth: { base: 2019, last_year: 2025, ytd_through: "2026-10", years, at },
  };
  if (level === "ba") file.region = ba.region;
  if (level === "region") {
    file.bas_summed =Object.keys(BAS).filter((b) => BAS[b].region === code && !BAS[b].generation_only);
    if (weather) {
      const wy = {};
      for (let y = 2022; y <= 2026; y++) {
        const fig = (key) => {
          const growth = i + (y - 2021);
          return { actual: avgOf(i, y), expected: avgOf(i, y) - 10, base: avgOf(i, 2020), growth_pct: growth, weather_pct: 1, unexplained_pct: growth - 1, uncertainty_pct: 2, holdouts: 3,
            finding: Math.abs(growth - 1) > 2, window: key === "energy" || key === "overnight_min" ? "the year" : "the season", used: 8700, wanted: 8760, at: key === "energy" || key === "overnight_min" ? null : `${y}-08-15T21:00:00Z` };
        };
        wy[String(y)] = { energy: fig("energy"), summer_peak: fig("summer_peak"), winter_peak: y === 2022 ? null : fig("winter_peak"), overnight_min: fig("overnight_min") };
      }
      const held = (y) => ({ growth_pct: 0.5, weather_pct: 0.25, unexplained_pct: r2(0.25 + (y - 2020) / 10), actual: avgOf(i, y), expected: avgOf(i, y) - 10 });
      file.weather = {
        name: NAMES[code], tz: TZ[code], through: "11-06", newest: 2026, train: [2019, 2020, 2021], weather_table: "region_weather_hourly",
        degrees_from: "the region's weighted temperature (base 65 F)",
        fit: { hours: 26000, kinds: 48, in_sample_mape_pct: 3, oos_mape_pct: r2(3 + i / 10), oos_daily_mape_pct: r2(2 + i / 10), plain_oos_mape_pct: 5, oos_by_year: {}, hours_not_used: 0, hours_held: 26304, shed_hours: 0 },
        years: wy,
        holdout: Object.fromEntries([2019, 2020, 2021].map((y) => [String(y), { energy: held(y), summer_peak: held(y), winter_peak: y === 2019 ? null : held(y), overnight_min: held(y) }])),
      };
    }
    if (ALIKE[code]) {
      file.alike = { grid: ALIKE[code], why: WHY, years: Object.fromEntries(Array.from({ length: 7 }, (_, k) => 2019 + k).map((y) => {
        const region = avgOf(i, y), grid = region - 100;
        return [String(y), { region_avg_demand_mw: region, grid_avg_demand_mw: grid, difference_pct: r2(((region - grid) / grid) * 100) }];
      })) };
    }
  }
  return file;
}

/** The fixture written as a folder of page files, as the data machine lays them out: index.json, a file for each of
 *  `regions` and each of `bas`. Returns the folder. */
export function writeFixtureFolder(dir, { regions = CODES, bas = Object.keys(BAS).filter((b) => !BAS[b].generation_only), index = true } = {}) {
  fs.mkdirSync(path.join(dir, "demand", "ba"), { recursive: true });
  if (index) fs.writeFileSync(path.join(dir, "index.json"), JSON.stringify(indexFixture()));
  for (const code of regions) fs.writeFileSync(path.join(dir, "demand", `${code.toLowerCase()}.json`), JSON.stringify(demandFixture(code)));
  for (const code of bas) fs.writeFileSync(path.join(dir, "demand", "ba", `${code.toLowerCase()}.json`), JSON.stringify(demandFixture(code, { level: "ba" })));
  return dir;
}
