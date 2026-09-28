// Energy Research Warehouse (ERW) site: bundle the committed markdown the site renders.
//
// Reads, from the repository (one level above site/):
//   docs/digest/YYYY-MM-DD.md and docs/digest/latest.md   the Energy Digest archive
//   docs/datastandard.md                                   the data standard
//   docs/methods/*.md                                      method documents
//   warehouse/metadata/sources.csv                         the source registry (session 21, /terms)
// and writes site/content/docs.json, which the pages import. Runs before
// `next dev` and `next build` (package.json predev and prebuild), so the
// content is part of the build and no page reads the file system at request
// time. A missing file fails the build: the site never shows a stand-in.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

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

const methods = {};
for (const f of fs.readdirSync(path.join(docs, "methods")).sort()) {
  if (f.endsWith(".md")) methods[f.replace(/\.md$/, "")] = read(path.join(docs, "methods", f));
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
function sources() {
  const [head, ...rows] = csvRows(read(path.join(repo, "warehouse", "metadata", "sources.csv")));
  return rows.filter((r) => r.length === head.length).map((r) => Object.fromEntries(head.map((h, i) => [h, r[i]])))
    .map(({ source, publisher, report, report_url, license, tables }) => ({ source, publisher, report, report_url, license, tables }));
}

const out = {
  built_at: new Date().toISOString(),
  sources: sources(),
  run_status_eia930: runStatus(),
  digests,
  weeklies,
  weekly_source: weeklySource,
  latest: read(path.join(digestDir, "latest.md")),
  datastandard: read(path.join(docs, "datastandard.md")),
  methods,
};
fs.mkdirSync(path.join(here, "..", "content"), { recursive: true });
fs.writeFileSync(path.join(here, "..", "content", "docs.json"), JSON.stringify(out));
console.log(`build-content: ${Object.keys(digests).length} digests, ${Object.keys(weeklies).length} weekly briefs, ${Object.keys(methods).length} method documents, the data standard`);
