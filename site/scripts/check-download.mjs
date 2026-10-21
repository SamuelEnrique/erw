// Energy Research Warehouse (ERW) site, session 368: /api/download gives every table whole.
//
//   node scripts/check-download.mjs [base-url] [table ...]      (default http://localhost:3000, the ten tables below)
//
// The six largest tables of the live set, whose download the route's exact row count and its paging by offset made fail
// (session 328's finding, the night note of 20 October 2026, item 3), and the four that sometimes failed. For each, the
// whole CSV is read from the route and checked:
//   answer    200, a CSV, and the stream ends cleanly (a stream cut short by an error is a failure, never a short file)
//   top       the provenance lines ("#"), the "Downloaded" line, then the catalogue's columns, in its order
//   rows      every row has as many fields as there are columns (quoted fields read as CSV)
//   keys      no row's key twice (entity, variable, ts_utc; entity_id; event_id), where the CSV carries the whole key
//   count     the rows read equal the rows the live set holds, counted by the database itself (Prefer: count=exact) in
//             ranges small enough for the anon role's statement timeout: a series or an events table by time (its own
//             index on ts_utc or event_date), an entities table whole, or by ranges of entity_id where the whole count
//             times out; and the count the "Downloaded" line states, where it states one
// It prints, for each table, the rows, the live set's count, the row count in warehouse/metadata/coverage.csv (which
// counts the whole table: a windowed table holds fewer in the live set), the seconds and the size. Reads only, with the
// anon key; a download counts against the route's limit of sixty an hour a visitor. Exit 0 only if every file is whole.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const base = (args[0] ?? "http://localhost:3000").replace(/\/$/, "");
const SIX = ["eia930_all_emissions", "carbon_intensity_hourly", "ercot_as_prices", "state_generation_mix_monthly", "eia930_all_generation", "iso_rtm_hub_prices"];
const FOUR = ["eia_fuel_spot_prices", "iso_dam_hub_prices", "event_window_daily", "energy_projects"];
const tables = args.length > 1 ? args.slice(1) : [...SIX, ...FOUR];

const SUPA = new URL(env("SUPABASE_URL") ?? "http://missing").origin, KEY = env("SUPABASE_ANON_KEY") ?? "";
if (!KEY) { console.log("FAIL SUPABASE_URL or SUPABASE_ANON_KEY is not set (site/.env.local or the environment)"); process.exit(1); }
const H = { apikey: KEY, Authorization: `Bearer ${KEY}` };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function rest(q, extra = {}) {
  const r = await fetch(`${SUPA}/rest/v1/${q}`, { headers: { ...H, ...extra } });
  if (!r.ok) throw new Error(`Supabase ${q.split("?")[0]}: HTTP ${r.status} ${(await r.text()).slice(0, 160)}`);
  return r;
}

/** The database's own count of rows matching a filter, or null when it times out (three tries). */
async function count(shape, table, filter) {
  for (let i = 0; i < 3; i += 1) {
    try {
      const r = await rest(`${shape}?select=table_name&table_name=eq.${table}${filter}&limit=1`, { Prefer: "count=exact" });
      const n = Number((r.headers.get("content-range") ?? "").split("/")[1]);
      if (Number.isFinite(n)) return n;
    } catch { /* a timeout: try again */ }
    await sleep(400 * (i + 1));
  }
  return null;
}

/** A series or an events table counted by time: [min, max] in ranges of `days`, a range that times out halved. */
async function countByTime(shape, table, col) {
  const edge = async (dir) => {
    const rows = await (await rest(`${shape}?select=${col}&table_name=eq.${table}&order=${col}.${dir}&limit=1`)).json();
    return rows.length ? Date.parse(rows[0][col]) : null;
  };
  const lo = await edge("asc"), hi = await edge("desc");
  if (lo === null) return 0;
  const iso = (t) => encodeURIComponent(new Date(t).toISOString());
  const DAY = 86400000;
  let total = 0;
  const span = async (a, b) => {                                     // [a, b)
    const n = await count(shape, table, `&${col}=gte.${iso(a)}&${col}=lt.${iso(b)}`);
    if (n !== null) { total += n; return; }
    if (b - a <= DAY) throw new Error(`${table}: one day from ${new Date(a).toISOString()} cannot be counted`);
    const mid = a + Math.floor((b - a) / 2 / DAY) * DAY;
    await span(a, mid); await span(mid, b);
  };
  for (let a = lo; a <= hi; a += 30 * DAY) await span(a, Math.min(a + 30 * DAY, hi + 1));
  return total;
}

/** An entities table: whole, or in ranges of entity_id cut at every 5,000th id of the file (the ranges cover every id). */
async function countEntities(table, ids) {
  const whole = await count("entities", table, "");
  if (whole !== null) return whole;
  const cuts = [...new Set(ids.filter((_, i) => i > 0 && i % 5000 === 0))];
  const q = (v) => encodeURIComponent(v);
  let total = 0;
  for (let i = 0; i <= cuts.length; i += 1) {
    const f = (i > 0 ? `&entity_id=gte.${q(cuts[i - 1])}` : "") + (i < cuts.length ? `&entity_id=lt.${q(cuts[i])}` : "");
    const n = await count("entities", table, f);
    if (n === null) throw new Error(`${table}: a range of entity_id cannot be counted`);
    total += n;
  }
  return total;
}

function coverageRows() {
  const f = path.join(here, "..", "..", "warehouse", "metadata", "coverage.csv");
  if (!fs.existsSync(f)) return {};
  const lines = fs.readFileSync(f, "utf-8").split(/\r?\n/);
  const head = lines[0].split(","), ti = head.indexOf("table"), ni = head.indexOf("n_rows");
  const out = {};
  for (const l of lines.slice(1)) {
    const c = l.split(",");          // the first columns carry no comma (table, iso, market, n_nodes, ..., n_rows)
    if (c.length > ni) out[c[ti]] = Number(c[ni]);
  }
  return out;
}

/** Reads the route's whole CSV as it streams: provenance, columns, rows by CSV rules, the key of each row. */
async function readCsv(table, columns, keyCols) {
  const t0 = Date.now();
  const res = await fetch(`${base}/api/download?table=${table}`, { signal: AbortSignal.timeout(600000) });
  const out = { status: res.status, type: res.headers.get("content-type") ?? "", prov: [], cols: null, rows: 0, badRows: 0, keys: new Set(), dupes: 0, bytes: 0, ids: [], error: null, stated: null };
  if (res.status !== 200) { out.error = (await res.text()).slice(0, 300).trim(); out.secs = (Date.now() - t0) / 1000; return out; }
  const keyIdx = keyCols && keyCols.every((k) => columns.includes(k)) ? keyCols.map((k) => columns.indexOf(k)) : null;
  const dec = new TextDecoder();
  let line = "", inQ = false, field = 0, cur = "", rec = [];
  const endRecord = () => {
    out.rows += 1;
    if (field + 1 !== columns.length) out.badRows += 1;
    if (keyIdx) {
      const k = keyIdx.map((i) => rec[i] ?? "").join("\u0001");
      if (out.keys.has(k)) out.dupes += 1; else out.keys.add(k);
      if (columns[0] === "entity_id") out.ids.push(rec[keyIdx[0]]);
    }
    field = 0; cur = ""; rec = [];
  };
  try {
    for await (const chunk of res.body) {
      out.bytes += chunk.length;
      const s = dec.decode(chunk, { stream: true });
      let i = 0;
      while (out.cols === null && i < s.length) {               // the top: whole lines until the columns
        const j = s.indexOf("\n", i);
        if (j < 0) { line += s.slice(i); i = s.length; break; }
        line += s.slice(i, j); i = j + 1;
        if (line.startsWith("#")) out.prov.push(line); else out.cols = line.replace(/\r$/, "").split(",");
        line = "";
      }
      for (; i < s.length; i += 1) {                            // the rows, by CSV rules: a quote toggles, "" is two toggles
        const c = s[i];
        if (c === '"') { inQ = !inQ; continue; }
        if (inQ) { cur += c; continue; }
        if (c === ",") { rec[field] = cur; field += 1; cur = ""; continue; }
        if (c === "\n") { rec[field] = cur; endRecord(); continue; }
        if (c !== "\r") cur += c;
      }
    }
    if (field > 0 || cur !== "") out.error = "the file ends inside a row";
  } catch (e) {
    out.error = `the stream broke after ${out.rows} rows: ${e.cause?.message ?? e.message}`;
  }
  out.secs = (Date.now() - t0) / 1000;
  const dl = out.prov.find((l) => l.startsWith("# Downloaded from the ERW site's live set"));
  const m = dl?.match(/: (\d+) rows\.$/);
  out.stated = m ? Number(m[1]) : null;
  out.downloadedLine = dl ?? null;
  return out;
}

const cover = coverageRows();
const KEYS = { series: ["entity", "variable", "ts_utc"], entities: ["entity_id"], events: ["event_id"] };
let bad = 0;
const results = [];
console.log(`check-download against ${base}, ${new Date().toISOString()}`);
for (const table of tables) {
  const lines = [];
  const check = (ok, what) => { lines.push(`${ok ? "ok  " : "FAIL"} ${table}: ${what}`); return ok; };
  let whole = true;
  try {
    const cat = await (await rest(`catalogue?select=columns,in_live_set,license&table_name=eq.${table}`)).json();
    if (!cat.length || !cat[0].columns) throw new Error("not in the public catalogue's live set");
    const columns = JSON.parse(cat[0].columns);
    const shape = columns[0] === "entity_id" ? "entities" : columns[0] === "event_id" ? "events" : "series";
    // a series table that carries an event column (event_window_daily) can hold one (entity, variable, ts_utc) twice
    const keyCols = shape === "series" && columns.includes("event") ? null : KEYS[shape];
    const f = await readCsv(table, columns, keyCols);
    whole = check(f.status === 200 && /^text\/csv/.test(f.type), `answers ${f.status} ${f.type}${f.error && f.status !== 200 ? ` (${f.error})` : ""}`) && whole;
    if (f.status === 200) {
      whole = check(!f.error, f.error ? f.error : "the stream ends cleanly") && whole;
      whole = check(f.prov.length > 1 && Boolean(f.downloadedLine) && JSON.stringify(f.cols) === JSON.stringify(columns),
        `${f.prov.length} provenance lines, the "Downloaded" line, then the catalogue's ${columns.length} columns`) && whole;
      whole = check(f.badRows === 0, `every row has ${columns.length} fields (${f.badRows} do not)`) && whole;
      if (keyCols) whole = check(f.dupes === 0, `no key twice (${keyCols.join(", ")}): ${f.dupes} repeated`) && whole;
      const live = shape === "entities" ? await countEntities(table, f.ids) : await countByTime(shape, table, shape === "events" ? "event_date" : "ts_utc");
      whole = check(f.rows === live, `${f.rows} rows read; the live set holds ${live} (counted by the database)`) && whole;
      if (f.stated !== null) whole = check(f.stated === f.rows, `the "Downloaded" line states ${f.stated} rows`) && whole;
      results.push({ table, status: f.status, rows: f.rows, live, coverage: cover[table] ?? null, secs: f.secs, mb: f.bytes / 1e6, stated: f.stated, whole });
    } else {
      results.push({ table, status: f.status, rows: null, live: null, coverage: cover[table] ?? null, secs: f.secs, mb: 0, stated: null });
    }
  } catch (e) {
    whole = check(false, e.message);
    results.push({ table, status: null, rows: null, live: null, coverage: cover[table] ?? null, secs: null, mb: 0, stated: null });
  }
  if (!whole) bad += 1;
  for (const l of lines) console.log(l);
}
console.log("\ntable | answer | rows read | live set | coverage.csv | stated | seconds | MB | whole");
for (const r of results) {
  console.log([r.table, r.status, r.rows, r.live, r.coverage, r.stated ?? "not stated", r.secs?.toFixed(1), r.mb.toFixed(1),
    r.whole ? "yes" : "NO"].join(" | "));
}
console.log(`\n${tables.length - bad} of ${tables.length} files whole`);
process.exit(bad ? 1 : 0);
