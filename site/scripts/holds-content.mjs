// Energy Research Warehouse (ERW) site, session 587: the list of held figures that show, for /internal/holds.
//
//   node scripts/holds-content.mjs [<holds.csv> [<license_status.csv>]]    prints the JSON the page reads
//
// scripts/check-holds.mjs --csv writes docs/licenses_holds.csv on a build: one line a page that draws a figure of a
// table held for a license without the words "license needed" (session 505). scripts/build-content.mjs calls
// holdsContent() before every build and writes site/content/holds.json, which lib/holds.ts imports for the internal
// page. Each row is the CSV's own line, its cells as written (nothing summed, nothing reworded), with each table it names
// looked up in warehouse/metadata/license_status.csv for its status and verdict. No figure of a held table is read here:
// the CSV holds addresses, tables, grids and a count of figures, never a figure. A missing or unreadable file is said
// on the page, and the build goes on: the list is a check's output, not a page for visitors.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
export const HOLDS_CSV = "docs/licenses_holds.csv";
export const STATUS_CSV = "warehouse/metadata/license_status.csv";
// the columns check-holds.mjs writes, in its order
export const HOLDS_COLUMNS = ["page", "figures", "kinds", "tables", "grids", "day"];

/** The lines of a CSV as arrays of cells: quoted cells with doubled quotes, blank lines dropped. */
export function csvRows(text) {
  const rows = [];
  for (const line of text.replace(/^﻿/, "").split(/\r?\n/)) {
    if (!line.trim()) continue;
    const cells = [];
    let cur = "", q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (q) { if (c === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (c === '"') q = false; else cur += c; }
      else if (c === '"') q = true;
      else if (c === ",") { cells.push(cur); cur = ""; }
      else cur += c;
    }
    cells.push(cur);
    rows.push(cells);
  }
  return rows;
}

/** license_status.csv as table -> { status, verdict, from, publishers } (a last column holding commas kept whole). */
export function statusOf(text) {
  const [head, ...body] = csvRows(text);
  if (!head || !head.includes("table") || !head.includes("status")) throw new Error(`its header is "${(head ?? []).join(",")}"`);
  const out = {};
  for (const r of body) {
    if (r.length < head.length) continue;
    const cells = [...r.slice(0, head.length - 1), r.slice(head.length - 1).join(",")];
    const o = Object.fromEntries(head.map((h, i) => [h, cells[i]]));
    out[o.table] = { status: o.status ?? "", verdict: o.verdict ?? "", from: o.from ?? "", publishers: o.publishers ?? "" };
  }
  return out;
}

/**
 * The page's content from the two files' texts (null for a file not found). Rows are the CSV's lines in its order, each
 * cell as written; `tables` gives each table a row names its record in license_status.csv (null when it has none).
 */
export function holdsContent(holdsText, statusText, builtAt = new Date().toISOString()) {
  const out = { built_at: builtAt, source: HOLDS_CSV, status_source: STATUS_CSV, columns: HOLDS_COLUMNS, unread: null, status_unread: null, rows: [], tables: {} };
  if (holdsText === null) { out.unread = `${HOLDS_CSV} was not found (scripts/check-holds.mjs --csv writes it)`; return out; }
  const [head, ...body] = csvRows(holdsText);
  if (!head || head.join(",") !== HOLDS_COLUMNS.join(",")) {
    out.unread = `the header of ${HOLDS_CSV} is "${(head ?? []).join(",")}", not "${HOLDS_COLUMNS.join(",")}"`;
    return out;
  }
  const bad = body.findIndex((r) => r.length !== HOLDS_COLUMNS.length);
  if (bad >= 0) { out.unread = `line ${bad + 2} of ${HOLDS_CSV} has ${body[bad].length} cells, not ${HOLDS_COLUMNS.length}`; return out; }
  out.rows = body.map((r) => Object.fromEntries(HOLDS_COLUMNS.map((h, i) => [h, r[i]])));
  let status = {};
  if (statusText === null) out.status_unread = `${STATUS_CSV} was not found`;
  else {
    try { status = statusOf(statusText); } catch (e) { out.status_unread = `${STATUS_CSV} could not be read: ${e.message}`; }
  }
  for (const r of out.rows) for (const t of tablesOf(r.tables)) if (!(t in out.tables)) out.tables[t] = status[t] ?? null;
  return out;
}

/** The tables a row names, as check-holds.mjs joins them ("; "). */
export function tablesOf(cell) {
  return cell.split(";").map((x) => x.trim()).filter(Boolean);
}

/** The two files read from the repository, as build-content.mjs reads them. */
export function holdsFromRepo(holdsFile = path.join(repo, HOLDS_CSV), statusFile = path.join(repo, STATUS_CSV)) {
  const rd = (f) => (fs.existsSync(f) ? fs.readFileSync(f, "utf-8") : null);
  return holdsContent(rd(holdsFile), rd(statusFile));
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  const a = process.argv.slice(2);
  const c = holdsFromRepo(a[0] ? path.resolve(a[0]) : undefined, a[1] ? path.resolve(a[1]) : undefined);
  console.log(JSON.stringify(c));
}
