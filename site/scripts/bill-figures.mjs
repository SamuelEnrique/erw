// Energy Research Warehouse (ERW) site, session 7533 (chain 304): the figures /learn/bill shows, read off the page drawn
// to HTML with the site's own code, for the replication (replication/bill/).
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/bill-figures.mjs            (writes the two files)
//   node --import ./scripts/battery-awards-page-register.mjs scripts/bill-figures.mjs --check    (compares, writes nothing)
//
// Two draws. (1) The whole page (app/learn/bill/page.tsx), its reads of cost_of_power_monthly answered by a stand-in for
// fetch from the rows of replication/bill/source_rows.csv (the live set's rows, read on 16 November 2026): the five
// default bills' cards, the calculator as it opens, the glossary, the decisions fold. (2) The calculator
// (app/learn/bill/BillCalc.tsx) for each case of replication/bill/cases.json: a case is a bill and the values a reader
// would type. No click runs in a draw, so the case's values are put in as the bill's defaults in a copy of the rules
// (the calculator takes its first values from them) and the bill is opened with the calculator's `first`. The
// wholesale price each case is set against is the page's own, read from the cards' data-raw. Nothing here computes a
// figure: every number written is the page's, as printed. No network, no table written, nothing stored.
import fs from "node:fs";
import { createElement as h, isValidElement, cloneElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const REP = new URL("../../replication/bill/", import.meta.url);
const rules = JSON.parse(fs.readFileSync(new URL("../data/bill_rules.json", import.meta.url), "utf-8"));
const cases = JSON.parse(fs.readFileSync(new URL("cases.json", REP), "utf-8")).cases;

/** Rows of a warehouse-shaped CSV ("#" header lines, then entity, variable, ts_utc, value, unit). */
function tableRows(file) {
  const out = [];
  let head = false;
  for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    if (!head) { head = true; continue; }
    const c = line.split(",");
    out.push({ entity: c[0], variable: c[1], ts_utc: c[2], value: Number(c[3]), unit: c[4] });
  }
  return out;
}

/** Async server components (the page, TableDownloads) resolved into plain elements, so renderToStaticMarkup can draw. */
async function resolve(node) {
  if (Array.isArray(node)) return Promise.all(node.map(resolve));
  if (!isValidElement(node)) return node;
  const t = node.type;
  if (typeof t === "function" && t.constructor && t.constructor.name === "AsyncFunction") return resolve(await t(node.props));
  if (node.props && node.props.children !== undefined) return cloneElement(node, { children: await resolve(node.props.children) });
  return node;
}

async function drawPage(rows) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const real = globalThis.fetch;
  const asked = [];
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = u.searchParams;
    const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
    if (!u.pathname.endsWith("/series") || name !== "cost_of_power_monthly") { asked.push(`${u.pathname} ${name}: not answered`); return new Response("stand-in", { status: 404 }); }
    const entity = (q.get("entity") ?? "").replace(/^eq\./, "");
    const got = rows.filter((r) => r.entity === entity).sort((a, b) => (a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : 1));
    const limit = Number(q.get("limit") ?? 100000), offset = Number(q.get("offset") ?? 0);
    asked.push(`series cost_of_power_monthly ${entity}: ${got.length} rows`);
    return new Response(JSON.stringify(got.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
  const log = console.error;
  console.error = () => {};
  try {
    const { default: Page } = await import("../app/learn/bill/page.tsx");
    return { html: renderToStaticMarkup(await resolve(await Page())), asked };
  } finally {
    globalThis.fetch = real;
    console.error = log;
  }
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1").trim();
const num = (s) => Number(String(s).replace(/[$,]/g, ""));
/** Half of the last digit the page shows. */
const tol = (s) => 0.5 * 10 ** -((String(s).replace(/^-/, "").split(".")[1] ?? "").length);
// a number the page holds for a license prints "license needed": kept as shown, with no value, so the replication names it
const fig = (key, name, shown) => (shown === "license needed" ? { key, name, shown, value: null, tolerance: 0 } : { key, name, shown, value: num(shown), tolerance: tol(String(shown).replace(/[$,]/g, "")) });

/** The calculator's figures: each line's amount and the numbers of its detail, the total, the all-in price, the bar. */
function calcFigures(html) {
  const out = [];
  const tbody = html.slice(html.indexOf("<tbody>"), html.indexOf("</tbody>"));
  let group = "";
  for (const tr of tbody.split("<tr").slice(1)) {
    const g = tr.match(/scope="rowgroup"[^>]*>([^<]*)</);
    if (g) {
      group = ent(g[1]);
      // session 7547: a Texas bill's delivery lines together, on the group's own row
      const gs = tr.match(/data-group-sum="[^"]*">([^<]*)</);
      if (gs) out.push(fig(`group|${group}`, `${group}: the lines together (USD)`, gs[1]));
      continue;
    }
    const name = tr.match(/<summary[^>]*>([\s\S]*?)<\/summary>/);
    const amt = tr.match(/<td[^>]*>([^<]*)<\/td>/);
    if (name && amt) {
      const n = ent(name[1]);
      const ps = [...tr.matchAll(/<p class="text-xs text-muted">([\s\S]*?)<\/p>/g)];
      const detail = ps.length ? words(ps[ps.length - 1][1]).split(". Effective ")[0] : "";
      out.push({ ...fig(`line|${n}`, `${group}: ${n} (USD)`, amt[1]), detail });
    } else if (/>Total</.test(tr) && amt) out.push(fig("total", "Total (USD)", amt[1]));
    else if (/Per kWh, all in/.test(tr) && amt) { if (amt[1]) out.push(fig("per_kwh", "Per kWh, all in (USD)", amt[1])); }
  }
  const bar = html.match(/<span class="text-accent">Wholesale energy (-?\$[\d,.]+), (\d+) percent<\/span>: ([\d.]+) kWh at [^$]*\$([\d.]+) per MWh in (\d{4}-\d{2})[\s\S]*?Everything else, (-?\$[\d,.]+):/);
  if (bar) {
    out.push(fig("bar|wholesale_usd", "The bar: wholesale energy (USD)", bar[1]));
    out.push(fig("bar|share_pct", "The bar: wholesale energy's share of the bill (percent)", bar[2]));
    out.push(fig("bar|kwh", "The bar: the kWh", bar[3]));
    out.push(fig("bar|price", "The bar: the wholesale price (USD/MWh)", bar[4]));
    out.push({ key: "bar|month", name: "The bar: the wholesale price's month", shown: bar[5], value: bar[5], tolerance: null });
    out.push(fig("bar|rest_usd", "The bar: everything else (USD)", bar[6]));
  }
  // session 7547 (chain 304, part B): the bill's own power line under the bar, and the month field's options
  const pw = html.match(/data-power-line="([^"]+)">([\s\S]*?)<\/p>/);
  if (pw && pw[1] === "none") out.push({ key: "power|none", name: "Under the bar: no power line (SDG&E)", shown: "none", value: "none", tolerance: null });
  else if (pw) {
    const m = pw[2].match(/<span data-power-usd="[^"]*">([^<]*?) (-?\$[\d,.]+), (\d+) percent of the bill<\/span>, beside the wholesale energy&#x27;s (-?\$[\d,.]+)\./);
    if (m) {
      out.push({ key: "power|line", name: "Under the bar: the power line's name", shown: ent(m[1]), value: ent(m[1]), tolerance: null });
      out.push(fig("power|usd", "Under the bar: the power line (USD)", m[2]), fig("power|share_pct", "Under the bar: the power line's share of the bill (percent)", m[3]), fig("power|wholesale_usd", "Under the bar: the wholesale energy beside it (USD)", m[4]));
    }
  }
  for (const [, mo, p, part] of html.matchAll(/<option value="(\d{4}-\d{2})"[^>]*>\d{4}-\d{2}: \$([\d.]+) per MWh( \(partial\))?<\/option>/g))
    out.push(fig(`month|${mo}${part ? "|partial" : ""}`, `The month field: ${mo}${part ? " (partial)" : ""}, USD/MWh`, p));
  return out;
}

const KEYS = ["CA", "SCE", "SDGE", "TX", "TXC"];
const rows = tableRows(new URL("source_rows.csv", REP));
const { html: pageHtml, asked } = await drawPage(rows);
if (process.env.BILL_DUMP) fs.writeFileSync(process.env.BILL_DUMP, pageHtml);  // the drawn page, for a reader of this script
const page = [];
// the five cards: name, total, wholesale USD, share, price and its month
const cards = pageHtml.split('<div class="border border-rule bg-panel p-3 text-sm">').slice(1).map((c) => c.split("</div>")[0]);
const wholesale = {};
cards.forEach((c, i) => {
  const k = KEYS[i];
  const t = words(c);
  const total = t.match(/Total: ([\d,.]+|license needed) USD for (\d+) kWh\./);
  page.push(fig(`card|${k}|total`, `${k} card: total (USD)`, total[1]), fig(`card|${k}|kwh`, `${k} card: kWh`, total[2]));
  const w = t.match(/Wholesale energy: ([\d,.]+|license needed) USD, ([\d,.]+|license needed) percent of the bill, at ([\d,.]+) USD\/MWh \((\d{4}-\d{2})(, a partial month)?\)\./);
  if (w) {
    page.push(fig(`card|${k}|wholesale_usd`, `${k} card: wholesale energy (USD)`, w[1]), fig(`card|${k}|share_pct`, `${k} card: wholesale share (percent)`, w[2]),
      fig(`card|${k}|price`, `${k} card: wholesale price (USD/MWh)`, w[3]), { key: `card|${k}|month`, name: `${k} card: the price's month`, shown: w[4] + (w[5] ?? ""), value: w[4] + (w[5] ?? ""), tolerance: null });
    const raw = c.match(/data-check="series\|cost_of_power_monthly\|([^|]+)\|rt_load_weighted\|([^"]+)" data-raw="([^"]+)"/);
    wholesale[k] = { price: Number(raw[3]), month: raw[2].slice(0, 7), partial: !!w[5], entity: raw[1] };
  } else wholesale[k] = null;
  const e = t.match(/Energy charge \$([\d.]+) per kWh/);
  if (e) page.push(fig(`card|${k}|energy_rate`, `${k} card: the energy charge of the default (USD per kWh)`, e[1]));
});
page.push(...calcFigures(pageHtml.slice(pageHtml.indexOf('<div class="grid gap-6'), pageHtml.indexOf("Ten terms"))).map((f) => ({ ...f, key: `opens|${f.key}` })));
// the option lists of the calculator as it opens (PG&E): each territory's daily kWh and each tier's daily charge
for (const [, t, s, w] of pageHtml.matchAll(/Territory (\w): ([\d.]+) kWh a day in summer, ([\d.]+) in winter/g)) page.push(fig(`opens|territory|${t}|summer`, `Territory ${t}: kWh a day in summer`, s), fig(`opens|territory|${t}|winter`, `Territory ${t}: kWh a day in winter`, w));
for (const [, t, r] of pageHtml.matchAll(/Tier (\d): \$([\d.]+) a day/g)) page.push(fig(`opens|tier|${t}`, `Income tier ${t}: USD a day`, r));


const clone = (o) => JSON.parse(JSON.stringify(o));
function rulesFor(c) {
  const r = clone(rules);
  const b = r.bills[c.bill];
  const x = c.typed;
  if (c.bill === "TX" || c.bill === "TXC") {
    if (x.kwh !== undefined) b.defaults.kwh = x.kwh;
    if (x.energyRate !== undefined) b.energy_default.rate = x.energyRate;
  } else {
    const map = { kwh: "kwh", peakShare: "peak_share", superShare: "super_share", season: "season", territory: "territory", tier: "income_tier", climateCredit: "climate_credit", region: "region", baselineKwh: "baseline_kwh" };
    for (const [k, v] of Object.entries(x)) if (k !== "month") b.defaults[map[k]] = v;
  }
  return r;
}

/** Session 7547: for a case that types a wholesale month, the months the page's server hands the calculator for the
 * bill's zone (page.tsx, wholesaleOf: every month with a load-weighted price, newest first, partial when its rt_hours
 * are not its hours_in_month), standing in for the server's read as the fetch stand-in does for the page. */
function historyOf(entity) {
  const by = new Map();
  for (const r of rows.filter((x) => x.entity === entity)) (by.get(r.ts_utc.slice(0, 7)) ?? by.set(r.ts_utc.slice(0, 7), {}).get(r.ts_utc.slice(0, 7)))[r.variable] = r.value;
  return [...by.keys()].filter((m) => by.get(m).rt_load_weighted !== undefined).sort().reverse()
    .map((m) => ({ month: m, price: by.get(m).rt_load_weighted, partial: by.get(m).rt_hours !== by.get(m).hours_in_month }));
}

const { BillCalc } = await import("../app/learn/bill/BillCalc.tsx");
const out = [{ id: "page", name: "The page as it opens (the five cards and the calculator on PG&E)", bill: null, typed: null, figures: page }];
for (const c of cases) {
  const extra = c.typed.month ? { history: { [c.bill]: historyOf(rules.bills[c.bill].wholesale_entity) }, firstMonth: c.typed.month } : {};
  const html = renderToStaticMarkup(h(BillCalc, { rules: rulesFor(c), wholesale: Object.fromEntries(KEYS.map((k) => [k, wholesale[k] && { price: wholesale[k].price, month: wholesale[k].month, partial: wholesale[k].partial }])), first: c.bill, ...extra }));
  out.push({ id: c.id, name: c.name, bill: c.bill, typed: c.typed, figures: calcFigures(html) });
}

const n = out.reduce((a, c) => a + c.figures.length, 0);
const json = JSON.stringify({
  about: "ERW, What is on an electricity bill (/learn/bill): every number the page prints, read off the page drawn to HTML by site/scripts/bill-figures.mjs: the page as it opens on the rows of source_rows.csv, and the calculator for each case of cases.json. 'shown' is the page's text; 'tolerance' is half of its last shown digit; a line's 'detail' is the words under its name. Written by session 7533; rewrite with the script, never by hand.",
  rules_version: rules.version, wholesale, figures: n, cases: out,
}, null, 1) + "\n";
const q = (v) => (/[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
const csv = "case,key,name,shown,value,tolerance,detail\n" + out.flatMap((c) => c.figures.map((f) => [c.id, f.key, f.name, f.shown, f.value, f.tolerance ?? "", f.detail ?? ""].map(q).join(","))).join("\n") + "\n";

console.log(asked.join("\n"));
for (const c of out) console.log(`${c.id}: ${c.figures.length} figures`);
if (process.argv.includes("--check")) {
  const same = fs.readFileSync(new URL("page_figures.json", REP), "utf-8").replace(/\r\n/g, "\n") === json && fs.readFileSync(new URL("page_figures.csv", REP), "utf-8").replace(/\r\n/g, "\n") === csv;
  console.log(same ? `page_figures: ${n} figures, as committed` : "page_figures: the page's figures differ from the committed files");
  if (!same) process.exitCode = 1;
} else {
  fs.writeFileSync(new URL("page_figures.json", REP), json);
  fs.writeFileSync(new URL("page_figures.csv", REP), csv);
  console.log(`page_figures: ${n} figures of ${out.length} cases written`);
}
