// Energy Research Warehouse (ERW) site, session 7516 (chain 304, part B): the ERCOT peak premium explorer
// (/explore/ercot-peak-premium) read as its reader, held on the page as drawn (docs/reviews/ercot-peak-premium-read-2026-11-16.md).
//
//   node --import ./scripts/tsx-register.mjs scripts/test-peak-premium-read.mjs <annual.csv> <monthly.csv> <coverage.csv>
//
// The page is drawn to HTML with the site's own code, its reads answered in the process from the two table files (as
// scripts/peak-premium-figures.mjs does; real rows: tests/fixtures/session7507 holds HB_HUBAVG and HB_WEST). It checks
// the rows the read fixed: two hubs side by side (row 1), the mark of a period not yet over wherever it heads a figure
// (row 2), what the worst-interval multiple is a multiple of (row 3), HB_BUSAVG in words (row 4) and where a node is
// read (row 5). It runs no click and no effect, asks no server, and writes nothing.
import fs from "node:fs";
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

const [annualFile, monthlyFile, coverageFile] = process.argv.slice(2);
if (!annualFile || !monthlyFile || !coverageFile) {
  console.error("usage: node --import ./scripts/tsx-register.mjs scripts/test-peak-premium-read.mjs <annual.csv> <monthly.csv> <coverage.csv>");
  process.exitCode = 2;
} else {
  await main();
}

function readTable(file) {
  const all = fs.readFileSync(file, "utf-8").split(/\r?\n/);
  const header = all.filter((l) => l.startsWith("#")).map((l) => l.replace(/^#\s?/, ""));
  const lines = all.filter((l) => l && !l.startsWith("#"));
  const cols = lines[0].split(",");
  const ix = Object.fromEntries(cols.map((k, i) => [k, i]));
  const rows = lines.slice(1).map((l) => {
    const c = l.split(",");
    return { entity: c[ix.entity], variable: c[ix.variable], ts_utc: c[ix.ts_utc], value: Number(c[ix.value]) };
  });
  return { header, rows };
}

async function main() {
  const T = { ercot_peak_premium_annual: readTable(annualFile), ercot_peak_premium_monthly: readTable(monthlyFile) };
  const clines = fs.readFileSync(coverageFile, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const ccols = clines[0].split(",");
  const catalogue = clines.slice(1).map((l) => Object.fromEntries(l.split(",").map((v, i) => [ccols[i], v])))
    .filter((r) => r.table in T)
    .map((r) => ({ table_name: r.table, interval: r.interval, ts_min: r.ts_min, ts_max: r.ts_max, n_rows: Number(r.n_rows), last_run: r.last_run, license: r.license, in_live_set: "yes" }));

  process.env.SUPABASE_URL = "http://peak-premium-read.invalid";
  process.env.SUPABASE_ANON_KEY = "local";
  const eq = (f) => (f?.startsWith("eq.") ? f.slice(3) : null);
  const among = (f) => (f?.startsWith("in.(") ? f.slice(4, -1).split(",").map((x) => x.replace(/^"|"$/g, "")) : null);
  const one = (f) => (f === undefined ? null : eq(f) !== null ? [eq(f)] : among(f));
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = Object.fromEntries(u.searchParams);
    let out = [];
    const t = T[eq(q.table_name) ?? ""];
    if (u.pathname === "/rest/v1/series" && t) {
      const ent = one(q.entity), vars = one(q.variable), when = one(q.ts_utc)?.map((x) => new Date(x).getTime());
      out = t.rows.filter((r) => (!ent || ent.includes(r.entity)) && (!vars || vars.includes(r.variable)) && (!when || when.includes(new Date(r.ts_utc).getTime())));
      const keys = (q.order ?? "").split(",").filter(Boolean);
      out = out.slice().sort((a, b) => { for (const k of keys) { if (a[k] < b[k]) return -1; if (a[k] > b[k]) return 1; } return 0; });
    } else if (u.pathname === "/rest/v1/headers" && t) {
      out = t.header.map((line) => ({ line }));
    } else if (u.pathname === "/rest/v1/catalogue") {
      out = catalogue;
    }
    const offset = Number(q.offset ?? 0), limit = Number(q.limit ?? 1000);
    out = out.slice(offset, offset + limit);
    return new Response(JSON.stringify(out), { status: 200, headers: { "Content-Type": "application/json" } });
  };

  const { prerenderToNodeStream } = await import("react-dom/static");
  const P = await import("../lib/explore/peakpremium.ts");
  const { default: Page } = await import("../app/explore/ercot-peak-premium/page.tsx");
  const decode = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const text = (html) => decode(html.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  const draw = async (q) => {
    const { prelude } = await prerenderToNodeStream(h(Page, { searchParams: Promise.resolve(q) }));
    const parts = [];
    for await (const c of prelude) parts.push(Buffer.from(c));
    return Buffer.concat(parts).toString("utf-8");
  };
  const keyed = (html) => [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)].map((m) => ({ key: decode(m[1]), raw: Number(m[2]), text: text(m[3]) }));
  const chosen = (html, name) => {
    const m = html.match(new RegExp(`<select[^>]*name="${name}"[^>]*>([\\s\\S]*?)</select>`));
    if (!m) return null;
    const opts = [...m[1].matchAll(/<option([^>]*)>([\s\S]*?)<\/option>/g)].map((o) => ({ value: decode(o[1].match(/value="([^"]*)"/)?.[1] ?? ""), label: text(o[2]), selected: /\sselected(=""|\s|$)/.test(o[1]) }));
    return { chosen: opts.find((o) => o.selected)?.value ?? null, values: opts.map((o) => o.value), labels: opts.map((o) => o.label) };
  };
  const section = (html) => html.match(/<section id="two-hubs"[\s\S]*?<\/section>/)?.[0] ?? null;

  let passed = 0;
  const failed = [];
  const ok = (cond, what) => { if (cond) passed++; else failed.push(what); };
  const tableValue = (table, e, v, ts) => T[table].rows.find((r) => r.entity === e && r.variable === v && r.ts_utc === ts)?.value;
  const two = (x) => x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const W = "ercot:HB_WEST", A = "ercot:HB_HUBAVG";

  // row 1: two hubs side by side, the whole year
  {
    const html = await draw({ hub: W, vs: A, from: "2024", to: "2025" });
    const s = section(html);
    ok(s !== null, "row 1: a section of two hubs is drawn when the address names a second hub");
    const st = text(s ?? "");
    ok(st.includes("Two hubs side by side: HB_WEST and HB_HUBAVG"), "row 1: the section's title names both hubs");
    const ks = keyed(s ?? "");
    ok(ks.length === P.SIDE.length * 4, `row 1: ${P.SIDE.length} figures by two hubs by two years (${ks.length} drawn)`);
    for (const e of [W, A]) for (const y of ["2024", "2025"]) for (const f of P.SIDE) {
      const k = ks.find((x) => x.key === `series|ercot_peak_premium_annual|${e}|${f.v}|${y}-01-01T00:00:00Z`);
      const v = tableValue("ercot_peak_premium_annual", e, f.v, `${y}-01-01T00:00:00Z`);
      ok(k !== undefined && v !== undefined && k.raw === v, `row 1: ${e} ${f.v} ${y} is the table's row`);
      if (k && f.unit !== "count") ok(/^-?[\d,]+\.\d\d$/.test(k.text), `row 1: ${e} ${f.v} ${y} has two decimals (${k.text})`);
    }
    const pm = (e) => ks.find((x) => x.key === `series|ercot_peak_premium_annual|${e}|peak_median|2025-01-01T00:00:00Z`)?.text;
    ok(pm(W) === "39.03" && pm(A) === "37.04", `row 1: the peak medians of 2025 read 39.03 and 37.04 (${pm(W)}, ${pm(A)})`);
    // no figure is drawn two ways on the page
    const all = keyed(html), seen = new Map();
    let clash = 0;
    for (const k of all) { if (seen.has(k.key) && seen.get(k.key) !== k.text) clash++; seen.set(k.key, k.text); }
    ok(clash === 0, "row 1: a figure in the two-hub table reads as the same row does above it");
    ok(all.length === 64 + ks.length, `row 1: the page's own 64 figures are all still drawn (${all.length - ks.length})`);
    const f = chosen(html, "vs");
    ok(f && f.chosen === A && !f.values.includes(W) && f.labels[0] === "None", "row 1: the filter 'Beside hub' holds the second hub, and never the first");
    ok(/data-tip="two-hubs"/.test(s ?? "") && st.includes("The page takes no difference between the two"), "row 1: the tip says no difference is taken, and why");
    ok(!/class="[^"]*text-muted[^"]*"[^>]*>The same rows/.test(s ?? ""), "row 1: the line above the table is not grey");
  }
  // row 1: the same for one month, the newest year's month partial
  {
    const html = await draw({ hub: W, vs: A, month: "9", from: "2025", to: "2026" });
    const s = section(html), ks = keyed(s ?? "");
    ok(ks.length === P.SIDE.length * 4 && ks.every((k) => k.key.startsWith("series|ercot_peak_premium_monthly|")), "row 1: a month's two hubs are rows of the monthly table");
    ok(/<th[^>]*>HB_HUBAVG, September 2026 \(partial\)<\/th>/.test(s ?? ""), "rows 1 and 2: a partial month is marked in the two-hub table's head");
    ok(/<th[^>]*>HB_WEST, September 2025<\/th>/.test(s ?? ""), "rows 1 and 2: a complete month carries no mark");
  }
  // row 1: no second hub by default, the same hub twice is none, an unknown one is said
  {
    const html = await draw({ hub: W });
    ok(section(html) === null && chosen(html, "vs")?.chosen === "", "row 1: no second hub by default");
    ok(keyed(html).length === 64, "row 1: the default view draws its 64 figures and no more");
    const same = await draw({ hub: W, vs: W });
    ok(section(same) === null && !/data-asked-unknown="1"/.test(same), "row 1: the same hub twice draws no second table and no warning");
    const bad = await draw({ hub: W, vs: "ercot:HB_NOWHERE" });
    ok(section(bad) === null && /data-asked-unknown="1"/.test(bad) && text(bad).includes("second hub"), "row 1: a second hub the tables do not hold is said in one line");
  }
  // row 2: the mark of a period not yet over
  {
    const html = await draw({ hub: A, from: "2025", to: "2026" });
    const t = text(html);
    for (const label of ["Peak-block IQR", "Peak median minus midday median", "Median, all intervals"]) ok(t.includes(`${label}, HB_HUBAVG, 2026 (partial)`), `row 2: the headline "${label}" names 2026 as partial`);
    ok((html.match(/<td[^>]*>2026 \(partial\)<\/td>/g) ?? []).length === 4, "row 2: the four blocks' period cells read 2026 (partial)");
    ok(/<th[^>]*>2026 \(partial\)<\/th>/.test(html) && /<th[^>]*>2025<\/th>/.test(html), "row 2: the thesis's figures head 2026 (partial) beside 2025");
    ok(!t.includes("2025 (partial)"), "row 2: a complete year carries no mark");
    const back = text(await draw({ hub: A, from: "2026", to: "2025" }));
    ok(back.includes("2026 (partial):"), "row 2: the first year under a headline number carries the mark too");
    const sep = text(await draw({ hub: A, month: "9", from: "2025", to: "2026" }));
    ok(sep.includes("Peak-block IQR, HB_HUBAVG, September 2026 (partial)"), "row 2: a partial month is marked in the headline");
    const aug = await draw({ hub: A, month: "8", from: "2025", to: "2026" });
    ok(!text(aug.replace(/<select[\s\S]*?<\/select>/g, "")).includes("(partial)"), "row 2: a complete month of the newest year is not marked");
    const open = await draw({});
    ok(!text(open.replace(/<select[\s\S]*?<\/select>/g, "").replace(/<details[\s\S]*?<\/details>/g, "")).includes("(partial)"), "row 2: the opening view (two complete years) carries no mark outside the filters");
  }
  // rows 3, 4 and 5: the words
  {
    const html = await draw({});
    const dflt = (k) => text(html.match(new RegExp(`data-decision-default="${k}"[^>]*>([\\s\\S]*?)</span></span>`))?.[1] ?? "");
    ok(dflt("thresholds").includes("The multiple is not of the single highest interval") && dflt("thresholds").includes("about 35 of a full year's 35,040"), "row 3: the thresholds' default says what the multiple is a multiple of");
    ok(dflt("hub").includes("HB_BUSAVG (ERCOT's average over the buses of the four hubs)") && dflt("hub").includes("Beside hub"), "row 4: HB_BUSAVG is said in words, and the second hub is a choice of the page");
    const n = html.match(/<span data-nodes-elsewhere="1">([\s\S]*?)<\/p>/)?.[1] ?? "";
    ok(text(n).includes("It holds the six hubs and no node") && text(n).includes("battery page"), "row 5: the page says it holds no node and where the storage nodes are read");
    ok(Math.abs(35040 * 0.001 - 35.04) < 1e-9 && Math.abs(2976 * 0.001 - 2.976) < 1e-9, "row 3: one interval in a thousand is about 35 of a year and about 3 of a month");
  }

  for (const f of failed) console.log(`FAIL ${f}`);
  console.log(`${passed} checks passed, ${failed.length} failed`);
  if (failed.length) process.exitCode = 1;
}
