// Energy Research Warehouse (ERW) site, session 469: every impact read of the policy monitor against the tables it cites,
// with the page's own function (lib/policyreads.ts, citeOf), so that the review and the page cannot disagree.
//
//   node --import ./scripts/alias-register.mjs scripts/audit-policy-reads.mjs <reads.json> <out.csv>
//
// <reads.json> is {"read_at_utc": ..., "rows": [...]}: the rows of policy_reads as the live set serves them (event_id,
// event_date and the extra fields action_event_id, title, agency, significance, plain_read, what_changes, timeline).
// The ERW's table names are coverage.csv's. Writes one CSV row a read and prints the counts as one JSON line. No request,
// no model.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const { citeOf } = await import("../lib/policyreads.ts");

const [src, out] = process.argv.slice(2);
if (!src || !out) { console.error("usage: audit-policy-reads.mjs <reads.json> <out.csv>"); process.exit(2); }
const { read_at_utc, rows } = JSON.parse(fs.readFileSync(src, "utf8"));
const coverage = fs.readFileSync(path.join(here, "..", "..", "warehouse", "metadata", "coverage.csv"), "utf8").split(/\r?\n/);
const head = coverage[0].split(",");
const ti = head.indexOf("table");
const tables = coverage.slice(1).filter(Boolean).map((l) => l.split(",")[ti]).filter(Boolean);

const q = (s) => `"${String(s ?? "").replace(/"/g, '""')}"`;
const lines = [["read_event_id", "action_event_id", "event_date", "agency", "significance", "cites", "mark", "figures", "tables_named"].join(",")];
const n = { reads: rows.length, text: 0, table: 0, none: 0, figures: 0, blank: 0 };
for (const r of [...rows].sort((a, b) => String(a.event_id).localeCompare(String(b.event_id)))) {
  const c = citeOf(r, tables);
  n[c.kind] += 1;
  n.figures += c.figures.length;
  if (!r.plain_read && !r.what_changes && !r.timeline) n.blank += 1;
  const mark = c.kind === "none" ? "no figure" : c.kind === "text" ? "the action's own text" : "an ERW table";
  lines.push([q(r.event_id), q(r.action_event_id), q(String(r.event_date ?? "").slice(0, 10)), q(r.agency), q(r.significance), c.kind, q(mark), q(c.figures.join("; ")), q(c.tables.join("; "))].join(","));
}
fs.writeFileSync(out, lines.join("\n") + "\n");
console.log(JSON.stringify({ read_at_utc, tables_known: tables.length, ...n }));
