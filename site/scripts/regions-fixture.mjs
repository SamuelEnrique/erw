// Energy Research Warehouse (ERW) site, session 8410 (chain 503): a fixture in the form of the data machine's page files
// of the whole country (docs/state/page_files_regions.md), for tests only. Every value here is made by a rule a test can
// recompute (a region's number times a round figure), is not data, and is never shown on the site: the file says so in
// its `fixture` line, and the site's reader (lib/countryfiles.ts readRegionFile) refuses a fixture in the site's own
// folder. The real files are written by the data machine from EIA's Form EIA-930.
export const CODES = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"];
export const SOURCE_KEYS = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"];
const FIXTURE = "made by a rule for a test (site/scripts/regions-fixture.mjs); not data";

/** An event's file: `n` hours from `start`. Region i (1 to 13 in EIA's order) has a baseline demand of 1000 i MW in
 *  every hour and an event demand of 1000 i + h MW in hour h; Tennessee's event demand is 1.2 times its baseline and the
 *  Carolinas' 0.9 times. Net imports: Tennessee +500 (baseline -100), the Carolinas -300 (baseline -300), the others
 *  10 i (baseline 0). Each source s (1 to 8) generates 100 i s in the event and 100 i s - 10 s in the baseline; storage
 *  is negative. The Northwest is not in the file; the Southwest's first six hours are null; Florida has no coal.
 *  Pairs: CAR-TEN +200 (baseline -50), SE-TEN -150 (baseline -150), FLA-SE 0 (baseline 25). */
export function eventFixture({ event = "elliott_2022", start = "2022-12-19", end = "2022-12-20", first = "2022-12-19T05:00:00Z", n = 48, license = "public", tables = ["eia930_region_hourly", "eia930_region_fuel_hourly", "eia930_region_pair_hourly"] } = {}) {
  const arr = (f) => Array.from({ length: n }, (_, h) => f(h));
  const regions = {};
  CODES.forEach((code, k) => {
    const i = k + 1;
    if (code === "NW") return;
    const nul = (f) => (code === "SW" ? arr((h) => (h < 6 ? null : f(h))) : arr(f));
    const demand = code === "TEN" ? nul(() => 1200 * i) : code === "CAR" ? nul(() => 900 * i) : nul((h) => 1000 * i + h);
    const imports = code === "TEN" ? nul(() => 500) : code === "CAR" ? nul(() => -300) : nul(() => 10 * i);
    const importsBase = code === "TEN" ? nul(() => -100) : code === "CAR" ? nul(() => -300) : nul(() => 0);
    const gen = {}, genBase = {};
    SOURCE_KEYS.forEach((s, j) => {
      if (code === "FLA" && s === "coal") return;
      const sign = s === "storage" ? -1 : 1;
      gen[s] = nul(() => sign * 100 * i * (j + 1));
      genBase[s] = nul(() => sign * (100 * i * (j + 1) - 10 * (j + 1)));
    });
    regions[code] = {
      demand_mw: demand, net_generation_mw: nul(() => 3000 * i), net_imports_mw: imports, gen,
      baseline: { demand_mw: nul(() => 1000 * i), net_generation_mw: nul(() => 2900 * i), net_imports_mw: importsBase, gen: genBase },
    };
  });
  return {
    fixture: FIXTURE, built: "2026-11-19T12:00:00Z", tables, method: "docs/methods/events.md", license,
    event, title: "A fixture", start, end,
    baseline: "same weekdays 364 and 728 days earlier", baseline_offsets_days: [364, 728],
    hours: { start: first, step_hours: 1, n },
    regions,
    pairs: {
      "CAR-TEN": { flow_mw: arr(() => 200), baseline_mw: arr(() => -50) },
      "SE-TEN": { flow_mw: arr(() => -150), baseline_mw: arr(() => -150) },
      "FLA-SE": { flow_mw: arr(() => 0), baseline_mw: arr(() => 25) },
    },
  };
}
