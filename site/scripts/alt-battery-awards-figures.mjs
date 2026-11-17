// Energy Research Warehouse (ERW) site, ruling alternatives of /cost-of-power/battery/awards (session 7705, 17 November
// 2026; wip/alt-battery-awards-* branches, not a default on main). The page's own library (lib/storageawards.ts) run on
// the public tables as the warehouse writes them, cut as the page's reads cut them, so that the figures under the other
// choice are pinned with the site's code. On wip/alt-battery-awards-1: the 2-hour and the 4-hour model beside the awards,
// by month and by year, and the gap in three parts under each; the offers section drawn with both.
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
const model = read(A.MODEL_TABLE, A.MODEL_ENTITY, [...A.MODEL_VARIABLES, ...A.MODEL_VARIABLES_4H]);
const offers = read(A.OFFERS_TABLE, A.ENTITY, A.OFFER_VARIABLES);
const firstOffer = offers.reduce((a, r) => (a === "" || r.ts_utc < a ? r.ts_utc : a), "");
const gapModel = read(A.MODEL_TABLE, A.MODEL_ENTITY, [...A.MODEL_GAP_VARIABLES, ...A.MODEL_GAP_VARIABLES_4H], firstOffer);
const ms2 = A.monthsOf(fleet, model), ms4 = A.monthsOf(fleet, model, A.MODEL_PREFIX_4H);
const y2 = A.years(ms2).find((y) => y.y === "2026"), y4 = A.years(ms4).find((y) => y.y === "2026");
const g2 = A.gapOf(fleet, offers, gapModel), g4 = A.gapOf(fleet, offers, gapModel, A.MODEL_PREFIX_4H);
const month = (ms, m) => ms.find((r) => r.m === m)?.model?.total ?? null;
const parts = (g) => g && { months: g.months, model: g.modelKw, awards: g.awardsKw, gap: g.gapKw, never: g.neverOfferedKw, unawarded: g.offeredNotAwardedKw, price: g.priceKw };
const html = renderToStaticMarkup(createElement(OffersSection, { gap: g2, gap4: g4, unread: null, loaded: true }));
process.stdout.write(JSON.stringify({
  july: [month(ms2, "2026-07"), month(ms4, "2026-07")], january: [month(ms2, "2026-01"), month(ms4, "2026-01")],
  year2026: { months: y2.completeMonths, awards: y2.awardsComplete, model2: y2.modelComplete, model4: y4.modelComplete },
  gap2: parts(g2), gap4: parts(g4),
  drawn: { cells4h: (html.match(/data-offers-part-4h="/g) ?? []).length, sentence: /data-offers-4h="1"/.test(html) },
}));
