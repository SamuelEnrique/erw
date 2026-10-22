// Energy Research Warehouse (ERW) site: bundle the committed markdown the site renders.
//
// Reads, from the repository (one level above site/):
//   docs/digest/YYYY-MM-DD.md and docs/digest/latest.md   the Energy Digest archive
//   docs/datastandard.md                                   the data standard
//   docs/methods/*.md                                      method documents
//   warehouse/metadata/sources.csv                         the source registry (session 21, /terms)
//   docs/licenses.md, warehouse/metadata/license_verdicts.csv  the licenses and each publisher's verdict (session 471, /data/licenses)
// and writes site/content/docs.json, which the pages import. Runs before
// `next dev` and `next build` (package.json predev and prebuild), so the
// content is part of the build and no page reads the file system at request
// time. A missing file fails the build: the site never shows a stand-in.
// Session 587: it also writes site/content/holds.json for /internal/holds, from docs/licenses_holds.csv and
// warehouse/metadata/license_status.csv (scripts/holds-content.mjs); that list may be missing, and the page says so.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { holdsFromRepo } from "./holds-content.mjs";  // session 587

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
const docs = path.join(repo, "docs");

function read(p) {
  if (!fs.existsSync(p)) {
    console.error(`build-content: missing ${path.relative(repo, p)}`);
    process.exit(1);
  }
  return fs.readFileSync(p, "utf-8").replace(/\r\n/g, "\n");
}

const digestDir = path.join(docs, "digest");
const digests = {};
for (const f of fs.readdirSync(digestDir).sort()) {
  const m = f.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
  if (m) digests[m[1]] = read(path.join(digestDir, f));
}
if (Object.keys(digests).length === 0) {
  console.error("build-content: no dated digests in docs/digest");
  process.exit(1);
}

// Session 17: the weekly briefs (docs/weekly/YYYY-Www.md, "Energy Week"); session 23: the Energy Roundup
// (docs/roundup/YYYY-Www.md, warehouse/news/roundup.py). Both are the weekly brief, by ISO week; where a
// week has a Roundup it is shown, else its Energy Week. None is not an error.
const weeklies = {};
const weeklySource = {};
for (const dir of ["weekly", "roundup"]) {
  const d = path.join(docs, dir);
  if (!fs.existsSync(d)) continue;
  for (const f of fs.readdirSync(d).sort()) {
    const m = f.match(/^(\d{4}-W\d{2})\.md$/);
    if (m) {
      weeklies[m[1]] = read(path.join(d, f));
      weeklySource[m[1]] = `docs/${dir}/${f}`;
    }
  }
}

// Session 135: a method note that stays on the server is not bundled, so no page of the site can show it. Thesis
// Builder's research plan and scoring rule are internal (the owner's ruling); its readers' note is docs/methods/thesis.md
const INTERNAL_METHODS = new Set(["thesis_builder"]);
const methods = {};
for (const f of fs.readdirSync(path.join(docs, "methods")).sort()) {
  if (f.endsWith(".md") && !INTERNAL_METHODS.has(f.replace(/\.md$/, ""))) methods[f.replace(/\.md$/, "")] = read(path.join(docs, "methods", f));
}

// Session 15: the run history's EIA-930 gaps and failures, so /grid can say why a day is missing
// (warehouse/metadata/run_status.csv is committed metadata, refreshed by the daily workflow's commit).
function runStatus() {
  const p = path.join(repo, "warehouse", "metadata", "run_status.csv");
  const lines = read(p).trim().split("\n");
  const cols = lines[0].split(",");
  const rows = [];
  for (const line of lines.slice(1)) {
    // detail is the last column and may be quoted with commas inside
    const parts = line.split(",");
    const head = parts.slice(0, cols.length - 1);
    let detail = parts.slice(cols.length - 1).join(",");
    if (detail.startsWith('"') && detail.endsWith('"')) detail = detail.slice(1, -1).replace(/""/g, '"');
    const r = Object.fromEntries(cols.slice(0, -1).map((c, i) => [c, head[i]]));
    r.detail = detail;
    if (r.connector === "eia930" && r.status !== "ok") rows.push(r);
  }
  return rows;
}

// session 21 (/terms): the source registry, warehouse/metadata/sources.csv, one row per source with its license
function csvRows(text) {
  const rows = [];
  let row = [], cell = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') q = false;
      else cell += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(cell); cell = ""; }
    else if (ch === "\n") { row.push(cell); rows.push(row); row = []; cell = ""; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows;
}
// Session 102: the items of one top-level list of warehouse/supabase/live_set.yaml ("key:" then "  - item" lines; a
// comment after an item is dropped). The build has no YAML reader and needs only this.
function liveSetList(key) {
  const lines = read(path.join(repo, "warehouse", "supabase", "live_set.yaml")).split(/\r?\n/);
  const at = lines.findIndex((l) => l.startsWith(`${key}:`));
  if (at < 0) return [];
  const out = [];
  for (const l of lines.slice(at + 1)) {
    if (/^\S/.test(l)) break;                       // the next top-level key
    const m = l.match(/^\s+-\s+([^\s#]+)/);
    if (m) out.push(m[1].replace(/^['"]|['"]$/g, ""));
  }
  return out;
}
// Session 102: /terms (a live page) lists the registry and counts it. A source that serves only tables whose pages are
// in review is held off the page until one of them opens (live_set.yaml, sources_hold), as catalogue_hold keeps such a
// table out of the home page's counts: the landing of sessions 91 to 101 moved "125 data sources" to 133 for an hour.
function sources() {
  const held = new Set(liveSetList("sources_hold"));
  const [head, ...rows] = csvRows(read(path.join(repo, "warehouse", "metadata", "sources.csv")));
  return rows.filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])))
    .filter((r) => !held.has(r.source))
    .map(({ source, publisher, report, report_url, license, tables }) => ({ source, publisher, report, report_url, license, tables }));
}

// Session 471: each publisher's verdict (warehouse/metadata/license_verdicts.csv, written with docs/licenses.md by
// scripts/licenses.py), for the short reading at the head of /data/licenses: the publisher, its verdict as the ERW is
// today and if the ERW sells anything, and the note (what the publisher asks for, an acknowledgment or a citation).
function licenseVerdicts() {
  // a row whose last cell (the note) holds an unquoted comma has more cells than the header (NLR's, 21 October 2026):
  // the extra cells are the note's, joined back, so no publisher is dropped
  const [head, ...rows] = csvRows(read(path.join(repo, "warehouse", "metadata", "license_verdicts.csv")));
  return rows.filter((r) => r.length >= head.length).map((r) => [...r.slice(0, head.length - 1), r.slice(head.length - 1).join(",")])
    .map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])))
    .map(({ key, verdict, if_commercial, note }) => ({ key, verdict, if_commercial, note }));
}

// Session 23: Automated Analysis (docs/analysis/, warehouse/analysis/run.py). Each week's chart of the week and
// results, the template list, and the gallery index go into the bundle; the PNGs and the gallery charts are copied
// to public/analysis-files/ so the pages and the Roundup's images can link them. None is not an error.
const analysisDir = path.join(docs, "analysis");
const analysis = { weeks: {}, results: {}, templates: [], gallery: { templates: [] } };
const publicAnalysis = path.join(here, "..", "public", "analysis-files");
fs.rmSync(publicAnalysis, { recursive: true, force: true });
if (fs.existsSync(analysisDir)) {
  for (const f of fs.readdirSync(analysisDir).sort()) {
    const dir = path.join(analysisDir, f);
    if (/^\d{4}-W\d{2}$/.test(f) && fs.existsSync(path.join(dir, "chart_of_the_week.json"))) {
      analysis.weeks[f] = JSON.parse(read(path.join(dir, "chart_of_the_week.json")));
      if (fs.existsSync(path.join(dir, "results.json"))) analysis.results[f] = JSON.parse(read(path.join(dir, "results.json")));
    }
  }
  if (fs.existsSync(path.join(analysisDir, "templates.json"))) analysis.templates = JSON.parse(read(path.join(analysisDir, "templates.json"))).templates;
  if (fs.existsSync(path.join(analysisDir, "gallery", "index.json"))) analysis.gallery = JSON.parse(read(path.join(analysisDir, "gallery", "index.json")));
  fs.cpSync(analysisDir, publicAnalysis, {
    recursive: true,
    filter: (src) => fs.statSync(src).isDirectory() || /\.(png|json|txt)$/.test(src),
  });
}

// Session 232: the Digest's chart of the day. warehouse/news/brief.py draws one picture a weekday into
// docs/digest/charts/<date>.png (warehouse/analysis/findings/daily_chart.py); the pictures are copied to
// public/digest-charts/ so the digest's page can show them (lib/markdown.ts maps the link). None is not an error.
const digestCharts = path.join(docs, "digest", "charts");
const publicDigestCharts = path.join(here, "..", "public", "digest-charts");
fs.rmSync(publicDigestCharts, { recursive: true, force: true });
if (fs.existsSync(digestCharts)) {
  fs.mkdirSync(publicDigestCharts, { recursive: true });
  for (const f of fs.readdirSync(digestCharts).sort()) {
    // session 815: the phone picture (<date>-600.png) beside the 1200 px one
    if (/^\d{4}-\d{2}-\d{2}(?:-600)?\.png$/.test(f)) fs.copyFileSync(path.join(digestCharts, f), path.join(publicDigestCharts, f));
  }
}
// Session 238: each day's record beside its picture (docs/digest/charts/<date>.json), for /research: the one fact, the
// table and the source it was read from, as the warehouse wrote them. A day with a picture and no record is not listed.
const digestChartRecords = {};
// Session 411: the picture's own size, read from its PNG header (the IHDR chunk: width and height at bytes 16 and 20), so
// a page reserves the right room for it before it arrives; the pages had written 1600 by 900 for pictures of 1200 by 880.
function pngSize(file) {
  const b = fs.readFileSync(file);
  if (b.length < 24 || b.toString("latin1", 12, 16) !== "IHDR") return {};
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
}
if (fs.existsSync(digestCharts)) {
  for (const f of fs.readdirSync(digestCharts).sort()) {
    const m = f.match(/^(\d{4}-\d{2}-\d{2})\.json$/);
    if (!m || !fs.existsSync(path.join(digestCharts, `${m[1]}.png`))) continue;
    const r = JSON.parse(read(path.join(digestCharts, f)));
    digestChartRecords[m[1]] = { date: r.date ?? m[1], title: r.title ?? "", fact: r.fact ?? "", table: r.table ?? "", source: r.flag?.source ?? "", unit: r.flag?.unit ?? "",
      rule: r.flag?.rule ?? "", rendered_at: r.rendered_at ?? "", image: `${m[1]}.png`, proof: r.proof === true,
      numbers: r.numbers && typeof r.numbers === "object" ? r.numbers : {} };   // session 315: the record's own figures, each a Num on /research
    Object.assign(digestChartRecords[m[1]], pngSize(path.join(digestCharts, `${m[1]}.png`)));   // session 411: width and height in pixels
    // session 815: the phone picture, when the day has one, so the page can offer it under 640 px
    if (fs.existsSync(path.join(digestCharts, `${m[1]}-600.png`))) digestChartRecords[m[1]].image_600 = `${m[1]}-600.png`;
  }
}

// Session 238: the downloads the finding cards may link (site/public/findings/: each card's CSV, Python file and Stata
// do-file), by name, so that /research names a file "not held" instead of linking one that is not there. Listed here,
// at build, because a page drawn again later is drawn by a server function, which does not hold the public folder.
const findingsPublic = path.join(here, "..", "public", "findings");
const findingsFiles = fs.existsSync(findingsPublic) ? fs.readdirSync(findingsPublic).filter((f) => /\.(csv|py|do)$/.test(f)).sort() : [];

// Session 24: the platform's tool counts by status, from docs/platform-tools.md (for /about)
const platform = { total: 0, yes: 0, partial: 0, no: 0, planned: 0 };
for (const line of read(path.join(docs, "platform-tools.md")).split("\n")) {
  const m = line.match(/^\| (\d+) \|.*\| \*\*(yes|partial|no|planned)\b/);
  if (m) {
    platform.total += 1;
    platform[m[2]] += 1;
  }
}

// Session 35: the grid pages' written layer (docs/grids/<slug>.md) and their config (docs/grids/grids.json); every grid
// the config names must have its markdown, or the build fails
const gridConfig = JSON.parse(read(path.join(docs, "grids", "grids.json")));
const grids = {};
for (const g of gridConfig.grids) grids[g.slug] = read(path.join(docs, "grids", `${g.slug}.md`));

// session 314: the tables each grid's scoped chat reads, by rule (warehouse/chat/grid_tables.py writes the file)
const gridTables = JSON.parse(read(path.join(docs, "grids", "grid_tables.json")));
const out = {
  built_at: new Date().toISOString(),
  grid_config: gridConfig.grids,
  grid_tables: { read_at: gridTables.read_at, grids: gridTables.grids },
  grids,
  platform,
  analysis,
  digest_charts: digestChartRecords,
  findings_files: findingsFiles,
  sources: sources(),
  run_status_eia930: runStatus(),
  digests,
  weeklies,
  weekly_source: weeklySource,
  latest: read(path.join(digestDir, "latest.md")),
  datastandard: read(path.join(docs, "datastandard.md")),
  licenses: read(path.join(docs, "licenses.md")),   // session 471
  license_verdicts: licenseVerdicts(),
  methods,
};
fs.mkdirSync(path.join(here, "..", "content"), { recursive: true });
fs.writeFileSync(path.join(here, "..", "content", "docs.json"), JSON.stringify(out));
console.log(`build-content: ${Object.keys(grids).length} grid pages, ${Object.keys(digests).length} digests, ${Object.keys(weeklies).length} weekly briefs, ${Object.keys(methods).length} method documents, the data standard, ${Object.keys(analysis.weeks).length} analysis weeks`);

// Session 587: the held figures that show (docs/licenses_holds.csv, written by scripts/check-holds.mjs --csv), with each
// table's record in warehouse/metadata/license_status.csv, for /internal/holds only (lib/holds.ts). A file of its own,
// so no page for visitors imports it; a missing list is said on that page and does not stop the build.
const holds = holdsFromRepo();
fs.writeFileSync(path.join(here, "..", "content", "holds.json"), JSON.stringify(holds));
console.log(`build-content: holds.json, ${holds.unread ? `not read (${holds.unread})` : `${holds.rows.length} pages with held figures shown`}`);
