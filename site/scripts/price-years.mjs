// Energy Research Warehouse (ERW) site, session 357: the price years, computed by the pages' own code.
//
//   node --import ./scripts/alias-register.mjs scripts/price-years.mjs <input.json> <output.json>
//
// Run by warehouse/derived/price_years.py, which writes <input.json> (the battery's rows of battery_stack_monthly,
// battery_stack_review_monthly and battery_stack_stress_daily, as the page reads them: variable, ts_utc, value, event)
// and reads <output.json> (one object a row of price_years_by_window, docs/methods/price_years.md). The generator's
// and the datacenter's inputs are the files their pages read: data/merchant_snapshot.json and data/datacenter/*.json.
// Every figure is the pages' own arithmetic: lib/batterystack.ts, lib/merchant.ts with lib/seller2.ts, and
// lib/datacenter.ts. What this file adds is only the choice of windows, and for the generator and the datacenter the
// taking out of a stress event's days, which the battery page does in lib/batterystack.ts (windowMonths) and the other
// two pages do not offer.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const B = await import("../lib/batterystack.ts");
const M = await import("../lib/merchant.ts");
const S2 = await import("../lib/seller2.ts");
const D = await import("../lib/datacenter.ts");

const [inPath, outPath] = process.argv.slice(2);
if (!inPath || !outPath) { console.error("usage: price-years.mjs <input.json> <output.json>"); process.exit(2); }
const input = JSON.parse(fs.readFileSync(inPath, "utf-8"));
const GRIDS = input.grids;              // the grids the table may hold (public): ["ercot", "caiso", "spp"]
const rows = [];
const proofs = [];

const ym = (m) => m.slice(0, 7);
/** One row of the table: the driver adds the columns every row shares. */
function row(o) {
  if (o.value === null || o.value === undefined || !Number.isFinite(o.value)) return;
  rows.push(o);
}
/** The last N full calendar years held, consecutive and ending with the newest full year; null when they are not all full. */
function lastFull(full, n) {
  const newest = full.at(-1);
  if (!newest) return null;
  const want = Array.from({ length: n }, (_, k) => String(Number(newest) - (n - 1) + k));
  return want.every((y) => full.includes(y)) ? want : null;
}

// ---------------------------------------------------------------------------------------------------------------------
// the battery: lib/batterystack.ts on the rows the page reads
// ---------------------------------------------------------------------------------------------------------------------
for (const [grid, g] of Object.entries(input.battery)) {
  if (!GRIDS.includes(grid)) continue;
  for (const strat of ["foresight", "dayahead"]) for (const dur of B.DURATIONS) {
    const pre = `${strat}_${dur}h_`;
    const rs = g.rows.filter((r) => r.variable.startsWith(pre));
    const srs = (g.stress ?? []).filter((r) => r.variable.startsWith(pre));
    const ms = B.monthsOf(rs, strat, dur);
    if (!ms.length) continue;
    const em = B.eventMonths(srs, strat, dur);
    const events = B.stress(srs, strat, dur).map((e) => e.event);
    const config = `${strat}_${dur}h`;
    const base = { tool: "battery", grid, entity: g.entity, node: g.node, config, unit: "USD/kW-year" };
    const heldIn = (from, to) => ms.filter((r) => r.held && r.m.slice(0, 4) >= from && r.m.slice(0, 4) <= to);
    const ys = B.years(ms);
    for (const y of ys) {
      const held = heldIn(y.y, y.y);
      const v = B.yearStream(ms, y.y, "total");
      row({ ...base, window: `year_${y.y}`, kind: "year", leftOut: [], value: v === null ? null : v / 1000, months: held.length,
        from: held[0].m, to: held.at(-1).m, complete: y.complete });
    }
    const l12 = B.lastTwelve(ms);
    if (l12) {
      row({ ...base, window: "last_12", kind: "last_12", leftOut: [], value: B.sumOf(l12, "total") / 1000, months: 12, from: l12[0].m, to: l12[11].m, complete: true });
      // the proof: the page's own check-key stat for the last twelve months, per kW
      proofs.push({ tool: "battery", grid, config, stat: "l12_kw:total", page: B.stat(rs, srs, { grid, dur, strat, mw: 100, fom: 0, ds: 0 }, "l12_kw:total") });
    }
    const full = ys.filter((y) => y.complete).map((y) => y.y);
    for (const [n, kind] of [[3, "avg_3y"], [7, "avg_7y"]]) {
      const want = lastFull(full, n);
      if (!want) continue;
      const v = B.windowAverage(ms, want[0], want.at(-1), [], em, "total");
      const held = heldIn(want[0], want.at(-1));
      row({ ...base, window: kind, kind, leftOut: [], value: v === null ? null : v / 1000, months: held.length, from: held[0].m, to: held.at(-1).m, complete: true });
    }
    const yrs = B.yearsHeld(ms);
    const first = yrs[0], last = yrs.at(-1);
    const all = heldIn(first, last);
    const windows = [["all", "all", []], ...events.map((e) => [`all_less_${e}`, "all_less", [e]])];
    if (events.length > 1) windows.push(["all_less_events", "all_less", [...events]]);
    for (const [window, kind, leftOut] of windows) {
      const v = B.windowAverage(ms, first, last, leftOut, em, "total");
      row({ ...base, window, kind, leftOut, value: v === null ? null : v / 1000, months: all.length, from: all[0].m, to: all.at(-1).m, complete: true });
    }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// the generator: lib/merchant.ts and lib/seller2.ts on the snapshot the page reads
// ---------------------------------------------------------------------------------------------------------------------
const snap = JSON.parse(fs.readFileSync(path.join(site, "data", "merchant_snapshot.json"), "utf-8"));
for (const grid of GRIDS) {
  const s = snap.isos[grid];
  if (!s || !S2.GRIDS.some((g) => g.id === grid)) continue;
  for (const a of S2.ASSETS) {
    const asset = a.id;
    const ms = S2.monthsOf(snap, { grid, asset });
    if (!ms.length) continue;
    const base = { tool: "generator", grid, entity: `${grid}:${s.hub}`, node: s.hub, config: asset, unit: "USD/kW-year" };
    const held = (yy) => ms.filter((r) => r.held && yy.includes(r.m.slice(0, 4)));
    const sp = S2.spans(ms);
    for (const y of S2.years(ms)) {
      const span = S2.spanOf(held([y.y]), 1);
      if (span) row({ ...base, window: `year_${y.y}`, kind: "year", leftOut: [], value: span.revenue_kw, months: span.months, from: span.from, to: span.to, complete: y.complete });
    }
    if (sp.twelve) {
      row({ ...base, window: "last_12", kind: "last_12", leftOut: [], value: sp.twelve.revenue_kw, months: sp.twelve.months, from: sp.twelve.from, to: sp.twelve.to, complete: true });
      const x = { iso: grid, asset, mw: 1, mwh: asset === "battery" ? 4 : 0, ds: 0, hr: M.HEAT_RATE, vom: M.VOM, fom: 0 };
      proofs.push({ tool: "generator", grid, config: asset, stat: "spans.twelve.revenue_kw", page: sp.twelve.revenue_kw, months: M.months(snap, x).filter((r) => r.held).length });
    }
    if (sp.three) row({ ...base, window: "avg_3y", kind: "avg_3y", leftOut: [], value: sp.three.revenue_kw, months: sp.three.months, from: sp.three.from, to: sp.three.to, complete: true });
    const want7 = lastFull(S2.fullYears(ms), 7);
    if (want7) {
      const span = S2.spanOf(held(want7), 7);
      if (span) row({ ...base, window: "avg_7y", kind: "avg_7y", leftOut: [], value: span.revenue_kw, months: span.months, from: span.from, to: span.to, complete: true });
    }
    if (sp.every) {
      row({ ...base, window: "all", kind: "all", leftOut: [], value: sp.every.revenue_kw, months: sp.every.months, from: sp.every.from, to: sp.every.to, complete: true });
      // a stress event's window days taken out of the months they fall in: the snapshot's own daily figures (ERCOT only),
      // per MW as lib/merchant.ts's stress() reads them; the years averaged over are the page's full years, unchanged
      const everyMonths = new Set(held(sp.everyYears).map((r) => r.m));
      const x = { iso: grid, asset, mw: 1, mwh: asset === "battery" ? 4 : 0, ds: 0, hr: M.HEAT_RATE, vom: M.VOM, fom: 0 };
      const k = M.keyOf(x);
      const dayValue = (d) => (k === "peaker" ? (d.i0 === null || d.i1 === null ? null : M.peakerOver(s, d.i0, d.i1, x.hr, x.vom).revenue) : d[k] ?? null);
      const out = {};
      for (const [event, e] of Object.entries(s.stress ?? {})) {
        let removed = 0, missing = 0;
        for (const d of e.days) {
          if (!d.window || !everyMonths.has(ym(d.day))) continue;
          const v = dayValue(d);
          if (v === null) missing++; else removed += v;
        }
        out[event] = { removed, missing };
      }
      const events = Object.keys(out);
      const every = held(sp.everyYears).reduce((t, r) => t + r.revenue, 0);
      const leaveOut = (ids) => {
        if (ids.some((id) => out[id].missing)) return null;  // a window day without its figure: not taken out by guess
        return (every - ids.reduce((t, id) => t + out[id].removed, 0)) / sp.everyYears.length / 1000;
      };
      const windows = events.map((e) => [`all_less_${e}`, [e]]);
      if (events.length > 1) windows.push(["all_less_events", events]);
      for (const [window, ids] of windows) {
        row({ ...base, window, kind: "all_less", leftOut: ids, value: leaveOut(ids), months: sp.every.months, from: sp.every.from, to: sp.every.to, complete: true });
      }
    }
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// the datacenter: lib/datacenter.ts on the year files the page reads
// ---------------------------------------------------------------------------------------------------------------------
const dcDir = path.join(site, "data", "datacenter");
const index = JSON.parse(fs.readFileSync(path.join(dcDir, "index.json"), "utf-8"));
const RUNS = ["flat", "hours", "share", "shift"];
const FLEX = { n: D.DEFAULTS.n, pct: D.DEFAULTS.pct, shift: D.DEFAULTS.shift };
const DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
const leap = (y) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
/** The day of the year, from 0, of a local date YYYY-MM-DD. */
const dayOfYear = (d) => {
  const y = Number(d.slice(0, 4)), m = Number(d.slice(5, 7)), day = Number(d.slice(8, 10));
  let n = day - 1;
  for (let k = 0; k < m - 1; k++) n += DAYS[k] + (k === 1 && leap(y) ? 1 : 0);
  return n;
};
for (const grid of GRIDS) {
  const g = index.grids[grid];
  if (!g) continue;
  const files = g.years.map((y) => JSON.parse(fs.readFileSync(path.join(dcDir, `${grid}_${y}.json`), "utf-8")));
  const events = input.events[grid] ?? {};   // event id -> the local days the battery page's leave-out box takes out
  for (const region of g.regions) for (const buy of ["rt", "da"]) {
    if (!region[buy]) continue;
    for (const run of RUNS) {
      const x = { run, ...FLEX };
      const ruled = D.monthsRuled(files, region.id, buy, x, "forecast");
      const ms = ruled.months;
      if (!ms.length) continue;
      const config = `${run}_${buy}`;
      const base = { tool: "datacenter", grid, entity: region.entity, node: region.id, config, unit: "USD/MWh" };
      const done = ms.filter((r) => r.complete);
      const ys = D.years(ms);
      for (const y of ys) {
        const dm = done.filter((r) => r.m.startsWith(y.y));
        row({ ...base, window: `year_${y.y}`, kind: "year", leftOut: [], value: y.per, months: y.months, from: dm[0].m, to: dm.at(-1).m, complete: y.complete });
      }
      const l12 = D.lastTwelve(ms);
      if (l12) {
        const s = D.span(l12);
        row({ ...base, window: "last_12", kind: "last_12", leftOut: [], value: s.per, months: 12, from: l12[0].m, to: l12[11].m, complete: true });
        if (region.id === g.main && run === "flat" && buy === "rt") proofs.push({ tool: "datacenter", grid, config, region: region.id, stat: "span(lastTwelve).per", page: s.per });
      }
      const full = ys.filter((y) => y.complete).map((y) => y.y);
      for (const [n, kind] of [[3, "avg_3y"], [7, "avg_7y"]]) {
        const want = lastFull(full, n);
        if (!want) continue;
        const dm = done.filter((r) => want.includes(r.m.slice(0, 4)));
        row({ ...base, window: kind, kind, leftOut: [], value: D.span(dm).per, months: dm.length, from: dm[0].m, to: dm.at(-1).m, complete: true });
      }
      if (!done.length) continue;
      const all = D.span(done);
      row({ ...base, window: "all", kind: "all", leftOut: [], value: all.per, months: done.length, from: done[0].m, to: done.at(-1).m, complete: true });
      // a stress event's days taken out of the complete months they fall in: each hour's price and the load's weight
      // in it, as the page's own run computed them (ruled.prices, ruled.weights), subtracted from the sums
      const doneSet = new Set(done.map((r) => r.m));
      const take = (ids) => {
        let cost = all.cost, energy = all.energy;
        for (const id of ids) for (const day of events[id] ?? []) {
          if (!doneSet.has(ym(day))) continue;
          const y = Number(day.slice(0, 4)), p = ruled.prices.get(y), w = ruled.weights.get(y);
          if (!p || !w) continue;
          const i0 = 24 * dayOfYear(day);
          for (let i = i0; i < i0 + 24; i++) if (p[i] !== null && p[i] !== undefined) { cost -= p[i] * w[i]; energy -= w[i]; }
        }
        return energy > 0 ? cost / energy : null;
      };
      const ids = Object.keys(events);
      const windows = ids.map((e) => [`all_less_${e}`, [e]]);
      if (ids.length > 1) windows.push(["all_less_events", ids]);
      for (const [window, left] of windows) row({ ...base, window, kind: "all_less", leftOut: left, value: take(left), months: done.length, from: done[0].m, to: done.at(-1).m, complete: true });
    }
  }
}

fs.writeFileSync(outPath, JSON.stringify({ rows, proofs, inputs: { snapshot: snap.built, datacenter: index.built } }));
console.log(`price-years: ${rows.length} rows, ${proofs.length} proofs`);
