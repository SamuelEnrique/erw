// Energy Research Warehouse (ERW) site, ruling alternatives of /play/battery (session 7718, 17 November 2026;
// wip/alt-play-battery-* branches, not a default on main). The game's own rules (lib/battery.ts) run on its committed
// famous days (data/battery_levels.json), so that the figures under the other choice are pinned with the site's code:
// for each day, the perfect battery's score on Normal with the game's default settings, and with the settings named
// on the command line as kwh=..,kw=.. (none: the defaults).
//   node --import ./scripts/tsx-register.mjs scripts/alt-play-battery-figures.mjs [kwh=20]
import fs from "node:fs";

const B = await import("../lib/battery.ts");
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf8")).levels;
const over = Object.fromEntries(process.argv.slice(2).map((a) => a.split("=")).map(([k, v]) => [k, Number(v)]));
const settings = { ...B.DEFAULT_SETTINGS, ...over };
const out = { defaults: B.DEFAULT_SETTINGS, settings };
for (const l of levels) {
  const r = B.rulesOf(settings, "normal");
  out[l.slug] = { date: l.date, perfect: B.optimum(l.price, r).score, start: r.start };
}
process.stdout.write(JSON.stringify(out));
