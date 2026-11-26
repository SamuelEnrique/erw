// Session 10207 (chain 710, part D): the severance tool's figures as the page's own code gives them, for the audit
// docs/reviews/severance-model-audit-2026-11-26.md. Run from site/:
//   node --import ./scripts/tsx-register.mjs ../runs/c10207/lib_figures.mjs <eia_fuel_spot_prices.csv> <now ISO> <out.json>
// The live set's one request (lib/data.ts series) is answered from the CSV by a stand-in for fetch: no network.
// It runs lib/leaseprices.ts latestMonthMean (the calculator's default prices), lib/severance.ts compute on every case
// of cases(), and draws the calculator (app/severance/Calculator.tsx) and the whole page (app/severance/page.tsx,
// default tab) to HTML, keeping the visible text. Nothing is written but <out.json> and the two HTML files beside it.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [csvPath, nowIso, outPath] = process.argv.slice(2);
const site = process.cwd();
const req = createRequire(path.join(site, "package.json"));
const React = req("react");
const { renderToStaticMarkup } = req("react-dom/server");
const h = React.createElement;
const imp = (rel) => import(pathToFileURL(path.join(site, rel)).href);

// the price rows, by entity, sorted, as the live set serves them
const lines = fs.readFileSync(csvPath, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
const cols = lines[0].split(",");
const ix = (c) => cols.indexOf(c);
const by = {};
for (const l of lines.slice(1)) {
  const r = l.split(",");
  const row = { entity: r[ix("entity")], variable: r[ix("variable")], ts_utc: r[ix("ts_utc")], value: Number(r[ix("value")]), unit: r[ix("unit")], freq: r[ix("freq")] };
  (by[row.entity] ??= []).push(row);
}
for (const k of Object.keys(by)) by[k].sort((a, b) => a.ts_utc.localeCompare(b.ts_utc));
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
const asked = [];
globalThis.fetch = async (url) => {
  const q = new URL(String(url)).searchParams;
  asked.push(String(url).replace(/\?.*/, "") + " " + (q.get("table_name") ?? ""));
  if (q.get("table_name") !== "eq.eia_fuel_spot_prices") return new Response("[]", { status: 200, headers: { "content-type": "application/json" } });
  const since = (q.get("ts_utc") ?? "gte.").replace(/^gte\./, "");
  const ent = (q.get("entity") ?? "").replace(/^eq\./, "");
  const v = (q.get("variable") ?? "").replace(/^eq\./, "");
  const rows = (by[ent] ?? []).filter((r) => r.variable === v && r.ts_utc >= since);
  const off = Number(q.get("offset") ?? 0), lim = Number(q.get("limit") ?? 1000);
  return new Response(JSON.stringify(rows.slice(off, off + lim)), { status: 200, headers: { "content-type": "application/json" } });
};

const now = Date.parse(nowIso);
const RealNow = Date.now;
Date.now = () => now;
const P = await imp("lib/leaseprices.ts");
const S = await imp("lib/severance.ts");
const rules = JSON.parse(fs.readFileSync(path.join(site, "data", "severance_rules.json"), "utf-8"));
const wti = await P.latestMonthMean("eia:wti_cushing", now);
const hh = await P.latestMonthMean("eia:henry_hub", now);
const out = { now: nowIso, price: { oil: wti, gas: hh }, cases: {}, printed: {} };

// every case: each state and product at 1,000 units and the default price, each option alone at its default, the credit
const cases = [];
for (const [st, s] of Object.entries(rules.states)) {
  for (const [p, pr] of Object.entries(s.products)) {
    const price = p === "gas" ? hh.value : wti.value;
    const base = { state: st, product: p, volume: 1000, price, variant: "la_oil_pre2025", choice: 0.0024, adval: 0, royaltyPct: 0, trucking: 0, transport: 0 };
    cases.push([`${st}|${p}|base`, base]);
    if (pr.variants) for (const v of pr.variants) cases.push([`${st}|${p}|variant=${v.id}`, { ...base, variant: v.id }]);
    for (const o of pr.options) {
      if (o.group === "rate") cases.push([`${st}|${p}|opt=${o.id}`, { ...base, option: { id: o.id, param: undefined, tierPct: undefined, period: o.certified ? o.certified.prices[0].period : undefined } }]);
      else cases.push([`${st}|${p}|credit=${o.id}`, { ...base, credit: { id: o.id, tierPct: 0, period: o.certified ? o.certified.prices[0].period : undefined } }]);
    }
    const dist = pr.base.find((b) => b.rate === "district")?.districts?.list;
    if (dist) for (const d of dist) cases.push([`${st}|${p}|district=${d.label}`, { ...base, adval: Math.round(d.rate * 1e6) / 1e4 }]);
    if (st === "NM") cases.push([`${st}|${p}|jal_royalty12.5_truck1`, { ...base, adval: Math.round(0.014863 * 1e6) / 1e4, royaltyPct: 12.5, trucking: 1 }]);
    if (st === "LA" && p !== "gas") cases.push([`${st}|${p}|transport2`, { ...base, transport: 2 }]);
  }
}
for (const [k, x] of cases) {
  const r = S.compute(rules, x);
  out.cases[k] = { gross: r.gross, taxable: r.taxable, baseTotal: r.baseTotal, withTotal: r.withTotal, savings: r.savings, lines: Object.fromEntries(r.base.map((l) => [l.id, l.tax])), fees: Object.fromEntries(r.fees.map((f) => [f.id, f.amount])) };
}

// the calculator drawn as it opens, with the page's own default prices and labels (app/severance/page.tsx CalculatorView)
const prices = {
  oil: wti?.value ?? null, gas: hh?.value ?? null,
  label: {
    oil: wti ? `WTI Cushing, the mean of ${wti.n} daily EIA spot prices in ${wti.month}, $${wti.value.toFixed(2)} per barrel` : "not held: enter a price",
    gas: hh ? `Henry Hub, the mean of ${hh.n} daily EIA spot prices in ${hh.month}, $${hh.value.toFixed(2)} per MMBtu, applied per Mcf as if one Mcf held one MMBtu` : "not held: enter a price",
  },
};
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const { Calculator } = await imp("app/severance/Calculator.tsx");
const calcHtml = renderToStaticMarkup(h(Calculator, { rules, prices }));
fs.writeFileSync(outPath.replace(/\.json$/, "_calculator.html"), calcHtml);
out.printed.calculator = words(calcHtml);

// the whole page, default tab: an async server component, drawn by awaiting each async part in turn
async function resolveTree(node) {
  if (node == null || typeof node !== "object") return node;
  if (Array.isArray(node)) return Promise.all(node.map(resolveTree));
  if (!React.isValidElement(node)) return node;
  let el = node;
  if (typeof el.type === "function" && el.type.constructor?.name === "AsyncFunction") {
    return resolveTree(await el.type(el.props));
  }
  const kids = el.props?.children;
  if (kids === undefined) return el;
  const rk = await resolveTree(kids);
  return React.cloneElement(el, undefined, ...(Array.isArray(rk) ? rk : [rk]));
}
try {
  const Page = (await imp("app/severance/page.tsx")).default;
  const tree = await resolveTree(await Page({ searchParams: Promise.resolve({}) }));
  const pageHtml = renderToStaticMarkup(tree);
  fs.writeFileSync(outPath.replace(/\.json$/, "_page.html"), pageHtml);
  out.printed.page = words(pageHtml);
} catch (e) {
  out.printed.page_error = String(e && e.stack || e);
}
out.requests = asked;
Date.now = RealNow;
fs.writeFileSync(outPath, JSON.stringify(out, null, 1));
console.log(`cases ${Object.keys(out.cases).length}; oil ${JSON.stringify(wti)}; gas ${JSON.stringify(hh)}; page ${out.printed.page ? "drawn" : "not drawn"}`);
