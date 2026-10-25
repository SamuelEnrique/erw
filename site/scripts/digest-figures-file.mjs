// Energy Research Warehouse (ERW) site, session 804: the figures of one Digest markdown file, with the key the page gives
// each (lib/digest.ts), as the JSON scripts/check_digest.py --figures reads. For a section built outside docs/digest/
// (a proof on a saved day's tables, a dry run under runs/): digest-figures.mjs reads only docs/digest/.
//
//   node --import ./scripts/alias-register.mjs scripts/digest-figures-file.mjs <file.md> <YYYY-MM-DD> <out.json> [--now YYYY-MM-DD]
//
// No chart record is read (the chart's figures are the record's, docs/digest/charts/<date>.json; a file outside the
// archive has none). Needs no build and no network.
import fs from "node:fs";
const { digestFigures } = await import("../lib/digest.ts");
const args = process.argv.slice(2);
const at = args.indexOf("--now");
const now = at >= 0 ? new Date(`${args[at + 1]}T12:00:00Z`) : new Date();
const rest = args.filter((a, i) => !a.startsWith("--") && (at < 0 || i !== at + 1));
const [md, date, out] = rest;
if (!md || !date || !out) {
  console.error("usage: digest-figures-file.mjs <file.md> <YYYY-MM-DD> <out.json> [--now YYYY-MM-DD]");
  process.exit(2);
}
const figs = digestFigures(fs.readFileSync(md, "utf-8"), date, null, now);
const data = { written_utc: new Date().toISOString(), holds_on: now.toISOString().slice(0, 10), digests: { [date]: { figures: figs, chart: null } } };
fs.writeFileSync(out, JSON.stringify(data, null, 1));
console.log(`${figs.length} figures of ${date} in ${md}`);
for (const f of figs) console.log(`  ${f.key} = ${f.raw}${f.held ? " (held)" : ""}`);
