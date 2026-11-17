// Energy Research Warehouse (ERW) site, ruling alternatives of /supply (session 7726, 17 November 2026; wip/alt-supply-*
// branches, not a default on main). The page's own library (lib/supply.ts) run on its committed file (data/supply.json),
// so that the figures under the other choice are pinned with the site's code. On wip/alt-supply-1: the list "Changes
// outside the five years' range" with the floor (surprises), its length and its first lines, and the rows the floor leaves out.
//   node --import ./scripts/tsx-register.mjs scripts/alt-supply-figures.mjs
import fs from "node:fs";

const S = await import("../lib/supply.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/supply.json", import.meta.url), "utf8"));
const list = S.surprises(file);
const out = file.rows.filter((r) => r.status === "ok" && r.change?.outside && r.change.surprise !== null && S.belowFloor(r));
const words = (r) => ({ label: r.label, at: r.at, unit: r.unit, last: r.last?.v ?? null });
process.stdout.write(JSON.stringify({ built: file.built, length: list.length, first: list.slice(0, 2).map(words), left_out: out.map(words) }));
