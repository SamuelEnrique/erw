// Energy Research Warehouse (ERW) site, session 7505 (chain 304): every figure of /cost-of-power/battery/awards (what
// Texas's storage resources were awarded day-ahead, what they offered, and the real-time side), as the page computes it.
//
//   node --import ./scripts/tsx-register.mjs scripts/battery-awards-figures.mjs <tables dir> [out.json]
//
// <tables dir> holds the five public tables the page reads, as the warehouse writes them (CSV with a # header):
// ercot_storage_dam_awards_monthly, battery_stack_monthly, ercot_storage_dam_offers_monthly, ercot_storage_rt_monthly and
// ercot_storage_node_basis. The rows are cut to what the page's five reads ask the live set for (the table, the entity,
// the variables), and the page's own functions are run on them: lib/storageawards.ts and lib/storagerealtime.ts for
// every number, and the two section components the page mounts (app/cost-of-power/battery/awards/Offers.tsx and
// RealTime.tsx) drawn to HTML, in which every figure of those two sections is then looked for as the page writes it.
// The page itself (page.tsx) is an async server component and does not draw here: its cells are written below with the
// same library calls, cell by cell. Prints, or writes to out.json, one object:
//   { tables: {table: its "Retrieved" stamp}, figures: {key: text as shown}, words: {key: sentence}, drawn: {...} }
// replication/battery_awards/replicate.py compares it with its own computation. No network, no table written.
import fs from "node:fs";
import path from "node:path";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const A = await import("../lib/storageawards.ts");
const R = await import("../lib/storagerealtime.ts");
const { OffersSection } = await import("../app/cost-of-power/battery/awards/Offers.tsx");
const { RealTimeSection } = await import("../app/cost-of-power/battery/awards/RealTime.tsx");

const dir = process.argv[2];
const outFile = process.argv[3];
if (!dir) { console.error("usage: battery-awards-figures.mjs <tables dir> [out.json]"); process.exitCode = 2; }

const stamps = {};
/** The rows of one table as the page's read asks for them: one entity, the named variables, optionally from a month on. */
function read(table, entity, variables, from = "") {
  const text = fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8");
  const want = new Set(variables), rows = [];
  let head = null;
  for (const line of text.split(/\r?\n/)) {
    if (!line) continue;
    if (line.startsWith("#")) { const m = /^# Retrieved: (\S+)/.exec(line); if (m && !stamps[table]) stamps[table] = m[1]; continue; }
    if (!head) { head = line.split(","); continue; }
    const c = line.split(",");  // the first four columns hold no comma in these tables
    if (c[0] !== entity || !want.has(c[1]) || (from && c[2] < from)) continue;
    rows.push({ variable: c[1], ts_utc: c[2], value: c[3] });
  }
  return rows.sort((a, b) => (a.variable < b.variable ? -1 : a.variable > b.variable ? 1 : a.ts_utc < b.ts_utc ? -1 : 1));
}

if (dir) {
  const fleet = read(A.TABLE, A.ENTITY, A.VARIABLES);
  const model = read(A.MODEL_TABLE, A.MODEL_ENTITY, A.MODEL_VARIABLES);
  const offers = read(A.OFFERS_TABLE, A.ENTITY, A.OFFER_VARIABLES);
  const rt = read(R.RT_TABLE, R.RT_ENTITY, R.RT_VARIABLES);
  const basisRows = read(R.BASIS_TABLE, R.BASIS_ENTITY, R.BASIS_VARIABLES);
  const firstOffer = offers.reduce((a, r) => (a === "" || r.ts_utc < a ? r.ts_utc : a), "");
  const gapModel = firstOffer ? read(A.MODEL_TABLE, A.MODEL_ENTITY, A.MODEL_GAP_VARIABLES, firstOffer) : [];

  const fig = {}, words = {}, section = {};
  const put = (sec, key, shown) => { fig[key] = String(shown); section[key] = sec; };
  const { kw, whole, usd, pct, span, monthName } = A;
  const two = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const one = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const points = (v) => (v * 100).toFixed(1);
  const mwh = (v) => Math.round(v).toLocaleString("en-US");
  const signed = (v) => (v > 0 ? "+" : "") + kw(v);

  // 1. the head of the page (page.tsx): the sentence, the chart's labels, "By month", "By year", "Why the two differ"
  const ms = A.monthsOf(fleet, model), ys = A.years(ms), newest = A.newestComplete(ms), share = A.energyAwardShare(ms);
  words["summary"] = A.summary(ms) ?? "";
  for (const r of ms) {
    put("page", `month|${r.m}|days_held`, r.daysHeld); put("page", `month|${r.m}|days_in_month`, r.daysInMonth);
    if (r.resources !== null) put("page", `month|${r.m}|resources`, whole(r.resources));
    if (r.mw !== null) put("page", `month|${r.m}|mw`, whole(r.mw));
    put("page", `month|${r.m}|energy_kw`, kw(r.energy)); put("page", `month|${r.m}|ancillary_kw`, kw(r.ancillary));
    put("page", `month|${r.m}|total_kw`, kw(r.total));  // also the bar's label in the chart
    if (r.model !== null) put("page", `month|${r.m}|model_kw`, kw(r.model.total));
    words[`month|${r.m}|state`] = `${r.complete ? "whole" : "partial"}; the model's month ${r.model === null ? "not held" : r.model.whole ? "whole" : "partial"}`;
  }
  for (const r of ys) {
    put("page", `year|${r.y}|days_held`, r.daysHeld); put("page", `year|${r.y}|days_in_months`, r.daysInMonths);
    put("page", `year|${r.y}|energy_kw`, kw(r.energy)); put("page", `year|${r.y}|ancillary_kw`, kw(r.ancillary)); put("page", `year|${r.y}|total_kw`, kw(r.total));
    words[`year|${r.y}|months_whole`] = r.completeMonths.length ? span(r.completeMonths) : "none";
    if (r.awardsComplete !== null) put("page", `year|${r.y}|awarded_whole_kw`, kw(r.awardsComplete));
    if (r.modelComplete !== null) put("page", `year|${r.y}|model_whole_kw`, kw(r.modelComplete));
    else words[`year|${r.y}|model`] = `not set beside it: ${r.noModel}`;
    if (r.modelComplete !== null && r.awardsComplete !== null && r.modelComplete > 0) put("page", `year|${r.y}|share_of_model_pct`, Math.round((r.awardsComplete / r.modelComplete) * 100));
  }
  if (share) { put("page", "share|energy_award_pct", (share.share * 100).toFixed(1)); put("page", "share|with_award", whole(share.withAward)); put("page", "share|resource_hours", whole(share.hours)); }
  if (newest && newest.resources !== null && newest.resourcesWithAward !== null) {
    words["newest|month"] = newest.m; put("page", "newest|resources_with_award", whole(newest.resourcesWithAward)); put("page", "newest|resources", whole(newest.resources));
  }

  // 2. the offers section (Offers.tsx)
  const g = fleet.length && offers.length && gapModel.length ? A.gapOf(fleet, offers, gapModel) : null;
  if (g) {
    const e = g.energy, of = (v) => (g.gapKw !== 0 ? pct(v / g.gapKw) : "");
    words["offers|months"] = span(g.months); words["offers|left_out"] = g.leftOut.map((x) => `${x.m} (${x.why})`).join("; ");
    put("offers", "offers|model_kw", usd(g.modelKw)); put("offers", "offers|awards_kw", usd(g.awardsKw)); put("offers", "offers|gap_kw", usd(g.gapKw));
    for (const [k, v] of [["never", g.neverOfferedKw], ["unawarded", g.offeredNotAwardedKw], ["price", g.priceKw]]) { put("offers", `offers|part|${k}_kw`, usd(v)); put("offers", `offers|part|${k}_share_pct`, of(v).replace("%", "")); }
    put("offers", "offers|no_offer_points", points(g.noOfferShare)); put("offers", "offers|no_offer_out_points", points(g.noOfferOutShare));
    put("offers", "offers|awards_usd_per_mwh", two(e.awardsUsdPerMwh)); put("offers", "offers|model_usd_per_mwh", two(e.modelUsdPerMwh));
    put("offers", "offers|energy_offer_share_pct", pct(g.energyOfferShare).replace("%", "")); put("offers", "offers|offered_mwh_per_mw_day", one(e.offeredPerMwDay));
    put("offers", "offers|model_mwh_per_mw_day", two(e.modelPerMwDay)); put("offers", "offers|at_clearing_mwh_per_mw_day", two(e.atClearingPerMwDay)); put("offers", "offers|sold_mwh_per_mw_day", two(e.soldPerMwDay));
    if (e.above1000 !== null) put("offers", "offers|above_1000_pct", pct(e.above1000).replace("%", ""));
    if (e.above100 !== null) put("offers", "offers|above_100_pct", pct(e.above100).replace("%", ""));
    for (const b of e.bands) { const k = b.le === null ? "any" : `le_${b.le}`; put("offers", `offers|band|${k}|mwh_per_mw_day`, two(b.perMwDay)); put("offers", `offers|band|${k}|share_pct`, pct(b.shareOfOffered, 1).replace("%", "")); }
    for (const s of g.services) {
      put("offers", `offers|service|${s.key}|offer_share_pct`, pct(s.offerShare, 1).replace("%", "")); put("offers", `offers|service|${s.key}|le_clearing_share_pct`, pct(s.atOrBelowClearingShare, 1).replace("%", ""));
      put("offers", `offers|service|${s.key}|award_share_pct`, pct(s.awardShare, 1).replace("%", "")); put("offers", `offers|service|${s.key}|award_of_offer_pct`, pct(s.awardOfOffer, 1).replace("%", ""));
      put("offers", `offers|service|${s.key}|awards_kw`, usd(s.awardsKw)); put("offers", `offers|service|${s.key}|model_kw`, usd(s.modelKw));
      put("offers", `offers|service|${s.key}|gap_kw`, usd(s.gapKw)); put("offers", `offers|service|${s.key}|unawarded_kw`, usd(s.unawardedKw));
    }
    put("offers", "offers|award_of_offer_low_pct", pct(Math.min(...g.services.map((s) => s.awardOfOffer))).replace("%", ""));
    put("offers", "offers|award_of_offer_high_pct", pct(Math.max(...g.services.map((s) => s.awardOfOffer))).replace("%", ""));
    put("offers", "offers|as_offer_share_of_limit_pct", pct(g.asOfferShareOfLimit).replace("%", "")); put("offers", "offers|as_award_share_of_limit_pct", pct(g.asAwardShareOfLimit).replace("%", ""));
    words["offers|covered"] = g.services.filter((s) => s.gapKw > 0 && s.unawardedKw >= s.gapKw).map((s) => s.key).join(",");
    words["offers|short"] = g.services.filter((s) => s.gapKw > 0 && s.unawardedKw < s.gapKw).map((s) => `${s.key} ${pct(s.unawardedKw / s.gapKw)}`).join(",");
  }

  // 3. the real-time section (RealTime.tsx)
  const rms = R.rtMonthsOf(rt, model, A.MODEL_PREFIX), basis = R.basisOf(basisRows);
  if (rms.length) {
    const total = R.rtTotal(rms), energy = R.rtEnergy(rms), anc = R.rtAncillary(rms);
    words["rt|months"] = span(rms.map((r) => r.m)); put("rt", "rt|days_held", whole(rms.reduce((a, r) => a + r.daysHeld, 0)));
    if (total) {
      words["rt|whole_months"] = span(total.months);
      put("rt", "rt|whole|dayahead_kw", usd(total.dayAhead / 1000)); put("rt", "rt|whole|deviation_kw", usd(Math.abs(total.deviationHub) / 1000)); put("rt", "rt|whole|market_kw", usd(total.marketHub / 1000));
      if (total.model !== null) put("rt", "rt|whole|model_kw", usd(total.model / 1000));
    }
    for (const r of rms) {
      put("rt", `rt|month|${r.m}|days_held`, r.daysHeld); put("rt", `rt|month|${r.m}|days_in_month`, r.daysInMonth);
      if (r.mw !== null) put("rt", `rt|month|${r.m}|mw`, whole(r.mw));
      put("rt", `rt|month|${r.m}|dayahead_kw`, kw(r.dayAhead)); put("rt", `rt|month|${r.m}|deviation_kw`, signed(r.deviationHub)); put("rt", `rt|month|${r.m}|market_kw`, kw(r.marketHub));
      if (r.complete && r.model !== null && r.model.whole) { put("rt", `rt|month|${r.m}|model_kw`, kw(r.model.total)); if (r.model.total > 0) put("rt", `rt|month|${r.m}|share_of_model_pct`, pct(r.marketHub / r.model.total).replace("%", "")); }
      if (r.discharged !== null) put("rt", `rt|month|${r.m}|discharged_mwh`, mwh(r.discharged));
      if (r.sold !== null) put("rt", `rt|month|${r.m}|sold_mwh`, mwh(r.sold));
      if (r.sold !== null && r.discharged !== null && r.discharged > 0) put("rt", `rt|month|${r.m}|sold_of_discharged_pct`, pct(r.sold / r.discharged).replace("%", ""));
      if (r.charged !== null) put("rt", `rt|month|${r.m}|charged_mwh`, mwh(r.charged));
      if (r.bought !== null) put("rt", `rt|month|${r.m}|bought_mwh`, mwh(r.bought));
      if (r.nodeLessHubSold !== null && r.nodeLessHubBought !== null) { put("rt", `rt|month|${r.m}|node_less_hub_sold`, usd(r.nodeLessHubSold)); put("rt", `rt|month|${r.m}|node_less_hub_bought`, usd(r.nodeLessHubBought)); }
    }
    if (energy) {
      put("rt", "rt|energy|days", whole(energy.days)); put("rt", "rt|energy|discharged_mwh", mwh(energy.discharged)); put("rt", "rt|energy|sold_mwh", mwh(energy.sold));
      put("rt", "rt|energy|charged_mwh", mwh(energy.charged)); put("rt", "rt|energy|bought_mwh", mwh(energy.bought));
      if (energy.soldOfDischarged !== null) put("rt", "rt|energy|sold_of_discharged_pct", pct(energy.soldOfDischarged).replace("%", ""));
      if (energy.dischargedPerMwDay !== null) put("rt", "rt|energy|discharged_mwh_per_mw_day", two(energy.dischargedPerMwDay));
      // at 1 the page says it in words ("every one of the resource-intervals"), with no figure
      if (energy.pricedShare !== null) { if (energy.pricedShare === 1) words["rt|energy|priced"] = "every one"; else put("rt", "rt|energy|priced_share_pct", pct(energy.pricedShare, 2).replace("%", "")); }
    }
    for (const a of anc) { put("rt", `rt|as|${a.key}|real_time_mwh`, mwh(a.realTime)); put("rt", `rt|as|${a.key}|day_ahead_mwh`, mwh(a.dayAhead)); put("rt", `rt|as|${a.key}|imbalance_mwh`, (a.imbalance > 0 ? "+" : "") + mwh(a.imbalance)); }
  }
  if (basis) {
    words["basis|from"] = basis.from; put("rt", "basis|nodes", whole(basis.nodes));
    for (const [k, v, f] of [["nodes_with_spread", basis.nodesWithSpread, whole], ["whole_days", basis.wholeDays, whole], ["spread_hub", basis.spreadHub, two], ["spread_node_median", basis.spreadMedian, two],
      ["spread_node_p10", basis.spreadP10, two], ["spread_node_p90", basis.spreadP90, two], ["nodes_spread_above_hub", basis.aboveHub, whole], ["mean_abs_difference_median", basis.meanAbsDifference, two]]) if (v !== null) put("rt", `basis|${k}`, f(v));
  }

  // 4. the two sections drawn with the page's own components: every figure of theirs is in the HTML as written above
  const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");
  const offersHtml = renderToStaticMarkup(h(OffersSection, { gap: g, unread: null, loaded: offers.length > 0 }));
  const rtHtml = renderToStaticMarkup(h(RealTimeSection, { months: rms, basis, unread: null, basisUnread: null }));
  const drawnText = { offers: text(offersHtml), rt: text(rtHtml) };
  const missing = [];
  let looked = 0;
  for (const [k, shown] of Object.entries(fig)) {
    const sec = section[k];
    if (sec === "page") continue;
    looked++;
    if (!drawnText[sec].includes(shown)) missing.push(`${k}=${shown}`);
  }
  words["rt|coverage_sentence"] = (/Held: [^.]*\./.exec(drawnText.rt) ?? [""])[0];
  words["basis|sentence"] = (/It is not from the months above[^.]*\./.exec(drawnText.rt) ?? [""])[0];
  const out = { tables: stamps, figures: fig, words, drawn: { looked, found: looked - missing.length, missing, offers_bytes: offersHtml.length, rt_bytes: rtHtml.length } };
  const json = JSON.stringify(out, null, 1);
  if (outFile) { fs.writeFileSync(outFile, json + "\n"); console.log(`${Object.keys(fig).length} figures, ${Object.keys(words).length} sentences; drawn sections: ${looked - missing.length} of ${looked} found${missing.length ? `; missing: ${missing.join(", ")}` : ""}; written to ${outFile}`); }
  else console.log(json);
  if (missing.length) process.exitCode = 1;
}
