// Session 43: the electricity bill explainer's arithmetic, on data/bill_rules.json (each rate cites the tariff page that
// states it). Shared by /learn/bill (the defaults on the server, the reader's inputs in the browser) and
// site/scripts/test-bill.mjs. No imports: Node runs this file as it is. An estimate for learning, not a bill.

export type Line = { id: string; name: string; group?: string; what: string; why: string; amount: number; cite: string; quote: string; effective: string; detail: string };
export type Bill = { lines: Line[]; total: number; kwh: number };

type Src = { id: string; name: string; what: string; why: string; basis: string; rate: unknown; cite: string; quote: string; effective: string; group?: string };
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Rules = any;

export type CAInput = { kwh: number; peakShare: number; season: "summer" | "winter"; territory: string; tier: string; days: number; climateCredit: boolean };
export type TXInput = { kwh: number; energyRate: number };

const mk = (s: Src, amount: number, detail: string): Line =>
  ({ id: s.id, name: s.name, group: s.group, what: s.what, why: s.why, amount, cite: s.cite, quote: s.quote, effective: s.effective, detail });

/** The baseline allowance for the bill: the territory's daily quantity (Code B) times the days, never more than the use. */
export function baselineKwh(rules: Rules, x: CAInput): number {
  const q = rules.bills.CA.baseline_quantities.code_B[x.territory];
  return Math.min(x.kwh, q[x.season === "summer" ? 0 : 1] * x.days);
}

/** California, E-TOU-C: the unbundled components line by line (as PG&E shows them), the base services charge and,
 * when chosen, the climate credit. Peak and off-peak use are pro-rated across the baseline, as the tariff says. */
export function billCA(rules: Rules, x: CAInput): Bill {
  const ca = rules.bills.CA;
  const base = baselineKwh(rules, x);
  const lines: Line[] = [];
  for (const c of ca.components as Src[]) {
    if (c.basis === "per_kWh_tou") {
      const [pk, off] = (c.rate as Record<string, number[]>)[x.season];
      lines.push(mk(c, x.kwh * (x.peakShare * pk + (1 - x.peakShare) * off), `${x.kwh} kWh, ${Math.round(x.peakShare * 100)}% at $${pk}, the rest at $${off}`));
    } else if (c.basis === "per_kWh_baseline_split") {
      const r = c.rate as { baseline: number; over: number };
      lines.push(mk(c, base * r.baseline + (x.kwh - base) * r.over, `${base} kWh within the baseline at $${r.baseline}, ${x.kwh - base} kWh above at $${r.over}`));
    } else {
      lines.push(mk(c, x.kwh * (c.rate as number), `${x.kwh} kWh at $${c.rate}`));
    }
  }
  const bs = ca.base_services;
  const perDay = bs.tiers[x.tier];
  lines.push({ id: "base_services", name: `Base Services Charge (Income Tier ${x.tier})`, group: "Fixed", what: bs.what, why: bs.why, amount: x.days * perDay,
    cite: bs.cite, quote: bs.quote, effective: bs.effective, detail: `${x.days} days at $${perDay} a day` });
  if (x.climateCredit) lines.push(mk({ ...ca.climate_credit, group: "Credits" }, ca.climate_credit.rate, "once, in the August or September bill"));
  return { lines, total: lines.reduce((a, l) => a + l.amount, 0), kwh: x.kwh };
}

/** California by the tariff's total rates (Sheet 2), to check the unbundled lines: energy at the TOU total, less the
 * baseline credit, plus the base services charge (and the climate credit). */
export function totalCA(rules: Rules, x: CAInput): number {
  const s = rules.bills.CA.seasons[x.season];
  const energy = x.kwh * (x.peakShare * s.peak + (1 - x.peakShare) * s.offpeak);
  const credit = baselineKwh(rules, x) * rules.bills.CA.baseline_credit.rate;
  return energy + credit + x.days * rules.bills.CA.base_services.tiers[x.tier] + (x.climateCredit ? rules.bills.CA.climate_credit.rate : 0);
}

/** Texas, Oncor: the retailer's energy charge (the reader's input), Oncor's fixed monthly charges and its per-kWh
 * charges and riders. */
export function billTX(rules: Rules, x: TXInput): Bill {
  const tx = rules.bills.TX;
  const lines: Line[] = [{
    id: "rep_energy", name: "Energy charge (your retail electric provider)", group: "Energy", amount: x.kwh * x.energyRate,
    what: "What your retailer charges for the power itself, under the plan you chose.", why: "In most of ERCOT, retailers compete to sell power; the price is on the plan's Electricity Facts Label.",
    cite: tx.energy_default.cite, quote: tx.energy_default.derivation, effective: "your plan", detail: `${x.kwh} kWh at $${x.energyRate}`,
  }];
  for (const f of tx.fixed as Src[]) lines.push(mk({ ...f, group: "Delivery (Oncor)" }, f.rate as number, "per month"));
  for (const p of tx.per_kwh as Src[]) lines.push(mk({ ...p, group: "Delivery (Oncor)" }, x.kwh * (p.rate as number), `${x.kwh} kWh at $${p.rate}`));
  return { lines, total: lines.reduce((a, l) => a + l.amount, 0), kwh: x.kwh };
}

export function defaultsCA(rules: Rules): CAInput {
  const d = rules.bills.CA.defaults;
  return { kwh: d.kwh, peakShare: d.peak_share, season: d.season, territory: d.territory, tier: d.income_tier, days: d.days, climateCredit: d.climate_credit };
}
export function defaultsTX(rules: Rules): TXInput {
  return { kwh: rules.bills.TX.defaults.kwh, energyRate: rules.bills.TX.energy_default.rate };
}

// --- session 52: SCE (TOU-D Option 4-9 PM), SDG&E (TOU-DR1) and CenterPoint -----------------------------------------

/** A three-period time-of-use bill's inputs: the share of use from 4 to 9 p.m. (peak), the share in the super
 * off-peak hours (winter for SCE, every season for SDG&E), and for SCE the share of days that are weekdays (summer 4 to
 * 9 p.m. is on-peak on weekdays and mid-peak on weekends). SCE's baseline comes from its region; SDG&E's is the
 * customer's own allowance from the bill (the credit applies up to 130 percent of it). */
export type TOUInput = {
  kwh: number; peakShare: number; superShare: number; weekdayShare: number; season: "summer" | "winter"; days: number;
  region?: string; baselineKwh?: number; climateCredit?: boolean;
};

/** Each period's share of the month's use, by the utility's own period definitions (bill_rules.json "periods"). */
export function periodShares(kind: string, x: TOUInput): Record<string, number> {
  const p = x.peakShare, s = x.superShare;
  if (kind === "sce") {
    return x.season === "summer" ? { on: p * x.weekdayShare, mid: p * (1 - x.weekdayShare), off: 1 - p } : { mid: p, super: s, off: 1 - p - s };
  }
  return { on: p, super: s, off: 1 - p - s };  // SDG&E: 4 to 9 p.m. every day, super off-peak, the rest
}

/** The kWh the baseline credit applies to: SCE's region allocation times the days (no more than the use); SDG&E's
 * allowance times 1.3 (no more than the use). */
export function touBaselineKwh(rules: Rules, key: string, x: TOUInput): number {
  const b = rules.bills[key];
  if (b.kind === "sce") {
    const q = b.baseline_quantities.basic[x.region ?? b.defaults.region];
    return Math.min(x.kwh, q[x.season === "summer" ? 0 : 1] * x.days);
  }
  return Math.min(x.kwh, (x.baselineKwh ?? 0) * (b.baseline_credit.share ?? 1));
}

export function billTOU(rules: Rules, key: string, x: TOUInput): Bill {
  const b = rules.bills[key];
  const sh = periodShares(b.kind, x);
  const lines: Line[] = [];
  for (const c of b.components as Src[]) {
    if (c.basis === "per_kWh_period") {
      const r = (c.rate as Record<string, Record<string, number>>)[x.season];
      const amount = Object.entries(sh).reduce((a, [k, share]) => a + x.kwh * share * r[k], 0);
      const detail = Object.entries(sh).map(([k, share]) => `${Math.round(x.kwh * share * 10) / 10} kWh ${k === "on" ? "on-peak" : k === "mid" ? "mid-peak" : k === "super" ? "super off-peak" : "off-peak"} at $${r[k]}`).join(", ");
      lines.push(mk(c, amount, detail));
    } else {
      lines.push(mk(c, x.kwh * (c.rate as number), `${x.kwh} kWh at $${c.rate}`));
    }
  }
  const base = touBaselineKwh(rules, key, x);
  const bc = b.baseline_credit;
  lines.push({ id: `${key.toLowerCase()}_baseline`, name: "Baseline credit", group: "Credits", what: bc.what, why: bc.why, amount: base * bc.rate,
    cite: bc.cite, quote: bc.quote, effective: bc.effective,
    detail: b.kind === "sce" ? `${base} kWh within the Region ${x.region ?? b.defaults.region} baseline at $${bc.rate}` : `${base} kWh (up to 130 percent of your ${x.baselineKwh ?? 0} kWh allowance) at $${bc.rate}` });
  const bs = b.base_services;
  lines.push({ id: `${key.toLowerCase()}_bsc`, name: "Base Services Charge", group: "Fixed", what: bs.what, why: bs.why, amount: x.days * bs.rate,
    cite: bs.cite, quote: bs.quote, effective: bs.effective, detail: `${x.days} days at $${bs.rate} a day` });
  if (x.climateCredit && b.climate_credit) lines.push(mk({ id: `${key.toLowerCase()}_climate`, name: "California Climate Credit", group: "Credits", basis: "per_bill", ...b.climate_credit }, b.climate_credit.rate, "once, twice a year"));
  return { lines, total: lines.reduce((a, l) => a + l.amount, 0), kwh: x.kwh };
}

export function defaultsTOU(rules: Rules, key: string): TOUInput {
  const d = rules.bills[key].defaults;
  return { kwh: d.kwh, peakShare: d.peak_share, superShare: d.super_share, weekdayShare: d.weekday_share ?? 5 / 7, season: d.season, days: d.days, region: d.region, baselineKwh: d.baseline_kwh, climateCredit: d.climate_credit ?? false };
}

/** Texas, any wires company (Oncor "TX", CenterPoint "TXC"): the retailer's energy charge, the company's fixed and
 * per-kWh charges. billTX is this for Oncor. */
export function billTDSP(rules: Rules, key: string, x: TXInput): Bill {
  const t = rules.bills[key];
  const lines: Line[] = [{
    id: `${key.toLowerCase()}_energy`, name: "Energy charge (your retail electric provider)", group: "Energy", amount: x.kwh * x.energyRate,
    what: "What your retailer charges for the power itself, under the plan you chose.", why: "In most of ERCOT, retailers compete to sell power; the price is on the plan's Electricity Facts Label.",
    cite: t.energy_default.cite, quote: t.energy_default.derivation, effective: "your plan", detail: `${x.kwh} kWh at $${x.energyRate}`,
  }];
  const who = key === "TXC" ? "Delivery (CenterPoint)" : "Delivery (Oncor)";
  for (const f of t.fixed as Src[]) lines.push(mk({ ...f, group: who }, f.rate as number, "per month"));
  for (const p of t.per_kwh as Src[]) lines.push(mk({ ...p, group: who }, x.kwh * (p.rate as number), `${x.kwh} kWh at $${p.rate}`));
  return { lines, total: lines.reduce((a, l) => a + l.amount, 0), kwh: x.kwh };
}
export function defaultsTDSP(rules: Rules, key: string): TXInput {
  return { kwh: rules.bills[key].defaults.kwh, energyRate: rules.bills[key].energy_default.rate };
}

/** Every bill's default, by key: the page's five. */
export const BILL_KEYS = ["CA", "SCE", "SDGE", "TX", "TXC"] as const;
export type BillKey = (typeof BILL_KEYS)[number];
export function defaultBill(rules: Rules, key: BillKey): Bill {
  if (key === "CA") return billCA(rules, defaultsCA(rules));
  if (key === "TX") return billTX(rules, defaultsTX(rules));
  if (key === "TXC") return billTDSP(rules, "TXC", defaultsTDSP(rules, "TXC"));
  return billTOU(rules, key, defaultsTOU(rules, key));
}
