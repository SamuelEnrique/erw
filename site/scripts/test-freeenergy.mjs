// Energy Research Warehouse (ERW) site, session 144: the arithmetic of the curtailment page's new sections
// (lib/freeenergy.ts), tested on the real files the builders wrote (data/curtailment/free_energy.json, worth.json and
// shares.json: real prices and real curtailment, nothing made for the test). No request, no browser.
//
//   node scripts/test-freeenergy.mjs
//
//   1. a negative-price hour is counted once: every place's hours under USD 5 hold its hours below zero, the two never
//      pass the hours held, and the heatmap of a whole year adds up to the year's counts, cell by cell once;
//   2. a share never passes 100 percent, and is null from a missing or empty denominator;
//   3. MISO and PJM are named with their words and no number; a place without its window has a reason and no count;
//   4. no point carries a coordinate (none is held, none is made up);
//   5. the gap is the dearest mean less the cheapest over the same hours; the summary pairs are the file's;
//   6. the worth: dollars are MWh times USD per MWh; the battery rule never passes one cycle a day.
// Prints one line per assertion; exits 1 if any fails.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const L = await import("../lib/freeenergy.ts");
const read = (name) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "curtailment", name), "utf8"));
const F = read("free_energy.json"), W = read("worth.json"), S = read("shares.json");

let failed = 0;
const ok = (cond, what) => { console.log(`${cond ? "ok  " : "FAIL"} ${what}`); if (!cond) failed++; };
const close = (a, b, tol = 1e-6) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));

// 1. counted once
const locs = Object.entries(F.grids).flatMap(([g, G]) => G.locations.map((l) => ({ g, ...l })));
ok(locs.length > 0, `${locs.length} places in ${Object.keys(F.grids).length} grids`);
for (const w of ["month", "year"]) {
  const held = locs.filter((l) => L.isHeld(l[w]));
  ok(held.every((l) => l[w].negative <= l[w].under5 && l[w].under5 <= l[w].hours_held && l[w].hours_held <= l[w].hours_in_window),
    `${w}: for each of ${held.length} places, hours below zero <= hours under USD 5 <= hours held <= hours of the window`);
  ok(held.every((l) => L.zeroToFive(l[w]) >= 0 && L.zeroToFive(l[w]) + l[w].negative === l[w].under5), `${w}: hours from zero to under 5 plus hours below zero are the hours under 5`);
  ok(held.every((l) => l[w].hours_held >= F.near_hours * l[w].hours_in_window), `${w}: a count is written only with ${F.near_hours * 100} percent of the window's hours`);
}
const wholeYear = locs.filter((l) => L.isHeld(l.year) && l.heat.whole);
ok(wholeYear.length > 0 && wholeYear.every((l) => l.heat.basis === l.year.basis && L.heatTotal(l.heat, "under5") === l.year.under5 && L.heatTotal(l.heat, "negative") === l.year.negative && L.heatTotal(l.heat, "held") === l.year.hours_held),
  `the heatmap of each of ${wholeYear.length} whole years adds up to the year's hours under 5, below zero and held: an hour is in one cell`);
ok(locs.every((l) => l.heat.under5.length === 12 && l.heat.under5.every((r) => r.length === 24) && l.heat.under5.every((r, m) => r.every((v, h) => l.heat.negative[m][h] <= v && v <= l.heat.held[m][h]))),
  "every heatmap is 12 months by 24 hours, and in each cell below zero <= under 5 <= held");
const one = wholeYear[0];
ok([...Array(12).keys()].reduce((a, m) => a + L.heatMonth(one.heat, "under5", m), 0) === L.heatTotal(one.heat, "under5") && [...Array(24).keys()].reduce((a, h) => a + L.heatHour(one.heat, "under5", h), 0) === L.heatTotal(one.heat, "under5"),
  `${one.entity}: the months' rows and the hours' columns add up to the same ${L.heatTotal(one.heat, "under5")} hours`);
ok(L.cellText({ held: [[0]], under5: [[0]], negative: [[0]] }, ["2026-01"], 0, 0).endsWith("not held"), "a cell with no hour held reads not held, not zero");

// 2. shares
ok(L.share(10, 90) === 10 && L.share(5, 0) === null && L.share(null, 5) === null && L.share(-1, 5) === null && L.share(1e9, 1e-9) <= 100, "share: 10 over 10 plus 90 is 10 percent; no output, a blank or a negative gives none; never above 100");
for (const [g, G] of Object.entries(S.grids)) {
  const ms = Object.entries(G.months);
  ok(ms.length > 0 && ms.every(([, r]) => r.share_pct >= 0 && r.share_pct <= 100), `${g}: each of ${ms.length} monthly shares is from 0 to 100 percent (the highest ${Math.max(...ms.map(([, r]) => r.share_pct))})`);
  ok(ms.every(([, r]) => close(L.share(r.curtailed_mwh, r.output_mwh), r.share_pct, 1e-4)), `${g}: each share is its curtailed MWh over curtailed plus output MWh`);
  ok(ms.every(([, r]) => r.hours_held >= S.near_hours * r.hours_in_month && r.output_mwh > 0), `${g}: each share rests on at least ${S.near_hours * 100} percent of the month's hours and an output above nothing`);
  ok(Object.entries(G.missing).every(([m, why]) => !(m in G.months) && typeof why === "string" && why.length > 10), `${g}: ${Object.keys(G.missing).length} months have no share, each with its reason and no figure`);
}

// 3. named, blank, no number
for (const id of ["miso", "pjm"]) {
  const b = F.blank[id];
  ok(b && !(id in F.grids) && Object.keys(b).sort().join() === "name,regions,words" && !JSON.stringify(b).match(/\d/), `${id}: named (${b?.name}), "${L.blankWords(F, id)}", and not a digit in its entry`);
  ok(!(id in W.grids) && W.blank[id] && !JSON.stringify(W.blank[id]).match(/\d/), `${id}: no worth is computed`);
}
ok(L.blankWords(F, "miso") === "paused while terms are reviewed" && L.blankWords(F, "pjm") === "licensed source needed", "MISO reads paused while terms are reviewed; PJM licensed source needed");
const lacking = locs.filter((l) => !L.isHeld(l.year));
ok(lacking.every((l) => typeof l.year.missing === "string" && l.year.under5 === undefined && l.year.negative === undefined && l.year.mean === undefined), `${lacking.length} places without a whole year: each has its reason and no count`);
ok(Object.values(F.grids).every((G) => L.ranked(G, "year").every((l) => l.kind !== "average") && L.ranked(G, "year").length + L.notHeld(G, "year").length + G.locations.filter((l) => l.kind === "average" && L.isHeld(l.year)).length === G.locations.length),
  "ranked leaves out the averages of hubs, and every other place is ranked or listed with its reason");

// 4. coordinates
ok(locs.every((l) => l.lat === null && l.lon === null) && F.coordinates.held === false, "no place carries a latitude or longitude: none is held and none is made up");
ok(L.shade(5, 10) === 0.5 && L.shade(0, 0) === 0 && L.shade(20, 10) === 1 && L.mostCheap(F, "year") === Math.max(...wholeYear.filter((l) => l.kind !== "average").map((l) => l.year.under5)), "shade is the count over the most of any place, from 0 to 1");

// 5. the gap and the pairs
for (const [g, G] of Object.entries(F.grids)) for (const w of ["month", "year"]) {
  const x = G.gap[w];
  if (!L.hasGap(x)) { ok(typeof x.missing === "string", `${g} ${w}: no gap, with its reason`); continue; }
  const means = Object.values(x.by_place).map((s) => s.mean);
  ok(close(x.gap, Math.max(...means) - Math.min(...means), 1e-9) && x.cheapest.mean === Math.min(...means) && x.dearest.mean === Math.max(...means) && x.hours_common >= F.near_hours * x.hours_in_window,
    `${g} ${w}: the gap ${x.gap} is ${x.dearest.id} less ${x.cheapest.id} over the ${x.hours_common} hours all ${x.places.length} places hold`);
}
const wide = L.widestGap(F, "year");
ok(wide !== null && Object.values(F.grids).every((G) => !L.hasGap(G.gap.year) || G.gap.year.gap <= wide.gap), `the widest gap of the year is ${wide?.grid}'s, ${wide?.gap} USD/MWh`);
const sp = L.summaryPairs(F, "year");
ok(sp.texas !== null && sp.california !== null && sp.texas.west.under5 >= sp.texas.west.negative && sp.california.south.under5 >= sp.california.south.negative,
  `the summary pairs: West Texas ${sp.texas?.west.under5} hours under 5 against Houston ${sp.texas?.houston.under5} (${sp.texas?.kind}); NP15 ${sp.california?.north.under5} against SP15 ${sp.california?.south.under5}`);

// 6. the worth
const ca = W.grids.caiso;
for (const [hub, sides] of Object.entries(ca.hubs)) for (const k of ["rt", "da"]) {
  const ms = Object.entries(sides[k].months ?? {});
  ok(ms.length > 0 && ms.every(([, m]) => m.value_usd === undefined || close(L.valueAgain(m), m.value_usd, 2e-3) || Math.abs(L.valueAgain(m) - m.value_usd) < 0.006 * m.curtailed_mwh_priced),
    `caiso ${hub} ${k}: in each of ${ms.length} months the dollars are the MWh priced times the USD per MWh curtailed`);
  ok(ms.every(([, m]) => m.curtailed_mwh_priced <= m.curtailed_mwh + 0.05 && (m.share_mwh_negative_pct ?? 0) <= (m.share_mwh_under5_pct ?? 100) + 1e-9 && (m.share_mwh_under5_pct ?? 0) <= 100),
    `caiso ${hub} ${k}: MWh priced never pass MWh curtailed; the share below zero never passes the share under 5, nor that 100`);
}
const bm = Object.entries(ca.battery.months);
ok(bm.every(([, r]) => W.durations_hours.every((d) => r.absorb_mwh_per_mw[d] <= L.batteryCeiling(d, r.days_held) + 1e-6)), `the battery rule: in each of ${bm.length} months a battery takes in no more than one cycle a day`);
ok(bm.every(([, r]) => r.absorb_mwh_per_mw["2"] <= r.absorb_mwh_per_mw["4"] && r.absorb_mwh_per_mw["4"] <= r.absorb_mwh_per_mw["8"]), "a longer battery never takes in less");
const fleet = bm.filter(([, r]) => r.fleet);
ok(fleet.length > 0 && fleet.every(([, r]) => W.durations_hours.every((d) => r.fleet.absorb_fleet_mwh[d] <= r.fleet.curtailed_mwh_battery_days + 0.5 && r.fleet.absorb_fleet_pct_of_curtailed[d] <= 100.001)),
  `the fleet: in each of ${fleet.length} months a fleet-sized battery takes in no more than was curtailed`);
ok(fleet.every(([, r]) => r.fleet.fleet_charged_in_curtailed_hours_mwh <= r.fleet.fleet_charged_mwh + 0.5), "what the fleet charged in the curtailed hours never passes what it charged in all hours");
ok(W.grids.spp.missing && !W.grids.spp.hubs && Object.keys(W.grids.ercot.months ?? {}).length === 0 && typeof W.grids.ercot.months_missing === "string", "SPP has no worth (held by day) and ERCOT no month (about nine days held), each with its reason");
ok(L.batteryFill(120, 4, 30) === 100 && L.ratio(1, 0) === null && L.ratio(3, 2) === 150 && L.flatLoad({ price_all_hours_mean: 30, price_curtailed_hours_mean: 10 }).less === 20, "batteryFill, ratio and flatLoad compute as stated");
ok(Object.keys(L.FACE).length === 7 && L.FACE.ercot.whose === "estimate" && L.FACE.caiso.whose === "operator", "the face has one line a grid: the operator's figure, or the ERW's estimate");

console.log(failed ? `${failed} FAILED` : "all passed");
process.exit(failed ? 1 : 0);
