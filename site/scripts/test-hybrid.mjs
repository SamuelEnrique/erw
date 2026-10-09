// Energy Research Warehouse (ERW) site, session 162: the co-optimized hybrid and the reader's profile on "What a
// generator earns" (/cost-of-power/seller), tested on the site's own files: data/seller/hybrid.json (the main hub's
// real day-ahead prices and the fleet's real output per MW over the last twelve months, ERCOT and CAISO),
// public/seller/prices/*.json (one calendar year of real day-ahead prices by hub) and data/seller/capture.json.
// No request, no browser.
//
//   node scripts/test-hybrid.mjs
//
//   1. the page's function (lib/sellerhybrid.ts, a simplex of its own) and the builder's (scipy's HiGHS,
//      warehouse/derived/seller_hybrid.py) agree on the page's own plants: plant, battery alone and pair, every
//      grid, fuel, duration and size written by the builder, to one part in a million;
//   2. the pair never earns less than the plant alone, on every day of every grid and fuel;
//   3. state of charge, power, the export limit and the one cycle a day hold in every hour of every day;
//   4. with a battery of zero size the pair is the plant, to the cent;
//   5. the two alone, added, are never below the pair (the pair is the same two assets under one more limit);
//   6. capture price times generation equals revenue: the hybrid's plants, a reader's profile, and every hub, fuel,
//      market and year of the capture table (to 0.01 USD in a million);
//   7. a profile of the wrong length, with a value below zero, a gap or a value that is not a number is refused, and
//      a year of 8,760 values (8,784 in a leap year) is read; a flat profile captures the flat average exactly;
//   8. the round trip is the battery page's.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const H = await import("../lib/sellerhybrid.ts");
const C = await import("../lib/capture.ts");
const B = await import("../lib/batterystack.ts");
const T = C;
const read = (...p) => JSON.parse(fs.readFileSync(path.join(here, "..", ...p), "utf8"));
const FILE = read("data", "seller", "hybrid.json");
const CAPTURE = read("data", "seller", "capture.json");

let failed = 0;
const ok = (cond, what) => { console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed++; };
const close = (a, b, tol = 1e-6) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));

ok(H.RTE === B.RTE && FILE.rte === B.RTE, `8. the round trip is the battery page's: ${H.RTE}, the file's ${FILE.rte}, the battery page's ${B.RTE}`);

const started = Date.now();
let solved = 0;
for (const [grid, g] of Object.entries(FILE.grids)) {
  // 1. the builder's figures, per MW of plant
  let worst = 0, n = 0;
  for (const c of g.check) {
    const days = H.daysOf(g, c.fuel, 1);
    const t = H.totals(days, c.battery_mw_per_plant_mw, c.hours, 1);
    solved += 2 * days.length;
    for (const [mine, theirs] of [[t.plant, c.plant], [t.battery, c.battery], [t.pair, c.pair], [t.energy, c.energy], [t.limit, c.limit]]) {
      worst = Math.max(worst, Math.abs(mine - theirs) / Math.max(1, Math.abs(theirs)));
    }
    n++;
    if (c.battery_mw_per_plant_mw === 1 && c.hours === 4) {
      console.log(`     ${grid} ${c.fuel}, 4-hour battery of the plant's size, ${g.fuels[c.fuel].months[0]} to ${g.fuels[c.fuel].months[11]}, USD per MW of plant: plant ${Math.round(t.plant)}, battery alone ${Math.round(t.battery)}, pair ${Math.round(t.pair)}, added ${Math.round(t.added)}`);
    }
  }
  ok(n > 0 && worst <= 1e-6, `1. ${grid}: the page's function and the builder's agree on ${n} cases (plant, battery alone, pair, energy, limit); the widest difference is ${worst.toExponential(2)} of the figure`);

  for (const fuel of Object.keys(g.fuels)) {
    const mw = 100, power = 100;
    const days = H.daysOf(g, fuel, mw);
    ok(days.length === g.fuels[fuel].days, `   ${grid} ${fuel}: ${days.length} days held whole, as the builder counted (${g.fuels[fuel].days}; ${g.fuels[fuel].left_out} left out)`);
    const limit = H.limitOf(days, mw);
    for (const hours of [2, 4, 8]) {
      let below = 0, broken = [], plant = 0, add = 0;
      for (const d of days) {
        const s = H.solveDay(d.p, d.g, power, power * hours, limit);
        solved++;
        if (s.value < -1e-6) below++;
        const bad = H.checkDay(s, d.p, d.g, power, power * hours, limit);
        if (bad.length) broken.push(bad[0]);
        plant += d.p.reduce((a, p, t) => a + p * d.g[t], 0);
        add += s.value;
      }
      ok(below === 0, `2. ${grid} ${fuel}, ${hours}-hour battery: the pair is never below the plant alone on any of ${days.length} days (the year: plant ${Math.round(plant)}, pair ${Math.round(plant + add)} USD for 100 MW and 100 MW)`);
      ok(broken.length === 0, `3. ${grid} ${fuel}, ${hours}-hour battery: state of charge, power, the limit and the cycle hold in every hour${broken.length ? `; first: ${broken[0]}` : ""}`);
      const t = H.totals(days, power, hours, mw);
      ok(t.added >= t.pair - 1e-6, `5. ${grid} ${fuel}, ${hours}-hour battery: the two alone added (${Math.round(t.added)}) are not below the pair (${Math.round(t.pair)})`);
      ok(t.capture !== null && Math.abs(t.capture * t.energy - t.plant) <= 1e-6 * Math.max(1, t.plant), `6. ${grid} ${fuel}: capture price ${t.capture?.toFixed(4)} x ${Math.round(t.energy)} MWh = revenue ${Math.round(t.plant)} USD`);
    }
    const zero = H.totals(days, 0, 4, mw);
    ok(Math.abs(zero.pair - zero.plant) < 0.005 && zero.battery === 0, `4. ${grid} ${fuel}: with a battery of zero size the pair is the plant (${zero.pair.toFixed(2)} and ${zero.plant.toFixed(2)})`);
  }
}
console.log(`     ${solved} days solved in ${Date.now() - started} ms`);

// 6. every hub, fuel, market and year of the capture table: capture price x generation = revenue
{
  const table = T.hubYears(CAPTURE);
  let cells = 0, held = 0, off = 0, widest = 0;
  for (const row of table.rows) {
    for (const fuel of C.FUELS) for (const market of ["rt", "da"]) for (const y of table.years) {
      const c = row.cells[market][fuel][y];
      cells++;
      if (!c) continue;
      held++;
      const d = Math.abs(c.price * c.mwh - c.revenue);
      widest = Math.max(widest, d / Math.max(1, Math.abs(c.revenue)));
      if (d > 1e-8 * Math.max(1, Math.abs(c.revenue)) + 0.01) off++;
    }
  }
  ok(held > 0 && off === 0, `6. the capture table: capture price x generation = revenue in each of ${held} cells held (of ${cells}; ${table.rows.length} hubs, years ${table.years[0]} to ${table.years.at(-1)}); the widest difference is ${widest.toExponential(2)} of the revenue`);
  ok(!table.rows.some((r) => /miso|pjm/i.test(r.grid)) && table.blank.length === 2, `   no MISO hub and no PJM hub in it; ${table.blank.map((b) => `${b.name}: ${b.words}`).join("; ")}`);
}

// 7. the reader's profile
{
  const year = 2025, leapYear = 2024;
  const flat = Array.from({ length: 8760 }, () => "1").join("\n");
  const good = H.parseProfile(flat, year);
  ok(good.ok && good.values.length === 8760, "7. 8,760 lines of one number are read");
  ok(H.parseProfile(`${flat}\n\n`, year).ok, "   empty lines after the last value are ignored");
  ok(H.parseProfile(`MW\r\n${flat.replace(/\n/g, "\r\n")}`, year).ok, "   a header line and Windows line ends are read");
  ok(H.parseProfile(`hour;mw\n${Array.from({ length: 8760 }, (_, i) => `2025-h${i};0.5`).join("\n")}`, year).ok, "   a CSV with one column of numbers is read");
  const refused = (text, y, what) => { const r = H.parseProfile(text, y); ok(!r.ok && r.why.length > 10, `   refused: ${what}: "${r.ok ? "READ" : r.why}"`); };
  refused(Array.from({ length: 8759 }, () => "1").join("\n"), year, "8,759 values");
  refused(flat, leapYear, "8,760 values for a leap year");
  ok(H.parseProfile(Array.from({ length: 8784 }, () => "1").join("\n"), leapYear).ok, "   8,784 values are read for a leap year");
  refused(flat.replace("1\n1\n", "1\n-1\n"), year, "a value below zero");
  refused(flat.replace("1\n1\n", "1\n\n1\n"), year, "a gap (an empty line)");
  refused(flat.replace("1\n1\n", "1\nNaN\n"), year, "a value that is not a number");
  refused(flat.replace("1\n1\n", "1\n1,5\n"), year, "a row with two values");
  refused(Array.from({ length: 8760 }, (_, i) => `${i},1`).join("\n"), year, "two columns of numbers");
  refused("", year, "nothing");
  for (const f of fs.readdirSync(path.join(here, "..", "public", "seller", "prices")).filter((n) => /^(ercot|caiso)_2025\.json$/.test(n))) {
    const P = read("public", "seller", "prices", f);
    const r = H.profileResult(good.values, P.price, 1, 4);
    ok(r.priced === P.held && P.price.length === P.hours, `   ${f}: ${r.priced} of ${P.hours} hours priced, as the file says (${P.held})`);
    ok(r.capture !== null && close(r.capture, r.flat, 1e-12) && close(r.ratio, 100, 1e-12), `   ${f}: a flat profile captures the flat average exactly (${r.capture?.toFixed(4)} and ${r.flat?.toFixed(4)} USD per MWh)`);
    ok(Math.abs(r.capture * r.energyPriced - r.revenue) <= 1e-9 * Math.max(1, r.revenue), `6. ${f}: capture price x generation = revenue (${r.capture?.toFixed(4)} x ${r.energyPriced} = ${r.revenue.toFixed(2)})`);
    ok(r.hybrid !== null && r.hybrid.pair >= r.hybrid.plant - 1e-6 && r.hybrid.added >= r.hybrid.pair - 1e-6 && r.days + r.daysOut === 365, `   ${f}: the pair (${Math.round(r.hybrid?.pair)}) is not below the plant (${Math.round(r.hybrid?.plant)}) nor above the two added (${Math.round(r.hybrid?.added)}); ${r.days} days solved, ${r.daysOut} left out`);
    const none = H.profileResult(good.values, P.price, 0, 4);
    ok(none.hybrid === null, `   ${f}: with no battery there is no pair`);
  }
}

console.log(failed ? `${failed} FAILED` : "all passed");
process.exit(failed ? 1 : 0);
