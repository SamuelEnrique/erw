// Energy Research Warehouse (ERW) site, session 120: the real-time side of what Texas's storage resources did
// (a section of /cost-of-power/battery/awards, in review).
//
// The arithmetic of the section, on the rows of ercot_storage_rt_monthly (warehouse/derived, from ERCOT's 60-Day SCED
// Disclosure Reports, the file 60d_ESR_Data_in_SCED, set beside the day-ahead awards of the same days) and of
// ercot_storage_node_basis (one real week of real-time prices at the storage settlement points against the hub
// average), with the battery model's day-ahead schedule from battery_stack_monthly beside whole months only. Pure
// functions, no imports (Node runs this file as it is, for tests/test_session120_page.py). Nothing is scaled, filled or
// estimated: a month whose days are not all matched is partial and is never set beside the model; a figure that is not
// held is null.
//
// Every real-time dollar here is at the HUB AVERAGE's price, not at each resource's own node, and every name that rests
// on it says so (Hub). ERCOT settles at the node (Nodal Protocols 6.6.3.1); the node price of a disclosed day is not
// public (docs/methods/ercot_storage_realtime.md).

export const RT_TABLE = "ercot_storage_rt_monthly";
export const RT_ENTITY = "ercot:esr_fleet";
export const BASIS_TABLE = "ercot_storage_node_basis";
export const BASIS_ENTITY = "ercot:esr_nodes";
export const SERVICES: { key: string; label: string }[] = [
  { key: "regup", label: "Regulation Up" }, { key: "regdn", label: "Regulation Down" }, { key: "rrs", label: "Responsive Reserve" },
  { key: "ecrs", label: "ECRS" }, { key: "nspin", label: "Non-Spin" },
];
export const RT_VARIABLES = [
  "days_held", "days_in_month", "resources", "resource_hours", "mw", "intervals", "intervals_priced",
  "rt_discharge_mwh", "rt_charge_mwh", "rt_net_mwh", "da_sold_mwh", "da_bought_mwh", "da_net_mwh", "rt_deviation_mwh",
  "revenue_da_energy_usd_per_mw", "revenue_da_ancillary_usd_per_mw", "revenue_da_usd_per_mw",
  "revenue_rt_output_hub_usd_per_mw", "revenue_da_position_hub_usd_per_mw", "revenue_rt_deviation_hub_usd_per_mw", "revenue_market_hub_usd_per_mw",
  "da_node_minus_hub_sold", "da_node_minus_hub_bought",
  ...SERVICES.flatMap((s) => [`as_rt_${s.key}_mwh`, `as_da_${s.key}_mwh`, `as_imbalance_${s.key}_mwh`]),
];
export const BASIS_VARIABLES = ["nodes", "nodes_with_spread", "whole_days", "spread_hub", "spread_node_median", "spread_node_mean", "spread_node_p10", "spread_node_p90",
  "nodes_spread_above_hub", "mean_node_median", "mean_hub", "mean_abs_difference_median", "intervals_median"];

/** A row of a series table as the live set serves it. */
export type Row = { variable: string; ts_utc: string; value: number | string };

export type Ancillary = { key: string; label: string; realTime: number; dayAhead: number; imbalance: number };

export type RtMonth = {
  /** YYYY-MM, the local (Central) month */
  m: string;
  /** the operating days both disclosures hold, and the month's days */
  daysHeld: number; daysInMonth: number; complete: boolean;
  resources: number | null; mw: number | null;
  /** USD per MW of the fleet: the day-ahead awards at their own prices (the floor), */
  dayAhead: number; dayAheadEnergy: number | null; dayAheadAncillary: number | null;
  /** real-time energy less the day-ahead position, at the hub average's real-time price, */
  deviationHub: number;
  /** its two halves, */
  outputHub: number | null; positionHub: number | null;
  /** and the two together */
  marketHub: number;
  /** MWh: telemetered discharge and charge, and the day-ahead energy sold and bought on the same days */
  discharged: number | null; charged: number | null; sold: number | null; bought: number | null; deviationMwh: number | null;
  /** resource-intervals, and those with a hub price */
  intervals: number | null; priced: number | null;
  /** the day-ahead price at the resources' nodes less the hub's, weighted by MWh sold and by MWh bought (USD/MWh) */
  nodeLessHubSold: number | null; nodeLessHubBought: number | null;
  ancillary: Ancillary[];
  /** the model's day-ahead schedule for the month, USD per MW, and whether the model holds every day of it */
  model: { total: number; whole: boolean } | null;
};

const num = (v: number | string | null | undefined): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

function byMonth(rows: Row[], prefix = ""): Map<string, Map<string, number>> {
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

/** The months of the table, oldest first. A month without its days or without its three sums per MW (the day-ahead
 * awards, the deviation at the hub price and their total) is not a month the section can show, and is left out.
 * model: the rows of the battery model whose variable begins with modelPrefix. */
export function rtMonthsOf(rows: Row[], model: Row[] = [], modelPrefix = "dayahead_2h_"): RtMonth[] {
  const by = byMonth(rows), mod = byMonth(model, modelPrefix);
  const out: RtMonth[] = [];
  for (const m of [...by.keys()].sort()) {
    const g = by.get(m)!;
    const get = (k: string) => (g.has(k) ? g.get(k)! : null);
    const daysHeld = get("days_held"), daysInMonth = get("days_in_month");
    const dayAhead = get("revenue_da_usd_per_mw"), deviationHub = get("revenue_rt_deviation_hub_usd_per_mw"), marketHub = get("revenue_market_hub_usd_per_mw");
    if (daysHeld === null || daysInMonth === null || dayAhead === null || deviationHub === null || marketHub === null) continue;
    const x = mod.get(m), mt = x?.get("revenue_total_usd_per_mw");
    const ancillary: Ancillary[] = [];
    for (const s of SERVICES) {
      const realTime = get(`as_rt_${s.key}_mwh`), da = get(`as_da_${s.key}_mwh`), imbalance = get(`as_imbalance_${s.key}_mwh`);
      if (realTime !== null && da !== null && imbalance !== null) ancillary.push({ key: s.key, label: s.label, realTime, dayAhead: da, imbalance });
    }
    out.push({
      m, daysHeld, daysInMonth, complete: daysHeld === daysInMonth, resources: get("resources"), mw: get("mw"),
      dayAhead, dayAheadEnergy: get("revenue_da_energy_usd_per_mw"), dayAheadAncillary: get("revenue_da_ancillary_usd_per_mw"),
      deviationHub, outputHub: get("revenue_rt_output_hub_usd_per_mw"), positionHub: get("revenue_da_position_hub_usd_per_mw"), marketHub,
      discharged: get("rt_discharge_mwh"), charged: get("rt_charge_mwh"), sold: get("da_sold_mwh"), bought: get("da_bought_mwh"), deviationMwh: get("rt_deviation_mwh"),
      intervals: get("intervals"), priced: get("intervals_priced"),
      nodeLessHubSold: get("da_node_minus_hub_sold"), nodeLessHubBought: get("da_node_minus_hub_bought"),
      ancillary,
      model: x && mt !== undefined ? { total: mt, whole: x.get("days_held") !== undefined && x.get("days_held") === x.get("days_in_month") } : null,
    });
  }
  return out;
}

export type RtTotal = {
  /** the months held whole by the table and, where a model figure stands, by the model too */
  months: string[];
  dayAhead: number; deviationHub: number; marketHub: number;
  /** the model's figure over the same months; null when the model lacks a whole month among them */
  model: number | null;
};

/** Over the months held whole: the sums per MW, and the model's figure for the same months when it holds every one of
 * them whole. A partial month is in neither. Null when no month is whole. */
export function rtTotal(ms: RtMonth[]): RtTotal | null {
  const full = ms.filter((r) => r.complete);
  if (!full.length) return null;
  const sum = (f: (r: RtMonth) => number) => full.reduce((a, r) => a + f(r), 0);
  const modelOk = full.every((r) => r.model !== null && r.model.whole);
  return { months: full.map((r) => r.m), dayAhead: sum((r) => r.dayAhead), deviationHub: sum((r) => r.deviationHub), marketHub: sum((r) => r.marketHub),
    model: modelOk ? sum((r) => r.model!.total) : null };
}

export type RtEnergy = {
  months: string[]; days: number;
  discharged: number; charged: number; sold: number; bought: number;
  /** the share of the MWh discharged in real time that had been sold day-ahead; null when nothing was discharged */
  soldOfDischarged: number | null;
  /** MWh discharged per MW of the fleet per day: with a 2-hour battery, two would be one full discharge a day */
  dischargedPerMwDay: number | null;
  /** MWh out over MWh in, as telemetered: not an efficiency, since what is in the batteries at the start and the end differs */
  outOverIn: number | null;
  /** the share of resource-intervals that had a hub price, and so were valued */
  pricedShare: number | null;
};

/** The fleet's energy over every month held (partial ones with the days they hold): a sum of MWh is a sum whatever the
 * month's days, and it is set beside nothing that covers other days. Null when a month lacks one of the four sums. */
export function rtEnergy(ms: RtMonth[]): RtEnergy | null {
  if (!ms.length || ms.some((r) => r.discharged === null || r.charged === null || r.sold === null || r.bought === null)) return null;
  const sum = (f: (r: RtMonth) => number) => ms.reduce((a, r) => a + f(r), 0);
  const discharged = sum((r) => r.discharged!), charged = sum((r) => r.charged!), sold = sum((r) => r.sold!), bought = sum((r) => r.bought!);
  const days = sum((r) => r.daysHeld);
  // the fleet's MW differs by month: MWh per MW per day is each month's MWh over its own MW, weighted by its days
  const perMw = ms.every((r) => r.mw !== null && r.mw > 0) && days > 0 ? sum((r) => r.discharged! / r.mw!) / days : null;
  const allIntervals = ms.every((r) => r.intervals !== null && r.priced !== null);
  const intervals = allIntervals ? sum((r) => r.intervals!) : 0;
  return { months: ms.map((r) => r.m), days, discharged, charged, sold, bought,
    soldOfDischarged: discharged > 0 ? sold / discharged : null, dischargedPerMwDay: perMw, outOverIn: charged > 0 ? discharged / charged : null,
    pricedShare: allIntervals && intervals > 0 ? sum((r) => r.priced!) / intervals : null };
}

/** Each Ancillary Service over every month held: MW-hours awarded in real time, awarded day-ahead, and the difference
 * ERCOT settles at the service's real-time price. A service a month does not hold is left out of the list. */
export function rtAncillary(ms: RtMonth[]): Ancillary[] {
  const out: Ancillary[] = [];
  for (const s of SERVICES) {
    const rows = ms.map((r) => r.ancillary.find((a) => a.key === s.key));
    if (!rows.length || rows.some((a) => a === undefined)) continue;
    out.push({ key: s.key, label: s.label, realTime: rows.reduce((a, r) => a + r!.realTime, 0), dayAhead: rows.reduce((a, r) => a + r!.dayAhead, 0),
      imbalance: rows.reduce((a, r) => a + r!.imbalance, 0) });
  }
  return out;
}

export type Basis = {
  /** the first day of node prices held (YYYY-MM-DD) */
  from: string;
  nodes: number; nodesWithSpread: number | null; wholeDays: number | null;
  spreadHub: number | null; spreadMedian: number | null; spreadP10: number | null; spreadP90: number | null; aboveHub: number | null;
  meanAbsDifference: number | null;
};

/** The week of real-time prices at the storage settlement points against the hub average, summed up by the builder. */
export function basisOf(rows: Row[]): Basis | null {
  const g = new Map<string, number>();
  let from = "";
  for (const r of rows) {
    const v = num(r.value);
    if (v === null) continue;
    g.set(r.variable, v);
    from = r.ts_utc.slice(0, 10);
  }
  const nodes = g.get("nodes");
  if (nodes === undefined) return null;
  const get = (k: string) => (g.has(k) ? g.get(k)! : null);
  return { from, nodes, nodesWithSpread: get("nodes_with_spread"), wholeDays: get("whole_days"), spreadHub: get("spread_hub"), spreadMedian: get("spread_node_median"),
    spreadP10: get("spread_node_p10"), spreadP90: get("spread_node_p90"), aboveHub: get("nodes_spread_above_hub"), meanAbsDifference: get("mean_abs_difference_median") };
}
