// Energy Research Warehouse (ERW) site, session 11408 (chain 770, part C): the ready branch "the board's blank equities
// rows as one line" (lib/equities.ts oneLineEquities), on the board's real files and on a row holding a figure.
//   node --import ./scripts/events-page-register.mjs scripts/test-ready-board-equities-one-line.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const E = await import("../lib/equities.ts");
let bad = 0;
const check = (ok, words) => { if (!ok) { bad++; console.log(`FAIL ${words}`); } else console.log(`ok   ${words}`); };
const board = JSON.parse(fs.readFileSync(path.join(SITE, "data", "board.json"), "utf8"));
const eq = JSON.parse(fs.readFileSync(path.join(SITE, "data", "equities", "board.json"), "utf8"));
const merged = E.withEquities(board, eq);
const one = E.oneLineEquities(merged);
const before = merged.rows.filter((r) => r.group === "equities"), after = one.rows.filter((r) => r.group === "equities");
check(after.length === 1 && after[0].status === "not_held" && after[0].label === `${before.length} segment lines, none held`, "no row holds a figure: one line, with the count");
check(after[0].note.startsWith(`None of the group's ${before.length} rows holds a figure. `), "the line says why");
check(JSON.stringify(one.rows.filter((r) => r.group !== "equities")) === JSON.stringify(merged.rows.filter((r) => r.group !== "equities")), "the board's own rows as they were");
const withValue = { ...eq, rows: eq.rows.map((r, i) => (i === 0 ? { ...r, status: "ok", last: { t: "2026-11-27", v: 1 } } : r)) };
const m2 = E.withEquities(board, withValue);
check(E.oneLineEquities(m2) === m2, "a row holding a figure: the group is drawn row by row");
console.log(JSON.stringify({ rows_before: before.length, rows_after: after.length, note: after[0].note }));
process.exitCode = bad ? 1 : 0;
