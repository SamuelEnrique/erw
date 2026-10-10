// Energy Research Warehouse (ERW) site, session 183: "What a generator earns" priced at the hub or zone chosen.
//
//   node --import ./scripts/alias-register.mjs scripts/test-seller-hubs.mjs            (from site/; exit 1 on a failure)
//
// On the site's own files (data/merchant_snapshot.json, data/seller/capture.json, data/seller/hubs), which hold real
// rows only:
//   main       the builder of the hub files, run at each grid's main hub, gives the page's snapshot month for month
//              (the check the builder wrote into the index): the hub files and the snapshot are one model
//   every hub  every hub and zone of the capture file but the main one has a model, in the market the page shows its
//              capture price in; each file's months lie on the grid's hourly index
//   aligned    a month's flat price is the mean of the hub's own hourly prices over the month's indices, and the
//              default peaker's month is the peaker computed again from the hourly prices and Henry Hub: the months,
//              the prices and Henry Hub of a file are one hub's
//   one hub    a month's flat price in a hub's model is the capture file's for that hub and market wherever both use
//              the same hours (the flat price does not depend on the weights); and the model's own capture price of
//              the last twelve months (sales over energy) is the capture file's to within the difference of the two
//              weights (output per MW of nameplate against generation; widest for SPP, whose solar fleet grew fastest)
//   moves      choosing another hub changes revenue of the last twelve months and debt coverage, and revenue equals
//              the model's capture price times its energy
// Prints one line of JSON with what it measured.
import fs from "node:fs";
import * as C from "../lib/capture.ts";
import * as HB from "../lib/sellerhubs.ts";
import * as M from "../lib/merchant.ts";
import * as S from "../lib/seller2.ts";

const read = (rel) => JSON.parse(fs.readFileSync(new URL(`../data/${rel}`, import.meta.url), "utf-8"));
const snap = read("merchant_snapshot.json"), cap = read("seller/capture.json"), index = read("seller/hubs/index.json");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } };
const out = { grids: {}, hubs: 0, moved: 0, compared: 0, worstCapture: 0, worstFlat: 0, worstPeaker: 0, flatMonths: 0, worstHubFlat: 0 };

// the page's rule for the market shown first (app/cost-of-power/seller/page.tsx, `mk`)
const cap12 = (h, f, m) => C.twelve(h[m]?.[f], cap.near);
const has = (h, m) => C.FUELS.some((f) => Object.keys(h[m]?.[f] ?? {}).length > 0);
const whole12 = (h, m) => C.FUELS.some((f) => cap12(h, f, m) !== null);
const marketOf = (h) => (whole12(h, "rt") ? "rt" : whole12(h, "da") ? "da" : has(h, "rt") || !has(h, "da") ? "rt" : "da");

for (const [iso, cg] of Object.entries(cap.grids)) {
  const ig = index.grids[iso];
  check(!!ig, `${iso}: the hub files hold the grid`);
  if (!ig) continue;
  // main: the builder at the main hub is the snapshot
  // (a month is compared when both hold the same hours of it; the peaker moves with Henry Hub's later days; New York's
  // main hub is read from another real-time table here than in the snapshot, and is reported, not held)
  const assets = Object.entries(ig.check ?? {}).filter(([a]) => a !== "peaker").map(([, c]) => c);
  const worst = Math.max(0, ...assets.map((c) => c.max_abs_usd_per_mw));
  const months = Math.min(...assets.filter((c) => c.months > 0).map((c) => c.months), Infinity);
  const peaker = ig.check?.peaker ?? null;
  out.grids[iso] = { main_months: months, main_worst_usd_per_mw: worst, main_hours_differ: Math.max(0, ...assets.map((c) => c.hours_differ ?? 0)), peaker_worst_share: peaker?.max_share ?? null, hubs: Object.keys(ig.hubs).length };
  if (iso !== "nyiso") {
    check(ig.check && months >= 12 && worst <= 0.0001, `${iso}: the builder at the main hub equals the snapshot on every month both hold whole (${months} months, largest difference USD ${worst} per MW)`);
    check(peaker && peaker.months >= 12 && peaker.max_share <= 0.01, `${iso}: the peaker at the main hub is the snapshot's to within Henry Hub's later days (${peaker?.max_share})`);
  } else check(!!ig.check, "nyiso: the main hub's check is written");
  const grid = read(`seller/hubs/${ig.file}`);
  const x = M.inputsOf({ iso, asset: iso === "nyiso" ? "wind" : "solar" });
  const perMw = { ...x, mw: 1, ds: 0, fom: 0 };
  const mainSpan = S.spans(M.months(snap, perMw)).twelve, mainCover = M.ttm(M.months(snap, x), x.ds).at(-1)?.dscr ?? null;
  for (const h of cg.hubs) {
    if (h.id === cg.main) { check(!ig.hubs[h.id], `${iso}: the main hub has no hub file (the page keeps its snapshot there)`); continue; }
    const e = ig.hubs[h.id];
    check(!!e, `${iso} ${h.id}: a hub of the capture file has a model`);
    if (!e) continue;
    out.hubs += 1;
    check(e.market === marketOf(h), `${iso} ${h.id}: the model's market (${e.market}) is the market the page shows the capture price in (${marketOf(h)})`);
    const file = read(`seller/hubs/${e.file}`);
    check(file.id === h.id && file.market === e.market && file.price.length === grid.hours && grid.hh.length === grid.hours, `${iso} ${h.id}: the file is this hub's, on the grid's hourly index`);
    check(Object.keys(file.months).every((m) => grid.months[m]), `${iso} ${h.id}: every month lies on the grid's index`);
    const s = HB.hubIso(snap.isos[iso], grid, file), priced = HB.withHub(snap, iso, s);
    // aligned: the flat price and the peaker from the hourly arrays
    for (const [m, r] of Object.entries(s.months)) {
      let sum = 0, k = 0;
      for (let i = r.i0; i < r.i1; i++) { const p = s.price[i]; if (p !== null && p !== undefined) { sum += p; k += 1; } }
      if (k) { const d = Math.abs(sum / k - r.flat); if (d > out.worstFlat) out.worstFlat = d; }
      if (r.peaker) {
        const p = M.peakerOver(s, r.i0, r.i1, M.HEAT_RATE, M.VOM);
        const d = Math.abs(p.revenue - r.peaker.revenue_per_mw) / Math.max(1, Math.abs(r.peaker.revenue_per_mw));
        if (d > out.worstPeaker) out.worstPeaker = d;
        check(p.hours === r.peaker.hours, `${iso} ${h.id} ${m}: the peaker's hours from the arrays (${p.hours}) are the month's (${r.peaker.hours})`);
      }
    }
    // one price: a month's flat price does not depend on the weights, so where the model and the capture file use the
    // same hours of a month their flat prices are one number
    for (const f of C.FUELS) {
      for (const [m, rec] of Object.entries(h[e.market]?.[f] ?? {})) {
        const mine = s.months[m]?.[f];
        if (!mine || mine.hours !== rec[0] || !rec[0]) continue;
        const d = Math.abs(mine.flat_price - rec[2] / rec[0]);
        out.flatMonths += 1;
        if (d > out.worstHubFlat) out.worstHubFlat = d;
      }
    }
    // one hub, and it moves
    const span = S.spans(M.months(priced, perMw)).twelve;
    const fuel = x.asset, c12 = cap12(h, fuel, e.market);
    if (span && c12 && span.capture !== null && span.from === c12.from && span.to === c12.to) {
      const own = Math.abs(span.capture - c12.price) / Math.abs(c12.price);
      out.compared += 1;
      if (own > out.worstCapture) out.worstCapture = own;
      check(own < 0.06, `${iso} ${h.id}: the model's capture price at the hub (${span.capture.toFixed(2)}) is the capture file's (${c12.price.toFixed(2)}) to within 6 percent`);
      check(Math.abs(span.revenue_kw * 1000 - span.capture * span.energy) < 1e-6 * Math.max(1, Math.abs(span.revenue_kw * 1000)), `${iso} ${h.id}: revenue is the capture price times the energy`);
    }
    if (span && mainSpan && span.from === mainSpan.from) {
      const cover = M.ttm(M.months(priced, x), x.ds).at(-1)?.dscr ?? null;
      if (Math.abs(span.revenue_kw - mainSpan.revenue_kw) > 0.005 && cover !== null && mainCover !== null && Math.abs(cover - mainCover) > 1e-9) out.moved += 1;
    }
  }
}
check(out.worstFlat < 0.006, `a month's flat price is the mean of the hub's hourly prices (largest difference USD ${out.worstFlat.toFixed(4)} per MWh)`);
check(out.flatMonths >= 1000 && out.worstHubFlat < 0.006, `a hub's month has the capture file's flat price for that hub and market wherever the two use the same hours (${out.flatMonths} months, largest difference USD ${out.worstHubFlat.toFixed(4)} per MWh)`);
check(out.worstPeaker < 0.002, `the default peaker's month is the peaker computed from the hourly arrays (largest relative difference ${out.worstPeaker.toExponential(2)})`);
check(out.hubs >= 30 && out.compared >= 12 && out.moved >= 12, `hubs with a model ${out.hubs}; set beside the capture file ${out.compared}; where revenue and debt coverage move with the hub ${out.moved}`);
// ERCOT's West hub by name: the page's example
{
  const iso = "ercot", e = index.grids[iso]?.hubs.HB_WEST;
  if (e) {
    const grid = read(`seller/hubs/${index.grids[iso].file}`), file = read(`seller/hubs/${e.file}`);
    const priced = HB.withHub(snap, iso, HB.hubIso(snap.isos[iso], grid, file));
    const x = M.inputsOf({});
    const one = (sn) => ({ kw: S.spans(M.months(sn, { ...x, mw: 1, ds: 0, fom: 0 })).twelve?.revenue_kw ?? null, cover: M.ttm(M.months(sn, x), x.ds).at(-1)?.dscr ?? null });
    out.west = { main: one(snap), hub: one(priced), market: e.market, stress: (M.stress(priced, x) ?? []).length };
    check(out.west.hub.kw !== null && out.west.hub.kw < out.west.main.kw && out.west.hub.cover < out.west.main.cover, "ERCOT solar at the West hub earns less and covers less debt than at the hub average");
    check(out.west.stress === 3, "ERCOT's West hub holds the three stress events");
  } else check(false, "ERCOT's West hub has a model");
}
const text = `${JSON.stringify(out)}\n${bad ? `FAILED: ${bad} of ${n}` : `ok: ${n} checks`}\n`;
await new Promise((done) => process.stdout.write(text, done));
process.exit(bad ? 1 : 0);
