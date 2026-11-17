// Energy Research Warehouse (ERW) site, ruling alternatives of /board (session 7722, 17 November 2026; wip/alt-board-*
// branches, not a default on main). The board's own library (lib/board.ts) on its committed file (data/board.json), so that
// the figures under the other choice are pinned with the site's code. No held value is read or printed: held rows carry
// none, and only counts and public rows' ids are written.
// On wip/alt-board-2: the rows past their stale age that draw a 7-day average, and the window cells blanked on them.
//   node --import ./scripts/tsx-register.mjs scripts/alt-board-figures.mjs
import fs from "node:fs";

const B = await import("../lib/board.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/board.json", import.meta.url), "utf8"));
const ok = file.rows.filter((r) => r.status === "ok" && r.last);
const stale = ok.filter((r) => !B.windowsShown(r, file.built));
const withAvg7 = stale.filter((r) => r.avg7);
const cells = withAvg7.reduce((a, r) => a + (r.avg7 ? 1 : 0) + (r.avg30 ? 1 : 0) + (r.lo30 !== undefined ? 2 : 0), 0);
process.stdout.write(JSON.stringify({
  built: file.built, rows: file.rows.length, ok: ok.length, stale: stale.length, stale_with_avg7: withAvg7.length, cells_blanked: cells,
  fresh_drawn: ok.filter((r) => B.windowsShown(r, file.built) && r.avg7).length,
}));
