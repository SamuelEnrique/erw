// Prints a reader's output compactly: node show.mjs <read.json> [rows] [--tips]
import fs from "node:fs";
const [file, rowsArg = "", flag = ""] = process.argv.slice(2);
const only = rowsArg && rowsArg !== "all" ? new Set(rowsArg.split(",").map(Number)) : null;
for (const r of JSON.parse(fs.readFileSync(file, "utf-8"))) {
  if (only && !only.has(r.row)) continue;
  console.log(`\n=== row ${r.row} @${r.width} ${r.path} ${r.error ? "ERROR " + r.error : ""}`);
  console.log(`  final ${r.finalUrl}; sideways ${JSON.stringify(r.sideways)}; inReview ${r.inReview}`);
  if (r.foldsAtOpen?.length) console.log(`  folds at open: ${r.foldsAtOpen.map((f) => (f.open ? "OPEN " : "closed ") + f.summary.slice(0, 50)).join(" | ")}`);
  if (r.found.length) console.log(`  found: ${r.found.join(" || ")}`);
  if (r.hiddenOnly.length) console.log(`  hidden only: ${r.hiddenOnly.join(" || ")}`);
  if (r.missing.length) console.log(`  MISSING: ${r.missing.join(" || ")}`);
  for (const n of r.notes) console.log(`  note: ${n}`);
  for (const c of r.collected) console.log(`  got: ${JSON.stringify(c).slice(0, flag === "--long" ? 4000 : 900)}`);
  const shown = r.tips.filter((t) => t.shown);
  const bad = shown.filter((t) => t.left < 0 || t.right > t.vw || t.sw > t.vw || t.cut);
  const notShown = r.tips.filter((t) => !t.shown);
  if (r.tips.length) console.log(`  tips: ${shown.length} shown of ${r.tips.length}; outside or cut ${bad.length}; not shown: ${[...new Set(notShown.map((t) => t.how + ":" + (t.label || "?")))].slice(0, 12).join(", ")}`);
  for (const t of bad) console.log(`   OUTSIDE ${t.how} ${t.label}: ${t.left}..${t.right} of ${t.vw}, top ${t.top} bottom ${t.bottom} of ${t.vh}, page ${t.sw}, cut ${t.cut}`);
  if (flag === "--tips") for (const t of shown.filter((t) => t.how === "hover")) console.log(`   tip ${t.label}: ${t.left}..${t.right}/${t.vw} :: ${t.words.slice(0, 300)}`);
  if (r.text) console.log(`  text: ${r.text.slice(0, 3000)}`);
}
