// Energy Research Warehouse (ERW) site, session 7502 (chain 304): every figure of the severance tool as the page
// computes it: /severance (the calculator at its default and at the named cases of replication/severance/cases.json,
// and the rule list's counts and certified prices), /severance?tab=lease (the page's own sample lease, as loaded and
// after "Tick the best flagged rule of each well") and /severance/lease/real (the county's counts and four real leases
// picked by a stated rule from rrc_lease_production_monthly, internal).
//
//   node --import ./scripts/tsx-register.mjs scripts/severance-figures.mjs <tables dir> [now, ISO] [--no-real]
//
// <tables dir> holds eia_fuel_spot_prices.csv (public) and, for the real leases, rrc_lease_production_monthly.csv
// (internal: on a warehouse machine only). The page's own functions are run on those rows: lib/severance.ts compute,
// lib/lease.ts parseLease, ticksFromFile, analyzeLease and bestTicks, lib/rrclease.ts parseRrc and leaseCsv, and
// lib/leaseprices.ts latestMonthMean and monthMeans, which read the live set through lib/data.ts: here the request is
// answered from the CSV by a stand-in for fetch, so nothing leaves the machine. A real lease is named by the rule that
// picks it, never by its id, its name or its operator, and only its totals are printed. Prints one JSON object:
// { now, figures: {key: number}, words: {key: text} }. replication/severance/replicate.py compares it with its own
// computation. No network, nothing written.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const noReal = process.argv.includes("--no-real");
const dir = args[0];
const now = args[1] ? Date.parse(args[1]) : Date.now();
if (!dir || Number.isNaN(now)) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/severance-figures.mjs <tables dir> [now, ISO] [--no-real]");
  process.exitCode = 2;
} else {
  await main();
}

/** The daily rows of the public price table, by entity, as the live set serves them. */
function priceRows() {
  const lines = fs.readFileSync(path.join(dir, "eia_fuel_spot_prices.csv"), "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  const [e, v, t, val, u, f] = ["entity", "variable", "ts_utc", "value", "unit", "freq"].map((c) => cols.indexOf(c));
  const by = {};
  for (const l of lines.slice(1)) {
    const r = l.split(",", 7);
    (by[r[e]] ??= []).push({ entity: r[e], variable: r[v], ts_utc: r[t], value: Number(r[val]), unit: r[u], freq: r[f] });
  }
  for (const k of Object.keys(by)) by[k].sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
  return by;
}

async function main() {
  const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "severance_rules.json"), "utf-8"));
  const cases = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "replication", "severance", "cases.json"), "utf-8")).cases;
  const out = {}, words = {};

  // the live set's answer, from the CSV: the one request lib/data.ts series makes (table, entity, variable, since, paged)
  const daily = priceRows();
  process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  globalThis.fetch = async (url) => {
    const q = new URL(String(url)).searchParams;
    if (q.get("table_name") !== "eq.eia_fuel_spot_prices") return new Response("[]", { status: 404 });
    const since = (q.get("ts_utc") ?? "gte.").replace(/^gte\./, "");
    const rows = (daily[(q.get("entity") ?? "").replace(/^eq\./, "")] ?? []).filter((r) => r.variable === (q.get("variable") ?? "").replace(/^eq\./, "") && r.ts_utc >= since);
    const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 1000);
    return new Response(JSON.stringify(rows.slice(off, off + lim)), { status: 200, headers: { "content-type": "application/json" } });
  };
  const P = await import("../lib/leaseprices.ts");
  const { compute, creditPct } = await import("../lib/severance.ts");
  const L = await import("../lib/lease.ts");
  const X = await import("../lib/rrclease.ts");
  const engine = { compute, creditPct };

  // 1. the calculator's default prices (app/severance/page.tsx CalculatorView)
  const wti = await P.latestMonthMean("eia:wti_cushing", now), hh = await P.latestMonthMean("eia:henry_hub", now);
  for (const [k, m] of [["oil", wti], ["gas", hh]]) {
    if (!m) { words[`price|${k}`] = "not held: enter a price"; continue; }
    out[`price|${k}|value`] = m.value;
    out[`price|${k}|days`] = m.n;
    words[`price|${k}|month`] = m.month;
  }

  // 2. the calculator (app/severance/Calculator.tsx): the input it builds from what a reader sets, then compute
  const latest = (id) => Object.values(rules.states).flatMap((st) => Object.values(st.products)).flatMap((pr) => pr.options).find((o) => o.id === id)?.certified?.prices[0]?.period;
  for (const c of cases) {
    const prod = rules.states[c.state].products[c.product];
    const price = c.price === "default" ? (c.product === "gas" ? hh?.value : wti?.value) : c.price;
    if (price === undefined) { words[`calc|${c.id}`] = "no default price held"; continue; }
    const d = c.district ? prod.base.find((b) => b.rate === "district").districts.list.find((q) => q.label === c.district) : null;
    const x = {
      state: c.state, product: c.product, volume: c.volume, price, variant: c.variant ?? "la_oil_pre2025", choice: 0.0024,
      adval: d ? Math.round(d.rate * 1e6) / 1e4 : 0, royaltyPct: c.royaltyPct ?? 0, trucking: c.trucking ?? 0, transport: c.transport ?? 0,
      option: c.option ? { id: c.option.id, param: c.option.param, tierPct: undefined, period: c.option.period ?? latest(c.option.id) } : undefined,
      credit: c.credit ? { id: c.credit.id, tierPct: 0, period: c.credit.period ?? latest(c.credit.id) } : undefined,
    };
    const r = compute(rules, x);
    const k = `calc|${c.id}|`;
    out[k + "gross"] = r.gross;
    out[k + "taxable"] = r.taxable;
    for (const l of r.base) out[`${k}line|${l.id}`] = l.tax;
    out[k + "base"] = r.baseTotal;
    out[k + "with"] = r.withTotal;
    out[k + "savings"] = r.savings;
    for (const f of r.fees) out[`${k}fee|${f.id}`] = f.amount;
    // the rate, cents or percent the page states for each rule applied ("5.625 percent of value", "3 cents per Mcf")
    for (const a of r.applied) out[`${k}effect|${a.id}`] = Number(/\d+(\.\d+)?/.exec(a.effect)[0]);
  }

  // 3. "Every rule, with its source": how many lines each state lists, and each certified price the list states
  for (const [s, st] of Object.entries(rules.states)) {
    const ps = Object.values(st.products);
    out[`rules|${s}|base`] = ps.reduce((a, p) => a + p.base.length, 0);
    out[`rules|${s}|options`] = ps.reduce((a, p) => a + p.options.length, 0);
    out[`rules|${s}|fees`] = ps.reduce((a, p) => a + p.fees.length, 0);
    for (const o of ps.flatMap((p) => p.options)) {
      if (!o.certified) continue;
      out[`rules|${o.id}|latest_certified`] = o.certified.prices[0].price;
      out[`rules|${o.id}|periods`] = o.certified.prices.length;
      words[`rules|${o.id}|latest_period`] = o.certified.as_of;
    }
  }
  words["rules|version"] = rules.version;

  // 4. the lease tab on the page's own sample (LeaseTool.tsx): as loaded, then the best flagged rule of each well ticked
  const book = {
    oil: await P.monthMeans("eia:wti_cushing", "WTI Cushing", "per barrel", ""),
    gas: await P.monthMeans("eia:henry_hub", "Henry Hub", "per MMBtu", ", applied per Mcf as if one Mcf held one MMBtu"),
  };
  out["lease|prices|oil_months"] = Object.keys(book.oil).length;
  out["lease|prices|gas_months"] = Object.keys(book.gas).length;
  words["lease|sample|sha256"] = crypto.createHash("sha256").update(L.SAMPLE_CSV).digest("hex");
  const analyse = (text, ticksOf) => {
    const parsed = L.parseLease(text, rules);
    const fromFile = L.ticksFromFile(rules, parsed.rows);
    const first = L.analyzeLease(rules, engine, parsed.rows, { prices: book, ticks: fromFile.ticks });
    const ticks = ticksOf ? ticksOf(first) : fromFile.ticks;
    return { parsed, a: ticksOf ? L.analyzeLease(rules, engine, parsed.rows, { prices: book, ticks }) : first, issues: parsed.errors.length + fromFile.unknown.length + first.issues.length };
  };
  const s = analyse(L.SAMPLE_CSV);
  const k4 = "lease|sample|";
  Object.assign(out, { [k4 + "base"]: s.a.lease.base, [k4 + "with"]: s.a.lease.withTicked, [k4 + "potential"]: s.a.lease.potential, [k4 + "fees"]: s.a.lease.fees,
    [k4 + "wells"]: s.a.wells.length, [k4 + "lines"]: s.a.lines.length, [k4 + "opportunities"]: s.a.opportunities.length, [k4 + "rows_to_check"]: s.issues });
  for (const w of s.a.wells) Object.assign(out, { [`${k4}well|${w.well}|months`]: w.months, [`${k4}well|${w.well}|base`]: w.base, [`${k4}well|${w.well}|potential`]: w.potential });
  for (const o of s.a.opportunities) { out[`${k4}may|${o.well}|${o.id}|savings`] = o.savings; out[`${k4}may|${o.well}|${o.id}|months`] = o.months.length; }
  for (const l of s.a.lines) {
    const k = `${k4}line|${l.well}|${l.month}|${l.product}|`;
    Object.assign(out, { [k + "price"]: l.price, [k + "base"]: l.base, [k + "with"]: l.withTicked, [k + "best"]: l.best, [k + "fees"]: l.fees });
    words[k + "flags"] = l.flags.map((f) => f.id).sort().join(";");
  }
  const t = analyse(L.SAMPLE_CSV, (a) => L.bestTicks(a, rules));
  out[k4 + "best_ticked|with"] = t.a.lease.withTicked;
  for (const w of t.a.wells) out[`${k4}best_ticked|well|${w.well}|with`] = w.withTicked;

  // 5. /severance/lease/real: the county's counts, and four real leases picked by rule (totals only; internal rows)
  const f = path.join(dir, "rrc_lease_production_monthly.csv");
  if (noReal || !fs.existsSync(f)) {
    words["real"] = noReal ? "not asked for" : "rrc_lease_production_monthly.csv is not in the tables folder (internal: a warehouse machine holds it)";
  } else {
    const tab = X.parseRrc(fs.readFileSync(f, "utf-8"));
    const leases = [...tab.leases.values()];
    out["real|leases"] = leases.length;
    out["real|operators"] = new Set(leases.map((l) => l.operatorNo)).size;
    const tot = (l, v) => Object.values(l.months).reduce((a, m) => a + (m[v] ?? 0), 0);
    const every = (l, v) => Object.keys(l.months).length === 24 && Object.values(l.months).every((m) => (m[v] ?? 0) > 0);
    const top = (xs, v, sign) => [...xs].sort((a, b) => sign * (tot(a, v) - tot(b, v)) || a.entity.localeCompare(b.entity))[0];
    const oil = leases.filter((l) => l.code === "O"), gas = leases.filter((l) => l.code === "G");
    const picks = {
      A: top(oil, "oil_bbl", -1), B: top(gas, "gas_mcf", -1),
      C: top(oil.filter((l) => l.wells === 1 && every(l, "oil_bbl")), "oil_bbl", 1), D: top(gas.filter((l) => every(l, "gas_mcf")), "gas_mcf", 1),
    };
    for (const [id, l] of Object.entries(picks)) {
      if (!l) { words[`real|${id}`] = "no lease meets the rule"; continue; }
      const r = analyse(X.leaseCsv(l, L.COLUMNS));
      const k = `real|${id}|`;
      Object.assign(out, { [k + "months"]: Object.keys(l.months).length, [k + "lines"]: r.a.lines.length, [k + "base"]: r.a.lease.base, [k + "with"]: r.a.lease.withTicked,
        [k + "potential"]: r.a.lease.potential, [k + "fees"]: r.a.lease.fees, [k + "rows_to_check"]: r.issues });
      for (const o of r.a.opportunities) { out[`${k}may|${o.id}|savings`] = o.savings; out[`${k}may|${o.id}|months`] = o.months.length; }
    }
  }
  console.log(JSON.stringify({ now: new Date(now).toISOString(), figures: out, words }, null, 1));
}
