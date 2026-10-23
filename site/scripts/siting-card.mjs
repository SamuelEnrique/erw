// Energy Research Warehouse (ERW) site, session 720 (chain 050): the All grids tab's research card, in the findings
// pipeline's format (lib/findings.ts, Card), written from the tab's own functions (lib/siting.ts, through
// scripts/siting-files.mjs), so every figure on the card is the tab's figure for the same load. Under the datacenter
// profile, a 1 GW load: where it pays least and most per MWh all-in, among the rows with every cost part held, and the
// range of months to connect across the grids; one chart (the all-in figure of each such row) with its source line. No
// verdict. Written, never posted or sent: the card is a file under data/findings/ and its data a CSV under
// public/findings/.
//
// Session 734 (chain 062): a second card, siting_flexible: under the flexible compute profile, the hours a 1 GW load gives
// up at ERCOT's four summer peaks and at or above its strike, at each ERCOT hub and zone, and what it saves per MWh
// all-in against a flat datacenter load at the same row. The same rules: the tab's functions, no verdict, not sent.
//
//   node scripts/siting-card.mjs            writes both cards' JSON under data/findings/ and their CSVs under public/findings/
//   node scripts/siting-card.mjs --check    exit 1 when a file on disk differs from a fresh computation (but for the time)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const F = await import("./siting-files.mjs");
const S = await import("../lib/siting.ts");
const f = F.files(), d = await F.dc();
const ID = "siting_gigawatt", MW = 1000;
const x = S.sitingInputs({ view: "allgrids", mw: String(MW) });
const hubs = S.hubRows(f.index);
const held = hubs.map((r) => ({ r, allin: S.columnValue(d, f, r, x, "allin"), energy: S.columnValue(d, f, r, x, "energy"), tx: S.columnValue(d, f, r, x, "transmission") }))
  .filter((v) => v.allin !== null).sort((a, b) => a.allin - b.allin || a.r.id.localeCompare(b.r.id));
if (!held.length) { console.error("siting-card: no row has every cost part held"); process.exit(1); }
const lo = held[0], hi = held.at(-1);
const ylo = S.yearOf(d, f, lo.r, x), yhi = S.yearOf(d, f, hi.r, x);
const connect = S.GRID_ORDER.map((g) => ({ g, v: S.connectCell(f, hubs.find((r) => r.grid === g)) })).filter((c) => "median" in c.v.gen && c.v.gen.median !== null)
  .map((c) => ({ g: c.g, m: c.v.gen.median, n: c.v.gen.n })).sort((a, b) => a.m - b.m);
const cmin = connect[0], cmax = connect.at(-1);
const name = (r) => `${S.GRID_NAMES[r.grid]} ${r.region}`;
const two = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const whole = (v) => Math.round(v).toLocaleString("en-US");
const notHeld = hubs.length - held.length;
const conn = f.connect;
const card = {
  id: ID, card_id: ID, title: "WHERE A GIGAWATT PAYS LEAST", kind: "visual", engine: "site/scripts/siting-card.mjs",
  subtitle: `A 1 GW datacenter load, all-in per MWh, at the ${held.length} rows of the All grids tab whose every cost part is held`,
  params: { mw: MW, profile: "datacenter" }, inputs_words: { mw: "1,000 MW", profile: "Datacenter: 0.90 in every hour, never curtails" },
  chart: {
    kind: "bars_free", x: held.map((v) => v.r.region), x_label: `Row of the All grids tab (${[...new Set(held.map((v) => S.GRID_NAMES[v.r.grid]))].join(", ")})`,
    series: [
      { name: "Energy, day-ahead, twelve months", type: "bar", unit: "USD per MWh", values: held.map((v) => v.energy) },
      { name: "Four-peak transmission charge", type: "bar", unit: "USD per MWh", values: held.map((v) => v.tx) },
    ],
    y_left_label: "USD per MWh", decimals: 2,
  },
  callouts: [
    { label: "All-in, USD per MWh, least and most", before: { period: name(lo.r), text: two(lo.allin) }, after: { period: name(hi.r), text: two(hi.allin) }, unit: "" },
    { label: "A year at 1 GW, USD", before: { period: lo.r.region, text: whole(ylo.usd) }, after: { period: hi.r.region, text: whole(yhi.usd) }, unit: "" },
    { label: "Median months to connect, generators", before: { period: S.GRID_NAMES[cmin.g], text: two(cmin.m) }, after: { period: S.GRID_NAMES[cmax.g], text: two(cmax.m) }, unit: "" },
  ],
  why: `A 1 GW datacenter load, drawing 0.90 of its size in every hour, paid least all-in at ${name(lo.r)}: USD ${two(lo.allin)} per MWh, USD ${whole(ylo.usd)} a year, and most at ${name(hi.r)}: USD ${two(hi.allin)} per MWh, USD ${whole(yhi.usd)} a year. All-in is the day-ahead price over the last twelve whole months, the four-peak transmission charge at the Commission's rate, and capacity, of which ERCOT has none. Only ${held.length} of the tab's ${hubs.length} rows hold every part: elsewhere transmission is not held, or capacity is held under a license (${notHeld} rows). Generators took a median of ${two(cmin.m)} months from request to operation in ${S.GRID_NAMES[cmin.g]} and ${two(cmax.m)} in ${S.GRID_NAMES[cmax.g]}, over the requests that came online from ${conn.from} to ${conn.to}.`,
  footnote: `Data: the All grids tab of "What a datacenter pays" (/cost-of-power?view=allgrids&mw=${MW}), computed by site/lib/siting.ts from the page's own files: the hourly hub and zone prices (ercot_all_hub_prices_history, ercot_zone_prices_history), ercot_4cp_intervals and the Commission's approved rate (texas_transmission_matrix), and ${conn.table} (Berkeley Lab's Queued Up, ${conn.vintage}). Method: docs/methods/siting.md. The replication: warehouse/replication/siting.py.`,
  numbers: {
    rows: hubs.length, rows_held: held.length, rows_not_held: notHeld,
    least_allin: lo.allin, least_row: lo.r.id, least_energy: lo.energy, least_tx: lo.tx, least_year_usd: ylo.usd,
    most_allin: hi.allin, most_row: hi.r.id, most_energy: hi.energy, most_tx: hi.tx, most_year_usd: yhi.usd,
    year_mwh: ylo.mwh, connect_least: cmin.m, connect_least_grid: cmin.g, connect_most: cmax.m, connect_most_grid: cmax.g,
  },
  source_line: `Source: ERW, the All grids tab (/cost-of-power?view=allgrids), from ERCOT's prices and four-peak intervals, the PUCT's transmission matrix and Berkeley Lab's Queued Up (${conn.vintage}).`,
  tables: ["ercot_all_hub_prices_history", "ercot_zone_prices_history", "ercot_4cp_intervals", "texas_transmission_matrix", conn.table],
  computed_at: new Date().toISOString().slice(0, 19) + "Z",
  method: "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/siting.md",
  downloads: { csv: `${ID}.csv`, python: "", stata: "" }, csv_sha256: "",
  csv_header: [`Energy Research Warehouse (ERW): finding ${ID}, WHERE A GIGAWATT PAYS LEAST`, "Computed by site/scripts/siting-card.mjs from site/lib/siting.ts (the All grids tab); method docs/methods/siting.md",
    "Rows: one per row of the tab whose every cost part is held, a 1 GW datacenter load: energy, transmission, capacity and all-in in USD per MWh, the year in USD"],
};
const csv = [...card.csv_header.map((h) => `# ${h}`), "row,grid,energy_usd_mwh,transmission_usd_mwh,capacity_usd_mwh,allin_usd_mwh,year_usd_1gw",
  ...held.map((v) => [v.r.id, v.r.grid, v.energy, v.tx, 0, v.allin, S.yearOf(d, f, v.r, x).usd].join(","))].join("\n") + "\n";
// ---- session 734: the second card, siting_flexible ----
const ID2 = "siting_flexible";
const xf = S.sitingInputs({ view: "allgrids", mw: String(MW), profile: "flexible" });
const ercot = hubs.filter((r) => r.grid === "ercot").map((r) => {
  const pc = S.profileCell(d, f, r, xf, f.cp);
  return { r, lost: "why" in pc ? null : pc.t.lost, run: "why" in pc ? null : pc.t.run, flat: S.columnValue(d, f, r, x, "allin"), flex: S.columnValue(d, f, r, xf, "allin") };
}).filter((v) => v.lost !== null && v.flat !== null && v.flex !== null).map((v) => ({ ...v, saved: v.flat - v.flex }))
  .sort((a, b) => a.saved - b.saved || a.r.id.localeCompare(b.r.id));
if (!ercot.length) { console.error("siting-card: no ERCOT row holds both profiles' all-in figures"); process.exit(1); }
const s0 = ercot[0], s1 = ercot.at(-1);
const byLost = [...ercot].sort((a, b) => a.lost - b.lost || a.r.id.localeCompare(b.r.id)), l0 = byLost[0], l1 = byLost.at(-1);
const hub = ercot.find((v) => v.r.id === "ercot:HB_HUBAVG") ?? ercot[0];
const strike = xf.strike ?? S.PROFILES.flexible.strike;
const card2 = {
  id: ID2, card_id: ID2, title: "WHAT STEPPING OFF SAVES", kind: "visual", engine: "site/scripts/siting-card.mjs",
  subtitle: `A 1 GW flexible compute load at ERCOT's ${ercot.length} hubs and load zones: off at the four summer peaks and at or above USD ${strike.toLocaleString("en-US")} per MWh, against a flat load`,
  params: { mw: MW, profile: "flexible", strike }, inputs_words: { mw: "1,000 MW", profile: `Flexible compute: 0.90, off in ERCOT's four summer peaks and at or above USD ${strike.toLocaleString("en-US")} per MWh` },
  chart: {
    kind: "bars_free", x: ercot.map((v) => v.r.region), x_label: "ERCOT hub or load zone, by the saving, smallest first",
    series: [
      { name: "All-in, a flat load (datacenter)", type: "bar", unit: "USD per MWh", values: ercot.map((v) => v.flat) },
      { name: "All-in, flexible compute", type: "bar", unit: "USD per MWh", values: ercot.map((v) => v.flex) },
    ],
    y_left_label: "USD per MWh", decimals: 2,
  },
  callouts: [
    { label: "Saved all-in, USD per MWh, least and most", before: { period: `ERCOT ${s0.r.region}`, text: two(s0.saved) }, after: { period: `ERCOT ${s1.r.region}`, text: two(s1.saved) }, unit: "" },
    { label: "Hours given up in the twelve months, fewest and most", before: { period: `ERCOT ${l0.r.region}`, text: whole(l0.lost) }, after: { period: `ERCOT ${l1.r.region}`, text: whole(l1.lost) }, unit: "" },
    { label: `All-in at ${hub.r.region}, USD per MWh, flat and flexible`, before: { period: "flat", text: two(hub.flat) }, after: { period: "flexible", text: two(hub.flex) }, unit: "" },
  ],
  why: `A 1 GW load that steps off in ERCOT's four summer peak intervals and in every hour at or above USD ${strike.toLocaleString("en-US")} per MWh gave up ${whole(l0.lost)} to ${whole(l1.lost)} hours of the last twelve whole months, row by row, and paid USD ${two(s0.saved)} (${s0.r.region}) to USD ${two(s1.saved)} (${s1.r.region}) per MWh less all-in than a flat load at the same row. At ${hub.r.region}: USD ${two(hub.flex)} against ${two(hub.flat)}. Most of the saving is the four-peak transmission charge, which a load off at the four peaks does not pay; the rest is the dearest hours' energy. All-in is energy over the hours the load runs, the four-peak charge at the Commission's rate, and capacity, of which ERCOT has none.`,
  footnote: `Data: the All grids tab of "What a datacenter pays" (/cost-of-power?view=allgrids&profile=flexible&mw=${MW}), computed by site/lib/siting.ts from the page's own files: the hourly hub and zone prices (ercot_all_hub_prices_history, ercot_zone_prices_history), ercot_4cp_intervals and the Commission's approved rate (texas_transmission_matrix). Method: docs/methods/siting.md. The replication: warehouse/replication/siting.py.`,
  numbers: {
    rows: ercot.length, strike, saved_least: s0.saved, saved_least_row: s0.r.id, saved_most: s1.saved, saved_most_row: s1.r.id,
    lost_fewest: l0.lost, lost_fewest_row: l0.r.id, lost_most: l1.lost, lost_most_row: l1.r.id, hub_row: hub.r.id, hub_flat: hub.flat, hub_flex: hub.flex,
  },
  source_line: "Source: ERW, the All grids tab (/cost-of-power?view=allgrids&profile=flexible), from ERCOT's hourly prices and four-peak intervals and the PUCT's transmission matrix.",
  tables: ["ercot_all_hub_prices_history", "ercot_zone_prices_history", "ercot_4cp_intervals", "texas_transmission_matrix"],
  computed_at: new Date().toISOString().slice(0, 19) + "Z",
  method: "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/siting.md",
  downloads: { csv: `${ID2}.csv`, python: "", stata: "" }, csv_sha256: "",
  csv_header: [`Energy Research Warehouse (ERW): finding ${ID2}, WHAT STEPPING OFF SAVES`, "Computed by site/scripts/siting-card.mjs from site/lib/siting.ts (the All grids tab); method docs/methods/siting.md",
    `Rows: one per ERCOT hub or load zone, a 1 GW load: the all-in figure flat and flexible (off at the four summer peaks and at or above USD ${strike} per MWh), USD per MWh, the saving, the hours given up and run`],
};
const csv2 = [...card2.csv_header.map((h) => `# ${h}`), "row,allin_flat_usd_mwh,allin_flexible_usd_mwh,saved_usd_mwh,hours_given_up,hours_run",
  ...ercot.map((v) => [v.r.id, v.flat, v.flex, v.saved, v.lost, v.run].join(","))].join("\n") + "\n";

// ---- session 773 (chain 064): the third card, siting_battery_swing ----
const ID3 = "siting_battery_swing";
const nf = f.nodes;
const [py, pm] = nf.pct_from.split("-").map(Number), [qy, qm] = nf.pct_to.split("-").map(Number);
const due = Math.round((Date.UTC(qy, qm, 1) - Date.UTC(py, pm - 1, 1)) / 86400000);
// the days the table holds in the window: the most any node holds (node_basis_daily lacks 30 days for every node)
const heldMax = Math.max(...nf.nodes.map((n) => n.swing?.[3] ?? 0));
const store = nf.nodes.filter((n) => n.cls === "storage" && n.swing && n.swing[3] >= 0.9 * heldMax)
  .map((n) => ({ id: n.id, mean: n.swing[0], p10: n.swing[1], p90: n.swing[2], days: n.swing[3] }))
  .sort((a, b) => a.mean - b.mean || a.id.localeCompare(b.id));
if (!store.length) { console.error("siting-card: no storage node holds 90 percent of its days"); process.exit(1); }
const b0 = store[0], b1 = store.at(-1);
const med = store.length % 2 ? store[(store.length - 1) / 2].mean : (store[store.length / 2 - 1].mean + store[store.length / 2].mean) / 2;
const step = 10, top = Math.ceil(b1.mean / step) * step;
const bot = Math.floor(b0.mean / step) * step;
const bins = Array.from({ length: (top - bot) / step }, (_, i) => ({ lo: bot + i * step, hi: bot + (i + 1) * step }));
const counts = bins.map((b) => store.filter((v) => v.mean >= b.lo && (v.mean < b.hi || (b.hi === top && v.mean <= b.hi))).length);
const card3 = {
  id: ID3, card_id: ID3, title: "WHERE A BATTERY'S DAY SWINGS MOST", kind: "visual", engine: "site/scripts/siting-card.mjs",
  subtitle: `ERCOT's ${store.length} storage nodes by their day-ahead intraday swing, the four dearest hours less the four cheapest, ${nf.pct_from} to ${nf.pct_to}`,
  params: { class: "storage", min_days: Math.ceil(0.9 * heldMax) }, inputs_words: { class: "storage nodes (ERCOT's disclosures, node_basis_daily x_class)", min_days: `at least 90 percent of the ${heldMax} days the table holds, of ${due}` },
  chart: {
    kind: "bars_free", x: bins.map((b) => `${b.lo}`), x_label: "Mean intraday swing, USD per MWh: each bar from its label to 10 more",   // session 970: labels that fit at 390
    series: [{ name: "Storage nodes", type: "bar", unit: "nodes", values: counts }],
    y_left_label: "Storage nodes", decimals: 0,
  },
  callouts: [
    { label: "Mean intraday swing, USD per MWh, narrowest and widest", before: { period: b0.id, text: two(b0.mean) }, after: { period: b1.id, text: two(b1.mean) }, unit: "" },
    { label: "The middle storage node, USD per MWh", before: { period: "median", text: two(med) }, after: { period: "nodes", text: whole(store.length) }, unit: "" },
    { label: `${b1.id}, one day in ten and nine in ten, USD per MWh`, before: { period: "10th", text: two(b1.p10) }, after: { period: "90th", text: two(b1.p90) }, unit: "" },
  ],
  why: `On a mean day from ${nf.pct_from} to ${nf.pct_to}, the four dearest day-ahead hours at ERCOT's storage nodes cost USD ${two(b0.mean)} (${b0.id}) to USD ${two(b1.mean)} (${b1.id}) per MWh more than the four cheapest, with a median of USD ${two(med)} across the ${store.length} storage nodes that hold at least 90 percent of the days. At ${b1.id} one day in ten swung USD ${two(b1.p10)} or less and one in ten USD ${two(b1.p90)} or more${b1.mean > b1.p90 ? `; its mean is above its 90th percentile, so a few days' swing carries it` : ""}. The swing is a day's spread of prices at the node, not a battery's earnings: it leaves out losses, cycling and the ancillary markets.`,
  footnote: `Data: the All grids tab of "What a datacenter pays" (/cost-of-power?view=allgrids&rows=nodes&ncls=storage&nsort=swing&ndir=desc), from node_basis_daily's dam_spread_4h (each day's four dearest day-ahead hours' mean less its four cheapest), by site/data/siting/nodes.json. node_basis_daily lacks 2026-08-21 to 2026-09-19 for every node. Method: docs/methods/siting.md (decision 24).`,
  numbers: { nodes: store.length, narrowest: b0.mean, narrowest_node: b0.id, widest: b1.mean, widest_node: b1.id, median: med, widest_p10: b1.p10, widest_p90: b1.p90 },
  source_line: "Source: ERW, the All grids tab's node list (/cost-of-power?view=allgrids&rows=nodes), from ERCOT's day-ahead settlement point prices as node_basis_daily holds them.",
  tables: ["node_basis_daily"],
  computed_at: new Date().toISOString().slice(0, 19) + "Z",
  method: "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/siting.md",
  downloads: { csv: `${ID3}.csv`, python: "", stata: "" }, csv_sha256: "",
  csv_header: [`Energy Research Warehouse (ERW): finding ${ID3}, WHERE A BATTERY'S DAY SWINGS MOST`, "Computed by site/scripts/siting-card.mjs from site/data/siting/nodes.json (node_basis_daily, dam_spread_4h); method docs/methods/siting.md",
    `Rows: one per ERCOT storage node holding at least 90 percent of the days, its mean day-ahead intraday swing and its 10th and 90th percentile, USD per MWh, and its days`],
};
const csv3 = [...card3.csv_header.map((h) => `# ${h}`), "node,swing_mean_usd_mwh,swing_p10_usd_mwh,swing_p90_usd_mwh,days",
  ...store.map((v) => [v.id, v.mean, v.p10, v.p90, v.days].join(","))].join("\n") + "\n";

const out = [[ID, card, csv], [ID2, card2, csv2], [ID3, card3, csv3]];
const paths = (id) => [path.join(here, "..", "data", "findings", `${id}.json`), path.join(here, "..", "public", "findings", `${id}.csv`)];
if (process.argv.includes("--check")) {
  // only the fields this script writes are compared: another step of the pipeline may add its own to the file (the data
  // machine's daily run adds session 361's "statistics"), and the time is the run's
  const mine = (c, keys) => JSON.stringify(Object.fromEntries(keys.filter((k) => k !== "computed_at").map((k) => [k, c[k]])));
  const bad = out.filter(([id, c, v]) => {
    const [cp, vp] = paths(id);
    return !fs.existsSync(cp) || mine(JSON.parse(fs.readFileSync(cp, "utf-8")), Object.keys(c)) !== mine(c, Object.keys(c)) || fs.readFileSync(vp, "utf-8") !== v;
  }).map(([id]) => id);
  console.log(bad.length ? `siting-card: the files differ from the tab's figures: ${bad.join(", ")}` : "siting-card: the files are the tab's figures");
  process.exit(bad.length ? 1 : 0);
}
// session 756: a field another step added to the file (session 361's "statistics") is kept as it is
for (const [id, c, v] of out) {
  const [cp, vp] = paths(id);
  const old = fs.existsSync(cp) ? JSON.parse(fs.readFileSync(cp, "utf-8")) : {};
  const kept = Object.fromEntries(Object.entries(old).filter(([k]) => !(k in c)));
  fs.writeFileSync(cp, JSON.stringify({ ...c, ...kept }, null, 1) + "\n");
  fs.writeFileSync(vp, v);
}
console.log(`siting-card: ${held.length} rows held; least ${lo.r.id} ${two(lo.allin)}, most ${hi.r.id} ${two(hi.allin)}; connect ${cmin.g} ${cmin.m} to ${cmax.g} ${cmax.m}`);
console.log(`siting-card: battery swing at ${store.length} storage nodes; ${b0.id} ${two(b0.mean)} to ${b1.id} ${two(b1.mean)}, median ${two(med)}`);
console.log(`siting-card: flexible at ${ercot.length} ERCOT rows; saved ${two(s0.saved)} (${s0.r.id}) to ${two(s1.saved)} (${s1.r.id}); hours given up ${l0.lost} to ${l1.lost}`);
