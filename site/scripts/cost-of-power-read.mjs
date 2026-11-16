// Sessions 7521 and 7524 (chain 304, part B): /cost-of-power's default view, "Your load", drawn to HTML with the
// site's own page (app/cost-of-power/page.tsx) for the cases of docs/reviews/datacenter-cost-read-2026-11-16.md. The
// page's reads of the live set (lib/supabase.ts) are answered here, in the process, from the warehouse's table files
// (read only), as scripts/demand-growth-figures.mjs of session 7508 does for its page. Nothing is asked of a server.
// Each case writes <id>.html, <id>.txt (the words a reader sees, hovers in brackets) and summary.json (the model's figures).
//   node --import ./scripts/tsx-register.mjs scripts/cost-of-power-read.mjs <tables dir> <out dir> [case ...]
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { register } from "node:module";
import { createElement as h } from "react";

register(`data:text/javascript,${encodeURIComponent(`
export async function resolve(specifier, context, next) {
  if (specifier === "next/font/google") return { url: "erw-font-stub:google", shortCircuit: true };
  return next(specifier, context);
}
export async function load(url, context, next) {
  if (url === "erw-font-stub:google") return { format: "module", shortCircuit: true, source:
    "const f = () => ({ className: '', variable: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;" };
  return next(url, context);
}`)}`);

const [dir, outDir, ...only] = process.argv.slice(2);
if (!dir || !outDir) { console.error("usage: cost-of-power-read.mjs <tables dir> <out dir> [case ...]"); process.exitCode = 2; }
else await main();

/** One line of a CSV into its fields (quotes, doubled quotes). */
function fields(line) {
  if (!line.includes('"')) return line.split(",");
  const out = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) { if (c === '"') { if (line[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
    else if (c === '"') q = true; else if (c === ",") { out.push(cur); cur = ""; } else cur += c;
  }
  out.push(cur);
  return out;
}
/** The rows of a table file a filter keeps, read line by line (the two largest files are hundreds of megabytes). */
async function readTable(name, keep) {
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(dir, `${name}.csv`), "utf-8"), crlfDelay: Infinity });
  let cols = null; const rows = []; let pending = "";
  for await (const raw of rl) {
    if (!cols && raw.startsWith("#")) continue;
    let line = pending ? `${pending}\n${raw}` : raw;
    if ((line.match(/"/g) ?? []).length % 2 === 1) { pending = line; continue; }   // a quoted field that holds a line break
    pending = "";
    if (!cols) { cols = fields(line); continue; }
    if (!line) continue;
    if (keep.pre && !keep.pre(line)) continue;
    const f = fields(line), r = {};
    for (let i = 0; i < cols.length; i++) r[cols[i]] = f[i] ?? "";
    if (!keep.row || keep.row(r)) rows.push(r);
  }
  return rows;
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  const cache = new Map();
  const table = (name, keep = {}) => { if (!cache.has(name)) cache.set(name, readTable(name, keep)); return cache.get(name); };
  const BAS = ["eia930:ERCO", "eia930:CISO", "eia930:NYIS", "eia930:ISNE", "eia930:SWPP"];
  const KEEP = {
    carbon_intensity_hourly: { pre: (l) => BAS.some((b) => l.startsWith(`${b},intensity_demand,`)) },
    carbon_intensity_monthly: { pre: (l) => BAS.some((b) => l.startsWith(`${b},intensity_demand,`)) },
    ercot_rtm_price_adders: { pre: (l) => l.startsWith("ercot:system,rtorpa_mean,202") && l.slice(25, 29) >= "2024" },
    scarcity_hours_by_grid: { pre: (l) => l.includes(",rt_hour_ge_1000,") || l.includes(",own_signal,") },
  };
  const log = [];
  process.env.SUPABASE_URL = "http://cost-of-power-read.invalid";
  process.env.SUPABASE_ANON_KEY = "local";
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  // one PostgREST filter on a field's value
  const test = (v, f) => {
    if (f.startsWith("eq.")) return String(v) === f.slice(3);
    if (f.startsWith("in.(")) return f.slice(4, -1).split(",").map((x) => x.replace(/^"|"$/g, "")).includes(String(v));
    if (f.startsWith("like.")) { const p = f.slice(5); return p.endsWith("*") ? String(v).startsWith(p.slice(0, -1)) : String(v) === p; }
    if (f.startsWith("gte.")) { const t = f.slice(4); return /^-?[0-9.]+$/.test(t) ? Number(v) >= Number(t) : String(v) >= t; }
    if (f.startsWith("lt.")) { const t = f.slice(3); return /^-?[0-9.]+$/.test(t) ? Number(v) < Number(t) : String(v) < t; }
    throw new Error(`a filter this script does not answer: ${f}`);
  };
  // the hourly carbon table in the live set is its last 430 days (warehouse/supabase/live_set.yaml): the file is cut the same way, from its own newest hour
  let hourlyCut = null;
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    const kind = u.pathname.replace("/rest/v1/", "");
    const name = (q.table_name ?? "").replace(/^eq\./, "");
    let rows = [];
    if (!fs.existsSync(path.join(dir, `${name}.csv`))) { log.push(`NOT ANSWERED ${kind} ${name}`); return new Response("[]", { status: 200, headers: { "Content-Type": "application/json" } }); }
    rows = await table(name, KEEP[name]);
    if (name === "carbon_intensity_hourly") {
      if (!hourlyCut) { const max = rows.reduce((a, r) => (r.ts_utc > a ? r.ts_utc : a), ""); hourlyCut = new Date(Date.parse(max) - 430 * 86400000).toISOString().replace(/\.\d{3}Z$/, "Z"); log.push(`carbon_intensity_hourly cut to the 430 days before its newest hour ${max}: from ${hourlyCut}`); }
      rows = rows.filter((r) => r.ts_utc >= hourlyCut);
    }
    for (const [k, f] of Object.entries(q)) {
      if (["select", "table_name", "order", "limit", "offset"].includes(k)) continue;
      if (k === "and") { for (const part of f.slice(1, -1).split(",")) { const [col, op, ...rest] = part.split("."); rows = rows.filter((r) => test(r[col], `${op}.${rest.join(".")}`)); } continue; }
      const col = k.startsWith("extra->>") ? k.slice(8) : k;
      rows = rows.filter((r) => test(r[col], f));
    }
    const keys = (q.order ?? "").split(",").filter(Boolean).map((k) => { const [c, d] = k.split("."); return [c, d === "desc" ? -1 : 1]; });
    rows = rows.slice().sort((a, b) => { for (const [c, d] of keys) { const x = cmp(a[c], b[c]); if (x) return x * d; } return 0; });
    const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
    if (offset === 0) log.push(`answered ${kind} ${name} ${u.searchParams.get("entity") ?? ""} ${u.searchParams.get("variable") ?? ""}: ${rows.length} rows`);
    const page = rows.slice(offset, offset + limit).map((r) => {
      const o = { ...r };
      if ("value" in o) o.value = Number(o.value);
      if ("mw" in o) o.mw = o.mw === "" ? null : Number(o.mw);
      return o;
    });
    return new Response(JSON.stringify(page), { status: 200, headers: { "Content-Type": "application/json" } });
  };

  const { prerenderToNodeStream } = await import("react-dom/static");
  const { default: Page } = await import("../app/cost-of-power/page.tsx");
  const M = await import("../app/cost-of-power/model.ts");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const draw = async (q) => {
    const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve(q) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    return Buffer.concat(parts).toString("utf-8");
  };
  // the words a reader sees, a block a line, a hover in brackets after the words it sits on
  const textOf = (html) => {
    let s = html.replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "").replace(/<!-- -->/g, "");
    s = s.replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span>/g, (_, t) => ` [tip: ${t.replace(/<[^>]+>/g, " ")}] `);
    s = s.replace(/<([a-z0-9]+)([^>]*?)\stitle="([^"]*)"([^>]*)>/g, (_, tag, a, t, b) => `<${tag}${a}${b}> [hover: ${t}] `);
    s = s.replace(/<option[^>]*>/g, "\n  option: ").replace(/<\/(td|th)>/g, " | ").replace(/<\/(p|div|tr|li|h1|h2|h3|h4|section|table|summary|label|legend|caption|details|form|nav|option)>/g, "\n");
    return decode(s.replace(/<[^>]+>/g, " ")).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
  };

  const CASES = {
    c1_rt: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "flat", buy: "rt" },
    c1_da: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "flat", buy: "da" },
    c1_lf85: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "share", pct: "15", buy: "rt" },
    c2_50h: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "hours", n: "50", buy: "rt" },
    c2_50h_cp: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "hours", n: "50", buy: "rt", cp: "1" },
    c2_flat_cp: { grid: "ercot", region: "LZ_WEST", mw: "300", run: "flat", buy: "rt", cp: "1" },
    c3_ab: { grid: "ercot", region: "LZ_NORTH", mw: "300", run: "flat", buy: "rt", bsite: "ercot:LZ_WEST" },
    c4_sp15: { grid: "caiso", region: "TH_SP15_GEN-APND", mw: "300", run: "flat", buy: "rt", bsite: "caiso:TH_NP15_GEN-APND" },
    c4_np15_da: { grid: "caiso", region: "TH_NP15_GEN-APND", mw: "300", run: "flat", buy: "da" },
    c5_pjm: { grid: "pjm", region: "DOM", mw: "300" },
    bare: {},
  };
  const summary = {};
  for (const [id, q] of Object.entries(CASES)) {
    if (only.length && !only.includes(id)) continue;
    const t0 = Date.now();
    const html = await draw(q);
    fs.writeFileSync(path.join(outDir, `${id}.html`), html);
    fs.writeFileSync(path.join(outDir, `${id}.txt`), textOf(html));
    const m = await M.loadModel(M.inputsFrom(q), typeof q.buy === "string", q.grid, q);
    const way = (w) => (w ? { per: w.per, cost: w.cost, energy: w.energy, held: w.held, down: w.down, flatCost: w.flatCost, bad: w.bad } : null);
    summary[id] = {
      q, x: m.x, l12Span: m.l12Span, s12: m.s12, sh12: m.sh12 ? { per: m.sh12.per, cost: m.sh12.cost, down: m.sh12.down } : null, saved: m.saved, savedH: m.savedH, ref12: m.ref12 ? { flat: m.ref12.flat } : null,
      bad: m.bad ? { m: m.bad.m, per: m.badPer } : null, ways: m.ways.map(way), b: m.facts.b ? { place: m.facts.b.place, span: m.facts.b.span, ways: m.facts.b.ways.map(way) } : null,
      win: m.win, pyWs: m.pyWs.map((w) => ({ id: w.id, value: w.value, from: w.from, to: w.to })), cp: m.cp, cpWhy: m.cpWhy, nodeBand: m.nodeBand ? { p10: m.nodeBand.p10, p50: m.nodeBand.p50, p90: m.nodeBand.p90 } : null, nodeBandWhy: m.nodeBandWhy,
      answers: m.answers ? (m.answers.ok ? { scarcity: { hours: m.answers.data.scarcity.hours, flatUsd: m.answers.data.scarcity.flatUsd, byMonth: m.answers.data.scarcity.byMonth, ways: m.answers.data.scarcity.ways }, carbonL12: m.answers.data.carbon.l12, window: m.answers.data.carbon.window, largeLoad: m.answers.data.largeLoad ? { latest: m.answers.data.largeLoad.latest, yearAgo: m.answers.data.largeLoad.yearAgo, change: m.answers.data.largeLoad.approvedChange, reports: m.answers.data.largeLoad.reports.length } : null, notices: m.answers.data.notices, adders: m.answers.data.adders, byGrid: m.answers.data.byGrid } : { failed: m.answers.reason }) : null,
      deliveryParts: m.deliveryParts.map((d) => ({ utility: d.utility, lines: d.lines, assumed: d.assumed })), rules: m.rules,
      keys: [...html.matchAll(/data-check="([^"]+)"/g)].length, ms: Date.now() - t0,
    };
    console.log(`${id}: ${html.length} bytes, ${summary[id].keys} checked numbers, ${Date.now() - t0} ms`);
  }
  fs.writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(summary, null, 1));
  fs.writeFileSync(path.join(outDir, "reads.log"), log.join("\n"));
  console.log(`${log.length} reads answered; ${log.filter((l) => l.startsWith("NOT")).length} not answered`);
}
