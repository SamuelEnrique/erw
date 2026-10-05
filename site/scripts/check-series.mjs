// Energy Research Warehouse (ERW) site, session 121: every chart Ask ERCOT would draw, against the rows it fetched.
//
//   node scripts/check-series.mjs <records.jsonl> [more.jsonl ...]
//
// The records are answers as the loop returns them (warehouse/chat/eval/results/*.jsonl, or the site's own answers
// saved one per line). For each series of each answer: the points the page's chart draws (lib/chat/series.ts
// chartPoints, the function the page calls) are set against the series' rows, key by key and value by value
// (pointsAreRows), and the loop's own check of the series against the tool's rows is read (check.same). A chart that
// shows a point no row holds, or leaves a row out without naming it, fails. No model call, no request. Exit 1 on a
// failure, 2 when there is nothing to check.
import fs from "node:fs";
import { chartPoints, isDrawn, pointsAreRows } from "../lib/chat/series.ts";

const files = process.argv.slice(2);
if (!files.length) { console.error("usage: node scripts/check-series.mjs <records.jsonl> [more.jsonl ...]"); process.exit(2); }
let answers = 0, series = 0, charts = 0, rows = 0, points = 0, undrawn = 0, bad = 0, unchecked = 0;
for (const f of files) {
  for (const line of fs.readFileSync(f, "utf8").split("\n")) {
    if (!line.trim()) continue;
    const rec = JSON.parse(line);
    if (!(rec.series ?? []).length) continue;
    answers += 1;
    for (const s of rec.series) {
      series += 1;
      const d = chartPoints(s.rows);
      rows += s.rows.length;
      undrawn += d.undrawn.length;
      if (isDrawn(s.kind, d)) { charts += 1; points += d.points.length; }
      const ok = pointsAreRows(s.rows, d);
      if (!s.check) unchecked += 1;
      if (!ok || (s.check && !s.check.same)) {
        bad += 1;
        console.log(`FAIL ${rec.id ?? ""} ${s.result_id} (${s.table}): ${!ok ? "the chart's points are not the series' rows" : "the series is not the rows the tool returned"}`);
      }
    }
  }
}
console.log(`${answers} answers with a series; ${series} series, ${rows} rows fetched; ${charts} drawn as a line chart, ${points} points; ${undrawn} rows named as not drawn; ` +
  `${unchecked} series without the loop's own check (answers from before session 121); ${bad} failed`);
process.exit(bad ? 1 : series ? 0 : 2);
