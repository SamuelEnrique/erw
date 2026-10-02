// Energy Research Warehouse (ERW) site, session 66: the server's scorer against lib/battery.ts, called directly.
//
//   node --import ./scripts/alias-register.mjs scripts/check-scorer.mjs
//
// No site, no network, no database: it imports lib/game.ts itself (the module /api/play/finish and /api/play/score
// call) and runs scoreOn, the function that scores a posted play, on every famous day under each difficulty and a
// custom Hard battery, and compares its score, its perfect-foresight score and its preset with lib/battery.ts's
// simulate, optimum and presetOf under the same rules. The rooftop add-on is checked on each famous day that holds a
// solar shape, and on a toy day with a toy shape (a test day, never a real one). Refusals: the roof on a level without
// a shape, an add-on off Hard, an unknown add-on, bad actions, bad settings. Posting nothing: the routes' database
// write is not called. Exits 1 on any mismatch. tests/test_session66.py runs it.
import fs from "node:fs";
import { DEFAULT_SETTINGS, LIGHTS_OUT, optimum, presetOf, RULES_VERSION, rulesOf, simulate, validSolar } from "../lib/battery.ts";
import { scoreOn } from "../lib/game.ts";

const levels = JSON.parse(fs.readFileSync(new URL("../data/battery_levels.json", import.meta.url), "utf-8")).levels;
let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const c = (v) => Math.round(v * 10_000) / 10_000;
const custom = { kwh: 10, kw: 4, rte: 0.88, reserve: 0.3, deg: 0.15 };
// a toy level: twelve intervals, a toy solar shape (test data, labeled so; no real day carries it)
const toy = { slug: "toy", date: "toy", title: "a toy day (test data)", why: "", table: "", ts_utc: [], source: [], source_url: [], retrieved_at: "",
  price: [15, 12, 10, 14, 300, 900, 450, 200, 30, 25, 20, 18], solar: [0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.5, 0.2, 0.05] };

function agree(level, label, settings, difficulty, addons, actions) {
  const rules = rulesOf(settings, difficulty, addons);
  const sun = rules.solarKw > 0 ? level.solar : undefined;
  const want = simulate(level.price, actions, rules, sun), plan = optimum(level.price, rules, sun);
  const got = scoreOn(level, { level: level.date, actions, settings, difficulty, addons });
  const ok = typeof got !== "string" && got.score === c(want.score) && got.optimal === c(plan.score) && got.cash === c(want.cash) && got.wear === c(want.wear) && got.bonus === c(want.bonus)
    && got.solar === c(want.solar) && got.penalty === c(want.penalty) && got.preset === presetOf(settings, difficulty, addons) && got.preset.endsWith(`-${RULES_VERSION}`);
  check(ok, `${level.date} ${label}: the server scores ${typeof got === "string" ? got : got.score} (lib ${want.score.toFixed(4)}), perfect ${typeof got === "string" ? "" : got.optimal} (lib ${plan.score.toFixed(4)}), preset ${typeof got === "string" ? "" : got.preset}${want.why ? `, ends ${want.why}` : ""}`);
}

for (const l of levels) {
  const n = l.price.length;
  // three plays per preset: the perfect plan, a plain rule (charge the first six hours, sell above 100 USD/MWh), and
  // one that sells from the start (on Hard it reaches the outage at its reserve)
  for (const [label, settings, difficulty, addons] of [
    ["easy", DEFAULT_SETTINGS, "easy", []], ["normal", DEFAULT_SETTINGS, "normal", []], ["hard", DEFAULT_SETTINGS, "hard", []], ["hard, custom battery", custom, "hard", []],
    ...(validSolar(l.solar, n) ? [["hard with rooftop solar", DEFAULT_SETTINGS, "hard", ["solar"]]] : []),
  ]) {
    const rules = rulesOf(settings, difficulty, addons);
    agree(l, `${label}, the perfect plan`, settings, difficulty, addons, optimum(l.price, rules, rules.solarKw > 0 ? l.solar : undefined).actions);
    agree(l, `${label}, a plain rule`, settings, difficulty, addons, l.price.map((p, i) => (i < 24 ? 1 : p > 100 ? -1 : 0)));
    agree(l, `${label}, selling from the start`, settings, difficulty, addons, l.price.map(() => -1));
  }
  if (!validSolar(l.solar, n)) {
    const r = scoreOn(l, { level: l.date, actions: l.price.map(() => 0), difficulty: "hard", addons: ["solar"] });
    check(typeof r === "string" && r.includes("rooftop solar is not available") && r.includes(l.date), `${l.date}: no solar shape held, so the roof is refused, not filled ("${r}")`);
  }
}
// the toy day: the roof on, and a play that goes dark (the penalty in the server's score)
{
  const zero = { ...DEFAULT_SETTINGS, kwh: 5, reserve: 0 };
  agree(toy, "hard with rooftop solar, the perfect plan", DEFAULT_SETTINGS, "hard", ["solar"], optimum(toy.price, rulesOf(DEFAULT_SETTINGS, "hard", ["solar"]), toy.solar).actions);
  agree(toy, "hard with rooftop solar, idle", DEFAULT_SETTINGS, "hard", ["solar"], toy.price.map(() => 0));
  agree(toy, "hard, sold out before the outage", zero, "hard", [], toy.price.map(() => -1));
  const dark = scoreOn(toy, { level: "toy", actions: toy.price.map(() => -1), settings: zero, difficulty: "hard" });
  check(typeof dark !== "string" && dark.penalty === c((4 * 0.375 * LIGHTS_OUT.usdPerMwh) / 1000), `the server's score carries the lights-out charge: USD ${typeof dark === "string" ? dark : dark.penalty}`);
  const refuse = (body, has, what) => { const r = scoreOn(toy, { level: "toy", actions: toy.price.map(() => 0), ...body }); check(typeof r === "string" && r.includes(has), `${what}: refused ("${r}")`); };
  refuse({ difficulty: "normal", addons: ["solar"] }, "only on Hard", "an add-on on Normal");
  refuse({ difficulty: "hard", addons: ["wind"] }, "addons:", "an unknown add-on");
  refuse({ difficulty: "hard", addons: "solar" }, "addons:", "add-ons that are not a list");
  refuse({ difficulty: "hard", addons: ["solar", "solar"] }, "addons:", "an add-on twice");
  refuse({ actions: [1, 0] }, "actions:", "short actions");
  refuse({ settings: { ...DEFAULT_SETTINGS, kwh: 99 } }, "settings:", "a setting out of range");
  refuse({ difficulty: "insane" }, "difficulty:", "an unknown difficulty");
  const plain = scoreOn(toy, { level: "toy", actions: toy.price.map(() => 0) });
  check(typeof plain !== "string" && plain.preset === "normal:13.5-5-90-v4" && plain.addons.length === 0, `a play without settings is Normal with the default battery: ${typeof plain === "string" ? plain : plain.preset}`);
}
console.log(bad ? `${bad} FAILED` : "the server's scorer and lib/battery.ts agree under v4");
process.exit(bad ? 1 : 0);
