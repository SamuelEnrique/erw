// Energy Research Warehouse (ERW) site, session 7531 (chain 304): the index /events and its nine event pages drawn to
// HTML without a build, each from its reads to its last cell. The page's own function is called (app/events/.../page.tsx)
// and its reads are answered by a stand-in for fetch, from the warehouse's CSV tables given by the caller. No network,
// no table written, no click, no chart seen.
//
//   node --import ./scripts/events-page-register.mjs scripts/events-pages.mjs <tables dir> <out dir> [<figures.json>]
//
// <tables dir> holds event_window_daily.csv and caiso_grid_emergencies.csv as the warehouse writes them (a "#" header).
// <out dir> gets <slug>.html and <slug>.txt for each page (the page as a reader meets it, one line a block). With
// <figures.json>, every figure the ten pages print through the checked-number component (its check key, the raw value
// and the text shown), the event study table's day counts and the "Over the N days" sentence, written for the
// replication (replication/events/replicate.py reads it and recomputes each one from the table on its own).
// A test imports drawPage and gives it rows itself (scripts/test-events-render.mjs).
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { renderToStaticMarkup } from "react-dom/server";

export const PAGES = [
  ["index", "../app/events/page.tsx"],
  ["uri-2021", "../app/events/uri-2021/page.tsx"],
  ["covid-2020", "../app/events/covid-2020/page.tsx"],
  ["caiso-heat-2020", "../app/events/caiso-heat-2020/page.tsx"],
  ["caiso-heat-2022", "../app/events/caiso-heat-2022/page.tsx"],
  ["elliott-2022", "../app/events/elliott-2022/page.tsx"],
  ["ercot-heat-2023", "../app/events/ercot-heat-2023/page.tsx"],
  ["cold-2025", "../app/events/cold-2025/page.tsx"],
  ["east-heat-2025", "../app/events/east-heat-2025/page.tsx"],
  ["cold-2026", "../app/events/cold-2026/page.tsx"],
];

/** The rows of a warehouse CSV as objects keyed by its column names (quoted fields read as CSV). */
export function csvRows(file) {
  const out = [];
  let cols = null;
  for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    const c = [];
    let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
      else if (ch === '"') q = true; else if (ch === ",") { c.push(cur); cur = ""; } else cur += ch;
    }
    c.push(cur);
    if (!cols) { cols = c; continue; }
    out.push(Object.fromEntries(cols.map((k, i) => [k, c[i] ?? ""])));
  }
  return out;
}

const unq = (v) => (v ?? "").replace(/^eq\./, "");
const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

/** One page drawn on the rows `rowsOf(table)` gives (objects with the table's columns, or null for a table that cannot be
 * read, which answers as a failed request). Returns the HTML and the reads the page made. */
export async function drawPage(file, rowsOf) {
  process.env.SUPABASE_URL = "http://localhost:9/";
  process.env.SUPABASE_ANON_KEY = "stand-in";
  const asked = [];
  const real = globalThis.fetch;
  globalThis.fetch = async (url) => {
    const u = new URL(String(url));
    const q = u.searchParams;
    const name = unq(q.get("table_name"));
    const all = rowsOf(name);
    if (all === null) { asked.push(`${name}: not answered`); return new Response("stand-in: the table is not held", { status: 404 }); }
    let rows = all;
    if (u.pathname.endsWith("/series")) {
      const ent = q.get("entity"), v = q.get("variable"), ev = q.get("event"), from = q.get("ts_utc");
      if (ent) {
        const set = ent.startsWith("in.(") ? new Set(ent.slice(4, -1).split(",").map((s) => s.replace(/^"|"$/g, ""))) : new Set([unq(ent)]);
        rows = rows.filter((r) => set.has(r.entity));
      }
      if (v) rows = rows.filter((r) => r.variable === unq(v));
      if (ev) rows = rows.filter((r) => r.event === unq(ev));
      if (from) rows = rows.filter((r) => r.ts_utc >= from.replace(/^gte\./, ""));
      rows = [...rows].sort((a, b) => cmp(a.entity, b.entity) || cmp(a.variable, b.variable) || cmp(a.ts_utc, b.ts_utc) || cmp(a.event, b.event));
      rows = rows.map((r) => ({ entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: Number(r.value), unit: r.unit, freq: r.freq || null }));
    } else if (u.pathname.endsWith("/events")) {
      const and = q.get("and");
      const m = and ? /event_date\.gte\.([^,]+),event_date\.lte\.([^)]+)/.exec(and) : null;
      if (m) rows = rows.filter((r) => r.event_date >= m[1] && r.event_date <= m[2]);
      rows = [...rows].sort((a, b) => cmp(a.event_date, b.event_date) || cmp(a.event_id, b.event_id));
      rows = rows.map((r) => ({ event_id: r.event_id, event_date: r.event_date, event_type: r.event_type, extra: null }));
    }
    const limit = Number(q.get("limit") ?? 1000), offset = Number(q.get("offset") ?? 0);
    asked.push(`${name} ${q.get("event") ?? ""} ${q.get("entity") ?? ""} ${q.get("variable") ?? ""}: ${rows.length} rows`.replace(/\s+/g, " "));
    return new Response(JSON.stringify(rows.slice(offset, offset + limit)), { status: 200, headers: { "content-type": "application/json" } });
  };
  const log = console.error;
  console.error = () => {};
  try {
    const mod = await import(new URL(file, import.meta.url).href);
    const el = await mod.default();
    // an async component inside the page (EventWindow, EventStudy) is drawn by resolving it first: react-dom/server's
    // static renderer does not await, so each async child is called and its result put in its place
    return { html: renderToStaticMarkup(await resolveAsync(el)), asked };
  } finally {
    globalThis.fetch = real;
    console.error = log;
  }
}

/** The element tree with every async function component called and awaited in place (server components). */
export async function resolveAsync(el) {
  if (Array.isArray(el)) return Promise.all(el.map(resolveAsync));
  if (!el || typeof el !== "object" || !("type" in el)) return el;
  const { type, props } = el;
  if (typeof type === "function" && type.constructor && type.constructor.name === "AsyncFunction") {
    return resolveAsync(await type(props));
  }
  if (props && props.children !== undefined) {
    const children = await resolveAsync(props.children);
    return { ...el, props: { ...props, children } };
  }
  return el;
}

const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
/** The drawn page as lines of text, with every hover kept and marked. */
export function pageText(html) {
  const t = html
    .replace(/<title>([\s\S]*?)<\/title>/g, "\n[hover] $1\n")
    .replace(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g, "\n[tip] $1\n")
    .replace(/<(span|abbr)[^>]* title="([^"]*)"[^>]*>/g, " [title: $2] ")
    .replace(/<\/(th|td)>/g, " | ")
    .replace(/<(h1|h2|h3|p|li|tr|caption|summary|figcaption|section|nav|aside|svg|div)([ >])/g, "\n<$1$2")
    .replace(/<[^>]+>/g, " ");
  return ent(t).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean).join("\n");
}

/** Every checked figure of a drawn page: its key, its raw value and the text shown. */
export function figuresOf(html) {
  const out = [];
  for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g)) out.push({ check: ent(m[1]), raw: Number(m[2]), shown: ent(m[3].replace(/<[^>]+>/g, "")) });
  return out;
}

/** The event study block's table: each row's grid, outcome and day count, and the lead sentence's days. */
export function studyCounts(html) {
  const rows = [];
  for (const tr of html.matchAll(/<tr class="border-b border-rule">([\s\S]*?)<\/tr>/g)) {
    const keys = [...tr[1].matchAll(/data-check="es\|([^|]+)\|([^|]+)\|([^|]+)\|pooled\|est"/g)];
    if (!keys.length) continue;
    const tds = [...tr[1].matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => ent(m[1].replace(/<[^>]+>/g, "")).trim());
    rows.push({ event: keys[0][1], entity: keys[0][2], variable: keys[0][3], days: Number(tds[5]) });
  }
  const lead = /Over the (\d+) days of the event window/.exec(ent(html.replace(/<[^>]+>/g, "")));
  return { rows, leadDays: lead ? Number(lead[1]) : null };
}

// Session 7531's held-row fix: the figures file sits in a public repository, so a figure of a held row is never written
// to it, even when the pages are drawn with the hold stood aside (EVENTS_DRAW_UNHELD). The rule is the site's
// (lib/license.ts licenseHeldRow and gridOfEntity), read from the real status file, not the loader's stand-in: a table
// "license needed" whose deciding publishers are all grids holds the rows of those grids' entities ("isone:", "miso:",
// "nyiso:"); an entity of no grid ("eia930:", "noaa:") is kept. Each page's count of held figures goes in heldFigures.
const GRID_PREFIX = { "ISO-NE": "isone", MISO: "miso", NYISO: "nyiso", PJM: "pjm", SPP: "spp", CAISO: "caiso", ERCOT: "ercot" };
const GRIDS = new Set(Object.values(GRID_PREFIX));
export function gridOf(entity) {
  const m = /^([a-z0-9_-]+):(.*)$/is.exec(entity ?? "");
  if (!m) return "";
  const head = m[1].toLowerCase();
  if (GRIDS.has(head)) return head;
  const q = /^([a-z]+)_(?:load_)?queue$/.exec(head);
  if (q && GRIDS.has(q[1])) return q[1];
  return head === "iso" && GRIDS.has(m[2].toLowerCase()) ? m[2].toLowerCase() : "";
}
export function heldRow(status, table, entity, day = new Date().toISOString().slice(0, 10)) {
  const r = status.tables?.[table];
  if (!r || r.status !== "license needed" || day < (r.from ?? "") || r.hold === "row") return false;
  const who = r.publishers ?? [];
  if (!(who.length && who.every((p) => p in GRID_PREFIX))) return true;
  const g = gridOf(entity);
  return !!g && who.some((p) => GRID_PREFIX[p] === g);
}
/** A figure's check key held: series|<table>|<entity>|... and es|<event>|<entity>|... (the table event_window_daily). */
export function heldKey(status, check) {
  const p = check.split("|");
  const table = p[0].startsWith("series") && p.length > 2 ? p[1] : p[0] === "es" && p.length > 2 ? "event_window_daily" : "";
  return !!table && heldRow(status, table, p[2]);
}

/** The retrieval stamp of a warehouse CSV (its "# Retrieved:" line). */
export function stamp(file) {
  for (const line of fs.readFileSync(file, "utf-8").split(/\r?\n/)) {
    if (!line.startsWith("#")) break;
    const m = /^# Retrieved: (\S+)/.exec(line);
    if (m) return m[1];
  }
  return "";
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [dir, outDir, figFile] = process.argv.slice(2);
  if (!dir || !outDir) { console.error("usage: events-pages.mjs <tables dir> <out dir> [<figures.json>]"); process.exitCode = 2; }
  else {
    fs.mkdirSync(outDir, { recursive: true });
    const cache = new Map();
    const rowsOf = (name) => {
      if (!cache.has(name)) { const f = path.join(dir, `${name}.csv`); cache.set(name, fs.existsSync(f) ? csvRows(f) : null); }
      return cache.get(name);
    };
    const status = JSON.parse(fs.readFileSync(new URL("../data/license_status.json", import.meta.url), "utf-8"));
    const figs = { tables: {}, pages: {} };
    for (const t of ["event_window_daily", "caiso_grid_emergencies"]) { const f = path.join(dir, `${t}.csv`); figs.tables[t] = fs.existsSync(f) ? stamp(f) : ""; }
    for (const [slug, file] of PAGES) {
      const { html, asked } = await drawPage(file, rowsOf);
      const text = pageText(html);
      fs.writeFileSync(path.join(outDir, `${slug}.html`), html);
      fs.writeFileSync(path.join(outDir, `${slug}.txt`), text + "\n");
      const all = figuresOf(html);
      const f = all.filter((x) => !heldKey(status, x.check));
      // the lines of a day list ("2022-09-06 : Flex Alert, ..."), so the replication reads CAISO's notices as the page lists them
      const lines = text.split("\n").filter((l) => /^\d{4}-\d\d-\d\d ?: /.test(l) && !l.includes("|"));
      figs.pages[slug] = { figures: f, study: studyCounts(html), lines, held: (html.match(/data-license-held=/g) ?? []).length, notHeld: (text.match(/not held/g) ?? []).length, reads: asked, heldFigures: all.length - f.length };
      console.log(`${slug}: ${f.length} figures, ${asked.length} reads, ${html.length} bytes`);
    }
    if (figFile) {
      fs.writeFileSync(figFile, JSON.stringify(figs, null, 1) + "\n");
      console.log(`wrote ${figFile}`);
    }
  }
}
