// Energy Research Warehouse (ERW) site, ruling alternatives of /play/battery (session 7718, 17 November 2026;
// wip/alt-play-battery-* branches, not a default on main). The game's own rules (lib/battery.ts) run on its committed
// famous days (data/battery_levels.json), so that the figures under the other choice are pinned with the site's code.
// On wip/alt-play-battery-2: for each day, the perfect battery's score on Normal net of the starting charge, the start's
// value, and a play of no move (the start held all day) scored by simulate.
//   node --import ./scripts/tsx-register.mjs scripts/alt-play-battery-figures.mjs
import fs from "node:fs";

const B = await import("../lib/battery.ts");
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf8")).levels;
const out = {};
for (const l of levels) {
  const r = B.rulesOf(B.DEFAULT_SETTINGS, "normal");
  const em = B.emergencyOf(l.price, r).prices;
  out[l.slug] = { perfect: B.optimum(l.price, r).score, start: B.startValue(em, r), idle: B.simulate(l.price, l.price.map(() => 0), r).score, first: l.price[0] };
}
process.stdout.write(JSON.stringify(out));
