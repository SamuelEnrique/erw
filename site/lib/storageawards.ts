// Energy Research Warehouse (ERW) site, session 115: what Texas's storage resources were awarded day-ahead
// (/cost-of-power/battery/awards, in review).
//
// The arithmetic of the page, on the rows of ercot_storage_dam_awards_monthly (warehouse/derived, from ERCOT's 60-Day
// DAM Disclosure Reports, the file 60d_DAM_ESR_Data) and, beside them, the battery model's day-ahead schedule for a
// 2-hour battery from battery_stack_monthly. Pure functions, no imports (Node runs this file as it is, for
// tests/test_session115_page.py). Nothing is scaled, filled or estimated: a month whose days are not all held is
// partial and is never set beside the model, whose month is whole; a figure that is not held is null.

export const TABLE = "ercot_storage_dam_awards_monthly";
export const ENTITY = "ercot:esr_fleet";
export const MODEL_TABLE = "battery_stack_monthly";
export const MODEL_ENTITY = "ercot:HB_HUBAVG";
/** The model's rows the page reads: the day-ahead schedule, a 2-hour battery, USD per MW by month, and its days. */
export const MODEL_PREFIX = "dayahead_2h_";
export const MODEL_VARIABLES = ["revenue_total_usd_per_mw", "revenue_energy_usd_per_mw", "revenue_ancillary_usd_per_mw", "days_held", "days_in_month"].map((v) => MODEL_PREFIX + v);
/** The fleet's variables the page reads. */
export const VARIABLES = [
  "days_held", "days_missing", "days_in_month", "resources", "resources_with_award", "resource_hours", "resource_hours_energy_award", "mw",
  "revenue_energy_usd_per_mw", "revenue_ancillary_usd_per_mw", "revenue_total_usd_per_mw",
  "revenue_regup_usd_per_mw", "revenue_regdn_usd_per_mw", "revenue_rrs_usd_per_mw", "revenue_ecrs_usd_per_mw", "revenue_nspin_usd_per_mw",
];
export const PRODUCTS: { key: string; label: string }[] = [
  { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "rrs", label: "Responsive Reserve" },
  { key: "ecrs", label: "ECRS" }, { key: "nspin", label: "Non-Spin" },
];

/** A row of a series table as the live set serves it. */
export type Row = { variable: string; ts_utc: string; value: number | string };

/** The model's figure for one month, USD per MW, and whether the model holds every day of it. */
export type Model = { energy: number | null; ancillary: number | null; total: number; whole: boolean };

export type Month = {
  /** YYYY-MM, the local (Central) month */
  m: string;
  daysHeld: number; daysMissing: number | null; daysInMonth: number;
  /** every day of the month is held */
  complete: boolean;
  resources: number | null; resourcesWithAward: number | null; resourceHours: number | null; resourceHoursEnergy: number | null;
  mw: number | null;
  /** day-ahead awards, USD per MW of the fleet: energy net of charging, the ancillary services together, and their sum */
  energy: number; ancillary: number; total: number;
  products: Record<string, number | null>;
  model: Model | null;
};

export type Year = {
  y: string;
  /** every month held, partial ones with the days they hold */
  months: number; daysHeld: number; daysInMonths: number;
  energy: number; ancillary: number; total: number;
  /** the complete months, and over them the awards and the model's figure for the same months (USD per MW) */
  completeMonths: string[]; awardsComplete: number | null; modelComplete: number | null;
  /** why no model figure stands beside the year, when none does */
  noModel: string | null;
};

const num = (v: number | string | null | undefined): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

/** The months of the table, oldest first, each with the model's figure for the same month where the model holds one.
 * A month without its days or without its three per-MW sums is not a month the page can show, and is left out. */
export function monthsOf(rows: Row[], model: Row[] = []): Month[] {
  const by = new Map<string, Map<string, number>>();
  for (const r of rows) {
    const v = num(r.value);
    if (v === null) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, new Map());
    by.get(m)!.set(r.variable, v);
  }
  const mod = new Map<string, Map<string, number>>();
  for (const r of model) {
    const v = num(r.value);
    if (v === null || !r.variable.startsWith(MODEL_PREFIX)) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!mod.has(m)) mod.set(m, new Map());
    mod.get(m)!.set(r.variable.slice(MODEL_PREFIX.length), v);
  }
  const out: Month[] = [];
  for (const m of [...by.keys()].sort()) {
    const g = by.get(m)!;
    const get = (k: string) => (g.has(k) ? g.get(k)! : null);
    const daysHeld = get("days_held"), daysInMonth = get("days_in_month");
    const energy = get("revenue_energy_usd_per_mw"), ancillary = get("revenue_ancillary_usd_per_mw"), total = get("revenue_total_usd_per_mw");
    if (daysHeld === null || daysInMonth === null || energy === null || ancillary === null || total === null) continue;
    const x = mod.get(m);
    const mt = x?.get("revenue_total_usd_per_mw");
    const model: Model | null = x && mt !== undefined
      ? { total: mt, energy: x.get("revenue_energy_usd_per_mw") ?? null, ancillary: x.get("revenue_ancillary_usd_per_mw") ?? null,
          whole: x.get("days_held") !== undefined && x.get("days_held") === x.get("days_in_month") }
      : null;
    out.push({
      m, daysHeld, daysMissing: get("days_missing"), daysInMonth, complete: daysHeld === daysInMonth,
      resources: get("resources"), resourcesWithAward: get("resources_with_award"), resourceHours: get("resource_hours"), resourceHoursEnergy: get("resource_hours_energy_award"),
      mw: get("mw"), energy, ancillary, total,
      products: Object.fromEntries(PRODUCTS.map((p) => [p.key, get(`revenue_${p.key}_usd_per_mw`)])),
      model,
    });
  }
  return out;
}

/** By calendar year: the sum of the months' per-MW figures over every day held; and, over the complete months only,
 * the awards beside the model's figure for the same months. A partial month is never scaled to a whole one. */
export function years(ms: Month[]): Year[] {
  const out: Year[] = [];
  for (const y of [...new Set(ms.map((r) => r.m.slice(0, 4)))].sort()) {
    const all = ms.filter((r) => r.m.startsWith(y));
    const full = all.filter((r) => r.complete);
    const sum = (rs: Month[], f: (r: Month) => number) => rs.reduce((a, r) => a + f(r), 0);
    const lacking = full.filter((r) => !r.model || !r.model.whole).map((r) => r.m);
    const noModel = !full.length ? "no month of the year is held whole"
      : lacking.length ? `the model does not hold every day of ${lacking.join(", ")}` : null;
    out.push({
      y, months: all.length, daysHeld: sum(all, (r) => r.daysHeld), daysInMonths: sum(all, (r) => r.daysInMonth),
      energy: sum(all, (r) => r.energy), ancillary: sum(all, (r) => r.ancillary), total: sum(all, (r) => r.total),
      completeMonths: full.map((r) => r.m),
      awardsComplete: full.length ? sum(full, (r) => r.total) : null,
      modelComplete: noModel ? null : sum(full, (r) => r.model!.total),
      noModel,
    });
  }
  return out;
}

/** The newest month held whole, or null. */
export function newestComplete(ms: Month[]): Month | null {
  const full = ms.filter((r) => r.complete);
  return full.length ? full[full.length - 1] : null;
}

/** The share of resource-hours that hold a day-ahead energy award, over every month that states both counts; null
 * when none does. */
export function energyAwardShare(ms: Month[]): { hours: number; withAward: number; share: number } | null {
  const rs = ms.filter((r) => r.resourceHours !== null && r.resourceHoursEnergy !== null && r.resourceHours > 0);
  if (!rs.length) return null;
  const hours = rs.reduce((a, r) => a + r.resourceHours!, 0), withAward = rs.reduce((a, r) => a + r.resourceHoursEnergy!, 0);
  return { hours, withAward, share: withAward / hours };
}

/** USD per MW as USD per kW. */
export const perKw = (usdPerMw: number): number => usdPerMw / 1000;
/** USD per kW as the page writes it: two decimals. */
export const kw = (usdPerMw: number): string => perKw(usdPerMw).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const whole = (v: number): string => Math.round(v).toLocaleString("en-US");
export const monthName = (m: string): string => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
export const shortMonth = (m: string): string => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });

/** The months of a list in words: "January to July 2026" for a run of one year, else each named. */
export function span(ms: string[]): string {
  if (!ms.length) return "";
  if (ms.length === 1) return monthName(ms[0]);
  const run = ms.every((m, i) => i === 0 || (Number(m.slice(0, 4)) * 12 + Number(m.slice(5, 7))) - (Number(ms[i - 1].slice(0, 4)) * 12 + Number(ms[i - 1].slice(5, 7))) === 1);
  if (!run) return ms.map(shortMonth).join(", ");
  const first = monthName(ms[0]), last = monthName(ms[ms.length - 1]);
  return ms[0].slice(0, 4) === ms[ms.length - 1].slice(0, 4) ? `${first.split(" ")[0]} to ${last}` : `${first} to ${last}`;
}

/** The page's one sentence, from the newest month held whole; null when no month is whole. */
export function summary(ms: Month[]): string | null {
  const r = newestComplete(ms);
  if (!r) return null;
  const fleet = r.resources !== null && r.mw !== null ? `${whole(r.resources)} storage resources with ${whole(r.mw)} MW between them` : "the storage fleet";
  return `In ${monthName(r.m)}, ERCOT's disclosure lists ${fleet}; their day-ahead awards came to USD ${kw(r.total)} per kW for the month, `
    + `${kw(r.energy)} from energy net of charging and ${kw(r.ancillary)} from ancillary services.`;
}

// ---------------------------------------------------------------------------------------------------------------------
// Session 116: where the gap comes from. What the fleet offered day-ahead (ercot_storage_dam_offers_monthly, from the
// Energy Bid/Offer Curves of 60d_DAM_ESR_Data and the blocks of 60d_DAM_ESR_ASOffers) set beside the awards and the
// model, over the months all three tables hold whole. The gap between the model and the awards is split in three by
// an identity (docs/methods/ercot_storage_dam_offers.md): capacity that offered nothing day-ahead (an allocation at
// the model's average), price (energy only), and the rest, offered and not awarded. Nothing is scaled or filled: a
// month that lacks a day or a figure in any of the three tables is left out and named.

export const OFFERS_TABLE = "ercot_storage_dam_offers_monthly";
/** The prices, USD per MWh, at or below which the table states what the energy curves offer to sell. */
export const ENERGY_BANDS = [0, 25, 50, 100, 250, 1000];
const SERVICE_PARTS = ["offer_mwh", "offer_mwh_le_mcpc", "award_mwh", "unawarded_usd_per_mw"];
/** The offers table's variables the page reads. */
export const OFFER_VARIABLES = [
  "days_held", "days_in_month", "mw", "limit_mwh", "limit_mwh_out", "limit_mwh_no_offer", "limit_mwh_no_offer_out", "limit_mwh_energy_offer", "limit_mwh_as_offer",
  "limit_mwh_award", "energy_offer_mwh", ...ENERGY_BANDS.map((b) => `energy_offer_mwh_le_${b}`), "energy_offer_mwh_at_clearing", "energy_sold_mwh",
  "as_offer_mwh", "as_award_mwh", "as_offer_mwh_unlisted",
  ...PRODUCTS.flatMap((p) => SERVICE_PARTS.map((k) => `${p.key}_${k}`)),
];
/** The awards table's variables the gap reads (all among VARIABLES). */
const GAP_AWARD_VARIABLES = ["days_held", "days_in_month", "revenue_total_usd_per_mw", "revenue_energy_usd_per_mw", ...PRODUCTS.map((p) => `revenue_${p.key}_usd_per_mw`)];
/** The model's variables the gap reads, without their prefix, and with it (the page's read). */
const GAP_MODEL = ["days_held", "days_in_month", "revenue_total_usd_per_mw", "revenue_energy_usd_per_mw", "discharged_mwh_per_mw", ...PRODUCTS.map((p) => `revenue_${p.key}_usd_per_mw`)];
export const MODEL_GAP_VARIABLES = GAP_MODEL.map((v) => MODEL_PREFIX + v);

export type Band = {
  /** the price, USD per MWh; null is "at any price" */
  le: number | null;
  /** offered to sell at that price or less: MWh per MW of the fleet per day, and as a share of what was offered at any price */
  perMwDay: number; shareOfOffered: number;
};

export type Service = {
  key: string; label: string;
  /** MW-hours as a share of the fleet's limit-hours: offered at any price, offered at or below the hour's clearing price, awarded */
  offerShare: number; atOrBelowClearingShare: number; awardShare: number;
  /** awarded over offered */
  awardOfOffer: number;
  /** USD per kW over the months: the awards, the model's, their difference, and the offered and unawarded capacity at the hour's clearing price */
  awardsKw: number; modelKw: number; gapKw: number; unawardedKw: number;
};

export type Gap = {
  /** the months all three tables hold whole, and their days */
  months: string[]; days: number;
  /** months the awards table holds whole that are not in the sums, each with the reason */
  leftOut: { m: string; why: string }[];
  /** USD per kW over the months */
  modelKw: number; awardsKw: number; gapKw: number;
  /** shares of the fleet's limit-hours: with no day-ahead offer of any kind; of those, on outage; with status OUT; offering to sell energy; with an ancillary offer; with any award */
  noOfferShare: number; noOfferOutShare: number; outShare: number; energyOfferShare: number; asOfferShare: number; awardShare: number;
  /** the gap's three parts, USD per kW: they add up to gapKw */
  neverOfferedKw: number; priceKw: number; offeredNotAwardedKw: number;
  /** energy: MWh per MW of the fleet per day, and USD per MWh (the model's per MWh discharged, the awards' net per MWh sold) */
  energy: {
    modelKw: number; awardsKw: number; modelPerMwDay: number; soldPerMwDay: number; offeredPerMwDay: number; atClearingPerMwDay: number;
    modelUsdPerMwh: number; awardsUsdPerMwh: number; bands: Band[];
    /** the share of what the curves offered to sell that was priced above USD 100 and above USD 1,000 per MWh */
    above100: number | null; above1000: number | null;
  };
  services: Service[];
  /** ancillary blocks, each once, and the awards, as shares of limit-hours; blocks of resources with no row in ERCOT's ESR data file, MWh */
  asOfferShareOfLimit: number; asAwardShareOfLimit: number; unlistedMwh: number;
};

function pivot(rows: Row[], prefix = ""): Map<string, Map<string, number>> {
  const by = new Map<string, Map<string, number>>();
  for (const r of rows) {
    const v = num(r.value);
    if (v === null || !r.variable.startsWith(prefix)) continue;
    const m = r.ts_utc.slice(0, 7);
    if (!by.has(m)) by.set(m, new Map());
    by.get(m)!.set(r.variable.slice(prefix.length), v);
  }
  return by;
}

/** The gap between the model and the awards over the months held whole, and its three parts; null when no month is
 * held whole by the awards table, the offers table and the model with every figure the arithmetic needs. */
export function gapOf(fleet: Row[], offers: Row[], model: Row[]): Gap | null {
  const A = pivot(fleet), O = pivot(offers), M = pivot(model, MODEL_PREFIX);
  const months: string[] = [], leftOut: { m: string; why: string }[] = [];
  const wholeIn = (g: Map<string, number> | undefined) => !!g && g.get("days_held") !== undefined && g.get("days_held") === g.get("days_in_month");
  const lacks = (g: Map<string, number>, need: string[]) => need.filter((k) => !g.has(k));
  for (const m of [...A.keys()].sort()) {
    const a = A.get(m)!, o = O.get(m), x = M.get(m);
    if (!wholeIn(a)) continue;  // a partial month is never set beside the model
    const why = !o ? "the offers table has no row for it" : !wholeIn(o) ? "the offers table does not hold every day of it"
      : !x ? "the model has no row for it" : !wholeIn(x) ? "the model does not hold every day of it"
      : lacks(a, GAP_AWARD_VARIABLES).length || lacks(o, OFFER_VARIABLES).length || lacks(x, GAP_MODEL).length
        ? `a figure is not held (${[...lacks(a, GAP_AWARD_VARIABLES), ...lacks(o, OFFER_VARIABLES), ...lacks(x, GAP_MODEL)].slice(0, 3).join(", ")})`
      : !(o.get("mw")! > 0) || !(o.get("limit_mwh")! > 0) ? "its MW or its limit-hours are not above zero" : null;
    if (why) leftOut.push({ m, why }); else months.push(m);
  }
  if (!months.length) return null;
  const sum = (T: Map<string, Map<string, number>>, k: string) => months.reduce((s, m) => s + T.get(m)!.get(k)!, 0);
  /** a month's MWh over the month's own MW, the months added up */
  const perMw = (k: string) => months.reduce((s, m) => s + O.get(m)!.get(k)! / O.get(m)!.get("mw")!, 0);
  const days = sum(O, "days_held"), lim = sum(O, "limit_mwh");
  const modelKw = sum(M, "revenue_total_usd_per_mw") / 1000, awardsKw = sum(A, "revenue_total_usd_per_mw") / 1000;
  const gapKw = modelKw - awardsKw;
  const noOfferShare = sum(O, "limit_mwh_no_offer") / lim;
  // capacity that offered nothing, valued at what the model makes on average: an allocation, not a measurement
  const neverOfferedKw = modelKw * noOfferShare;
  // price, energy only: the awards' volume at the difference between the model's and the awards' net USD per MWh
  const eModelKw = sum(M, "revenue_energy_usd_per_mw") / 1000, eAwardsKw = sum(A, "revenue_energy_usd_per_mw") / 1000;
  const vm = sum(M, "discharged_mwh_per_mw") / days, va = perMw("energy_sold_mwh") / days;
  if (!(vm > 0) || !(va > 0)) return null;
  const pm = (eModelKw * 1000) / (vm * days), pa = (eAwardsKw * 1000) / (va * days);
  const priceKw = (va * days * (pm - pa)) / 1000;
  const offered = sum(O, "energy_offer_mwh");
  const bands: Band[] = [...ENERGY_BANDS.map((b) => ({ le: b as number | null, k: `energy_offer_mwh_le_${b}` })), { le: null, k: "energy_offer_mwh" }]
    .map(({ le, k }) => ({ le, perMwDay: perMw(k) / days, shareOfOffered: offered > 0 ? sum(O, k) / offered : 0 }));
  const services: Service[] = PRODUCTS.map((p) => {
    const off = sum(O, `${p.key}_offer_mwh`), aw = sum(O, `${p.key}_award_mwh`);
    const sAwards = sum(A, `revenue_${p.key}_usd_per_mw`) / 1000, sModel = sum(M, `revenue_${p.key}_usd_per_mw`) / 1000;
    return { key: p.key, label: p.label, offerShare: off / lim, atOrBelowClearingShare: sum(O, `${p.key}_offer_mwh_le_mcpc`) / lim, awardShare: aw / lim,
             awardOfOffer: off > 0 ? aw / off : 0, awardsKw: sAwards, modelKw: sModel, gapKw: sModel - sAwards, unawardedKw: sum(O, `${p.key}_unawarded_usd_per_mw`) / 1000 };
  });
  return {
    months, days, leftOut, modelKw, awardsKw, gapKw,
    noOfferShare, noOfferOutShare: sum(O, "limit_mwh_no_offer_out") / lim, outShare: sum(O, "limit_mwh_out") / lim,
    energyOfferShare: sum(O, "limit_mwh_energy_offer") / lim, asOfferShare: sum(O, "limit_mwh_as_offer") / lim, awardShare: sum(O, "limit_mwh_award") / lim,
    neverOfferedKw, priceKw, offeredNotAwardedKw: gapKw - neverOfferedKw - priceKw,
    energy: { modelKw: eModelKw, awardsKw: eAwardsKw, modelPerMwDay: vm, soldPerMwDay: va, offeredPerMwDay: perMw("energy_offer_mwh") / days,
              atClearingPerMwDay: perMw("energy_offer_mwh_at_clearing") / days, modelUsdPerMwh: pm, awardsUsdPerMwh: pa, bands,
              above100: offered > 0 ? 1 - sum(O, "energy_offer_mwh_le_100") / offered : null, above1000: offered > 0 ? 1 - sum(O, "energy_offer_mwh_le_1000") / offered : null },
    services,
    asOfferShareOfLimit: sum(O, "as_offer_mwh") / lim, asAwardShareOfLimit: sum(O, "as_award_mwh") / lim, unlistedMwh: sum(O, "as_offer_mwh_unlisted"),
  };
}

/** USD per kW, already per kW, as the page writes it: two decimals, a minus sign for a negative. */
export const usd = (v: number): string => (v < 0 ? "-" : "") + Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** A share as a percentage. */
export const pct = (v: number, digits = 0): string => `${(v * 100).toFixed(digits)}%`;
/** Words joined as a list: "a", "a and b", "a, b and c". */
export const list = (xs: string[]): string => (xs.length <= 1 ? xs.join("") : `${xs.slice(0, -1).join(", ")} and ${xs[xs.length - 1]}`);
