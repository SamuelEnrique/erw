// Energy Research Warehouse (ERW) site, session 720 (chain 050): the All grids tab's research card, in the findings
// pipeline's format (lib/findings.ts, Card), written from the tab's own functions (lib/siting.ts, through
// scripts/siting-files.mjs), so every figure on the card is the tab's figure for the same load. Under the datacenter
// profile, a 1 GW load: where it pays least and most per MWh all-in, among the rows with every cost part held, and the
// range of months to connect across the grids; one chart (the all-in figure of each such row) with its source line. No
// verdict. Written, never posted or sent: the card is a file under data/findings/ and its data a CSV under
// public/findings/.
//
//   node scripts/siting-card.mjs            writes data/findings/siting_gigawatt.json and public/findings/siting_gigawatt.csv
//   node scripts/siting-card.mjs --check    exit 1 when the files on disk differ from a fresh computation (but for the time)
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
const cardPath = path.join(here, "..", "data", "findings", `${ID}.json`), csvPath = path.join(here, "..", "public", "findings", `${ID}.csv`);
if (process.argv.includes("--check")) {
  const old = JSON.parse(fs.readFileSync(cardPath, "utf-8"));
  const strip = (c) => JSON.stringify({ ...c, computed_at: "" });
  const same = strip(old) === strip(card) && fs.readFileSync(csvPath, "utf-8") === csv;
  console.log(same ? "siting-card: the files are the tab's figures" : "siting-card: the files differ from the tab's figures");
  process.exit(same ? 0 : 1);
}
fs.writeFileSync(cardPath, JSON.stringify(card, null, 1) + "\n");
fs.writeFileSync(csvPath, csv);
console.log(`siting-card: ${held.length} rows held; least ${lo.r.id} ${two(lo.allin)}, most ${hi.r.id} ${two(hi.allin)}; connect ${cmin.g} ${cmin.m} to ${cmax.g} ${cmax.m}`);
