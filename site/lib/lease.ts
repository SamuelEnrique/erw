// Session 45: severance v0.2, the lease tool (/severance/lease). A lease file (a CSV dropped or pasted in the browser,
// never sent to the server) is read into well-months; each well-month and product is taxed at the base rate and with
// the reduced rates the reader ticks, by the calculator of lib/severance.ts on the cited rules of
// data/severance_rules.json, and each rule whose thresholds the well's own numbers meet is flagged "may qualify", with
// its citation. Only type imports, so Node runs this file as it is (site/scripts/test-lease.mjs); the calculator is
// passed in. An estimate for education and planning, not tax advice.
import type { Input, Option, Result, Rules } from "./severance";

export type Engine = {
  compute: (rules: Rules, x: Input) => Result;
  creditPct: (o: Option, pick: { tierPct?: number; period?: string }) => { pct: number; price?: number; period?: string };
};
export type Product = "oil" | "gas" | "condensate";
export const PRODUCTS: Product[] = ["oil", "gas", "condensate"];

/** The template's columns, in order. state, well_id and month are required; the rest are optional. */
export const COLUMNS = [
  "state", "well_id", "month", "oil_bbl", "gas_mcf", "condensate_bbl", "oil_price", "gas_price", "condensate_price",
  "completion_date", "depth_ft", "horizontal", "days_produced", "water_cut_pct", "well_type", "inactive_months",
  "hcg_cost_ratio", "nm_district", "royalty_pct", "trucking_per_unit", "transport_per_bbl", "exemptions",
] as const;
export const COLUMN_HELP: Record<(typeof COLUMNS)[number], string> = {
  state: "TX, LA or NM",
  well_id: "any label; one well per label and state",
  month: "production month, YYYY-MM",
  oil_bbl: "oil produced in the month, barrels",
  gas_mcf: "gas produced in the month, Mcf",
  condensate_bbl: "condensate produced in the month, barrels (TX, LA)",
  oil_price: "USD per bbl; blank: the month's WTI Cushing mean from the warehouse",
  gas_price: "USD per Mcf; blank: the month's Henry Hub mean (USD per MMBtu, applied per Mcf)",
  condensate_price: "USD per bbl; blank: the month's WTI Cushing mean",
  completion_date: "YYYY-MM-DD; Louisiana's oil rate, and the windows of the horizontal, deep and high-cost gas rules",
  depth_ft: "true vertical depth, feet (Louisiana deep wells)",
  horizontal: "yes or no (Louisiana horizontal wells)",
  days_produced: "producing days in the month (Louisiana stripper and incapable oil wells); blank: the calendar days",
  water_cut_pct: "produced water as a percent of oil and water (TX low-producing oil lease, LA incapable oil well)",
  well_type: "oil or gas, as the state designates the well (TX low-producing and high-cost gas, LA incapable gas)",
  inactive_months: "months without production before the well's production resumed (two-year inactive wells)",
  hcg_cost_ratio: "drilling and completion costs over the median for high-cost gas wells (TX high-cost gas)",
  nm_district: "New Mexico: the TRD suffix (e.g. 2510) or the county, district and suffix label",
  royalty_pct: "New Mexico: royalties to the US, the state or a tribe, percent of value",
  trucking_per_unit: "New Mexico: trucking, USD per bbl or Mcf",
  transport_per_bbl: "Louisiana oil and condensate: trucking, barging and pipeline fees, USD per bbl",
  exemptions: "rule ids you claim, separated by ';' (e.g. tx_eor;tx_lp_oil); you can also tick them on the page",
};

export type Facts = {
  completion?: string; depth?: number; horizontal?: boolean; days?: number; waterCut?: number; wellType?: "oil" | "gas";
  inactiveMonths?: number; hcgRatio?: number; district?: { label: string; rate: number }; royaltyPct?: number;
  trucking?: number; transport?: number;
};
export type WellMonth = {
  line: number; state: string; well: string; key: string; month: string;
  vol: Partial<Record<Product, number>>; price: Partial<Record<Product, number>>; facts: Facts; exemptions: string[];
};
export type Issue = { line: number; message: string };
export type Parsed = { rows: WellMonth[]; errors: Issue[]; unknownColumns: string[] };

const ALIASES: Record<string, string> = {
  well: "well_id", wellid: "well_id", well_name: "well_id", oil: "oil_bbl", gas: "gas_mcf", condensate: "condensate_bbl",
  depth: "depth_ft", tvd: "depth_ft", tvd_ft: "depth_ft", water_cut: "water_cut_pct", days: "days_produced",
  district: "nm_district", completion: "completion_date", royalty: "royalty_pct", trucking: "trucking_per_unit",
  transport: "transport_per_bbl", production_month: "month",
};
const STATE_NAMES: Record<string, string> = { texas: "TX", louisiana: "LA", "new mexico": "NM" };
const WELL_FACTS = ["completion_date", "depth_ft", "horizontal", "well_type", "inactive_months", "hcg_cost_ratio",
  "nm_district", "royalty_pct", "trucking_per_unit", "transport_per_bbl"];

/** RFC 4180 fields: quotes, doubled quotes, commas or tabs (whichever the header uses), CRLF. */
export function splitCsv(text: string): { cells: string[]; line: number }[] {
  const src = text.replace(/^﻿/, "");
  const firstLine = src.split(/\r?\n/).find((l) => l.trim() && !l.startsWith("#")) ?? "";
  const sep = firstLine.includes("\t") && !firstLine.includes(",") ? "\t" : ",";
  const out: { cells: string[]; line: number }[] = [];
  let cells: string[] = [], cur = "", q = false, line = 1, start = 1;
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (q) {
      if (c === '"' && src[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') q = false;
      else { if (c === "\n") line++; cur += c; }
    } else if (c === '"' && cur === "") q = true;
    else if (c === sep) { cells.push(cur); cur = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && src[i + 1] === "\n") i++;
      cells.push(cur); out.push({ cells, line: start }); cells = []; cur = ""; line++; start = line;
    } else cur += c;
  }
  if (cur !== "" || cells.length) { cells.push(cur); out.push({ cells, line: start }); }
  return out.filter((r) => r.cells.some((c) => c.trim() !== "") && !r.cells[0].trim().startsWith("#"));
}

const norm = (h: string) => {
  const k = h.trim().toLowerCase().replace(/[\s\-/]+/g, "_").replace(/[^a-z0-9_]/g, "");
  return ALIASES[k] ?? k;
};

function num(v: string, what: string, line: number, errors: Issue[]): number | undefined {
  const t = v.trim().replace(/[$,\s]/g, "");
  if (t === "") return undefined;
  const n = Number(t);
  if (!Number.isFinite(n) || n < 0) { errors.push({ line, message: `${what}: "${v.trim()}" is not a number of zero or more` }); return undefined; }
  return n;
}

/** The New Mexico district a cell names: its TRD suffix (leading zeros optional) or its label. */
export function findDistrict(rules: Rules, cell: string): { label: string; rate: number } | undefined {
  const list = rules.states.NM?.products.oil.base.find((b) => b.rate === "district")?.districts?.list ?? [];
  const t = cell.trim().toLowerCase();
  if (!t) return undefined;
  if (/^\d+$/.test(t)) return list.find((d) => Number(d.label.match(/suffix (\d+)$/)?.[1]) === Number(t));
  return list.find((d) => d.label.toLowerCase() === t);
}

/** Read a lease file into well-months. Nothing here touches the network. */
export function parseLease(text: string, rules: Rules): Parsed {
  const errors: Issue[] = [];
  const table = splitCsv(text);
  if (!table.length) return { rows: [], errors: [{ line: 0, message: "The file is empty" }], unknownColumns: [] };
  const header = table[0].cells.map(norm);
  const known = new Set<string>(COLUMNS);
  const unknownColumns = header.filter((h) => h && !known.has(h));
  for (const need of ["state", "well_id", "month"]) {
    if (!header.includes(need)) errors.push({ line: table[0].line, message: `The header has no ${need} column` });
  }
  if (errors.length) return { rows: [], errors, unknownColumns };
  const rows: WellMonth[] = [];
  const seen = new Set<string>();
  // well facts given on any row of a well hold for its other rows (session 45)
  const wellFacts = new Map<string, Record<string, string>>();
  const recs = table.slice(1).map(({ cells, line }) => {
    const r: Record<string, string> = {};
    header.forEach((h, i) => { r[h] = (cells[i] ?? "").trim(); });
    return { r, line };
  });
  const stateOf = (s: string) => { const u = s.trim().toUpperCase(); return rules.states[u] ? u : STATE_NAMES[s.trim().toLowerCase()] ?? u; };
  for (const { r } of recs) {
    const k = `${stateOf(r.state)}|${r.well_id}`;
    const f = wellFacts.get(k) ?? {};
    for (const c of WELL_FACTS) if (r[c] && !f[c]) f[c] = r[c];
    wellFacts.set(k, f);
  }
  for (const { r, line } of recs) {
    const state = stateOf(r.state ?? "");
    if (!rules.states[state]) { errors.push({ line, message: `state "${r.state}" is not one of ${Object.keys(rules.states).join(", ")}` }); continue; }
    const well = r.well_id;
    if (!well) { errors.push({ line, message: "no well_id" }); continue; }
    let month = (r.month ?? "").trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(month)) month = month.slice(0, 7);
    const mm = /^(\d{1,2})\/(\d{4})$/.exec(month);
    if (mm) month = `${mm[2]}-${mm[1].padStart(2, "0")}`;
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)) { errors.push({ line, message: `month "${r.month}" is not YYYY-MM` }); continue; }
    const key = `${state}|${well}`;
    if (seen.has(`${key}|${month}`)) { errors.push({ line, message: `${well} (${state}) ${month} appears twice; only the first row is used` }); continue; }
    seen.add(`${key}|${month}`);
    const w = { ...wellFacts.get(key), ...Object.fromEntries(Object.entries(r).filter(([, v]) => v !== "")) } as Record<string, string>;
    const vol: WellMonth["vol"] = {}, price: WellMonth["price"] = {};
    const col = { oil: "oil_bbl", gas: "gas_mcf", condensate: "condensate_bbl" } as const;
    for (const p of PRODUCTS) {
      const v = num(r[col[p]] ?? "", col[p], line, errors);
      if (v !== undefined) {
        if (!rules.states[state].products[p]) { if (v > 0) errors.push({ line, message: `${rules.states[state].name} ${p} is not in the rules file; not computed` }); }
        else vol[p] = v;
      }
      const pr = num(r[`${p}_price`] ?? "", `${p}_price`, line, errors);
      if (pr !== undefined) price[p] = pr;
    }
    const facts: Facts = {};
    const comp = (w.completion_date ?? "").trim();
    if (comp) {
      if (/^\d{4}-\d{2}(-\d{2})?$/.test(comp)) facts.completion = comp.length === 7 ? `${comp}-01` : comp;
      else errors.push({ line, message: `completion_date "${comp}" is not YYYY-MM-DD` });
    }
    facts.depth = num(w.depth_ft ?? "", "depth_ft", line, errors);
    const hz = (w.horizontal ?? "").trim().toLowerCase();
    if (hz) facts.horizontal = ["yes", "y", "true", "1", "horizontal"].includes(hz);
    facts.days = num(r.days_produced ?? "", "days_produced", line, errors);
    if (facts.days !== undefined && facts.days > daysIn(month)) {
      errors.push({ line, message: `days_produced ${facts.days} is more than the ${daysIn(month)} days of ${month}` });
      facts.days = undefined;
    }
    facts.waterCut = num(r.water_cut_pct ?? "", "water_cut_pct", line, errors);
    if (facts.waterCut !== undefined && facts.waterCut > 100) { errors.push({ line, message: "water_cut_pct is over 100" }); facts.waterCut = undefined; }
    const wt = (w.well_type ?? "").trim().toLowerCase();
    if (wt === "oil" || wt === "gas") facts.wellType = wt;
    else if (wt) errors.push({ line, message: `well_type "${w.well_type}" is not oil or gas` });
    facts.inactiveMonths = num(w.inactive_months ?? "", "inactive_months", line, errors);
    facts.hcgRatio = num(w.hcg_cost_ratio ?? "", "hcg_cost_ratio", line, errors);
    if (state === "NM" && w.nm_district) {
      facts.district = findDistrict(rules, w.nm_district);
      if (!facts.district) errors.push({ line, message: `nm_district "${w.nm_district}" is not a suffix or label of TRD's 2026 table; ad valorem left out` });
    }
    facts.royaltyPct = num(w.royalty_pct ?? "", "royalty_pct", line, errors);
    facts.trucking = num(w.trucking_per_unit ?? "", "trucking_per_unit", line, errors);
    facts.transport = num(w.transport_per_bbl ?? "", "transport_per_bbl", line, errors);
    const exemptions = (r.exemptions ?? "").split(/[;|\s]+/).map((s) => s.trim()).filter(Boolean);
    rows.push({ line, state, well, key, month, vol, price, facts, exemptions });
  }
  return { rows, errors, unknownColumns };
}

// --- months -------------------------------------------------------------------------------------------------------

export function daysIn(month: string): number {
  const [y, m] = month.split("-").map(Number);
  return new Date(Date.UTC(y, m, 0)).getUTCDate();
}
export function shift(month: string, k: number): string {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + k, 1));
  return d.toISOString().slice(0, 7);
}
/** Whole months from a date's month to a production month (a well completed in March produces month 0 in March). */
export function monthsFrom(date: string, month: string): number {
  const [y1, m1] = date.slice(0, 7).split("-").map(Number);
  const [y2, m2] = month.split("-").map(Number);
  return (y2 - y1) * 12 + (m2 - m1);
}

// --- prices -------------------------------------------------------------------------------------------------------

export type PricePoint = { value: number; n: number; label: string };
/** Monthly means of the warehouse's EIA daily spot prices: oil (WTI Cushing, also condensate) and gas (Henry Hub). */
export type PriceBook = { oil: Record<string, PricePoint>; gas: Record<string, PricePoint> };

// --- the analysis -------------------------------------------------------------------------------------------------

export type Flag = {
  id: string; name: string; product: Product; cite: string; test: string; notes: string[];
  savings: number; info?: boolean;
};
export type Line = {
  line: number; state: string; well: string; key: string; month: string; product: Product; unit: string;
  volume: number; price: number | null; priceSource: string; base: number | null; withTicked: number | null;
  ticked: string[]; fees: number; flags: Flag[]; best: number; notes: string[];
};
export type WellSum = { key: string; state: string; well: string; months: number; base: number; withTicked: number; fees: number; potential: number };
export type Opportunity = { key: string; state: string; well: string; id: string; name: string; cite: string; months: string[]; savings: number };
export type Analysis = {
  lines: Line[]; wells: WellSum[]; lease: { base: number; withTicked: number; fees: number; potential: number };
  opportunities: Opportunity[]; issues: Issue[];
};

type Ctx = { rules: Rules; engine: Engine; byWell: Map<string, Map<string, WellMonth>>; rows: WellMonth[] };

const pctTxt = (r: number) => `${(r * 100).toLocaleString("en-US", { maximumFractionDigits: 4 })}%`;
const n2 = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });

function optionOf(rules: Rules, state: string, product: Product, id: string): Option | undefined {
  return rules.states[state]?.products[product]?.options.find((o) => o.id === id);
}

/** The calculator's input for one well-month and product at the base rate (no option). */
export function baseInput(rules: Rules, r: WellMonth, product: Product, price: number): Input {
  const x: Input = { state: r.state, product, volume: r.vol[product] ?? 0, price };
  if (r.state === "LA" && product === "oil") {
    // La. R.S. 47:633: 6.5 percent for a well completed on or after July 1, 2025, else 12.5 percent
    x.variant = r.facts.completion && r.facts.completion >= "2025-07-01" ? "la_oil_post2025" : "la_oil_pre2025";
  }
  if (r.state === "LA") x.transport = r.facts.transport ?? 0;
  if (r.state === "NM") {
    x.adval = r.facts.district ? r.facts.district.rate * 100 : 0;
    x.royaltyPct = r.facts.royaltyPct ?? 0;
    x.trucking = r.facts.trucking ?? 0;
  }
  return x;
}

/** The option part of an input: a rate-group option or the credit, with the well's parameter and the month's period. */
function withOption(x: Input, o: Option, r: WellMonth): Input {
  const pick = { id: o.id, period: r.month, param: o.id === "tx_hcg" ? r.facts.hcgRatio ?? o.param?.default : o.param?.default };
  return o.group === "credit" ? { ...x, credit: pick } : { ...x, option: pick };
}

function savingsOf(c: Ctx, x: Input, o: Option, r: WellMonth, base: number): number {
  return base - c.engine.compute(c.rules, withOption(x, o, r)).withTotal;
}

/** The TX low-producing oil lease test for a month: the lease's barrels per well per day, and its oil per barrel of
 * water, over the months of the 90 days ending with it that the file holds (session 45). */
export function txOilLease(rows: WellMonth[], month: string): { perWellDay: number; months: string[]; wells: number; oilPerWater: number | null } | null {
  const months = [shift(month, -2), shift(month, -1), month];
  let oil = 0, wellDays = 0, water = 0, waterKnown = true;
  const wells = new Set<string>(), held: string[] = [];
  for (const m of months) {
    // the lease's oil wells: the Texas wells with oil in that month
    const rs = rows.filter((r) => r.state === "TX" && r.month === m && (r.vol.oil ?? 0) > 0);
    if (!rs.length) continue;
    held.push(m);
    for (const r of rs) {
      const o = r.vol.oil ?? 0;
      oil += o; wellDays += daysIn(m); wells.add(r.key);
      const wc = r.facts.waterCut;
      if (wc === undefined) waterKnown = false;
      else if (wc >= 100) water = Infinity;
      else water += (o * wc) / (100 - wc);
    }
  }
  if (!wellDays || !held.includes(month)) return null;
  return { perWellDay: oil / wellDays, months: held, wells: wells.size, oilPerWater: waterKnown && water > 0 ? oil / water : null };
}

/** The TX low-producing gas test: the well's average Mcf per day over the three months before, as the file holds them
 * (or the month itself when it holds none of them). */
export function txGasAverage(byMonth: Map<string, WellMonth>, month: string): { perDay: number; months: string[]; prior: boolean } {
  const prior = [shift(month, -3), shift(month, -2), shift(month, -1)].filter((m) => byMonth.get(m)?.vol.gas !== undefined);
  const ms = prior.length ? prior : [month];
  const gas = ms.reduce((a, m) => a + (byMonth.get(m)?.vol.gas ?? 0), 0);
  const days = ms.reduce((a, m) => a + daysIn(m), 0);
  return { perDay: gas / days, months: ms, prior: prior.length > 0 };
}

/** Months without production before a month: the reader's inactive_months, else the file's run of zero months. */
export function inactiveBefore(byMonth: Map<string, WellMonth>, r: WellMonth): { months: number; from: "fact" | "file" } {
  if (r.facts.inactiveMonths !== undefined) return { months: r.facts.inactiveMonths, from: "fact" };
  let k = 0;
  for (let m = shift(r.month, -1); ; m = shift(m, -1)) {
    const p = byMonth.get(m);
    if (!p || PRODUCTS.some((q) => (p.vol[q] ?? 0) > 0)) break;
    k++;
  }
  return { months: k, from: "file" };
}

function flagsFor(c: Ctx, r: WellMonth, product: Product, x: Input, base: number): { flags: Flag[]; notes: string[] } {
  const flags: Flag[] = [], notes: string[] = [];
  const add = (id: string, test: string, extra: string[] = []) => {
    const o = optionOf(c.rules, r.state, product, id);
    if (!o) return;
    flags.push({ id, name: o.name, product, cite: o.cite, test, notes: extra, savings: savingsOf(c, x, o, r, base) });
  };
  const byMonth = c.byWell.get(r.key)!;
  const vol = r.vol[product] ?? 0;
  const days = r.facts.days ?? daysIn(r.month);
  const daysNote = r.facts.days === undefined ? `the ${daysIn(r.month)} calendar days (days_produced not given)` : `${r.facts.days} producing days`;
  const inact = inactiveBefore(byMonth, r);
  const inactTxt = `${inact.months} months without production before it (${inact.from === "fact" ? "inactive_months" : "zero months in the file"}), 24 or more`;

  if (r.state === "TX") {
    if (product === "oil") {
      const t = txOilLease(c.rows, r.month);
      if (t && vol > 0) {
        const byRate = t.perWellDay < 15, byWater = t.oilPerWater !== null && t.oilPerWater < 0.05;
        if (byRate || byWater) {
          const o = optionOf(c.rules, "TX", "oil", "tx_lp_oil")!;
          const cp = c.engine.creditPct(o, { period: r.month });
          const extra = [cp.price !== undefined
            ? `certified price for ${r.month}: $${cp.price} (2005 dollars), a ${cp.pct} percent credit`
            : `no certified price is published for ${r.month} in the rules file: no credit computed`];
          const parts = [];
          if (byRate) parts.push(`the lease averages ${n2(t.perWellDay)} bbl per well per day over ${t.months.join(", ")} (${t.wells} wells), under 15`);
          if (byWater) parts.push(`${n2(t.oilPerWater! * 100)}% oil per barrel of produced water, under 5%`);
          add("tx_lp_oil", parts.join("; "), extra);
        }
      }
      if (inact.months >= 24) add("tx_oil_inactive", inactTxt, ["the Railroad Commission must designate the well; five years from then"]);
    }
    if (product === "gas") {
      if (r.facts.wellType !== "oil") {
        const g = txGasAverage(byMonth, r.month);
        if (g.perDay <= 90) {
          const o = optionOf(c.rules, "TX", "gas", "tx_lp_gas")!;
          const cp = c.engine.creditPct(o, { period: r.month });
          add("tx_lp_gas", `${n2(g.perDay)} Mcf per day over ${g.months.join(", ")}${g.prior ? "" : " (the file holds none of the three months before, so this month)"}, 90 or less`, [
            cp.price !== undefined ? `certified price for ${r.month}: $${cp.price} (2005 dollars), a ${cp.pct} percent credit` : `no certified price is published for ${r.month}: no credit computed`,
            ...(r.facts.wellType ? [] : ["for a gas well only: casinghead gas is not eligible (well_type not given)"]),
            "cannot be reported with high-cost gas for the same well and period",
          ]);
        }
        if (r.facts.hcgRatio !== undefined && r.facts.hcgRatio > 0) {
          const within = r.facts.completion ? monthsFrom(r.facts.completion, r.month) : undefined;
          if (within === undefined || within < 120) {
            const rate = Math.max(0, 0.075 - 0.075 * (r.facts.hcgRatio / 2));
            add("tx_hcg", `costs ${r.facts.hcgRatio} times the median: 7.5% less 7.5% x ${r.facts.hcgRatio} / 2 = ${pctTxt(rate)}`, [
              within === undefined ? "120-month window not checked: completion_date not given" : `month ${within + 1} of the 120 from completion`,
              "the Railroad Commission must certify the well; the reduction stops at 50 percent of drilling and completion costs",
            ]);
          }
        }
      }
      if (inact.months >= 24) add("tx_gas_inactive", inactTxt, ["the Railroad Commission must designate the well; five years from then"]);
    }
  }

  if (r.state === "LA") {
    const deep = r.facts.depth !== undefined && r.facts.depth > 15000;
    const deepWhen = !r.facts.completion || r.facts.completion > "1994-07-31";
    const deepMonths = r.facts.completion ? monthsFrom(r.facts.completion, r.month) : undefined;
    const deepId = { oil: "la_oil_deep", gas: "la_gas_deep", condensate: "la_cond_deep" }[product];
    if (deep && deepWhen && (deepMonths === undefined || deepMonths < 24)) {
      add(deepId, `true vertical depth ${n2(r.facts.depth!)} ft, more than 15,000`, [
        deepMonths === undefined ? "24-month window not checked: completion_date not given" : `month ${deepMonths + 1} of 24 from completion (commercial production assumed to begin then)`,
        "or until payout of the well cost, which the file does not show",
      ]);
    }
    if (product === "oil" && vol > 0) {
      const perDay = vol / days;
      if (perDay <= 10) add("la_stripper", `${n2(perDay)} bbl per producing day over ${daysNote}, 10 or less`, ["certified by the Department of Revenue; exempt in a month its value is below $20 a barrel"]);
      if (perDay <= 25) {
        if (r.facts.waterCut === undefined) notes.push(`LA incapable oil well not assessed: ${n2(perDay)} bbl per producing day is 25 or less, but water_cut_pct is not given (50 percent salt water or more)`);
        else if (r.facts.waterCut >= 50) add("la_incapable", `${n2(perDay)} bbl per producing day (${daysNote}), 25 or less, with ${n2(r.facts.waterCut)}% water, 50 or more`, ["every well on a multiple-well lease must be certified"]);
      }
    }
    if (product === "gas" && vol > 0 && r.facts.wellType !== "oil") {
      const perDay = vol / daysIn(r.month);
      if (perDay < 250) add("la_gas_incapable", `${n2(perDay)} Mcf per day over the ${daysIn(r.month)} days of ${r.month}, under 250`, r.facts.wellType ? [] : ["for a well designated a gas well (well_type not given)"]);
    }
    if ((product === "oil" || product === "gas") && inact.months >= 24) {
      add(product === "oil" ? "la_oil_inactive" : "la_gas_inactive", inactTxt, ["certified, producing from the same interval; ten years if production commences before October 1, 2028"]);
    }
    if ((product === "oil" || product === "gas") && r.facts.horizontal) {
      const limit = product === "gas" && r.facts.completion && r.facts.completion >= "2025-07-01" ? 18 : 24;
      const k = r.facts.completion ? monthsFrom(r.facts.completion, r.month) : undefined;
      if (k === undefined || k < limit) {
        add(product === "oil" ? "la_oil_horizontal" : "la_gas_horizontal", `a horizontal well producing on or after July 1, 2015`, [
          k === undefined ? `${limit}-month window not checked: completion_date not given` : `month ${k + 1} of ${limit} from completion`,
          "or until payout of the well cost, which the file does not show",
        ]);
      }
    }
  }

  if (r.state === "NM") {
    const b = c.rules.states.NM.products[product]?.base.find((q) => q.rate === "district");
    if (b) {
      const list = b.districts!.list.map((d) => d.rate);
      flags.push({
        id: "nm_district", name: "Ad valorem production tax, the district's rate", product, cite: b.districts!.cite, savings: 0, info: true,
        test: r.facts.district
          ? `${r.facts.district.label}: ${pctTxt(r.facts.district.rate)} applied`
          : `nm_district not given: the ad valorem production tax is left out (the 2026 districts run from ${pctTxt(Math.min(...list))} to ${pctTxt(Math.max(...list))})`,
        notes: ["no reduced New Mexico rate is flagged: no TRD page read states the stripper, enhanced recovery or workover rates (the method)"],
      });
    }
  }
  return { flags, notes };
}

/** Tax every well-month and product: base, with the reader's ticks, and each rule the numbers meet. */
export function analyzeLease(rules: Rules, engine: Engine, rows: WellMonth[], opts: { prices: PriceBook; ticks: Record<string, string[]> }): Analysis {
  const byWell = new Map<string, Map<string, WellMonth>>();
  for (const r of rows) {
    if (!byWell.has(r.key)) byWell.set(r.key, new Map());
    byWell.get(r.key)!.set(r.month, r);
  }
  const c: Ctx = { rules, engine, byWell, rows };
  const lines: Line[] = [];
  const issues: Issue[] = [];
  for (const r of [...rows].sort((a, b) => a.key.localeCompare(b.key) || a.month.localeCompare(b.month))) {
    const ticks = opts.ticks[r.key] ?? [];
    for (const product of PRODUCTS) {
      const vol = r.vol[product];
      if (vol === undefined || vol <= 0) continue;
      const prod = rules.states[r.state].products[product];
      const kind = product === "gas" ? "gas" : "oil";
      let price: number | null = r.price[product] ?? null, priceSource = "the file";
      if (price === null) {
        const p = opts.prices[kind][r.month];
        if (p) { price = p.value; priceSource = p.label; }
        else priceSource = `no ${kind === "gas" ? "Henry Hub" : "WTI"} mean held for ${r.month}: enter ${product}_price`;
      }
      const line: Line = {
        line: r.line, state: r.state, well: r.well, key: r.key, month: r.month, product, unit: prod.unit, volume: vol, price, priceSource,
        base: null, withTicked: null, ticked: [], fees: 0, flags: [], best: 0, notes: [],
      };
      if (price === null) { issues.push({ line: r.line, message: `${r.well} ${r.month} ${product}: ${priceSource}` }); lines.push(line); continue; }
      const x = baseInput(rules, r, product, price);
      const res = engine.compute(rules, x);
      line.base = res.baseTotal;
      line.fees = res.fees.reduce((a, f) => a + f.amount, 0);
      if (r.state === "LA" && product === "oil") line.notes.push(r.facts.completion ? `completed ${r.facts.completion}: ${pctTxt(res.base[0].rate)}` : `completion_date not given: ${pctTxt(res.base[0].rate)}, the rate for wells completed before July 1, 2025`);
      // the reader's ticks: one rate-group option per product, and the credit (Texas oil)
      const own = ticks.map((id) => optionOf(rules, r.state, product, id)).filter((o): o is Option => !!o);
      const rate = own.filter((o) => o.group === "rate"), credit = own.find((o) => o.group === "credit");
      if (rate.length > 1) line.notes.push(`${rate.map((o) => o.id).join(" and ")} both ticked: only ${rate[0].id} applied (one reduced rate per well and month)`);
      let xi: Input = x;
      if (rate[0]) xi = withOption(xi, rate[0], r);
      if (credit) xi = withOption(xi, credit, r);
      line.withTicked = rate[0] || credit ? engine.compute(rules, xi).withTotal : res.baseTotal;
      line.ticked = [rate[0]?.id, credit?.id].filter((s): s is string => !!s);
      const f = flagsFor(c, r, product, x, res.baseTotal);
      line.flags = f.flags;
      line.notes.push(...f.notes);
      line.best = Math.max(0, ...f.flags.filter((q) => !q.info).map((q) => q.savings));
      lines.push(line);
    }
  }
  const wells = new Map<string, WellSum>();
  for (const l of lines) {
    const w = wells.get(l.key) ?? { key: l.key, state: l.state, well: l.well, months: 0, base: 0, withTicked: 0, fees: 0, potential: 0 };
    w.base += l.base ?? 0; w.withTicked += l.withTicked ?? 0; w.fees += l.fees; w.potential += l.best;
    wells.set(l.key, w);
  }
  for (const w of wells.values()) w.months = byWell.get(w.key)?.size ?? 0;
  const opp = new Map<string, Opportunity>();
  for (const l of lines) {
    for (const f of l.flags) {
      if (f.info) continue;
      const k = `${l.key}|${f.id}`;
      const o = opp.get(k) ?? { key: l.key, state: l.state, well: l.well, id: f.id, name: f.name, cite: f.cite, months: [], savings: 0 };
      if (!o.months.includes(l.month)) o.months.push(l.month);
      o.savings += f.savings;
      opp.set(k, o);
    }
  }
  const ws = [...wells.values()].sort((a, b) => b.potential - a.potential || a.key.localeCompare(b.key));
  const sum = (k: "base" | "withTicked" | "fees" | "potential") => ws.reduce((a, w) => a + w[k], 0);
  return {
    lines, wells: ws, lease: { base: sum("base"), withTicked: sum("withTicked"), fees: sum("fees"), potential: sum("potential") },
    opportunities: [...opp.values()].sort((a, b) => b.savings - a.savings || a.key.localeCompare(b.key)), issues,
  };
}

/** The ticks a file claims in its exemptions column, per well (unknown ids are reported). */
export function ticksFromFile(rules: Rules, rows: WellMonth[]): { ticks: Record<string, string[]>; unknown: Issue[] } {
  const ticks: Record<string, string[]> = {}, unknown: Issue[] = [];
  for (const r of rows) {
    for (const id of r.exemptions) {
      const known = PRODUCTS.some((p) => optionOf(rules, r.state, p, id));
      if (!known) { unknown.push({ line: r.line, message: `exemption "${id}" is not a ${r.state} rule id` }); continue; }
      const t = (ticks[r.key] ??= []);
      if (!t.includes(id)) t.push(id);
    }
  }
  return { ticks, unknown };
}

/** For each well, the flagged option of each product with the largest total savings (and the credit, when flagged). */
export function bestTicks(a: Analysis, rules: Rules): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  const tot = new Map<string, { key: string; state: string; product: Product; id: string; s: number }>();
  for (const l of a.lines) {
    for (const f of l.flags) {
      if (f.info) continue;
      const k = JSON.stringify([l.key, l.product, f.id]);
      const t = tot.get(k) ?? { key: l.key, state: l.state, product: l.product, id: f.id, s: 0 };
      t.s += f.savings;
      tot.set(k, t);
    }
  }
  const best = new Map<string, { key: string; id: string; s: number }>();
  for (const t of tot.values()) {
    const o = optionOf(rules, t.state, t.product, t.id);
    if (!o || t.s <= 0) continue;
    const slot = JSON.stringify([t.key, t.product, o.group]);
    if (!best.has(slot) || best.get(slot)!.s < t.s) best.set(slot, { key: t.key, id: t.id, s: t.s });
  }
  for (const b of best.values()) {
    const t = (out[b.key] ??= []);
    if (!t.includes(b.id)) t.push(b.id);
  }
  return out;
}

const q = (v: string | number) => {
  const s = String(v);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
const r4 = (v: number | null) => (v === null ? "" : (Math.round(v * 10000) / 10000).toString());

/** The results as CSV, one row per well, month and product (built in the browser for a download link). */
export function toCsv(a: Analysis, rulesVersion: string): string {
  const head = ["state", "well_id", "month", "product", "volume", "unit", "price", "price_source", "base_tax", "tax_with_ticked",
    "ticked", "regulatory_fees", "may_qualify", "best_potential_savings", "notes"];
  const out = [
    `# ERW severance lease tool (session 45), rules version ${rulesVersion}. An estimate for education and planning, not tax advice.`,
    head.join(","),
  ];
  for (const l of a.lines) {
    out.push([l.state, l.well, l.month, l.product, l.volume, l.unit, l.price ?? "", l.priceSource, r4(l.base), r4(l.withTicked),
      l.ticked.join(";"), r4(l.fees),
      l.flags.map((f) => (f.info ? `${f.id}: ${f.test}` : `${f.id} (saves ${r4(f.savings)}): ${f.test}`)).join(" | "),
      r4(l.best), l.notes.join(" | ")].map(q).join(","));
  }
  return out.join("\n") + "\n";
}

export const TEMPLATE_CSV = COLUMNS.join(",") + "\n";

/** A sample lease of clearly fictional wells (session 45), to try the tool; months with warehouse prices and certified
 * Texas prices (June to August 2026). */
export const SAMPLE_CSV = `# SAMPLE: FICTIONAL WELLS, made up to try the ERW lease tool. Not real wells, operators or production.
${COLUMNS.join(",")}
TX,FICTIONAL-TX-1,2026-06,420,1500,,,,,2019-05-01,,,30,96,oil,,,,,,,
TX,FICTIONAL-TX-1,2026-07,400,1450,,,,,2019-05-01,,,31,96,oil,,,,,,,
TX,FICTIONAL-TX-1,2026-08,390,1400,,,,,2019-05-01,,,31,96,oil,,,,,,,
TX,FICTIONAL-TX-2,2026-06,0,2400,,,,,2021-02-01,,,30,,gas,,,,,,,
TX,FICTIONAL-TX-2,2026-07,0,2300,,,,,2021-02-01,,,31,,gas,,,,,,,
TX,FICTIONAL-TX-2,2026-08,0,2250,,,,,2021-02-01,,,31,,gas,,,,,,,
TX,FICTIONAL-TX-3,2026-07,0,45000,,,,,2024-03-01,,,31,,gas,,1.2,,,,,
TX,FICTIONAL-TX-3,2026-08,0,43000,,,,,2024-03-01,,,31,,gas,,1.2,,,,,
LA,FICTIONAL-LA-1,2026-07,240,600,,,,,2012-06-01,9800,no,28,65,oil,,,,,,1.5,
LA,FICTIONAL-LA-1,2026-08,230,580,,,,,2012-06-01,9800,no,29,66,oil,,,,,,1.5,
LA,FICTIONAL-LA-2,2026-07,0,6000,40,,,,2025-11-01,16200,yes,31,,gas,,,,,,1.5,
LA,FICTIONAL-LA-2,2026-08,0,5800,38,,,,2025-11-01,16200,yes,31,,gas,,,,,,1.5,
LA,FICTIONAL-LA-3,2026-07,3100,2000,,,,,2025-09-15,11000,no,31,20,oil,,,,,,1.5,
LA,FICTIONAL-LA-3,2026-08,2950,1900,,,,,2025-09-15,11000,no,31,22,oil,,,,,,1.5,
NM,FICTIONAL-NM-1,2026-07,2600,9000,,,,,2020-08-01,,yes,31,,oil,,,2510,12.5,1.0,,
NM,FICTIONAL-NM-1,2026-08,2500,8800,,,,,2020-08-01,,yes,31,,oil,,,2510,12.5,1.0,,
NM,FICTIONAL-NM-2,2026-07,0,30000,,,,,2018-04-01,,yes,31,,gas,,,4510,12.5,0,,
NM,FICTIONAL-NM-2,2026-08,0,29000,,,,,2018-04-01,,yes,31,,gas,,,4510,12.5,0,,
NM,FICTIONAL-NM-3,2026-08,150,300,,,,,2009-01-01,,no,20,,oil,,,,0,0,,
`;
