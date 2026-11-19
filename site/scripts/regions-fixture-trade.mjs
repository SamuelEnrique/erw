// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): fixtures in the form of the data machine's
// trade, matrix, mix and index files of the whole country (docs/state/page_files_regions.md, sections 5, 7, 4 and 2),
// for tests only. Every value here is made by a rule a test can recompute (a region's number times a round figure), is
// not data, and is never shown on the site: each file says so in its `fixture` line, and the site's reader
// (lib/countryfiles.ts readRegionFile) refuses a fixture in the site's own folder. The real files are written by the
// data machine from EIA's Form EIA-930. Session 8410's fixture of an event's file is scripts/regions-fixture.mjs.
export const CODES = ["CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NW", "NY", "SE", "SW", "TEN", "TEX"];
export const PLACES = [...CODES, "CAN", "MEX"];
export const SOURCE_KEYS = ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"];
const FIXTURE = "made by a rule for a test (site/scripts/regions-fixture-trade.mjs); not data";
const BUILT = "2026-11-19T12:00:00Z";
const head = (tables, license, method) => ({ fixture: FIXTURE, built: BUILT, tables, method, license });

/** The months from July 2018 to October 2026, 100 of them. */
export function fixtureMonths(first = "2018-07", n = 100) {
  const out = [];
  let y = Number(first.slice(0, 4)), m = Number(first.slice(5, 7));
  for (let i = 0; i < n; i++) { out.push(`${y}-${String(m).padStart(2, "0")}`); m++; if (m > 12) { m = 1; y++; } }
  return out;
}
/** The fixture's own neighbours of each region (a rule of the fixture, not a map of the grid). */
export const NEIGHBOURS = {
  CAL: ["NW", "SW", "MEX"], CAR: ["MIDA", "SE", "TEN"], CENT: ["MIDW", "SW", "TEX"], FLA: ["SE"], MIDA: ["CAR", "MIDW", "NY", "TEN"], MIDW: ["CENT", "MIDA", "TEN", "CAN"],
  NE: ["NY", "CAN"], NW: ["CAL", "SW", "CAN"], NY: ["MIDA", "NE", "CAN"], SE: ["CAR", "FLA", "TEN"], SW: ["CAL", "CENT", "NW"], TEN: ["CAR", "CENT", "MIDA", "MIDW", "SE"], TEX: ["CENT", "MEX"],
};
/** The place of a code in PLACES, from 1. */
export const at = (code) => PLACES.indexOf(code) + 1;
/** The own report of region `code` with neighbour `nb` in month position m, MWh: 1000 (j - i) + 10 m. */
export const ownOf = (code, nb, m) => 1000 * (at(nb) - at(code)) + 10 * m;

/** A region's trade file. For each neighbour and month position m: the own report is ownOf; the neighbour's report is
 *  the own report less 50 (a gap of +50), but Tennessee's neighbour the Southeast reports 0.8 of Tennessee's own (a gap
 *  of 0.2 of it); hours 720 on the neighbour's side and both, 744 on the own side in an even position, 720 in an odd.
 *  The Carolinas hold nothing of the Southeast in the first three months (so the total is null there), and the Midwest's
 *  report of Tennessee is null in position 90 (January 2026), with its gap. The total is the sum of the own reports. */
export function tradeFixture(code, { license = "public", tables = ["eia930_region_pair_hourly"] } = {}) {
  const months = fixtureMonths();
  const neighbors = {};
  for (const nb of NEIGHBOURS[code]) {
    const none = (m) => code === "CAR" && nb === "SE" && m < 3;
    const own = months.map((_, m) => (none(m) ? null : ownOf(code, nb, m)));
    const their = months.map((_, m) => (none(m) ? null : code === "TEN" && nb === "MIDW" && m === 90 ? null : code === "TEN" && nb === "SE" ? 0.8 * ownOf(code, nb, m) : ownOf(code, nb, m) - 50));
    neighbors[nb] = {
      net_imports_mwh: own, their_report_mwh: their, gap_mwh: own.map((v, m) => (v === null || their[m] === null ? null : v - their[m])),
      hours_own: months.map((_, m) => (none(m) ? null : m % 2 === 0 ? 744 : 720)), hours_their: months.map((_, m) => (none(m) || their[m] === null ? null : 720)),
      hours_both: months.map((_, m) => (none(m) || their[m] === null ? null : 720)),
    };
  }
  const net = months.map((_, m) => { const vs = NEIGHBOURS[code].map((nb) => neighbors[nb].net_imports_mwh[m]); return vs.some((v) => v === null) ? null : vs.reduce((s, v) => s + v, 0); });
  return { ...head(tables, license, "docs/methods/regions_trade.md"), code, name: code, months, net_imports_mwh: net, neighbors };
}

export const MATRIX_YEARS = [2023, 2024, 2025, 2026];
export const REGION_PAIRS = [["CAR", "SE"], ["CAR", "TEN"], ["SE", "TEN"], ["FLA", "SE"], ["CAL", "NW"], ["CAL", "MEX"], ["CAN", "NW"], ["MIDA", "NY"], ["CENT", "TEX"], ["NW", "SW"]];
export const BA_PAIRS = [["DUK", "TVA"], ["SOCO", "TVA"], ["BPAT", "CISO"], ["ERCO", "SWPP"]];
/** One pair's year. Pair k (from 1) in year y: the first side's report is 1,000,000 k + 1000 (y - 2023), below zero for
 *  an even k (the flow runs from the second to the first); the second side's report is 0.98 of it. SE-TEN's second side
 *  reports half (a large gap); FLA-SE is zero on both sides and names no direction; NW-SW's second side is not held, so
 *  it has no mean, no gap and no direction. */
export function pairOf([a, b], k, y) {
  const key = `${a}-${b}`;
  if (key === "FLA-SE") return { a, b, year: y, a_report_mwh: 0, b_report_mwh: 0, mean_mwh: 0, gap_mwh: 0, direction: null };
  const one = (k % 2 === 0 ? -1 : 1) * (1_000_000 * k + 1000 * (y - 2023));
  if (key === "NW-SW") return { a, b, year: y, a_report_mwh: one, b_report_mwh: null, mean_mwh: null, gap_mwh: null, direction: null };
  const two = (key === "SE-TEN" ? 0.5 : 0.98) * one;
  return { a, b, year: y, a_report_mwh: one, b_report_mwh: two, mean_mwh: (one + two) / 2, gap_mwh: one - two, direction: one + two > 0 ? "a_to_b" : "b_to_a" };
}
export const PARTNERS = {
  TVA: { by_gross: ["SOCO", "MISO", "PJM", "DUK"], by_net: ["MISO", "SOCO", "PJM", "DUK"], share: 7.5 },
  DUK: { by_gross: ["TVA", "SOCO"], by_net: ["SOCO", "TVA"], share: -2.25 },
  BPAT: { by_gross: ["CISO"], by_net: ["CISO"], share: -12 },
};
/** The matrix file: every pair in every year by pairOf (the balancing authorities' pairs counted on from the regions'),
 *  and three authorities' partners, the same lists each year, the share plus the year less 2023. */
export function matrixFixture({ license = "public", tables = ["interchange_pair_monthly", "ba_trade_partners"] } = {}) {
  const partners = {};
  for (const [ba, p] of Object.entries(PARTNERS)) partners[ba] = Object.fromEntries(MATRIX_YEARS.map((y) => [String(y), { by_gross: p.by_gross, by_net: p.by_net, net_import_share_of_demand_pct: p.share + (y - 2023) }]));
  return {
    ...head(tables, license, "docs/methods/regions_trade.md"), years: MATRIX_YEARS, regions: PLACES,
    region_pairs: MATRIX_YEARS.flatMap((y) => REGION_PAIRS.map((p, i) => pairOf(p, i + 1, y))),
    ba_pairs: MATRIX_YEARS.flatMap((y) => BA_PAIRS.map((p, i) => pairOf(p, REGION_PAIRS.length + i + 1, y))),
    partners,
  };
}

const DAYS = (month) => new Date(Date.UTC(Number(month.slice(0, 4)), Number(month.slice(5, 7)), 0)).getUTCDate();
/** A source's energy in a region's month, MWh: 1000 i j + 10 m for source j (from 1) of region i in month position m;
 *  storage (j 7) is -100 i. */
export const energyOf = (code, j, m) => (j === 7 ? -100 * at(code) : 1000 * at(code) * j + 10 * m);
/** A region's mix file. Net generation is the sum of the sources; a share is the energy over it, in percent, to two
 *  decimals. Florida has no coal; the Southwest's first month is January 2019; the Carolinas lack June 2025; Tennessee
 *  holds 26 of February 2025's 28 days. */
export function mixFixture(code, { license = "public", tables = ["eia930_region_fuel_hourly"] } = {}) {
  const all = fixtureMonths();
  const months = {};
  all.forEach((month, m) => {
    if (code === "SW" && month < "2019-01") return;
    if (code === "CAR" && month === "2025-06") return;
    const keys = SOURCE_KEYS.filter((s) => !(code === "FLA" && s === "coal"));
    const e = Object.fromEntries(keys.map((s) => [s, energyOf(code, SOURCE_KEYS.indexOf(s) + 1, m)]));
    const net = Object.values(e).reduce((s, v) => s + v, 0);
    const days = DAYS(month);
    const row = { avg: {}, net_generation_mwh: net, days_held: code === "TEN" && month === "2025-02" ? 26 : days, days_in_month: days, side: "eia930" };
    for (const s of keys) {
      row[`${s}_mwh`] = e[s];
      row[`${s}_share_pct`] = Math.round((e[s] / net) * 10000) / 100;
      row.avg[s] = Array.from({ length: 24 }, () => Math.round(e[s] / (days * 24)));
    }
    months[month] = row;
  });
  const held = Object.keys(months).sort();
  return { ...head(tables, license, "docs/methods/regions_mix.md"), grid: code.toLowerCase(), name: code, tz: "America/New_York", join: null, first: held[0], upto: held[held.length - 1], sources: SOURCE_KEYS, months, years: {} };
}

/** The index file, as far as the section reads it: the names and regions of nine balancing authorities. */
export function indexFixture() {
  const bas = [["TVA", "Tennessee Valley Authority", "TEN"], ["DUK", "Duke Energy Carolinas", "CAR"], ["SOCO", "Southern Company Services", "SE"], ["BPAT", "Bonneville Power Administration", "NW"],
    ["CISO", "California Independent System Operator", "CAL"], ["ERCO", "Electric Reliability Council of Texas", "TEX"], ["SWPP", "Southwest Power Pool", "CENT"], ["MISO", "Midcontinent Independent System Operator", "MIDW"], ["PJM", "PJM Interconnection", "MIDA"]];
  return { ...head(["eia930_ba_demand_hourly"], "public", "docs/methods/regions_index.md"), regions: CODES.map((code) => ({ code, name: code, bas: bas.filter((b) => b[2] === code).map((b) => b[0]) })), bas: bas.map(([code, name, region]) => ({ code, name, region })) };
}

/** The four readers the section takes, from the fixtures; `without` lists files that are not built ("trade/fla", "mix/nw", "matrix", "index"). */
export function fixtureReaders({ without = [], license = "public", tables } = {}) {
  const gone = (k) => without.includes(k);
  return {
    trade: (code) => (gone(`trade/${code.toLowerCase()}`) || !NEIGHBOURS[code] ? null : tradeFixture(code, { license, ...(tables ? { tables } : {}) })),
    mix: (code) => (gone(`mix/${code.toLowerCase()}`) || !CODES.includes(code) ? null : mixFixture(code, { license, ...(tables ? { tables } : {}) })),
    matrix: () => (gone("matrix") ? null : matrixFixture({ license, ...(tables ? { tables } : {}) })),
    index: () => (gone("index") ? null : indexFixture()),
  };
}
