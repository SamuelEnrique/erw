// Energy Research Warehouse (ERW) site, ruling alternatives of /cost-of-power/battery/awards (session 7705, 17 November
// 2026; wip/alt-battery-awards-* branches, not a default on main). The page's own library (lib/storageawards.ts) run on
// the public tables as the warehouse writes them, cut as the page's reads cut them, so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-awards-2: the gap's three parts for each month, and the
// offers section drawn with them.
//   node --import ./scripts/tsx-register.mjs scripts/alt-battery-awards-figures.mjs <tables dir>
import fs from "node:fs";
import path from "node:path";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const A = await import("../lib/storageawards.ts");
const { OffersSection } = await import("../app/cost-of-power/battery/awards/Offers.tsx");
const dir = process.argv[2];
function read(table, entity, variables, from = "") {
  const want = new Set(variables), rows = [];
  let head = null;
  for (const line of fs.readFileSync(path.join(dir, `${table}.csv`), "utf-8").split(/\r?\n/)) {
    if (!line || line.startsWith("#")) continue;
    if (!head) { head = line; continue; }
    const c = line.split(",");
    if (c[0] !== entity || !want.has(c[1]) || (from && c[2] < from)) continue;
    rows.push({ variable: c[1], ts_utc: c[2], value: c[3] });
  }
  return rows;
}
const fleet = read(A.TABLE, A.ENTITY, A.VARIABLES);
const offers = read(A.OFFERS_TABLE, A.ENTITY, A.OFFER_VARIABLES);
const firstOffer = offers.reduce((a, r) => (a === "" || r.ts_utc < a ? r.ts_utc : a), "");
const gapModel = read(A.MODEL_TABLE, A.MODEL_ENTITY, A.MODEL_GAP_VARIABLES, firstOffer);
const all = A.gapOf(fleet, offers, gapModel);
const byMonth = A.gapByMonth(fleet, offers, gapModel);
const html = renderToStaticMarkup(createElement(OffersSection, { gap: all, gapMonths: byMonth, unread: null, loaded: true }));
process.stdout.write(JSON.stringify({
  together: { months: all.months, gap: all.gapKw, never: all.neverOfferedKw, unawarded: all.offeredNotAwardedKw, price: all.priceKw, leftOut: all.leftOut.map((x) => x.m) },
  byMonth: byMonth.map((g) => ({ m: g.months[0], gap: g.gapKw, never: g.neverOfferedKw, unawarded: g.offeredNotAwardedKw, price: g.priceKw })),
  drawn: (html.match(/data-offers-month-part="/g) ?? []).length,
}));
