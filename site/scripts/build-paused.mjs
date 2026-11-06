// Energy Research Warehouse (ERW) site, session 2401: the paused publishers, as the site's own file.
//
//   node scripts/build-paused.mjs            (runs before `next build` and `next dev`: package.json prebuild and predev)
//
// Reads warehouse/metadata/paused_sources.csv (one row per publisher the ERW never requests: MISO since 4 October 2026,
// the Virginia State Corporation Commission since 10 October 2026; only a person adds or removes a row) and writes
// site/data/policy/paused.json, which the policy monitor reads so that a paused source is shown as "paused" in place,
// with the file's reason, date and condition on hover, whatever the data machine's refresh file says of it. The file
// is committed beside the other data/policy files and written again here from the CSV, so that it never drifts from
// the record: a build with no CSV fails (the site never shows a stand-in). No request; the standard library only.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, "..", "..");
const CSV = path.join(repo, "warehouse", "metadata", "paused_sources.csv");
const OUT = path.join(here, "..", "data", "policy", "paused.json");

/** RFC 4180: fields in double quotes may hold commas, newlines and doubled quotes. */
export function parseCsv(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else quoted = false; }
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = ""; rows.push(row); row = [];
    } else field += c;
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  const [head, ...body] = rows.filter((r) => r.length > 1 || (r.length === 1 && r[0] !== ""));
  return body.map((r) => Object.fromEntries(head.map((h, i) => [h.trim(), (r[i] ?? "").trim()])));
}

/** The file the page reads, from the CSV's rows: the key is the row's scope (miso, vascc), as the refresh file and the grids file key them. */
export function pausedFromCsv(text) {
  const sources = parseCsv(text).filter((r) => r.scope && r.publisher).map((r) => ({
    key: r.scope, publisher: r.publisher, paused_on: r.paused_on, reason: r.reason, terms_url: r.terms_url || null,
    terms_quoted: r.terms_quoted || null, ruled_by: r.ruled_by || null, until: r.until || null, note: r.note || null,
  }));
  return { from: "warehouse/metadata/paused_sources.csv", sources };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (!fs.existsSync(CSV)) { console.error(`build-paused: missing ${path.relative(repo, CSV)}`); process.exit(1); }
  const out = pausedFromCsv(fs.readFileSync(CSV, "utf-8"));
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(out, null, 1) + "\n");
  console.log(`build-paused: ${out.sources.length} paused sources (${out.sources.map((s) => s.key).join(", ")}) -> ${path.relative(path.join(here, ".."), OUT)}`);
}
