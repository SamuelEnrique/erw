// Energy Research Warehouse (ERW) site, session 47: the event study estimator (lib/eventstudy.ts).
//
//   node scripts/test-eventstudy.mjs      (tests/test_session47.py runs this)
//
// 1. A synthetic panel with a known effect: baseline years 2019 and 2020 (level -5 and +5 about the mean), 2021 the
//    event year, a day-of-week pattern, and a per-day event effect of 20 + k; with no noise every effect is recovered
//    exactly; a constant effect of 25 is recovered by the pooled indicator; with noise the intervals cover the truth.
// 2. Parity: where the warehouse files are on this machine, every daily and pooled estimate, standard error and
//    counterfactual mean of warehouse/output/event_study_estimates.csv (Python) equals this estimator's on the same
//    rows of event_window_daily, to 1e-6 relative.
// Exits 1 on any failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ENTITY_BA, estimate, gridWeather, STATION_BA, studyOf, WINDOWS } from "../lib/eventstudy.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
let bad = 0, n = 0;
const check = (ok, name, detail = "") => { n++; if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${name}${detail ? ` | ${detail}` : ""}`); };
const close = (a, b, rel = 1e-6) => Math.abs(a - b) <= rel * Math.max(1, Math.abs(a), Math.abs(b));

// --- 1. synthetic
function panel(noise, constant = false) {
  const dates = [], y = [], ev = [], truth = [];
  let seed = 7;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647 - 0.5; };
  for (const [yr, lvl] of [[2019, -5], [2020, 5], [2021, 0]]) {
    for (let k = 0; k < 20; k++) {
      const d = new Date(Date.UTC(yr, 1, 1 + k)).toISOString().slice(0, 10);
      const w = (new Date(`${d}T12:00:00Z`).getUTCDay() + 6) % 7;
      const effect = yr === 2021 ? (constant ? 25 : 20 + k) : 0;
      dates.push(d); ev.push(yr === 2021); truth.push(effect);
      y.push(100 + lvl + 3 * w + effect + noise * rnd());
    }
  }
  return { dates, y, ev, truth };
}
{
  const p = panel(0);
  const s = estimate(p.dates, p.y, p.ev);
  const want = p.truth.filter((_, i) => p.ev[i]);
  check(s.days.every((d, i) => close(d.estimate, want[i], 1e-9)), "no noise: every event day's effect is recovered exactly (20 to 39)");
  // the pooled indicator recovers a constant effect exactly (with effects that vary by day it is a weekday-weighted mean)
  const c = panel(0, true), sc = estimate(c.dates, c.y, c.ev);
  check(close(sc.pooled.estimate, 25, 1e-9), "no noise, a constant effect of 25: the pooled effect is 25", String(sc.pooled.estimate));
  const q = panel(4, true), t = estimate(q.dates, q.y, q.ev);
  check(t.pooled.lo < 25 && 25 < t.pooled.hi, "noise: the pooled 95 percent interval covers 25", `${t.pooled.lo.toFixed(2)} to ${t.pooled.hi.toFixed(2)}`);
  check(t.days.every((d) => d.se > 0) && t.days.filter((d, i) => d.lo < q.truth[40 + i] && q.truth[40 + i] < d.hi).length >= 17, "noise: day intervals cover the truth on at least 17 of 20 days");
}

// --- 2. parity with the Python table
const out = path.join(here, "..", "..", "warehouse", "output");
const read = (f) => {
  const lines = fs.readFileSync(path.join(out, f), "utf-8").split("\n").filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  return lines.slice(1).map((l) => {
    const c = [];
    let cur = "", q = false;
    for (const ch of l) { if (ch === '"') q = !q; else if (ch === "," && !q) { c.push(cur); cur = ""; } else cur += ch; }
    c.push(cur);
    return Object.fromEntries(head.map((h, i) => [h, c[i]]));
  });
};
if (fs.existsSync(path.join(out, "event_study_estimates.csv")) && fs.existsSync(path.join(out, "event_window_daily.csv"))) {
  const all = read("event_window_daily.csv");
  const win = all.filter((r) => r.freq === "P1D" && (r.variable === "demand_mwh" || r.variable === "rt_mean"));
  const wx = all.filter((r) => r.entity.startsWith("noaa:") && (r.variable === "hdd_65f" || r.variable === "cdd_65f"));
  const py = read("event_study_estimates.csv").filter((r) => !r.variable.startsWith("demand_mw_effect_h") && !r.variable.endsWith("_trend"));
  const groups = new Map();
  for (const r of win) { const k = `${r.event}|${r.entity}|${r.variable}`; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(r); }
  let m = 0, miss = 0;
  for (const [k, rows] of groups) {
    const [event, entity, variable] = k.split("|");
    const rs = rows.map((r) => ({ ts_utc: r.ts_utc, value: Number(r.value), freq: r.freq }));
    const s = studyOf(event, rs);
    const mine = new Map([[`${variable}_effect_pooled|${WINDOWS[event][0]}`, [s.pooled.estimate, s.pooled.se]],
      [`${variable}_counterfactual_mean|${WINDOWS[event][0]}`, [s.counterfactualMean, null]],
      ...s.days.map((d) => [`${variable}_effect_day|${d.day}`, [d.estimate, d.se]])]);
    // session 49: the temperature-controlled specification, from the grid's stations
    const ws = gridWeather(wx.filter((r) => r.event === event && STATION_BA[r.entity] === ENTITY_BA(entity)).map((r) => ({ ...r, value: Number(r.value) })));
    if (ws.size) {
      const t = studyOf(event, rs, ws);
      mine.set(`${variable}_effect_pooled_temp|${WINDOWS[event][0]}`, [t.pooled.estimate, t.pooled.se]);
      mine.set(`${variable}_counterfactual_mean_temp|${WINDOWS[event][0]}`, [t.counterfactualMean, null]);
      for (const d of t.days) mine.set(`${variable}_effect_day_temp|${d.day}`, [d.estimate, d.se]);
    }
    for (const r of py.filter((x) => x.event === event && x.entity === entity && x.variable.startsWith(variable + "_"))) {
      const t = mine.get(`${r.variable}|${r.ts_utc.slice(0, 10)}`);
      m++;
      if (!t || !close(t[0], Number(r.value)) || (t[1] !== null && !close(t[1], Number(r.x_std_error)))) {
        miss++;
        if (miss <= 5) console.log(`  mismatch ${k} ${r.variable} ${r.ts_utc}: python ${r.value} (${r.x_std_error}), ts ${t}`);
      }
    }
  }
  check(m > 1000 && miss === 0, `parity: every daily and pooled estimate of the Python table equals this estimator's (${m} compared)`, `${miss} mismatched`);
} else console.log("  (parity skipped: the warehouse files are not on this machine)");

console.log(bad ? `${bad} of ${n} FAILED` : `every check passes (${n}): the estimator recovers a known effect and matches the Python table`);
process.exit(bad ? 1 : 0);
