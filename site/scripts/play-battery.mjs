// Energy Research Warehouse (ERW) site, session 38: one scripted play of the home battery game through the server
// routes, marked as an ERW check (header x-erw-check: 1, so it stays off the leaderboard and out of the research data).
//
//   node scripts/play-battery.mjs [base-url]
//
// Plays a famous day (2023-08-10) with the perfect-foresight actions and today's level with a plain rule (charge from
// the day's start for four hours, sell in its last four), and checks: /api/play/finish scores and stores each play, the
// server's score equals lib/battery.ts's on the same prices, /api/play/score stores the score and answers with the
// level's leaderboard, and bad input is refused. Exits 1 on any failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DEFAULT_SETTINGS, optimum, presetOf, rulesOf, simulate } from "../lib/battery.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const levels = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "battery_levels.json"), "utf-8")).levels;
const H = { "Content-Type": "application/json", "x-erw-check": "1" };
let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const post = async (route, body) => {
  const r = await fetch(`${base}${route}`, { method: "POST", headers: H, body: JSON.stringify(body) });
  return [r.status, await r.json()];
};

// 1. a famous day, the optimum's actions
const heat = levels.find((l) => l.date === "2023-08-10");
const best = optimum(heat.price);
let [s, j] = await post("/api/play/finish", { level: heat.date, actions: best.actions });
check(s === 200 && j.stored === true, `finish ${heat.date}: HTTP ${s}, stored ${j.stored}`);
check(Math.abs(j.score - Math.round(best.score * 1e4) / 1e4) < 1e-9 && Math.abs(j.optimal - j.score) < 1e-9, `finish ${heat.date}: server score ${j.score} = optimum ${best.score.toFixed(4)}`);
[s, j] = await post("/api/play/score", { level: heat.date, actions: best.actions, nickname: "ERWcheck" });
check(s === 200 && Array.isArray(j.top) && !j.top.some((r) => r.nickname === "ERWcheck"), `score ${heat.date}: HTTP ${s}, leaderboard of ${j.top?.length} rows, the check row left out`);

// 2. today's level, from the page
const html = await fetch(`${base}/play/battery?more=1`).then((r) => r.text());  // session 63: the full game names the day; the simple page does not
const today = /the operating day (?:<!-- -->)?(\d{4}-\d{2}-\d{2})/.exec(html)?.[1];
check(Boolean(today), `today's level on the page: ${today}`);
if (today) {
  const n = 96;
  const actions = Array.from({ length: n }, (_, i) => (i < 16 ? 1 : i >= n - 16 ? -1 : 0));
  [s, j] = await post("/api/play/finish", { level: today, actions });
  check(s === 200 && j.stored === true && typeof j.score === "number" && j.optimal >= j.score, `finish ${today}: HTTP ${s}, score ${j.score}, perfect foresight ${j.optimal}`);
  [s, j] = await post("/api/play/score", { level: today, actions });
  check(s === 200 && j.level === today, `score ${today} without a nickname: HTTP ${s}`);
}

// 3. refusals
[s, j] = await post("/api/play/score", { level: heat.date, actions: best.actions, nickname: "no spaces" });
check(s === 400, `bad nickname refused: HTTP ${s} (${j.error})`);
[s, j] = await post("/api/play/finish", { level: heat.date, actions: [1, 0] });
check(s === 400, `short actions refused: HTTP ${s} (${j.error})`);
[s, j] = await post("/api/play/finish", { level: "1999-01-01", actions: best.actions });
check(s === 400, `unknown level refused: HTTP ${s} (${j.error})`);
// the local rule check: the same actions scored here
check(Math.abs(simulate(heat.price, best.actions).score - best.score) < 1e-9, "lib/battery.ts replays the optimum");

// 4. session 50: one scripted play per difficulty, and a custom battery on Hard: the server rescoring under each preset
// equals lib/battery.ts's, the optimum too, and the stored preset is the one played
const custom = { kwh: 10, kw: 4, rte: 0.88, reserve: 0.3, deg: 0.15 };
for (const [label, settings, difficulty] of [["easy", DEFAULT_SETTINGS, "easy"], ["normal", DEFAULT_SETTINGS, "normal"], ["hard", DEFAULT_SETTINGS, "hard"], ["hard, custom", custom, "hard"]]) {
  const r = rulesOf(settings, difficulty);
  const plan = optimum(heat.price, r);
  const greedy = heat.price.map((p, i) => (i < 24 ? 1 : p > 100 ? -1 : 0));  // charge the first six hours, sell above 100 USD/MWh
  const want = simulate(heat.price, greedy, r).score;
  [s, j] = await post("/api/play/finish", { level: heat.date, actions: greedy, settings, difficulty });
  const preset = presetOf(settings, difficulty);
  check(s === 200 && j.stored === true && Math.abs(j.score - Math.round(want * 1e4) / 1e4) < 1e-9 && Math.abs(j.optimal - Math.round(plan.score * 1e4) / 1e4) < 1e-9 && j.preset === preset,
    `${label}: finish scored ${j.score} (lib ${want.toFixed(4)}), perfect ${j.optimal} (lib ${plan.score.toFixed(4)}), preset ${j.preset}`);
  [s, j] = await post("/api/play/score", { level: heat.date, actions: greedy, settings, difficulty });
  check(s === 200 && j.preset === preset && Array.isArray(j.top) && j.top.every((x) => x.preset === preset), `${label}: score stored under ${preset}; leaderboard of ${j.top?.length} rows, all of that preset`);
}
[s, j] = await post("/api/play/finish", { level: heat.date, actions: best.actions, settings: { ...DEFAULT_SETTINGS, kwh: 99 }, difficulty: "hard" });
check(s === 400, `a setting out of range refused: HTTP ${s} (${j.error})`);
[s, j] = await post("/api/play/finish", { level: heat.date, actions: best.actions, difficulty: "insane" });
check(s === 400, `an unknown difficulty refused: HTTP ${s} (${j.error})`);
// 5. session 56: one scripted play on each California day (CAISO SP15), the optimum's actions on Normal with the default
// battery: the server finds the level, rescoring equals lib/battery.ts's optimum, the score is stored under its preset,
// and the leaderboard's read route answers for the level
for (const l of levels.filter((x) => x.grid === "CAISO")) {
  const o = optimum(l.price);
  [s, j] = await post("/api/play/finish", { level: l.date, actions: o.actions });
  check(s === 200 && j.stored === true && Math.abs(j.score - Math.round(o.score * 1e4) / 1e4) < 1e-9 && Math.abs(j.optimal - j.score) < 1e-9,
    `CAISO ${l.slug} ${l.date}: finish scored ${j.score}, the optimum ${o.score.toFixed(4)} USD`);
  [s, j] = await post("/api/play/score", { level: l.date, actions: o.actions, nickname: "ERWcheck" });
  check(s === 200 && j.preset === presetOf(DEFAULT_SETTINGS, "normal") && Array.isArray(j.top) && !j.top.some((r) => r.nickname === "ERWcheck"),
    `CAISO ${l.slug}: score stored under ${j.preset}; leaderboard of ${j.top?.length} rows, the check row left out`);
  const r = await fetch(`${base}/api/play/top?${new URLSearchParams({ level: l.date, preset: presetOf(DEFAULT_SETTINGS, "hard") })}`);
  const t = await r.json();
  check(r.status === 200 && t.level === l.date && Array.isArray(t.top), `CAISO ${l.slug}: /api/play/top for Hard answers ${r.status} with ${t.top?.length} rows`);
  const h = optimum(l.price, rulesOf(DEFAULT_SETTINGS, "hard"));
  console.log(`     ${l.date}: perfect foresight ${o.score.toFixed(4)} USD on Normal, ${h.score.toFixed(4)} USD on Hard (default battery)`);
}
console.log(bad ? `${bad} FAILED` : "scripted play: every check passed");
process.exit(bad ? 1 : 0);
