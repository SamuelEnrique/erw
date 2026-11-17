// Energy Research Warehouse (ERW) site, ruling alternatives of /board (session 7722, 17 November 2026; wip/alt-board-*
// branches, not a default on main). The board's own library (lib/board.ts) on its committed file (data/board.json), so that
// the figures under the other choice are pinned with the site's code. No held value is read or printed: the strip draws
// public rows only (status ok).
// On wip/alt-board-4: the strip's highest and lowest in their year's range, daily series only (rangeExtremes), beside the
// same rule with any step (main's), recomputed here from main's filter.
//   node --import ./scripts/tsx-register.mjs scripts/alt-board-figures.mjs
import fs from "node:fs";

const B = await import("../lib/board.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const cell = (r) => ({ id: r.id, label: r.label, freq: r.freq, v: r.last.v, t: r.last.t, pos: r.range.pos });
const BENCH = ["power", "gas", "crude", "products", "metals", "rates", "carbon"];
const mainRows = file.rows.filter((r) => r.status === "ok" && !r.formula && BENCH.includes(r.group) && r.range && r.range.pos !== null && (r.tags.scope ?? "main") === "main" && (r.tags.kind ?? "daily") === "daily")
  .sort((a, b) => b.range.pos - a.range.pos);
const rx = B.rangeExtremes(file);
process.stdout.write(JSON.stringify({
  built: file.built, main: { candidates: mainRows.length, top: cell(mainRows[0]), bottom: cell(mainRows.at(-1)) },
  branch: { candidates: mainRows.filter((r) => r.freq === "D").length, top: cell(rx.top), bottom: cell(rx.bottom) },
}));
