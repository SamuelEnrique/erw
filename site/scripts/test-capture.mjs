// Energy Research Warehouse (ERW) site, session 145: the arithmetic of the capture price, the contract and the hybrid
// on "What a generator earns" (/cost-of-power/seller), tested on saved real samples (tests/fixtures/session145: the
// price rows of ERCOT's West hub for the week from 1 June 2026, real time and day-ahead, and the grid's hourly solar
// and wind generation of the same week) and on the site's own file (data/seller/capture.json). No request, no browser.
//
//   node scripts/test-capture.mjs
//
//   1. the generation-weighted price of the real week, by hand, equals the library's;
//   2. a plant that generates the same in every hour captures the flat average exactly;
//   3. the premium in dollars and in percent agree;
//   4. a month under 95 percent of its hours writes no figure; at 95 percent it counts;
//   5. MISO has no number;
//   6. the contract arithmetic equals the battery page's (lib/batterystack.ts, contractResult);
//   7. the combined figure is the sum of its two parts;
//   8. the last twelve months and the years of the site's file are the sums of their months.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const C = await import("../lib/capture.ts");
const D = await import("../lib/datacenter.ts");
const B = await import("../lib/batterystack.ts");
const fx = (name) => fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "session145", name), "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#")).slice(1).map((l) => l.split(","));
const FILE = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "seller", "capture.json"), "utf8"));

let failed = 0;
const ok = (cond, what) => { console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed++; };
const close = (a, b, tol = 1e-9) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));

// the real week: the hours of generation, and each hour's price (real time: the mean of its four 15-minute prices,
// held only when all four are; day-ahead: the hour's own)
const gen = fx("generation_week.csv").map(([ts, solar, wind]) => ({ ts, solar: Number(solar), wind: Number(wind) }));
const rows = fx("prices_week.csv").map(([entity, side, freq, ts, value]) => ({ entity, side, freq, ts, value: Number(value) }));
const quarters = new Map();
for (const r of rows.filter((x) => x.side === "rtm")) {
  const hour = `${r.ts.slice(0, 13)}:00:00Z`;
  if (!quarters.has(hour)) quarters.set(hour, []);
  quarters.get(hour).push(r.value);
}
const rt = new Map([...quarters].filter(([, q]) => q.length === 4).map(([h, q]) => [h, (q[0] + q[1] + q[2] + q[3]) / 4]));
const da = new Map(rows.filter((x) => x.side === "dam").map((r) => [r.ts, r.value]));

// 1. by hand
ok(gen.length === 168 && rt.size === 168 && da.size === 168 && rows.every((r) => r.entity === "ercot:HB_WEST"), `the sample is one whole week of ERCOT's West hub: ${gen.length} hours of generation, ${rt.size} hours of real-time price (${rows.filter((r) => r.side === "rtm").length} quarter hours), ${da.size} of day-ahead`);
for (const [name, price] of [["real time", rt], ["day-ahead", da]]) {
  for (const fuel of ["solar", "wind"]) {
    let sumPG = 0, sumG = 0, sumP = 0, n = 0;
    for (const h of gen) {
      if (!price.has(h.ts)) continue;
      sumPG += price.get(h.ts) * h[fuel]; sumG += h[fuel]; sumP += price.get(h.ts); n += 1;
    }
    const hand = { price: sumPG / sumG, flat: sumP / n };
    const w = C.weighted(gen.map((h) => price.get(h.ts) ?? null), gen.map((h) => h[fuel]));
    const f = C.figure([[w.n, 168, w.sp, w.g, w.pg]]);
    ok(f && w.n === n && close(f.price, hand.price) && close(f.flat, hand.flat) && close(f.premium, hand.price - hand.flat),
      `${fuel}, ${name}: by hand USD ${hand.price.toFixed(4)} per MWh received against a flat USD ${hand.flat.toFixed(4)} over ${n} hours; the library says the same`);
  }
}
{
  // an hour without a price, or without generation, is in neither sum; generation below zero weighs nothing
  const w = C.weighted([10, null, 30, 40, 50], [1, 1, null, -5, 3]);
  ok(w.n === 3 && w.sp === 100 && w.g === 4 && w.pg === 160, "an hour without a price or without generation is in neither sum, and generation below zero weighs nothing but stays in the flat average");
}

// 2. the same generation in every hour: the flat average, exactly
for (const [name, price] of [["real time", rt], ["day-ahead", da]]) {
  const p = gen.map((h) => price.get(h.ts));
  const w = C.weighted(p, p.map(() => 250));
  const f = C.figure([[w.n, 168, w.sp, w.g, w.pg]]);
  ok(close(f.price, f.flat, 1e-12) && Math.abs(f.premium) < 1e-9 && Math.abs(f.pct) < 1e-9, `a plant that generates the same in every hour captures the flat average of the week's ${name} prices exactly (USD ${f.flat.toFixed(4)})`);
}

// 3. dollars and percent agree, on every last-twelve-month figure of the site's file
{
  let n = 0, bad = 0;
  for (const g of Object.values(FILE.grids)) for (const h of g.hubs) for (const m of ["rt", "da"]) for (const fuel of C.FUELS) {
    const s = C.twelve(h[m]?.[fuel], FILE.near);
    if (!s) continue;
    n += 1;
    if (!close(s.premium, s.price - s.flat) || !close(s.pct, (100 * s.premium) / s.flat) || Math.sign(s.pct) !== Math.sign(s.premium)) bad += 1;
  }
  ok(n > 0 && bad === 0, `the premium in dollars and in percent agree on each of the ${n} last-twelve-month figures of the site's file`);
}

// 4. a month under 95 percent writes no figure
{
  const w = C.weighted(gen.map((h) => rt.get(h.ts)), gen.map((h) => h.wind));
  const week = { "2026-06": [w.n, 720, w.sp, w.g, w.pg] };
  ok(!C.counted(week["2026-06"], 0.95) && C.lastTwelve(week, 0.95) === null && C.twelve(week, 0.95) === null && C.years(week, 0.95).length === 0, "a month that holds one week of its hours (168 of 720) counts for nothing: no last twelve months, no year");
  ok(C.counted([684, 720, 0, 0, 0], 0.95) && !C.counted([683, 720, 0, 0, 0], 0.95), "a month counts at 95 percent of its hours (684 of 720) and not one hour under");
  const months = {};
  for (let i = 0; i < 24; i++) { const m = new Date(Date.UTC(2024, i, 1)).toISOString().slice(0, 7); months[m] = [720, 720, 720 * 30, 7200, 7200 * 25]; }
  months["2025-06"] = [600, 720, 600 * 30, 6000, 6000 * 25];
  const t = C.lastTwelve(months, 0.95), ys = C.years(months, 0.95);
  ok(t !== null && t[0] === "2024-06" && t[11] === "2025-05" && ys.find((y) => y.y === "2024").whole && !ys.find((y) => y.y === "2025").whole && ys.find((y) => y.y === "2025").months === 11 && ys.find((y) => y.y === "2025").f.hours === 11 * 720,
    "a short month ends the last twelve months at the month before it and leaves its year partial, with its counted months only: nothing is scaled up");
}

// 5. MISO has no number
{
  const text = JSON.stringify(FILE.grids);
  ok(!("miso" in FILE.grids) && !("pjm" in FILE.grids) && FILE.blank.miso.words === "paused while terms are reviewed" && FILE.blank.pjm.words === "licensed source needed" && !/miso:|\.HUB"|INDIANA/i.test(text) && C.hubOf(FILE, "miso", undefined) === null,
    'MISO has no number in the site\'s file: it is listed as "paused while terms are reviewed", PJM as "licensed source needed"');
}

// 6. the contract arithmetic equals the battery page's
{
  const s = C.twelve(FILE.grids.ercot.hubs.find((h) => h.id === "HB_HUBAVG").rt.solar, FILE.near);
  const energy = 2600, mw = 150, share = 40, price = 45;                 // MWh per MW a year; MW; percent; USD per MWh
  const r = D.contractResult(C.contractSpan(energy, s.price), mw, { share, price });
  // the battery page's contract pays a price per kW-month on a share of the power: the same dollars when that price is
  // the energy's price times the energy of a kW-month
  const ms = Array.from({ length: 12 }, (_, i) => ({ m: `2025-${String(i + 1).padStart(2, "0")}`, held: true, daysHeld: 30, daysOut: 0, daysOutAncillary: 0, daysOutEnergy: 0, daysInMonth: 30,
    energy: (energy * s.price) / 12, ancillary: 0, total: (energy * s.price) / 12, products: {} }));
  const b = B.contractResult(ms, { grid: "ercot", dur: 4, strat: "foresight", mw, fom: 0, ds: 1 }, { share, price: (price * energy) / 12000, end: "" });
  ok(close(r.contracted, b.contracted) && close(r.market, b.market12) && close(r.without, b.after12) && close(r.total, b.contracted + b.market12) && close(r.total, b.coverageWith) && close(r.without, b.coverageWithout),
    `the contract arithmetic equals the battery page's: ${share} percent at USD ${price} gives USD ${Math.round(r.total).toLocaleString("en-US")} with the contract and USD ${Math.round(r.without).toLocaleString("en-US")} without, by both`);
  ok(close(r.per, (share / 100) * price + (1 - share / 100) * s.price) && close(r.perWithout, s.price), "per MWh: the contracted share at its price, the rest at the hub's generation-weighted price");
  const none = D.contractResult(C.contractSpan(energy, s.price), mw, { share: 0, price });
  ok(close(none.total, none.without), "with nothing contracted, revenue with the contract equals revenue without it");
}

// 7. the combined figure is the sum of its two parts
ok(C.combined(1234567, 7654321) === 1234567 + 7654321 && C.combined(null, 5) === null && C.combined(5, null) === null, "the combined figure is the solar plant's revenue plus the battery's, and is not shown when either is not held");

// 8. the spans of the site's file are the sums of their months
{
  const m = FILE.grids.ercot.hubs.find((h) => h.id === "HB_WEST").rt.solar;
  const t = C.lastTwelve(m, FILE.near), s = C.twelve(m, FILE.near);
  let n = 0, sp = 0, g = 0, pg = 0;
  for (const k of t) { n += m[k][0]; sp += m[k][2]; g += m[k][3]; pg += m[k][4]; }
  ok(t.length === 12 && s.from === t[0] && s.to === t[11] && close(s.price, pg / g) && close(s.flat, sp / n) && s.hours === n,
    `ERCOT's West hub, solar, real time, ${s.from} to ${s.to}: USD ${s.price.toFixed(2)} received against a flat USD ${s.flat.toFixed(2)}, the sums of its twelve months`);
  const y = C.years(m, FILE.near);
  ok(y.every((r) => r.whole === (r.months === 12)) && y.some((r) => r.whole) && y.some((r) => !r.whole), "a year is whole with twelve counted months and partial with fewer");
  const w = C.widest(FILE, "solar", "rt");
  ok(w.discount && w.discount.s.premium < 0 && (!w.premium || w.premium.s.premium > 0), "the widest premium is above zero and the widest discount below it");
  ok(C.freeEnergyHref("caiso", "TH_SP15_GEN-APND") === "/curtailment?grid=caiso&place=TH_SP15_GEN-APND#free-energy", "the link to the curtailment page's free-energy section carries the grid and the hub");
}

console.log(failed ? `${failed} failed` : "all passed");
process.exit(failed ? 1 : 0);
