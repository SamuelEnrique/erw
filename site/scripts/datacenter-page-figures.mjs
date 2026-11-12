// Session 3779 (chain 212): the figures /cost-of-power prints at its bare address, computed by the page's own code
// (lib/datacenter.ts, lib/datacenter/finance.ts and lib/datacenter/answers.ts, through scripts/datacenter-ways.mjs) on
// the page's own files (data/datacenter/) and the public carbon file (public/datacenter/erw_2026_datacenter_carbon.csv,
// as scripts/datacenter-window-on-file.mjs reads it), printed as JSON keyed by the fields of
// replication/datacenter/page_figures.json. No request is made. replication/datacenter/figures_of_the_page.py writes
// them into page_figures.json, so the replication's test (tests/test_session1491.py) holds the published mirror to the
// page's code on the files of the same run, not to a reading of 5 November that the data machine's refresh moves.
// The two years by window are read by the page from the live set (price_years_by_window), not from these files, and
// are not printed: a past year does not move with a refresh.
// node scripts/datacenter-page-figures.mjs [path of the carbon file]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as F from "../lib/datacenter/finance.ts";
import * as W from "./datacenter-ways.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const file = process.argv[2] ?? path.join(here, "..", "public", "datacenter", "erw_2026_datacenter_carbon.csv");
const lines = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const head = lines[0].split(",");
const col = (n) => head.indexOf(n);
const [ki, ti, vi] = [col("kind"), col("ts_utc"), col("kg_co2_per_mwh")];
const rowsOf = (kind) => lines.slice(1).map((l) => l.split(",")).filter((c) => c[ki] === kind).map((c) => ({ ts_utc: c[ti], value: Number(c[vi]) }));
const byTable = { carbon_intensity_monthly: rowsOf("month"), carbon_intensity_hourly: rowsOf("hour") };
async function reader(table, params) {
  if (table !== "series") return [];
  return byTable[String(params.table_name).replace(/^eq\./, "")] ?? [];
}

const A = await import("../lib/datacenter/answers.ts");
const page = W.pageOf({});
const x = page.x, g = W.INDEX.grids[x.grid];
const [flat] = page.ways;
if (!flat || !page.l12) {
  console.error("the bare address has no last twelve months on these files");
  process.exit(1);
}
const d = F.defaultsOf(page.load);
const r0 = F.resultOf(d, flat);
const da = W.pageOf({ buy: "da" });
const l12 = page.l12.map((r) => r.m);
const a = await A.readAnswers({ grid: x.grid, mw: x.mw, l12, behind: g.std_hours_behind_utc, ruled: await W.ruledWays(page), rows: reader });
const stat = (k) => A.statOf(a, k);
const out = {
  address: { grid: x.grid, region: x.region, buy: x.buy, mw: x.mw, l12_first: l12[0], l12_last: l12.at(-1) },
  figures: {
    l12_usd_mwh: r0.price,
    l12_usd: r0.bill * x.mw,
    gpu_hour: r0.gpuHour,
    gpus: x.mw * F.gpusPerMw(d),
    da_usd_mwh: da.x.buy === "da" && da.s12 ? da.s12.per : null,
    bad_usd_mwh: flat.bad ? flat.bad.per : null,
    bad_month: flat.bad ? flat.bad.m : null,
    scarce_hours: stat("scarce:hours"),
    scarce_usd: stat("scarce:flat_usd"),
    co2_kg_mwh: stat("co2:l12:kg:flat"),
    co2_tonnes: stat("co2:l12:tonnes:flat"),
    window_hours: stat("co2:window:hours"),
    window_kg_mwh: stat("co2:window:flat"),
  },
};
console.log(JSON.stringify(out));
