// Session 51: the cost of power, the seller's side ("What a generator earns", /cost-of-power/seller). Every number on
// the tab is computed here from site/data/merchant_snapshot.json (warehouse/derived/merchant_revenue.py, whose table
// merchant_revenue_monthly holds the same monthly figures), by the page and by scripts/check-values.mjs alike (key
// mr|<inputs>|<stat>). No imports: Node runs this file as it is. docs/methods/cost_of_power.md, "The seller's side".
//
// Merchant only: no PPA, hedge, capacity payment or ancillary service. Asset sizes, the heat rate, the variable and
// fixed O&M and the debt service are the reader's inputs; their defaults come from Lazard's LCOE+ (June 2025): the
// midpoint of each range (DEFAULTS), with debt service at 60 percent debt, 8 percent, amortized over the asset's life.

export type Asset = "solar" | "wind" | "battery" | "peaker";
export type AssetKey = "solar" | "wind" | "battery_2h" | "battery_4h" | "peaker";
export type MonthRow = { revenue_per_mw: number; sales_per_mw: number; energy_per_mw: number; capture_price: number | null; flat_price: number; capture_rate: number | null; hours: number };
export type SnapMonth = { flat: number; him: number; i0: number; i1: number } & Partial<Record<AssetKey, MonthRow>>;
export type StressDay = { day: string; window: boolean; hours: number; i0: number | null; i1: number | null } & Partial<Record<"solar" | "wind" | "battery_2h" | "battery_4h", number | null>>;
export type SnapIso = {
  iso: string; hub: string; ba: string; tz: string; start: string; months: Record<string, SnapMonth>;
  price: (number | null)[]; hh: (number | null)[]; stress?: Record<string, { start: string; end: string; days: StressDay[] }>;
  over_nameplate: Record<string, number>; negative: Record<string, number>;
};
export type Snapshot = { built: string; isos: Record<string, SnapIso>; defaults: { rte: number; heat_rate: number; vom: number; near: number; durations: number[] }; source: string[] };
export type Inputs = { iso: string; asset: Asset; mw: number; mwh: number; ds: number; hr: number; vom: number; fom: number };

export const ISO_NAMES: Record<string, string> = { ercot: "ERCOT", caiso: "CAISO", isone: "ISO-NE", miso: "MISO", nyiso: "NYISO", spp: "SPP" };
export const ASSET_NAMES: Record<Asset, string> = { solar: "Solar", wind: "Wind", battery: "Battery", peaker: "Gas peaker" };
export const EVENTS: Record<string, string> = { uri_2021: "Winter Storm Uri, February 2021", elliott_2022: "Winter Storm Elliott, December 2022", ercot_heat_2023: "ERCOT's summer 2023 heat" };

/** Lazard, "Levelized Cost of Energy+", June 2025: LCOE v18.0 Key Assumptions (solar PV utility, wind onshore, gas
 * peaking new build) and LCOS v10.0 Key Assumptions (utility-scale standalone 100 MW / 200 MWh and / 400 MWh).
 * capex USD/kW and fixed O&M USD/kW-yr: the midpoint of Lazard's low and high; life in years (Lazard's facility or
 * project life); storage O&M is Lazard's USD/kWh times the hours. */
export const DEFAULTS: Record<AssetKey, { capex: number; life: number; fom: number; capexRange: string; fomRange: string }> = {
  solar: { capex: 1375, life: 35, fom: 12.5, capexRange: "1,150 to 1,600", fomRange: "11.00 to 14.00" },
  wind: { capex: 2100, life: 30, fom: 32.25, capexRange: "1,900 to 2,300", fomRange: "24.50 to 40.00" },
  battery_2h: { capex: 610, life: 20, fom: 11.2, capexRange: "340 to 880 (total installed, 100 MW / 200 MWh)", fomRange: "3.0 to 8.2 per kWh, x 2 hours" },
  battery_4h: { capex: 1110, life: 20, fom: 22, capexRange: "620 to 1,600 (total installed, 100 MW / 400 MWh)", fomRange: "3.0 to 8.0 per kWh, x 4 hours" },
  peaker: { capex: 1300, life: 30, fom: 13.5, capexRange: "1,150 to 1,450", fomRange: "10.00 to 17.00" },
};
export const DEBT = { share: 0.6, rate: 0.08 };  // Lazard: "60% debt at an 8% interest rate"; the debt amortizes over the life
export const HEAT_RATE = 10.725, VOM = 4.25;   // MMBtu/MWh and USD/MWh: Lazard gas peaking (new build) midpoints

/** The capital recovery factor: the level annual payment per dollar borrowed at `rate` over `n` years. */
export const crf = (rate: number, n: number) => rate / (1 - (1 + rate) ** -n);
/** The default annual debt service of one MW: Lazard's midpoint capex, 60 percent debt at 8 percent, over the life. */
export const debtPerMw = (k: AssetKey) => DEFAULTS[k].capex * 1000 * DEBT.share * crf(DEBT.rate, DEFAULTS[k].life);

/** A battery's duration: the nearer of the two Lazard prices, 2 or 4 hours (MWh / MW). */
export const durationOf = (mw: number, mwh: number) => (mwh / mw <= 3 ? 2 : 4);
export const keyOf = (x: Pick<Inputs, "asset" | "mw" | "mwh">): AssetKey => (x.asset === "battery" ? (`battery_${durationOf(x.mw, x.mwh)}h` as AssetKey) : x.asset);

export const DEFAULT_SIZE: Record<Asset, { mw: number; mwh: number }> = { solar: { mw: 100, mwh: 0 }, wind: { mw: 100, mwh: 0 }, battery: { mw: 100, mwh: 400 }, peaker: { mw: 100, mwh: 0 } };

/** The inputs from a query (strings), each defaulted and bounded; the debt service and fixed O&M default by asset. */
export function inputsOf(q: Record<string, string | undefined>): Inputs {
  const num = (v: string | undefined, d: number, lo: number, hi: number) => {
    const x = v === undefined || v === "" ? NaN : Number(v);
    return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
  };
  const iso = q.iso && q.iso in ISO_NAMES ? q.iso : "ercot";
  const asset = (q.asset && q.asset in ASSET_NAMES ? q.asset : "solar") as Asset;
  const mw = num(q.mw, DEFAULT_SIZE[asset].mw, 1, 5000);
  const mwh = asset === "battery" ? num(q.mwh, mw * 4, mw, mw * 8) : 0;
  const k = keyOf({ asset, mw, mwh });
  return {
    iso, asset, mw, mwh,
    ds: Math.round(num(q.ds, debtPerMw(k) * mw, 0, 1e10)),
    hr: asset === "peaker" ? num(q.hr, HEAT_RATE, 6, 16) : HEAT_RATE,
    vom: asset === "peaker" ? num(q.vom, VOM, 0, 50) : VOM,
    fom: num(q.fom, DEFAULTS[k].fom, 0, 200),
  };
}
/** The inputs as a stable string: the check keys' and the links' form. */
export const inputsKey = (x: Inputs) => `iso=${x.iso}&asset=${x.asset}&mw=${x.mw}&mwh=${x.mwh}&ds=${x.ds}&hr=${x.hr}&vom=${x.vom}&fom=${x.fom}`;
export function parseKey(k: string): Inputs {
  return inputsOf(Object.fromEntries(k.split("&").map((p) => p.split("=") as [string, string])));
}

export type Month = { m: string; held: boolean; share: number; revenue: number; energy: number; capture: number | null; flat: number; rate: number | null; cfads: number; dscr: number | null };

/** The peaker over hours [i0, i1): runs where price > Henry Hub x heat rate + variable O&M; per MW. */
export function peakerOver(s: SnapIso, i0: number, i1: number, hr: number, vom: number) {
  let sales = 0, cost = 0, run = 0, n = 0, sum = 0;
  for (let i = i0; i < i1; i++) {
    const p = s.price[i], g = s.hh[i];
    if (p === null || g === null || p === undefined || g === undefined) continue;
    n++; sum += p;
    const c = g * hr + vom;
    if (p > c) { sales += p; cost += c; run++; }
  }
  return { revenue: sales - cost, sales, energy: run, hours: n, flat: n ? sum / n : 0 };
}

/** Every month of the window for the inputs: revenue (USD, for the reader's size), energy (MWh), the capture price and
 * rate, the flat price, the cash flow available for debt service (revenue less fixed O&M) and its coverage of a
 * month's debt service. A month is held when the asset's hours (or a battery's days) are at least `near` of the
 * month's; the others are shown but not counted. */
export function months(snap: Snapshot, x: Inputs): Month[] {
  const s = snap.isos[x.iso];
  const k = keyOf(x);
  const near = snap.defaults.near;
  const dsMonth = x.ds / 12;
  const out: Month[] = [];
  for (const [m, r] of Object.entries(s.months).sort()) {
    let row: { revenue: number; energy: number; sales: number; flat: number; hours: number } | null = null;
    if (k === "peaker" && (x.hr !== HEAT_RATE || x.vom !== VOM)) {
      const p = peakerOver(s, r.i0, r.i1, x.hr, x.vom);
      row = { revenue: p.revenue, energy: p.energy, sales: p.sales, flat: p.flat, hours: p.hours };
    } else if (r[k]) {
      const a = r[k]!;
      row = { revenue: a.revenue_per_mw, energy: a.energy_per_mw, sales: a.sales_per_mw, flat: a.flat_price, hours: a.hours };
    }
    if (!row) continue;
    const days = Number(m.slice(5, 7)) && new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 0)).getUTCDate();
    const share = k.startsWith("battery") ? row.hours / days : row.hours / r.him;
    const revenue = row.revenue * x.mw, energy = row.energy * x.mw;
    const capture = row.energy > 0 ? row.sales / row.energy : null;
    const cfads = revenue - (x.fom * 1000 * x.mw) / 12;
    out.push({
      m, held: share >= near - 1e-9, share, revenue, energy, capture, flat: row.flat, rate: capture !== null && row.flat ? (capture / row.flat) * 100 : null,
      cfads, dscr: dsMonth > 0 ? cfads / dsMonth : null,
    });
  }
  return out;
}

/** The held months' summary: the median and 10th-percentile month (nearest rank), the worst three, the count. */
export function summary(ms: Month[]) {
  const held = ms.filter((r) => r.held);
  const sorted = [...held].sort((a, b) => a.revenue - b.revenue || a.m.localeCompare(b.m));
  const rank = (p: number) => sorted[Math.max(0, Math.ceil(p * sorted.length) - 1)];
  return { n: held.length, median: sorted.length ? rank(0.5) : null, p10: sorted.length ? rank(0.1) : null, worst: sorted.slice(0, 3), first: held[0]?.m ?? null, last: held.at(-1)?.m ?? null };
}

/** Trailing-twelve-month coverage: at each held month whose eleven months before it are all held, the sum of the twelve
 * months' cash flow available for debt service over the annual debt service. */
export function ttm(ms: Month[], ds: number): { m: string; dscr: number; cfads: number }[] {
  const by = new Map(ms.map((r) => [r.m, r]));
  const prev = (m: string, k: number) => {
    const d = new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)) - 1 - k, 1));
    return d.toISOString().slice(0, 7);
  };
  const out: { m: string; dscr: number; cfads: number }[] = [];
  for (const r of ms) {
    if (!r.held) continue;
    const twelve = Array.from({ length: 12 }, (_, k) => by.get(prev(r.m, k)));
    if (twelve.some((t) => !t || !t.held)) continue;
    const c = twelve.reduce((a, t) => a + t!.cfads, 0);
    out.push({ m: r.m, cfads: c, dscr: ds > 0 ? c / ds : NaN });
  }
  return out;
}

/** Revenue on the ERCOT stress days of event_window_daily (Uri, Elliott, the 2023 heat) against the baseline days of
 * the same event: per day for the reader's size (USD), the window's mean and total, and a normal week (seven times
 * the baseline days' mean). Null for a hub without them (the other ISOs' prices do not reach back to these events). */
export function stress(snap: Snapshot, x: Inputs) {
  const s = snap.isos[x.iso];
  if (!s.stress) return null;
  const k = keyOf(x);
  const out: { event: string; start: string; end: string; days: number; windowMean: number; windowTotal: number; baseMean: number; normalWeek: number; best: { day: string; v: number } }[] = [];
  for (const [event, e] of Object.entries(s.stress)) {
    const val = (d: StressDay): number | null => {
      if (k === "peaker") return d.i0 === null || d.i1 === null ? null : peakerOver(s, d.i0, d.i1, x.hr, x.vom).revenue * x.mw;
      const v = d[k as "solar"];
      return v === null || v === undefined ? null : v * x.mw;
    };
    const w = e.days.filter((d) => d.window).map((d) => ({ day: d.day, v: val(d) })).filter((d) => d.v !== null) as { day: string; v: number }[];
    const b = e.days.filter((d) => !d.window).map(val).filter((v) => v !== null) as number[];
    if (!w.length || !b.length) continue;
    const total = w.reduce((a, d) => a + d.v, 0), baseMean = b.reduce((a, v) => a + v, 0) / b.length;
    const best = w.reduce((a, d) => (d.v > a.v ? d : a));
    out.push({ event, start: e.start, end: e.end, days: w.length, windowMean: total / w.length, windowTotal: total, baseMean, normalWeek: baseMean * 7, best });
  }
  return out;
}

/** One number for a check key's stat, from the snapshot: what the page shows and check-values recomputes. */
export function stat(snap: Snapshot, x: Inputs, what: string): number | null {
  const ms = months(snap, x);
  const sm = summary(ms);
  const t = ttm(ms, x.ds);
  const st = stress(snap, x) ?? [];
  const [a, b] = what.split(":");
  switch (a) {
    case "median": return sm.median?.revenue ?? null;
    case "p10": return sm.p10?.revenue ?? null;
    case "worst": return sm.worst[Number(b)]?.revenue ?? null;
    case "n": return sm.n;
    case "ds": return x.ds;
    case "under1": return ms.filter((r) => r.held && r.dscr !== null && r.dscr < 1).length;
    case "under125": return ms.filter((r) => r.held && r.dscr !== null && r.dscr < 1.25).length;
    case "ttm_last": return t.at(-1)?.dscr ?? null;
    case "ttm_min": return t.length ? Math.min(...t.map((r) => r.dscr)) : null;
    case "ttm_under1": return t.filter((r) => r.dscr < 1).length;
    case "ttm_under125": return t.filter((r) => r.dscr < 1.25).length;
    case "annual_mean": { const held = ms.filter((r) => r.held); return held.length ? (held.reduce((s, r) => s + r.revenue, 0) / held.length) * 12 : null; }
    case "stress_mean": return st.find((e) => e.event === b)?.windowMean ?? null;
    case "stress_total": return st.find((e) => e.event === b)?.windowTotal ?? null;
    case "stress_week": return st.find((e) => e.event === b)?.normalWeek ?? null;
    case "stress_best": return st.find((e) => e.event === b)?.best.v ?? null;
    case "month": { const r = ms.find((y) => y.m === b); return r ? r.revenue : null; }
    case "dscr": { const r = ms.find((y) => y.m === b); return r ? r.dscr : null; }
    case "capture": { const r = ms.find((y) => y.m === b); return r ? r.capture : null; }
    case "rate": { const r = ms.find((y) => y.m === b); return r ? r.rate : null; }
    default: return null;
  }
}
