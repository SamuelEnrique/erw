// Energy Research Warehouse (ERW) site, session 138: the arithmetic of "What a datacenter pays" (/cost-of-power),
// tested on saved real samples (tests/fixtures/session138: ERCOT HB_HUBAVG, every hour of 2021 and of 2025, real time
// and day-ahead). No request, no browser.
//
//   node scripts/test-datacenter.mjs
//
//   1. the cost of a flat load equals the mean of the hourly prices (the year, and each month);
//   2. a flexible load never pays more than a flat one (per MWh for a load that turns off; in dollars and per MWh for
//      a load that shifts), for a range of each setting, in a calm year and in the year of Winter Storm Uri;
//   3. the contract arithmetic matches the battery page's (lib/batterystack.ts, contractResult): a share at the typed
//      price, the rest at the market's last twelve months;
//   4. a load that turns off n hours a year is off in exactly n; a shifted day keeps its energy; hours not held are
//      left out, never filled; the address is read into inputs with every grid held and no other.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const L = await import("../lib/datacenter.ts");
const B = await import("../lib/batterystack.ts");
const fx = (y) => JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session138", `ercot_HB_HUBAVG_${y}.json`), "utf8"));
const F = { 2021: fx(2021), 2025: fx(2025) };

let failed = 0;
const ok = (cond, what) => { console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed++; };
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));
const FLAT = { run: "flat", n: 0, pct: 0, shift: 0 };

// 1. a flat load pays the mean of the hourly prices
for (const y of [2021, 2025]) for (const buy of ["rt", "da"]) {
  const raw = F[y].regions.HB_HUBAVG[buy].v.filter((v) => v !== null);
  const mean = raw.reduce((a, v) => a + v, 0) / raw.length;
  const p = L.expand(F[y], "HB_HUBAVG", buy);
  const ms = L.monthsOfYear(y, p, L.weights(p, FLAT));
  const s = L.span(ms);
  ok(close(s.flat, mean) && close(s.per, mean) && s.held === raw.length, `${y} ${buy}: a flat load pays the mean of the ${raw.length} hourly prices, ${mean.toFixed(4)} USD/MWh`);
  ok(close(L.flatMean(p).mean, mean), `${y} ${buy}: flatMean is the same mean`);
  const st = L.monthStarts(y);
  const each = ms.every((r, i) => { const part = p.slice(st[i], st[i + 1]).filter((v) => v !== null); return close(r.flat / r.held, part.reduce((a, v) => a + v, 0) / part.length) && close(r.cost, r.flat) && r.energy === r.held; });
  ok(ms.length === 12 && each, `${y} ${buy}: each of the twelve months is the mean of its own hours, and its cost is the sum of them`);
}

// 2. a flexible load never pays more than a flat one
for (const y of [2021, 2025]) for (const buy of ["rt", "da"]) {
  const p = L.expand(F[y], "HB_HUBAVG", buy);
  const flat = L.span(L.monthsOfYear(y, p, L.weights(p, FLAT)));
  const tries = [...[1, 10, 100, 500, 2000].map((n) => ({ run: "hours", n, pct: 0, shift: 0 })), ...[0.5, 5, 25, 60].map((pct) => ({ run: "share", n: 0, pct, shift: 0 })), ...[1, 10, 20, 33, 50].map((shift) => ({ run: "shift", n: 0, pct: 0, shift }))];
  let worst = Infinity, all = true, months = true;
  for (const x of tries) {
    const ms = L.monthsOfYear(y, p, L.weights(p, x));
    const s = L.span(ms);
    if (!(s.per <= flat.per + 1e-9)) all = false;
    if (x.run === "shift" && !(s.cost <= flat.cost + 1e-6 && close(s.energy, flat.energy, 1e-12))) all = false;
    if (!ms.every((r) => r.energy === 0 || r.cost / r.energy <= r.flat / r.held + 1e-9)) months = false;
    worst = Math.min(worst, flat.per - s.per);
  }
  ok(all, `${y} ${buy}: none of ${tries.length} flexible loads pays more per MWh than the flat load (the least saved: ${worst.toFixed(4)} USD/MWh); a shifted load pays no more in dollars for the same energy`);
  ok(months, `${y} ${buy}: nor in any single month`);
}

// 3. the contract arithmetic matches the battery page's
{
  const p = L.expand(F[2025], "HB_HUBAVG", "rt");
  const ms = L.monthsOfYear(2025, p, L.weights(p, FLAT));
  const l12 = L.lastTwelve(ms), s = L.span(l12);
  const mw = 250, share = 40, price = 45;
  const mine = L.contractResult(s, mw, { share, price });
  // the same twelve months handed to the battery page's function: a month's "revenue per MW" is the load's cost per MW,
  // and its contract price per kW-month is the one that pays the same dollars for the contracted share
  const months = ms.map((r) => ({ m: r.m, held: true, total: r.cost, energy: r.cost, ancillary: 0, daysHeld: 30, daysInMonth: 30, daysOut: 0, daysOutAncillary: 0 }));
  const kwMonth = (price * s.energy) / 12000;
  const theirs = B.contractResult(months, { mw, fom: 0, ds: 1, dur: 2, strat: "foresight", grid: "ercot" }, { share, price: kwMonth, end: "" });
  ok(close(mine.contracted, theirs.contracted) && close(mine.market, theirs.market12) && close(mine.without, theirs.after12),
    `contract: ${share} percent at USD ${price}: contracted ${Math.round(mine.contracted).toLocaleString("en-US")}, market on the rest ${Math.round(mine.market).toLocaleString("en-US")}, as the battery page's contractResult computes them`);
  ok(close(mine.total, theirs.coverageWith) && close(mine.without, theirs.coverageWithout), "contract: the total with and without it equal the battery page's (its coverage at debt 1 and no fixed cost)");
  ok(close(L.contractResult(s, mw, { share: 0, price }).per, s.per) && close(L.contractResult(s, mw, { share: 100, price }).per, price), "contract: no share is the market's price per MWh; the whole load is the contract's");
  ok(close(L.contractResult(s, mw, { share: 250, price }).total, L.contractResult(s, mw, { share: 100, price }).total), "contract: a share above 100 is 100, as on the battery page");
}

// 4. the rules of the load
{
  const p = L.expand(F[2025], "HB_HUBAVG", "rt");
  for (const n of [0, 1, 100, 876]) {
    const w = L.weights(p, { run: "hours", n, pct: 0, shift: 0 });
    const off = w.filter((v, i) => v === 0 && p[i] !== null).length;
    const kept = p.filter((v, i) => w[i] === 1), cut = p.filter((v, i) => w[i] === 0 && v !== null);
    ok(off === n && (n === 0 || Math.min(...cut) >= Math.max(...kept)), `hours: off in exactly ${n} hours of 2025, and no hour kept costs more than an hour cut`);
  }
  const w = L.weights(p, { run: "shift", n: 0, pct: 0, shift: 20 });
  let days = true;
  for (let d = 0; d < p.length; d += 24) { const sum = w.slice(d, d + 24).reduce((a, v) => a + v, 0); if (!close(sum, 24) || w.slice(d, d + 24).some((v) => v < -1e-12 || v > 2 + 1e-12)) days = false; }
  ok(days, "shift: every day keeps its 24 MWh per MW, and no hour draws less than nothing or more than twice the load");
  // an hour not held is left out
  const holes = [...p]; for (let i = 100; i < 130; i++) holes[i] = null;
  const mh = L.monthsOfYear(2025, holes, L.weights(holes, FLAT));
  ok(mh[0].held === 744 - 30 && close(mh[0].flat, p.slice(0, 744).reduce((a, v, i) => a + (i >= 100 && i < 130 ? 0 : v), 0)), "a month with 30 hours not held sums the 714 held, and nothing in their place");
  const ws = L.weights(holes, { run: "shift", n: 0, pct: 0, shift: 20 });
  ok([4, 5].every((d) => ws.slice(d * 24, d * 24 + 24).every((v, i) => v === (holes[d * 24 + i] === null ? 0 : 1))), "a day with an hour missing is not shifted");
  const few = L.monthsOfYear(2025, p.map((v, i) => (i < 400 ? null : v)), L.weights(p.map((v, i) => (i < 400 ? null : v)), FLAT));
  ok(few[0].complete === false && few[1].complete === true && L.lastTwelve(few) === null, "a month under 95 percent of its hours is not complete, and no twelve months are claimed without it");
  ok(L.monthStarts(2024)[2] === (31 + 29) * 24 && L.monthStarts(2025)[12] === 8760 && L.hoursIn(2024) === 8784, "the hours of a year and its months, with the leap day");
  const idx = { grids: { ercot: { name: "ERCOT", main: "HB_HUBAVG", regions: [{ id: "HB_HUBAVG" }, { id: "HB_WEST" }] }, caiso: { name: "CAISO", main: "SP15", regions: [{ id: "SP15" }] } }, blank: { miso: {}, pjm: {} } };
  const a = L.inputsOf({ grid: "miso", region: "X", mw: "abc", run: "nope" }, idx);
  ok(a.grid === "ercot" && a.region === "HB_HUBAVG" && a.mw === L.DEFAULTS.mw && a.run === "flat" && a.buy === "rt", "an address naming MISO, an unknown region and no number opens ERCOT's main hub with the defaults");
  const b = L.inputsOf({ grid: "caiso", region: "HB_WEST", mw: "250", run: "hours", n: "50", buy: "da" }, idx);
  ok(b.grid === "caiso" && b.region === "SP15" && b.mw === 250 && b.n === 50 && b.buy === "da", "a region of another grid falls back to the chosen grid's main hub");
  ok(close(L.gpuHour(40, 1.3, 1.5), 0.078) && close(L.gpus(100, 1.3, 1.5), 100000 / 1.95), "a GPU-hour is its kW with the facility's overhead at the price per MWh; a facility powers its MW over that");
  const bad = L.badMonth(Array.from({ length: 36 }, (_, i) => ({ m: `m${String(i).padStart(2, "0")}`, complete: true, cost: i, energy: 1 })));
  ok(bad.m === "m32", "a bad month of 36 is the fourth dearest: one month in ten cost that or more");
}

console.log(failed ? `${failed} failed` : "all passed");
process.exit(failed ? 1 : 0);
