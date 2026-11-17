// Energy Research Warehouse (ERW) site, session 7532 (chain 304): every figure of the Flex Alert scorecard
// (/grid/caiso/alerts), as the page itself draws it, without a build (this machine cannot build the site).
//
//   node --import ./scripts/battery-awards-page-register.mjs scripts/caiso-alerts-figures.mjs <tables dir> <out.json> [<out.html> <out.txt>]
//
// The page's own function (app/grid/caiso/alerts/page.tsx) is called and its three reads of the live set
// (lib/flexalerts.ts: flex_alert_effects and flex_alert_model without the coefficients; lib/reliability.ts: the notices of
// caiso_grid_emergencies from 2018-07-01 to 2025-10-31) are answered here, in the process, by a stand-in for fetch, from
// the tables as the warehouse writes them (<tables dir>/<table>.csv, "#" header lines). Nothing is asked of a server and
// nothing is written but the files named. From the HTML it keeps: every checked number (its key, the value read and the
// text shown, in the order drawn, with the section it is drawn in); each row of "Every alert day, ranked" as drawn (the
// day, CAISO's notices, the alert hours, the cells); the figures the page writes without a key (the days with a price,
// the alert days, the words that turn on a sign); and the charts' axis labels. replication/caiso_alerts/replicate.py sets
// these beside its own reading of the tables. No click, no effect, no chart seen (the charts' points are a browser read).
import fs from "node:fs";
import path from "node:path";
import { renderToReadableStream } from "react-dom/server";

/** A CSV line split on commas outside double quotes ("" inside quotes is one quote). */
export function splitCsv(line) {
  const out = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) {
      if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') q = false;
      else cur += c;
    } else if (c === '"') q = true;
    else if (c === ",") { out.push(cur); cur = ""; }
    else cur += c;
  }
  out.push(cur);
  return out;
}

/** A warehouse table: its "#" header lines, and its rows as objects keyed by the column names. */
export function readTable(file) {
  const all = fs.readFileSync(file, "utf-8").split(/\r?\n/);
  const header = all.filter((l) => l.startsWith("#")).map((l) => l.replace(/^#\s?/, ""));
  const lines = all.filter((l) => l && !l.startsWith("#"));
  const cols = splitCsv(lines[0]);
  const rows = lines.slice(1).map((l) => { const c = splitCsv(l); return Object.fromEntries(cols.map((k, i) => [k, c[i] ?? ""])); });
  return { header, rows };
}

const retrieved = (header) => (header.join(" ").match(/Retrieved: (\d{8}T\d{6}Z)/) ?? [])[1] ?? "";

/** The page drawn on the tables `T` (name to { rows }); returns the HTML and the reads it made. */
export async function drawPage(T) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const real = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = u.searchParams;
    const name = (q.get("table_name") ?? "").replace(/^eq\./, "");
    const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
    const t = T[name];
    if (!t) { asked.push(`${name}: not answered`); return new Response("stand-in: the table is not held", { status: 404 }); }
    let rows;
    if (u.pathname.endsWith("/series")) {
      const v = q.get("variable") ?? "";
      const notLike = v.startsWith("not.like.") ? v.slice(9).replace(/\*$/, "") : null;
      rows = t.rows.filter((r) => notLike === null || !r.variable.startsWith(notLike))
        .map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value), unit: r.unit, freq: r.freq || null }));
      rows.sort((a, b) => (a.ts_utc < b.ts_utc ? -1 : a.ts_utc > b.ts_utc ? 1 : a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : 0));
    } else {
      const m = (q.get("and") ?? "").match(/event_date\.gte\.([\d-]+),event_date\.lte\.([\d-]+)/);
      rows = t.rows.filter((r) => !m || (r.event_date.slice(0, 10) >= m[1] && r.event_date.slice(0, 10) <= m[2]))
        .map((r) => ({ event_id: r.event_id, event_date: r.event_date, event_type: r.event_type,
          extra: Object.fromEntries(Object.entries(r).filter(([k]) => k.startsWith("x_")).map(([k, v]) => [k.slice(2), v])) }));
      rows.sort((a, b) => (a.event_date < b.event_date ? -1 : a.event_date > b.event_date ? 1 : a.event_id < b.event_id ? -1 : 1));
    }
    if (offset === 0) asked.push(`${name}: ${rows.length} rows`);
    return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
  const log = console.error;
  console.error = () => {};
  try {
    const { default: Page } = await import("../app/grid/caiso/alerts/page.tsx");
    // the page's source line (components/Cite.tsx) is an async component: the stream waits for it, as the server does
    const stream = await renderToReadableStream(await Page());
    await stream.allReady;
    const html = await new Response(stream).text();
    return { html, asked };
  } finally {
    globalThis.fetch = real;
    console.error = log;
  }
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#39;/g, "'");
export const text = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();

/** Every figure of the drawn page. */
export function figuresOf(html) {
  // the sections, by the offset of each h2
  const heads = [...html.matchAll(/<h2[^>]*>([\s\S]*?)<\/h2>/g)].map((m) => ({ at: m.index, title: text(m[1]) }));
  const sectionAt = (i) => { let s = "head"; for (const h of heads) if (h.at < i) s = h.title; return s; };
  const nums = [...html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)]
    .map((m) => ({ key: ent(m[1]), raw: m[2], shown: text(m[3]), section: sectionAt(m.index) }));
  // the ranked table: the rows of the section "Every alert day, ranked"
  const a = html.indexOf(">Every alert day, ranked<"), b = html.indexOf(">Year by year<");
  const ranked = [...html.slice(a, b).matchAll(/<tr class="border-b border-rule">([\s\S]*?)<\/tr>/g)].map((m) => {
    const cells = [...m[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((c) => text(c[1]));
    return { day: (m[1].match(/href="#d([\d-]+)"/) ?? [])[1], notices: cells[1], hours: cells[2], high: cells[3], as_hot: cells[4], cut: cells[5], pct: cells[6], value: cells[7] };
  });
  // the day panels' captions, in the order drawn
  const panels = [...html.matchAll(/<div id="d([\d-]+)"[^>]*>\s*<p[^>]*>([\s\S]*?)<\/p>/g)].map((m) => ({ day: m[1], caption: text(m[2]) }));
  const t = text(html);
  const held = t.match(/Prices are held for (\d+) of the (\d+) alert days/);
  const words = {
    h1: text((html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) ?? ["", ""])[1]),
    ran: (t.match(/demand served ran (below|above) what the weather/) ?? [])[1] ?? null,
    zero: (t.match(/The interval (includes zero|excludes zero)/) ?? [])[1] ?? null,
    last_alert: (t.match(/from July 2018 to (\d{4}-\d{2}-\d{2})/) ?? [])[1] ?? null,
    days_priced: held ? Number(held[1]) : null,
    days_shown: held ? Number(held[2]) : null,
    oasis_months: Number((t.match(/OASIS serves (\d+) months of history/) ?? [])[1] ?? NaN),
    // session 7532: the last caution says how far CAISO's notices run, and how many alert days lie after the scorecard's last
    report_ends: (t.match(/as the warehouse holds it, runs to ([\d-]+) ?;/) ?? [])[1] ?? null,
    later_alert_days: /it lists no Flex Alert or emergency notice after/.test(t) ? 0 : Number((t.match(/it lists (\d+) days? with a Flex Alert/) ?? [])[1] ?? NaN),
    tip_left_out: /One alert day of CAISO's notices is not in the table: 2021-07-12/.test(t),
    decisions: (html.match(/data-decision="/g) ?? []).length,
  };
  // the charts' axis labels (svg text), by chart
  const svgs = [...html.matchAll(/<svg[^>]*aria-label="([^"]+)"[^>]*>([\s\S]*?)<\/svg>/g)].map((m) => ({
    label: ent(m[1]), texts: [...m[2].matchAll(/<text[^>]*>([\s\S]*?)<\/text>/g)].map((x) => text(x[1])),
    // session 7546: an hour's hover strip (data-alerts-hour) is not a box of the chart
    rects: (m[2].match(/<rect (?![^>]*data-alerts-hour)/g) ?? []).length, circles: (m[2].match(/<circle /g) ?? []).length,
    hours: [...m[2].matchAll(/<rect [^>]*data-alerts-hour="([^"]*)"[^>]*><title>([\s\S]*?)<\/title>/g)].map((x) => ({ at: x[1], tip: ent(x[2]) })),
  }));
  return { nums, ranked, panels, words, svgs };
}

if (process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]))) {
  const [dir, outJson, outHtml, outTxt] = process.argv.slice(2);
  if (!dir || !outJson) { console.error("usage: caiso-alerts-figures.mjs <tables dir> <out.json> [<out.html> <out.txt>]"); process.exitCode = 2; }
  else {
    const T = {};
    for (const name of ["flex_alert_effects", "flex_alert_model", "caiso_grid_emergencies"]) {
      const f = path.join(dir, `${name}.csv`);
      if (fs.existsSync(f)) T[name] = readTable(f);
    }
    const { html, asked } = await drawPage(T);
    const f = figuresOf(html);
    const out = { page: "/grid/caiso/alerts", drawn_by: "site/scripts/caiso-alerts-figures.mjs (session 7532)",
      tables: Object.fromEntries(Object.entries(T).map(([k, v]) => [k, retrieved(v.header)])), asked, ...f };
    fs.writeFileSync(outJson, JSON.stringify(out, null, 1) + "\n");
    if (outHtml) fs.writeFileSync(outHtml, html);
    if (outTxt) fs.writeFileSync(outTxt, text(html).replace(/ (?=[A-Z][a-z]+ [a-z])/g, " ") + "\n");
    console.log(asked.join("\n"));
    console.log(`${f.nums.length} checked numbers, ${f.ranked.length} ranked rows, ${f.panels.length} day panels, ${f.svgs.length} charts; ${html.length} bytes of HTML`);
  }
}
