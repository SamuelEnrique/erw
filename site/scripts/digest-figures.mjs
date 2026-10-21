// Energy Research Warehouse (ERW) site, session 402: every figure of every Digest, with the key the page gives it
// (lib/digest.ts), as JSON, for scripts/check_digest.py to trace to the warehouse. Reads docs/digest/<date>.md and the
// chart records beside them (docs/digest/charts/<date>.json, where its picture is held, as scripts/build-content.mjs
// reads them); needs no build and no network.
//
//   node --import ./scripts/alias-register.mjs scripts/digest-figures.mjs [out.json] [--now YYYY-MM-DD]
//
// --now: the day the holds are read for (lib/license.ts), today (UTC) when not given.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const { digestFigures } = await import("../lib/digest.ts");
const dir = path.join(here, "..", "..", "docs", "digest");
const args = process.argv.slice(2);
const at = args.indexOf("--now");
const now = at >= 0 ? new Date(`${args[at + 1]}T12:00:00Z`) : new Date();
const outFile = args.find((a, i) => !a.startsWith("--") && (at < 0 || i !== at + 1));

const out = { written_utc: new Date().toISOString(), holds_on: now.toISOString().slice(0, 10), digests: {} };
for (const f of fs.readdirSync(dir).sort()) {
  const m = /^(\d{4}-\d{2}-\d{2})\.md$/.exec(f);
  if (!m) continue;
  const date = m[1];
  const rec = path.join(dir, "charts", `${date}.json`);
  let chart = null;
  if (fs.existsSync(rec) && fs.existsSync(path.join(dir, "charts", `${date}.png`))) {
    const r = JSON.parse(fs.readFileSync(rec, "utf-8"));
    chart = { table: r.table ?? "", numbers: r.numbers && typeof r.numbers === "object" ? r.numbers : {}, flag: r.flag ?? null };
  }
  const md = fs.readFileSync(path.join(dir, f), "utf-8").replace(/\r\n/g, "\n");
  out.digests[date] = { figures: digestFigures(md, date, chart, now), chart: chart ? { table: chart.table, numbers: chart.numbers,
    entity: chart.flag?.series?.entity ?? "", variable: chart.flag?.series?.variable ?? "", date: chart.flag?.date ?? "",
    old_record_date: chart.flag?.compared?.old_record_date ?? "" } : null };
}
const text = JSON.stringify(out, null, 1);
if (outFile) fs.writeFileSync(outFile, text + "\n");
else process.stdout.write(text + "\n");
