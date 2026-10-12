// Session 200, read only: what /internal/waits lists, built by the page's own script from a folder of reports.
//   node waits_list.mjs <site/scripts/build-waits.mjs> <repo folder holding archive/sessions> <out.json> <out.txt>
import fs from "node:fs";
import { pathToFileURL } from "node:url";

const [script, repo, outJson, outTxt] = process.argv.slice(2);
const { build } = await import(pathToFileURL(script).href);
const made = build(repo);
fs.writeFileSync(outJson, JSON.stringify(made, null, 1));
const lines = [];
lines.push(`marker: last_answered ${made.marker.last} (${made.marker.error ?? "read"}); reports after: ${made.counts.after}; listed: ${made.counts.listed}; items: ${made.counts.items}`);
for (const r of [...made.reports].sort((a, b) => a.order - b.order)) {
  lines.push("");
  lines.push(`===== ${r.id} | ${r.date ?? "no date"} | ${r.heading} | ${r.waits.length} items`);
  for (const w of r.waits) {
    lines.push(`--- ${r.id}:${w.line} [${w.kind}] section: ${w.section}`);
    lines.push(w.md);
  }
}
fs.writeFileSync(outTxt, lines.join("\n"));
console.log(lines[0]);
for (const r of [...made.reports].sort((a, b) => a.order - b.order)) console.log(`${r.id}: ${r.waits.length}`);
