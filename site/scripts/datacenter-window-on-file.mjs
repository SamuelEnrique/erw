// Session 1523: the page's own carbon window (lib/datacenter/answers.ts, readAnswers and windowCarbon) computed on the
// public carbon file (public/datacenter/erw_2026_datacenter_carbon.csv) instead of the live set, for the default
// address, printed as JSON. No request is made: the reader serves carbon_intensity_monthly and carbon_intensity_hourly
// from the file's rows and nothing for the other tables. The replication's test (tests/test_session1523.py) compares
// it with the published mirror's figures on the same file: the two codes on the same rows.
// node scripts/datacenter-window-on-file.mjs [path of the carbon file]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
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
const l12 = (page.l12 ?? []).map((r) => r.m);
const a = await A.readAnswers({ grid: x.grid, mw: x.mw, l12, behind: g.std_hours_behind_utc, ruled: await W.ruledWays(page), rows: reader });
console.log(JSON.stringify({ file: path.basename(file), hourly_rows: byTable.carbon_intensity_hourly.length, window: a.carbon.window }));
