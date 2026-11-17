// Energy Research Warehouse (ERW) site, session 88: what a battery saves a customer (/battery/customer, in review).
// The page's arithmetic, and nothing else. It reads no table and no file: every number in it is one the reader typed.
// It runs in the reader's browser (app/battery/customer/Calc.tsx); nothing typed is sent, stored or put in the
// address. No imports: Node runs this file as it is (tests/test_session88.py).
//
// The bill it works on is a commercial bill with two parts a battery can lower:
//   a demand charge   USD per kW of the month's highest demand
//   energy rates      USD per kWh, one for the peak hours and one for the off-peak hours
// The battery does two things with one discharge a day:
//   shaves the peak   it discharges through the customer's peak, so the meter's highest demand is lower
//   shifts energy     it charges in the off-peak hours and discharges in the peak hours
// What it assumes, stated on the page: the customer's peak falls in the peak-rate hours; the battery knows when the
// peak comes and is full when it does; one full cycle on each day it runs; the demand charge is set by one monthly
// peak. A real bill has ratchets, seasons and riders this does not know.

export type Field = { key: keyof Inputs; label: string; unit: string; hint: string; start?: string; min: number; max: number; zero?: boolean };
export type Inputs = {
  peakKw: number; demandCharge: number; peakRate: number; offPeakRate: number; batteryKw: number; batteryKwh: number;
  peakHours: number; days: number; roundTrip: number;
};

/** The fields, in the order the page asks for them. `start` is a starting value the reader can change; a field with
 * none starts empty. Limits only keep a typing slip (a rate in cents, a negative size) from giving a result. */
export const FIELDS: Field[] = [
  { key: "peakKw", label: "Your peak demand", unit: "kW", hint: "The highest demand on your bill in a month.", min: 0, max: 1e6 },
  { key: "demandCharge", label: "Demand charge", unit: "USD per kW a month", hint: "What your tariff charges for each kW of that peak.", min: 0, max: 500, zero: true },
  { key: "peakRate", label: "Energy rate, peak hours", unit: "USD per kWh", hint: "In dollars: 0.25 is 25 cents.", min: 0, max: 5, zero: true },
  { key: "offPeakRate", label: "Energy rate, off-peak hours", unit: "USD per kWh", hint: "The rate in the hours the battery would charge, in dollars.", min: 0, max: 5, zero: true },
  { key: "batteryKw", label: "Battery power", unit: "kW", hint: "How fast it can discharge.", min: 0, max: 1e6 },
  { key: "batteryKwh", label: "Battery energy", unit: "kWh", hint: "How much it holds. Energy over power is its duration.", min: 0, max: 1e7 },
  { key: "peakHours", label: "How long your peak lasts", unit: "hours", hint: "How long your own demand stays near its highest, in the hours your demand charge counts. The battery must hold its discharge this long to lower the peak.", start: "2", min: 0, max: 24 },
  { key: "days", label: "Days a month it runs", unit: "days", hint: "The days with peak-rate hours: about 21 if weekends are off-peak.", start: "21", min: 0, max: 31, zero: true },
  { key: "roundTrip", label: "Round trip", unit: "percent", hint: "Of each kWh put in, how much comes back out.", start: "86", min: 1, max: 100 },
];

/** A typed value as a number, or null: empty, not a number, or outside the field's limits. Never a guess. */
export function read(text: string, f: Field): number | null {
  const s = text.trim().replace(/,/g, "");
  if (s === "" || !/^\d*\.?\d+$|^\d+\.$/.test(s)) return null;
  const v = Number(s);
  if (!Number.isFinite(v) || v < f.min || v > f.max || (v === 0 && !f.zero)) return null;
  return v;
}

/** Every field read, or the keys that are missing or cannot be read. */
export function readAll(text: Record<string, string>): { ok: true; x: Inputs } | { ok: false; missing: string[] } {
  const x: Record<string, number> = {};
  const missing: string[] = [];
  for (const f of FIELDS) {
    const v = read(text[f.key] ?? "", f);
    if (v === null) missing.push(f.key);
    else x[f.key] = v;
  }
  return missing.length ? { ok: false, missing } : { ok: true, x: x as Inputs };
}

export type Result = {
  shavedKw: number;            // kW taken off the monthly peak
  limit: "power" | "energy" | "peak";  // what set it: the battery's power, its energy over the peak's hours, or the peak itself
  demandSaved: number;         // USD a month
  dischargedKwh: number;       // kWh a day out of the battery, in the peak hours
  chargedKwh: number;          // kWh a day into it, in the off-peak hours
  shiftPerDay: number;         // USD a day: peak energy avoided less off-peak energy bought (can be negative)
  shifts: boolean;             // whether shifting pays; when it does not, the battery is not run for it
  energySaved: number;         // USD a month
  cyclesForPeak: number;       // kWh a day the peak shave alone needs
  monthSaved: number; yearSaved: number;
  demandBefore: number;        // USD a month, the demand charge without the battery
  hours: number;               // the battery's duration
  breakEvenRate: number;       // the peak rate at which shifting just pays, USD per kWh
};

/** The saving. A pure function of what was typed. */
export function saving(x: Inputs): Result {
  const eta = x.roundTrip / 100;
  const byEnergy = x.batteryKwh / x.peakHours;
  const shavedKw = Math.min(x.batteryKw, byEnergy, x.peakKw);
  const limit: Result["limit"] = shavedKw === x.peakKw ? "peak" : shavedKw === x.batteryKw ? "power" : "energy";
  const demandSaved = shavedKw * x.demandCharge;
  // one cycle a day: the whole battery out in the peak hours, and that much over the round trip back in off-peak
  const dischargedKwh = x.batteryKwh;
  const chargedKwh = x.batteryKwh / eta;
  const shiftPerDay = dischargedKwh * x.peakRate - chargedKwh * x.offPeakRate;
  const shifts = shiftPerDay > 0;
  // when shifting does not pay, the battery still cycles for the peak: the energy it loses on the round trip is a cost
  const cyclesForPeak = shavedKw * x.peakHours;
  const peakOnlyPerDay = cyclesForPeak * x.peakRate - (cyclesForPeak / eta) * x.offPeakRate;
  const energySaved = (shifts ? shiftPerDay : peakOnlyPerDay) * x.days;
  const monthSaved = demandSaved + energySaved;
  return {
    shavedKw, limit, demandSaved, dischargedKwh: shifts ? dischargedKwh : cyclesForPeak, chargedKwh: shifts ? chargedKwh : cyclesForPeak / eta,
    shiftPerDay, shifts, energySaved, cyclesForPeak, monthSaved, yearSaved: monthSaved * 12,
    demandBefore: x.peakKw * x.demandCharge, hours: x.batteryKwh / x.batteryKw, breakEvenRate: x.offPeakRate / eta,
  };
}

/** Money and quantities as the page prints them. */
export function usd(v: number): string {
  const r = Math.round(v);
  return `${r < 0 ? "-" : ""}$${Math.abs(r).toLocaleString("en-US")}`;
}
export function qty(v: number, digits = 0): string {
  return v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

// Session 7504 (chain 304): what the reader typed is printed back as typed. Until this session the page printed a
// typed size, peak or count of days with qty(v) (no decimals) and a typed demand charge with usd(v) (whole dollars),
// so a demand charge of 5.36 read "At $5 per kW that is $1,072 a month" beside a figure made with 5.36, and a 13.5 kWh
// battery read "14 kWh". The arithmetic was right; the number printed beside it was not the one it used.
/** A number the reader typed, as typed: grouped, never rounded to a whole number. */
export function typed(v: number): string {
  return v.toLocaleString("en-US", { maximumFractionDigits: 6 });
}
/** A rate in dollars the reader typed: whole dollars as they are, otherwise to the cent or as far as was typed. */
export function rate(v: number): string {
  return `$${v.toLocaleString("en-US", { minimumFractionDigits: Number.isInteger(v) ? 0 : 2, maximumFractionDigits: 6 })}`;
}
/** The values a field takes, in words. A field that refuses zero says so (it said "0 to 1,000,000" and refused 0). */
export function range(f: Field): string {
  return f.min === 0 && !f.zero ? `more than 0, up to ${qty(f.max)}` : `${qty(f.min)} to ${qty(f.max)}`;
}

// Session 7513 (chain 304, part B): the line under a field whose typed value is refused. A tariff sheet can print its
// energy rates in cents (Southern California Edison's, as NREL/TP-5400-63162 prints it: 14.66 cents per kWh). Typed so,
// 14.66 is over the field's limit and was refused with "(0 to 5)" alone, in the place of the one hint that said the
// field takes dollars; the off-peak field never said it. A refused rate is now told the unit as well as the range.
/** What a refused rate per kWh is told after its range: that the field takes dollars. Nothing for another field. */
export function inDollars(f: Field): string {
  return f.unit === "USD per kWh" ? " The rate is typed in dollars: 12 cents is 0.12." : "";
}

// Ruling alternative 2 of /battery/customer (session 7704, branch wip/alt-battery-customer-2; not a default on main):
// "Saved a year" by the plan's own seasons. A tariff with seasons (Salt River Project E-32: 2 summer peak months, 4
// summer, 6 winter) charges a different demand charge and different energy rates in each; twelve of one month's saving
// is then not the year. The reader may type up to two more seasons, each its months and its three rates; the rates in
// the fields above hold for the months left. With no other season typed the year is twelve of the month, as on main.
export type Season = { months: number; demandCharge: number; peakRate: number; offPeakRate: number };
/** The fields of one more season: its months, then the three rates of the fields above with their limits. */
export const SEASON_FIELDS: Field[] = [
  { key: "days", label: "Months of this season", unit: "months",   // key: a Field needs one; the season's inputs are named by their place, not by it
    hint: "How many months of the year these rates hold.", min: 1, max: 11 },
  ...FIELDS.filter((f) => f.key === "demandCharge" || f.key === "peakRate" || f.key === "offPeakRate"),
];
/** One more season read from its four typed values: the season, "empty" when nothing is typed, or null when it is typed
 * only in part or a value cannot be read (never a guess). */
export function readSeason(text: string[]): Season | "empty" | null {
  if (text.every((t) => t.trim() === "")) return "empty";
  const v = SEASON_FIELDS.map((f, i) => read(text[i] ?? "", f));
  if (v.some((n) => n === null)) return null;
  return { months: v[0] as number, demandCharge: v[1] as number, peakRate: v[2] as number, offPeakRate: v[3] as number };
}
/** The year by seasons: the months left at the fields' own rates, and each season's months at its own. Null when the
 * seasons typed take twelve months or more (no month is left for the rates above). */
export function yearBySeasons(x: Inputs, seasons: Season[]): { year: number; firstMonths: number; parts: { months: number; month: number }[] } | null {
  const taken = seasons.reduce((a, s) => a + s.months, 0);
  if (taken >= 12) return null;
  const parts = [{ months: 12 - taken, month: saving(x).monthSaved },
    ...seasons.map((s) => ({ months: s.months, month: saving({ ...x, demandCharge: s.demandCharge, peakRate: s.peakRate, offPeakRate: s.offPeakRate }).monthSaved }))];
  return { year: parts.reduce((a, p) => a + p.months * p.month, 0), firstMonths: 12 - taken, parts };
}
