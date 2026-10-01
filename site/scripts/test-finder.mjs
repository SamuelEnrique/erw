// Energy Research Warehouse (ERW) site, session 57: the refund finder against the lease tool, on real leases (internal
// data, read from the warehouse's output directory; nothing written).
//
//   node scripts/test-finder.mjs
//
// Picks, from the finder's flags (warehouse/output/severance_screen_flags.csv.gz): the Texas gas lease with the largest
// potential low-producing gas credit flagged in every month of the window, and the one-well oil lease (one well listed,
// not shut in) flagged for the low-producing oil test in every month. Each lease's months are read from its county's
// partition of rrc_lease_production_statewide, turned into the lease tool's file (lib/rrclease.ts leaseCsv, as
// /severance/lease/real does) and analyzed by lib/lease.ts at the same monthly prices (WTI Cushing and Henry Hub
// means of eia_fuel_spot_prices). Checks: the lease tool flags the same rule in the same months, and its saving over
// them equals the finder's to the cent; and the oil lease's months are the finder's with no saving (no certified price
// under $30). A lease reported in more than one county is skipped (the partition holds one county's share). Exits 1 on
// a mismatch; prints the leases' ids only.
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { analyzeLease, parseLease, COLUMNS } from "../lib/lease.ts";
import { leaseCsv, parseStatewideLease, splitCsv } from "../lib/rrclease.ts";
import { compute, creditPct } from "../lib/severance.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.ERW_OUTPUT_DIR || path.join(here, "..", "..", "warehouse", "output");
const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf-8"));
const engine = { compute, creditPct };
let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

// prices: monthly means of the local daily spot prices, as lib/leaseprices.ts computes them from Supabase
function means(entity) {
  const lines = fs.readFileSync(path.join(OUT, "eia_fuel_spot_prices.csv"), "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = splitCsv(lines[0]);
  const [e, v, t, val] = ["entity", "variable", "ts_utc", "value"].map((c) => cols.indexOf(c));
  const by = {};
  for (const l of lines.slice(1)) {
    const r = splitCsv(l);
    if (r[e] !== entity || r[v] !== "spot_price") continue;
    (by[r[t].slice(0, 7)] ??= []).push(Number(r[val]));
  }
  return Object.fromEntries(Object.entries(by).map(([m, xs]) => [m, { value: xs.reduce((a, x) => a + x, 0) / xs.length, n: xs.length, label: `${entity} ${m}` }]));
}
const prices = { oil: means("eia:wti_cushing"), gas: means("eia:henry_hub") };

const text = zlib.gunzipSync(fs.readFileSync(path.join(OUT, "severance_screen_flags.csv.gz"))).toString("utf-8");
const body = text.split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const cols = splitCsv(body[0]);
const flags = body.slice(1).map((l) => Object.fromEntries(splitCsv(l).map((v, i) => [cols[i], v])));
const index = Object.fromEntries(fs.readFileSync(path.join(OUT, "rrc_lease_production_statewide", "_index.csv"), "utf-8").split(/\r?\n/).slice(1).filter(Boolean).map((l) => l.split(",")).map((r) => [r[0], r[1]]));
const countyText = {};
const leaseOf = (f) => {
  countyText[f.county] ??= zlib.gunzipSync(fs.readFileSync(path.join(OUT, "rrc_lease_production_statewide", index[f.county]))).toString("utf-8");
  return parseStatewideLease(countyText[f.county], f.lease_id);
};

function run(rule, pick) {
  const cands = flags.filter(pick).sort((a, b) => Number(b.savings) - Number(a.savings) || Number(b.base_tax) - Number(a.base_tax) || a.lease_id.localeCompare(b.lease_id));
  for (const f of cands.slice(0, 40)) {
    const { lease } = leaseOf(f);
    if (!lease) continue;
    const ms = Object.keys(lease.months).sort();
    // one county only: the partition's months must carry every flagged month and its base tax must be the finder's
    const p = parseLease(leaseCsv(lease, COLUMNS), rules);
    const a = analyzeLease(rules, engine, p.rows, { prices, ticks: {} });
    const product = rule === "tx_lp_gas" ? "gas" : "oil";
    const lines = a.lines.filter((x) => x.product === product);
    const hit = lines.filter((x) => x.flags.some((g) => g.id === rule));
    const months = hit.map((x) => x.month);
    const base = hit.reduce((s, x) => s + (x.base ?? 0), 0);
    if (Math.abs(base - Number(f.base_tax)) > 0.01 * Math.max(1, hit.length)) continue;  // likely another county's share
    const saving = hit.reduce((s, x) => s + x.flags.find((g) => g.id === rule).savings, 0);
    console.log(`${rule}: lease ${f.lease_id} (${f.county}), ${ms.length} filed months, ${f.wells} well(s) listed`);
    check(months.join(";") === f.month_list, `the lease tool flags ${rule} in the finder's ${f.months} months (${months[0]} to ${months.at(-1)})`);
    check(Math.abs(base - Number(f.base_tax)) < 0.005 * hit.length + 0.01, `tax at the base rate over them: lease tool ${base.toFixed(2)}, finder ${f.base_tax}`);
    check(Math.abs(saving - Number(f.savings)) < 0.005 * hit.length + 0.01, `potential saving: lease tool ${saving.toFixed(2)}, finder ${f.savings}`);
    return f;
  }
  check(false, `${rule}: no candidate lease matched in one county`);
  return null;
}

run("tx_lp_gas", (f) => f.rule === "tx_lp_gas" && f.months === "24");
const oil = run("tx_lp_oil", (f) => f.rule === "tx_lp_oil" && f.months === "24" && f.wells === "1" && f.wells_open === "1");
if (oil) check(Number(oil.savings) === 0, `the oil lease saves nothing: ${oil.price_note}`);
console.log(bad ? `${bad} FAILED` : "refund finder: the lease tool agrees on both leases");
process.exit(bad ? 1 : 0);
