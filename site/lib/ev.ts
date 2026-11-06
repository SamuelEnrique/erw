// Session 294: "Should your family get an EV?" (/play/ev), the arithmetic and the defaults. No imports: Node runs this
// file as it is (site/scripts/test-ev.mjs). Every price is a table's (site/data/ev_prices.json, built from the warehouse
// by scripts/build-ev-prices.mjs) or the family's own; every default below says where it comes from. docs/methods/ev_game.md.

export type Defaults = Record<"miles" | "mpg" | "kwhPerMile" | "gasCar" | "evCar" | "homeShare" | "years" | "rate" | "credit", { value: number; min: number; max: number; step: number; label: string; source: string }>;

// fueleconomy.gov, read on 15 October 2026 through its web service (www.fueleconomy.gov/ws/rest/vehicle/<id>):
// 2025 Chevrolet Equinox FWD (id 48061), regular gasoline, 27 mpg combined; 2025 Chevrolet Equinox EV FWD (id 48697),
// 31.24 kWh per 100 miles combined. The same small SUV, gasoline and electric, so the comparison is like for like.
export const DEFAULTS: Defaults = {
  miles: { value: 15000, min: 3000, max: 30000, step: 500, label: "Miles a year", source: "15,000 miles a year: the yearly distance fueleconomy.gov's fuel cost estimates assume (its 2025 Fuel Economy Guide)" },
  mpg: { value: 27, min: 12, max: 60, step: 1, label: "The gasoline car's miles per gallon", source: "27 mpg: the 2025 Chevrolet Equinox FWD, combined city and highway (fueleconomy.gov, vehicle 48061)" },
  kwhPerMile: { value: 0.31, min: 0.2, max: 0.5, step: 0.01, label: "The EV's kWh per mile", source: "0.31 kWh a mile: the 2025 Chevrolet Equinox EV FWD, 31.24 kWh per 100 miles combined (fueleconomy.gov, vehicle 48697)" },
  gasCar: { value: 28600, min: 10000, max: 90000, step: 100, label: "The gasoline car's price, USD", source: "$28,600: the starting price Chevrolet lists for the 2025 Equinox LT, before destination (chevrolet.com, its previous-year page, as a search read it on 15 October 2026). To confirm: type the price a dealer quotes you" },
  evCar: { value: 33600, min: 10000, max: 90000, step: 100, label: "The EV's price, USD", source: "$33,600: the starting price of the 2025 Equinox EV LT1 before destination; GM's own announcement gave $34,995 with the $1,395 destination charge (as a search read it on 15 October 2026). To confirm: type the price a dealer quotes you" },
  // session 3276: the share of charging done at home; the rest at a public charger's price, which the family types (no
  // table in the warehouse holds what public chargers charge, so the game has no default for it)
  homeShare: { value: 100, min: 0, max: 100, step: 5, label: "Charging done at home, percent", source: "100 percent: an assumption that every mile is charged at home, at the home price. Below 100, type the price a public charger near you asks: the warehouse holds no public charging prices, so the game does not guess one" },
  years: { value: 8, min: 1, max: 15, step: 1, label: "Years you keep the car", source: "8 years: an assumption for you to change" },
  rate: { value: 5, min: 0, max: 10, step: 0.5, label: "Interest rate, percent a year", source: "5 percent: a round rate the game chooses, for you to change. It says how much less money counts the later it comes. OMB's rates for 2026 are lower: 3.6 percent on a 7-year Treasury note and 3.7 on a 10-year, or 1.4 and 1.6 after inflation (Circular A-94, Appendix C, revised 6 March 2026)" },
  credit: { value: 7500, min: 0, max: 7500, step: 100, label: "Federal tax credit, USD (your assumption)", source: "your family's own assumption: the IRS says no federal credit for new clean vehicles acquired after 30 September 2025 (irs.gov, Credits for new clean vehicles purchased in 2023 or after, reviewed 13 July 2026); $7,500 was its most" },
};

export const NO_CREDIT_LINE = "No federal credit for cars bought after 30 September 2025.";
export const IRS_URL = "https://www.irs.gov/credits-deductions/credits-for-new-clean-vehicles-purchased-in-2023-or-after";

export type Inputs = { miles: number; mpg: number; kwhPerMile: number; gasUsdPerGal: number; powerUsdPerMwh: number; gasCar: number; evCar: number; years: number; rate: number; credit: number;
  /** session 3276: percent of charging at home (default 100) and the public charger's price for the rest, USD/MWh */
  homeShare?: number; publicUsdPerMwh?: number | null };
export type Verdict = {
  gasPer100: number; evPer100: number; gasYear: number; evYear: number; saveYear: number;
  extra: number;            // what the EV costs more to buy, less any credit (negative: it costs less)
  payback: number | null;   // years until the savings repay the extra; 0 when the EV costs no more; null when it never does
  npv: number;              // today's value of choosing the EV: the savings of each year, discounted, less the extra
};

/** Cost to drive 100 miles on gasoline: 100 / mpg gallons at the gasoline price. */
export const gasPer100 = (mpg: number, usdPerGal: number) => (100 / mpg) * usdPerGal;
/** Cost to drive 100 miles on electricity: 100 x kWh per mile at the power price (USD/MWh / 1,000 = USD/kWh). */
export const evPer100 = (kwhPerMile: number, usdPerMwh: number) => 100 * kwhPerMile * (usdPerMwh / 1000);

/** Session 3276: the price a kWh of charging costs on average, USD/MWh: the home price for the home share, the public
 *  charger's for the rest. Null when some charging is away from home and no public price was given (nothing is guessed). */
export function chargePrice(x: Pick<Inputs, "powerUsdPerMwh" | "homeShare" | "publicUsdPerMwh">): number | null {
  const h = x.homeShare ?? 100;
  if (h >= 100) return x.powerUsdPerMwh;
  if (x.publicUsdPerMwh === null || x.publicUsdPerMwh === undefined || !Number.isFinite(x.publicUsdPerMwh)) return null;
  return (h / 100) * x.powerUsdPerMwh + (1 - h / 100) * x.publicUsdPerMwh;
}

export function verdict(x: Inputs): Verdict {
  const price = chargePrice(x);
  if (price === null) throw new Error("some charging is away from home and no public charger price was given");
  const g = gasPer100(x.mpg, x.gasUsdPerGal), e = evPer100(x.kwhPerMile, price);
  const gasYear = (g * x.miles) / 100, evYear = (e * x.miles) / 100, saveYear = gasYear - evYear;
  const extra = x.evCar - x.gasCar - x.credit;
  const payback = extra <= 0 ? 0 : saveYear > 0 ? extra / saveYear : null;
  let pv = 0;
  for (let t = 1; t <= x.years; t++) pv += saveYear / (1 + x.rate / 100) ** t;
  return { gasPer100: g, evPer100: e, gasYear, evYear, saveYear, extra, payback, npv: pv - extra };
}

export type YearRow = { year: number; gas: number; ev: number };
/** Session 3276: what each car has cost by the end of each year, 0 to the years kept: its price (the EV's less any
 *  credit) plus that many years of fuel, not discounted, so the lines cross at the payback year. `cross` is that year
 *  when it falls inside the years kept and the EV costs more to buy; null otherwise. */
export function cumulative(x: Inputs): { rows: YearRow[]; cross: number | null } {
  const r = verdict(x);
  const rows = Array.from({ length: x.years + 1 }, (_, t) => ({ year: t, gas: x.gasCar + r.gasYear * t, ev: x.evCar - x.credit + r.evYear * t }));
  return { rows, cross: r.payback !== null && r.payback > 0 && r.payback <= x.years ? r.payback : null };
}

/** Session 3276: the figures the page keys for check-values (ev|<state>|<figure>), at the defaults and the state's held
 *  prices, rounded as the page writes them. scripts/check-values.mjs recomputes them with this function from
 *  data/ev_prices.json; the page renders the same values. */
export function keyed(powerUsdPerMwh: number, gasUsdPerGal: number): { power_cents: number; gas: number; payback: number | null; npv: number } {
  const D = Object.fromEntries(Object.entries(DEFAULTS).map(([k, d]) => [k, d.value])) as Record<keyof Defaults, number>;
  const r = verdict({ ...D, gasUsdPerGal, powerUsdPerMwh, credit: 0 });
  return { power_cents: Math.round(powerUsdPerMwh * 10) / 100, gas: gasUsdPerGal, payback: r.payback === null ? null : Math.round(r.payback * 10) / 10, npv: Math.round(r.npv) };
}
