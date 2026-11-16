// Energy Research Warehouse (ERW) site, session 7534 (chain 304): every figure of the problem sets (/learn/problems and
// its five sets, live and as the dated edition), as the pages compute and draw them, for the replication
// (replication/problem_sets/replicate.py) to compare with its own computation.
//
//   node --import ./scripts/problem-sets-register.mjs scripts/problem-sets-figures.mjs record <dir>
//   node --import ./scripts/problem-sets-register.mjs scripts/problem-sets-figures.mjs replay <dir> [out.json]
//
// record: reads the live set (SUPABASE_URL and SUPABASE_ANON_KEY from the environment, else from the file the variable
//   ERW_ENV_LOCAL names, else site/.env.local; nothing else is read from that file), with the clock stopped at the
//   moment the run starts. Every read the five sets make is kept: <dir>/live_reads.json (the clock, each read's address
//   without the host, and the network snapshot when Storage gave one) and <dir>/live_rows.csv (every row each read gave).
//   Then <dir>/page_figures.json: each set's worked example and five questions as lib/problems.ts built them, each
//   figure with its check key, its value and the text the page shows; each set's page (app/learn/problems/[slug]/
//   page.tsx) drawn to HTML with the site's own components, every figure looked for in it by its check key and text;
//   and the dated edition's students' and teacher's copies drawn the same way, every frozen figure looked for.
// replay: the same, from <dir>'s kept reads alone (no network: a read not kept fails), the clock set to the kept one;
//   writes out.json (default: stdout). The test (tests/test_session7534_problem_sets.py) compares it with the kept
//   page_figures.json, so the kept figures are the page's own on the kept rows.
// No table written; no model called.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const [mode, dirArg, outArg] = process.argv.slice(2);
if (!["record", "replay"].includes(mode) || !dirArg) {
  console.error("usage: problem-sets-figures.mjs record|replay <dir> [out.json]");
  process.exit(2);
}
const dir = path.resolve(dirArg);
process.env.ERW_SPEND_CAP_USD = "0";

// ------------------------------------------------------------------ the reads: kept, or given back
const ROWS = path.join(dir, "live_rows.csv"), READS = path.join(dir, "live_reads.json");
const COLS = ["entity", "variable", "ts_utc", "value", "unit", "freq"];
const NULL = "\\N";
const cell = (x) => { const s = x === null || x === undefined ? NULL : String(x); return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s; };
function parseCsvLine(line) {
  const out = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (q) { if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
    else if (c === '"') q = true; else if (c === ",") { out.push(cur); cur = ""; } else cur += c;
  }
  out.push(cur);
  return out;
}

let NOW, reads = [], network = null;
const kept = new Map();   // address -> body
if (mode === "record") {
  const envFile = process.env.ERW_ENV_LOCAL ?? path.join(site, ".env.local");
  const fromFile = (k) => { try { return (fs.readFileSync(envFile, "utf-8").match(new RegExp(`^${k}=(.*)$`, "m"))?.[1] ?? "").trim(); } catch { return ""; } };
  for (const k of ["SUPABASE_URL", "SUPABASE_ANON_KEY"]) if (!process.env[k]) process.env[k] = fromFile(k);
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_ANON_KEY) { console.error("record needs SUPABASE_URL and SUPABASE_ANON_KEY"); process.exit(2); }
  NOW = Date.now();
} else {
  const r = JSON.parse(fs.readFileSync(READS, "utf-8"));
  NOW = Date.parse(r.now);
  network = r.network ?? null;
  const byId = new Map(r.reads.map((x) => [x.id, x.address]));
  for (const x of r.reads) kept.set(x.address, []);
  const lines = fs.readFileSync(ROWS, "utf-8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = parseCsvLine(lines[0]);
  for (const l of lines.slice(1)) {
    const c = parseCsvLine(l), o = {};
    head.forEach((k, i) => { o[k] = c[i] === NULL ? null : c[i]; });
    const row = {};
    for (const k of COLS) row[k] = k === "value" ? (o[k] === null ? null : Number(o[k])) : o[k];
    kept.get(byId.get(Number(o.read)))?.push(row);
  }
  // the page's reader asks for the rows; a held read is not asked: these hosts are stand-ins with no network
  process.env.SUPABASE_URL = "https://kept-reads.invalid";
  process.env.SUPABASE_ANON_KEY = "kept";
}
/** Two addresses of the same read, one page apart (equal but for the offset). */
function samePaged(a, b) {
  const strip = (s) => { const x = new URL(s, "http://x"); x.searchParams.delete("offset"); return x.pathname + x.search; };
  return strip(a) === strip(b);
}
const realNow = Date.now;
Date.now = () => NOW;
const NETWORK_PATH = "network";
const realFetch = globalThis.fetch;
globalThis.fetch = async (input, init) => {
  const u = new URL(typeof input === "string" ? input : input.url);
  const address = u.pathname.startsWith("/rest/v1/") ? u.pathname + u.search : NETWORK_PATH;
  if (mode === "replay") {
    if (address === NETWORK_PATH) return network ? new Response(JSON.stringify(network), { status: 200 }) : new Response("not kept", { status: 404 });
    if (!kept.has(address) && !(Number(u.searchParams.get("offset") ?? "0") > 0)) throw new Error(`a read that was not kept: ${address}`);
    // the held rows were not kept, so a page can come back shorter than it was and the reader would stop paging there:
    // the first page gives every kept row of the read's pages, in their order, and the later pages give none
    const offset = Number(u.searchParams.get("offset") ?? "0");
    const rows = offset > 0 ? [] : [...kept.entries()].filter(([a]) => samePaged(a, address))
      .sort((x, y) => Number(new URL(x[0], "http://x").searchParams.get("offset") ?? 0) - Number(new URL(y[0], "http://x").searchParams.get("offset") ?? 0))
      .flatMap(([, r]) => r);
    return new Response(JSON.stringify(rows), { status: 200, headers: { "content-type": "application/json" } });
  }
  const r = await realFetch(input, init);
  if (r.ok) {
    const body = await r.clone().json();
    if (address === NETWORK_PATH) network = body;
    else if (!kept.has(address)) { kept.set(address, body); reads.push(address); }
  }
  return r;
};

// ------------------------------------------------------------------ the pages' own code
const { problemSet, SETS } = await import("../lib/problems.ts");
const { shown } = await import("../lib/format.ts");
const { editions, edition } = await import("../lib/problemEditions.ts");
const Live = (await import("../app/learn/problems/[slug]/page.tsx")).default;
const Students = (await import("../app/learn/problems/[slug]/[edition]/page.tsx")).default;
const Teacher = (await import("../app/learn/problems/[slug]/[edition]/teacher/page.tsx")).default;
const Index = (await import("../app/learn/problems/page.tsx")).default;
const { heldBy } = await import("../components/Num.tsx");

const attr = (s) => s.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const textOf = (parts) => parts.map((p) => (typeof p === "string" ? p : `${shown(p.v)}${p.u ? ` ${p.u}` : ""}`)).join("");
function questionOut(q) {
  const figs = [];
  const walk = (where, parts) => parts.forEach((p, i) => { if (typeof p !== "string") figs.push({ where, i, k: p.k, v: p.v, u: p.u ?? "", shown: shown(p.v) }); });
  walk("answer", q.answer);
  if (q.line) walk("line", q.line);
  q.steps.forEach((s, j) => walk(`step${j + 1}`, s));
  if (q.day) figs.push({ where: "day", i: 0, k: q.day.k, v: null, u: "", shown: q.day.d });
  return {
    id: q.id, q: q.q, tables: q.tables, day: q.day ?? null,
    answer: textOf(q.answer), line: q.line ? textOf(q.line) : null, steps: q.steps.map(textOf),
    // the words between the figures: the dates, names and counts the page writes in them (not keyed)
    words: [q.q, ...[q.answer, q.line ?? [], ...q.steps].flatMap((ps) => ps.filter((p) => typeof p === "string"))].join(" | "),
    figures: figs,
  };
}

const out = { now: new Date(NOW).toISOString().replace(/\.\d{3}Z$/, "Z"), sets: {}, edition: {} };
let missing = 0;
for (const s of SETS) {
  const set = await problemSet(s.slug);
  const html = renderToStaticMarkup(await Live({ params: Promise.resolve({ slug: s.slug }) }));
  const qs = [set.example, ...set.questions].filter(Boolean).map(questionOut);
  // a figure of a held table is drawn as "license needed" (components/Num.tsx, heldBy): counted as held, and it must not
  // be drawn as a number; every other figure must be found by its check key and its text
  const drawn = { figures: 0, found: 0, held: 0, missing: [], held_keys: [] };
  for (const q of qs) for (const f of q.figures) {
    if (f.where === "day") continue;
    drawn.figures++;
    const asNumber = html.includes(`data-check="${attr(f.k)}"`);
    if (heldBy(f.k)) {
      if (asNumber) drawn.missing.push(`${q.id} ${f.where} ${f.k} (held, yet drawn as a number)`);
      else { drawn.held++; if (!drawn.held_keys.includes(`${q.id} ${f.k}`)) drawn.held_keys.push(`${q.id} ${f.k}`); }
      continue;
    }
    if (asNumber && html.includes(`>${attr(f.shown)}</span>`)) drawn.found++; else drawn.missing.push(`${q.id} ${f.where} ${f.k}`);
  }
  missing += drawn.missing.length;
  out.sets[s.slug] = { title: s.title, example: set.example ? set.example.id : null, order: set.questions.map((q) => q.id), questions: qs, drawn,
    held: (html.match(/data-license-held/g) ?? []).length,
    // session 7534: the decisions block at the page's foot, its choices by key
    decisions: html.includes(`data-decisions="${s.slug}"`) ? [...html.matchAll(/data-decision="([^"]+)"/g)].map((m) => m[1]) : null };
}
for (const d of editions()) {
  const e = edition(d);
  out.edition[d] = {};
  for (const s of e.sets) {
    const st = renderToStaticMarkup(await Students({ params: Promise.resolve({ slug: s.slug, edition: d }) }));
    const te = renderToStaticMarkup(await Teacher({ params: Promise.resolve({ slug: s.slug, edition: d }) }));
    let figures = 0, found = 0; const lost = [];
    for (const q of s.questions) for (const ps of [q.answer, ...q.steps]) for (const p of ps) {
      if (typeof p === "string") continue;
      figures++;
      if (te.includes(`data-frozen="${attr(p.k)}">${attr(shown(p.v))}`)) found++; else lost.push(`${q.id} ${p.k}`);
    }
    missing += lost.length;
    // the students' copy holds no answer: no frozen figure in it
    out.edition[d][s.slug] = { teacher: { figures, found, missing: lost }, students_frozen: (st.match(/data-frozen=/g) ?? []).length,
      students_rows_links: s.questions.map((q) => st.includes(`href="${attr(q.csv)}"`)) };
  }
}
const indexHtml = renderToStaticMarkup(Index());
out.index_decisions = indexHtml.includes('data-decisions="problem-sets"') ? [...indexHtml.matchAll(/data-decision="([^"]+)"/g)].map((m) => m[1]) : null;

if (mode === "record") {
  fs.mkdirSync(dir, { recursive: true });
  const lines = [`# The rows every read of the five problem sets gave, recorded by site/scripts/problem-sets-figures.mjs at ${out.now} from the ERW live set (Supabase, the anon key). read: the read's number in live_reads.json.`,
    ["read", ...COLS].join(",")];
  // a held table's held rows (cost_of_power_monthly's ISO-NE, MISO and NYISO hubs) come back from the read and are dropped
  // by the page's reader (lib/supabase.ts); they are not kept here either, so the repository never holds them
  const { licenseHeldRow, rowLicenseHeld, licenseByRow } = await import("../lib/license.ts");
  let dropped = 0;
  reads.forEach((a, i) => {
    const table = new URLSearchParams(a.split("?")[1]).get("table_name")?.replace(/^eq\./, "") ?? "";
    for (const r of kept.get(a)) {
      if (licenseByRow(table) ? rowLicenseHeld(r) : licenseHeldRow(table, r.entity ?? "")) { dropped++; continue; }
      lines.push([i, ...COLS.map((k) => cell(r[k]))].join(","));
    }
  });
  console.log(`rows a license holds, not kept: ${dropped}`);
  fs.writeFileSync(ROWS, lines.join("\n") + "\n");
  fs.writeFileSync(READS, JSON.stringify({ now: out.now, note: "Each read the five problem sets made of the live set, without the host or the key; the rows are in live_rows.csv. network: the hourly network snapshot from Supabase Storage, or null when the committed site/data/grid_network.json was used.", reads: reads.map((address, id) => ({ id, address })), network }, null, 1) + "\n");
  fs.writeFileSync(path.join(dir, "page_figures.json"), JSON.stringify(out, null, 1) + "\n");
  console.log(`recorded ${reads.length} reads at ${out.now}; figures missing from the drawn pages: ${missing}`);
} else {
  const text = JSON.stringify(out, null, 1) + "\n";
  if (outArg) fs.writeFileSync(outArg, text); else process.stdout.write(text);
  console.error(`replayed at ${out.now}; figures missing from the drawn pages: ${missing}`);
}
Date.now = realNow;
globalThis.fetch = realFetch;
process.exitCode = missing ? 1 : 0;
