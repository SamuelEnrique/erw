// Session 294: "Should your family get an EV?" (/play/ev), the arithmetic and the defaults. No imports: Node runs this
// file as it is (site/scripts/test-ev.mjs). Every price is a table's (site/data/ev_prices.json, built from the warehouse
// by scripts/build-ev-prices.mjs) or the family's own; every default below says where it comes from. docs/methods/ev_game.md.

export type Defaults = Record<"miles" | "mpg" | "kwhPerMile" | "gasCar" | "evCar" | "years" | "rate" | "credit", { value: number; min: number; max: number; step: number; label: string; source: string }>;

// fueleconomy.gov, read on 15 October 2026 through its web service (www.fueleconomy.gov/ws/rest/vehicle/<id>):
// 2025 Chevrolet Equinox FWD (id 48061), regular gasoline, 27 mpg combined; 2025 Chevrolet Equinox EV FWD (id 48697),
// 31.24 kWh per 100 miles combined. The same small SUV, gasoline and electric, so the comparison is like for like.
export const DEFAULTS: Defaults = {
  miles: { value: 15000, min: 3000, max: 30000, step: 500, label: "Miles a year", source: "15,000 miles a year: the yearly distance fueleconomy.gov's fuel cost estimates assume (its 2025 Fuel Economy Guide)" },
  mpg: { value: 27, min: 12, max: 60, step: 1, label: "The gasoline car's miles per gallon", source: "27 mpg: the 2025 Chevrolet Equinox FWD, combined city and highway (fueleconomy.gov, vehicle 48061)" },
  kwhPerMile: { value: 0.31, min: 0.2, max: 0.5, step: 0.01, label: "The EV's kWh per mile", source: "0.31 kWh a mile: the 2025 Chevrolet Equinox EV FWD, 31.24 kWh per 100 miles combined (fueleconomy.gov, vehicle 48697)" },
  gasCar: { value: 28600, min: 10000, max: 90000, step: 100, label: "The gasoline car's price, USD", source: "$28,600: the starting price Chevrolet lists for the 2025 Equinox LT, before destination (chevrolet.com, its previous-year page, as a search read it on 15 October 2026). To confirm: type the price a dealer quotes you" },
  evCar: { value: 33600, min: 10000, max: 90000, step: 100, label: "The EV's price, USD", source: "$33,600: the starting price of the 2025 Equinox EV LT1 before destination; GM's own announcement gave $34,995 with the $1,395 destination charge (as a search read it on 15 October 2026). To confirm: type the price a dealer quotes you" },
  years: { value: 8, min: 1, max: 15, step: 1, label: "Years you keep the car", source: "8 years: an assumption for you to change" },
  rate: { value: 5, min: 0, max: 10, step: 0.5, label: "Interest rate, percent a year", source: "5 percent: a simple rate for money in the future, an assumption for you to change" },
  credit: { value: 7500, min: 0, max: 7500, step: 100, label: "Federal tax credit, USD (your assumption)", source: "your family's own assumption: the IRS says no federal credit for new clean vehicles acquired after 30 September 2025 (irs.gov, Credits for new clean vehicles purchased in 2023 or after, reviewed 13 July 2026); $7,500 was its most" },
};

export const NO_CREDIT_LINE = "No federal credit for cars bought after 30 September 2025.";
export const IRS_URL = "https://www.irs.gov/credits-deductions/credits-for-new-clean-vehicles-purchased-in-2023-or-after";

export type Inputs = { miles: number; mpg: number; kwhPerMile: number; gasUsdPerGal: number; powerUsdPerMwh: number; gasCar: number; evCar: number; years: number; rate: number; credit: number };
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

export function verdict(x: Inputs): Verdict {
  const g = gasPer100(x.mpg, x.gasUsdPerGal), e = evPer100(x.kwhPerMile, x.powerUsdPerMwh);
  const gasYear = (g * x.miles) / 100, evYear = (e * x.miles) / 100, saveYear = gasYear - evYear;
  const extra = x.evCar - x.gasCar - x.credit;
  const payback = extra <= 0 ? 0 : saveYear > 0 ? extra / saveYear : null;
  let pv = 0;
  for (let t = 1; t <= x.years; t++) pv += saveYear / (1 + x.rate / 100) ** t;
  return { gasPer100: g, evPer100: e, gasYear, evYear, saveYear, extra, payback, npv: pv - extra };
}
