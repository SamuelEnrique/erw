// Energy Research Warehouse (ERW) site, session 7535 (chain 304): the home battery game's pieces this session changed,
// drawn to HTML with the site's own components, and checked.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-game-render.mjs
// 1. The decisions block (Decisions.tsx): 15 choices, each with its default, source and session; the five settings
//    marked editable and their defaults read from lib/battery.ts's SETTINGS.
// 2. The outage banner (faults row 5): with a need it names the dark house's charge; with the roof carrying the house
//    (need 0) it says so and names no "$0.00".
// 3. The perfect plan keeps no move that moves nothing (rows 3 and 4): on every frozen day and mode, each kept charge
//    or sale moves the charge by more than a nanowatt-hour; on the California duck day, Normal, the debrief's sale ends at
//    07:15 (it said 07:30).
// 4. The offer cap's date (row 6): the decisions block says "since 1 January 2022", and no piece says "since 2023".
// Exit 1 on any failure. No request, nothing written.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const lib = await import("../lib/battery.ts");
const G = await import("../app/play/battery/Game.tsx");
const D = await import("../app/play/battery/Decisions.tsx");
const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels
  .map((l) => ({ ...l, grid: l.grid ?? "ERCOT", tz: l.tz ?? "America/Chicago" }));
let bad = 0, n = 0;
const ok = (cond, what) => { n++; if (cond) console.log(`ok   ${what}`); else { bad++; console.log(`FAIL ${what}`); } };
const words = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();

// 1. the decisions block
const dec = renderToStaticMarkup(h(D.GameDecisions));
ok(D.GAME_DECISIONS.length === 15 && dec.includes('data-decision-count="15"'), "the decisions block holds 15 choices");
for (const d of D.GAME_DECISIONS) {
  ok(dec.includes(`data-decision-default="${d.key}"`) && dec.includes(`data-decision-source="${d.key}"`) && dec.includes(`data-decision-session="${d.key}"`), `decision ${d.key}: default, source and session drawn`);
}
const editable = D.GAME_DECISIONS.filter((d) => d.editable).map((d) => d.key).join(",");
ok(editable === "kwh,kw,rte,reserve,deg", `the five settings are the editable choices (${editable})`);
for (const k of ["kwh", "kw", "rte", "reserve", "deg"]) ok(D.GAME_DECISIONS.find((d) => d.key === k).source === lib.SETTINGS[k].source, `decision ${k}: its source is SETTINGS.${k}.source`);
ok(words(dec).includes("13.5 kWh (5 to 30)") && words(dec).includes("25 percent of the usable energy, 3.38 kWh"), "the settings' defaults as lib/battery.ts holds them");

// 2. the outage banner
const R = lib.rulesOf(lib.DEFAULT_SETTINGS, "hard", []);
const withNeed = words(renderToStaticMarkup(h(G.OutageBanner, { need: 3.1623, rules: R })));
ok(/the house needed in the whole outage \(\$105\.00\)/.test(withNeed), `banner with a need: ${withNeed.slice(-120)}`);
const RS = lib.rulesOf(lib.DEFAULT_SETTINGS, "hard", ["solar"]);
const roof = words(renderToStaticMarkup(h(G.OutageBanner, { need: 0, rules: RS })));
ok(roof.includes("Today the roof carries the house through the whole outage") && !roof.includes("$0.00"), "banner with the roof carrying the house: no $0.00");

// 3. no move that moves nothing, on every day and mode
const modes = [["easy", []], ["normal", []], ["hard", []], ["hard", ["solar"]]];
for (const l of levels) {
  for (const [d, add] of modes) {
    const r = lib.rulesOf(lib.DEFAULT_SETTINGS, d, add);
    if (add.length && !l.solar) continue;
    const sun = r.solarKw > 0 ? l.solar : undefined;
    const best = lib.optimum(l.price, r, sun);
    const sim = lib.simulate(l.price, best.actions, r, sun);
    const em = lib.emergencyOf(l.price, r);
    let idle = 0;
    best.actions.forEach((a, i) => {
      const out = em.outage && i >= em.outage.first && i <= em.outage.last;
      if (a !== 0 && !out && (sim.end === null || i <= sim.end) && Math.abs(sim.soc[i + 1] - sim.soc[i]) <= 1e-9) idle++;
    });
    ok(idle === 0, `${l.slug} ${d}${add.length ? "+solar" : ""}: the perfect plan keeps ${idle} moves that move nothing (score ${best.score.toFixed(4)} = simulate ${sim.score.toFixed(4)})`);
    ok(Math.abs(best.score - sim.score) < 1e-9, `${l.slug} ${d}${add.length ? "+solar" : ""}: the plan replays to its score`);
  }
}
const duck = levels.find((l) => l.slug === "caiso-duck");
const rn = lib.rulesOf(lib.DEFAULT_SETTINGS, "normal", []);
const plan = lib.optimum(duck.price, rn).actions;
const deb = words(renderToStaticMarkup(h(G.Debrief, { level: duck, result: { rules: rn }, best: plan, vppFirst: lib.vppHour(duck.price).first })));
ok(deb.includes("07:00 to 07:15") && !deb.includes("07:00 to 07:30"), "the duck day, Normal: the debrief's sale runs 07:00 to 07:15");

// 4. the offer cap's date
ok(words(dec).includes("since 1 January 2022"), "the decisions block dates the USD 5,000 cap from 1 January 2022");
const page = fs.readFileSync(new URL("../app/play/battery/page.tsx", import.meta.url), "utf-8");
ok(!page.includes("cap since 2023") && page.includes("offer cap since 1 January 2022"), "the rules section dates the cap from 1 January 2022");
ok(page.includes("<GameDecisions />"), "the page mounts the decisions block");

console.log(`\n${n - bad} of ${n} checks pass`);
process.exitCode = bad ? 1 : 0;
