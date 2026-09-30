// Session 44: problem sets v0 (education). Every answer is computed here, on the server, from warehouse tables (Supabase
// live set) and the bill rules, never typed: each number carries a check key that scripts/check-values.mjs recomputes.
// Derived answers use calc|<op>|<A>|<B>, where A and B are check keys with "~" for "|" (op: ratio, diff, pct).
import bills from "@/data/bill_rules.json";
import { billCA, billTX, defaultsCA, defaultsTX } from "@/lib/bill";
import { series, type SeriesRow } from "@/lib/data";

export type V = { v: number; k: string; u?: string };
export type Part = string | V;
export type Question = {
  id: string; q: string; tables: string[]; answer: Part[]; steps: Part[][]; why: string;
};
export type ProblemSet = { slug: string; title: string; line: string; teacher: string; pages: { href: string; label: string }[]; questions: Question[] };

const DAY = 86_400_000;
const iso = (t: number) => new Date(t).toISOString().replace(/\.\d{3}Z$/, "Z");
const tildes = (k: string) => k.replaceAll("|", "~");
const calc = (op: "ratio" | "diff" | "pct", a: V, b: V, u?: string): V => {
  const v = op === "ratio" ? a.v / b.v : op === "diff" ? a.v - b.v : (a.v / b.v) * 100;
  return { v, k: `calc|${op}|${tildes(a.k)}|${tildes(b.k)}`, u };
};
const row = (t: string, r: SeriesRow, u?: string, event?: string): V =>
  ({ v: r.value, k: `series|${t}|${r.entity}|${r.variable}|${r.ts_utc}${event ? `|${event}` : ""}`, u: u ?? r.unit });
const pick = (rows: SeriesRow[], how: "max" | "min") => rows.reduce((a, b) => (how === "max" ? (b.value > a.value ? b : a) : (b.value < a.value ? b : a)));
const day = (ts: string) => ts.slice(0, 10);

/** The UTC instant of a local midnight (America/Chicago is UTC-5 or UTC-6). */
function localMidnight(d: string, tz: string): number {
  const fmt = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" });
  for (const h of [4, 5, 6, 7, 8]) {
    const t = Date.parse(`${d}T${String(h).padStart(2, "0")}:00:00Z`);
    if (fmt.format(new Date(t)) === d && fmt.format(new Date(t - 60_000)) !== d) return t;
  }
  throw new Error(`no local midnight for ${d}`);
}

// ---------------------------------------------------------------- set A: know your grid (ERCOT and CAISO)
async function setA(): Promise<Question[]> {
  const D = "eia930_all_demand", G = "eia930_all_generation", S = "storage_daily_cycle", C = "carbon_intensity_daily";
  const E = "eia930:ERCO", CA = "eia930:CISO";
  const since = iso(Date.now() - 6 * DAY);
  const dem = await series(D, { variable: "demand_mw", entities: [E, CA], since });
  const hours = (e: string, d: string) => dem.filter((r) => r.entity === e && day(r.ts_utc) === d).length;
  const days = [...new Set(dem.map((r) => day(r.ts_utc)))].sort().reverse();
  const d0 = days.find((d) => hours(E, d) === 24 && hours(CA, d) === 24)!;
  const s0 = `${d0}T00:00:00Z`, s1 = iso(Date.parse(s0) + DAY);
  const peak = (e: string): V => ({ v: Math.max(...dem.filter((r) => r.entity === e && day(r.ts_utc) === d0).map((r) => r.value)), k: `series_max|${D}|demand_mw|${s0}|${s1}|${e}`, u: "MW" });
  const pE = peak(E), pC = peak(CA);
  const q1: Question = {
    id: "a1", tables: [D],
    q: "On the latest UTC day both grids report in full, what was the highest hour of demand in ERCOT and in CAISO, and how many times CAISO's was ERCOT's?",
    answer: [`${d0}: ERCOT `, pE, `, CAISO `, pC, `; ERCOT's peak was `, calc("ratio", pE, pC, "times"), ` CAISO's.`],
    steps: [[`Take the 24 hourly demand values of ${d0} (UTC) for each grid (entity eia930:ERCO and eia930:CISO, variable demand_mw).`],
      ["The highest ERCOT hour is ", pE, "; the highest CAISO hour is ", pC, "."], ["Divide: ", pE, " / ", pC, " = ", calc("ratio", pE, pC, "times"), "."]],
    why: "Peak demand, not average demand, sets how much generation and wire a grid has to build.",
  };
  const gen = await series(G, { entities: [E, CA], since: s0 });
  const sum = (e: string, v: string): V => ({ v: gen.filter((r) => r.entity === e && r.variable === v && r.ts_utc < s1).reduce((a, r) => a + r.value, 0), k: `series_sum|${G}|${v}|${s0}|${s1}|${e}`, u: "MWh" });
  const gE = sum(E, "net_generation_natural_gas_mw"), tE = sum(E, "net_generation_mw"), gC = sum(CA, "net_generation_natural_gas_mw"), tC = sum(CA, "net_generation_mw");
  const q2: Question = {
    id: "a2", tables: [G],
    q: `On the same day, what share of each grid's net generation came from natural gas?`,
    answer: ["ERCOT ", calc("pct", gE, tE, "%"), ", CAISO ", calc("pct", gC, tC, "%"), "."],
    steps: [[`Add the 24 hourly values of net_generation_natural_gas_mw and of net_generation_mw for ${d0} (UTC).`],
      ["ERCOT: ", gE, " from gas of ", tE, " in all: ", calc("pct", gE, tE, "%"), "."], ["CAISO: ", gC, " from gas of ", tC, " in all: ", calc("pct", gC, tC, "%"), "."]],
    why: "The fuel that runs most often sets both the price and the emissions of a grid's power.",
  };
  const st = await series(S, { entities: [E, "caiso:ISO"], variable: "mwh_discharged", since: iso(Date.now() - 10 * DAY) });
  const sd = [...new Set(st.map((r) => day(r.ts_utc)))].sort().reverse().find((d) => st.some((r) => r.entity === E && day(r.ts_utc) === d) && st.some((r) => r.entity === "caiso:ISO" && day(r.ts_utc) === d))!;
  const bE = row(S, st.find((r) => r.entity === E && day(r.ts_utc) === sd)!, "MWh"), bC = row(S, st.find((r) => r.entity === "caiso:ISO" && day(r.ts_utc) === sd)!, "MWh");
  const q3: Question = {
    id: "a3", tables: [S],
    q: "On the latest day both are held, how many MWh did batteries discharge in ERCOT and in CAISO, and how many times ERCOT's was CAISO's?",
    answer: [`${sd}: ERCOT `, bE, ", CAISO ", bC, "; CAISO's was ", calc("ratio", bC, bE, "times"), " ERCOT's."],
    steps: [[`Read mwh_discharged for ${sd} (each grid's local day): ERCOT (eia930:ERCO, EIA-930) `, bE, ", CAISO (caiso:ISO, CAISO's own data) ", bC, "."],
      ["Divide: ", bC, " / ", bE, " = ", calc("ratio", bC, bE, "times"), "."]],
    why: "Batteries move solar power from midday into the evening peak; how much they discharge shows how far that shift has gone.",
  };
  const ci = await series(C, { entities: [E, CA], variable: "intensity_generation", since: iso(Date.now() - 10 * DAY) });
  const cd = [...new Set(ci.map((r) => day(r.ts_utc)))].sort().reverse().find((d) => ci.some((r) => r.entity === E && day(r.ts_utc) === d) && ci.some((r) => r.entity === CA && day(r.ts_utc) === d))!;
  const iE = row(C, ci.find((r) => r.entity === E && day(r.ts_utc) === cd)!, "kg CO2/MWh"), iC = row(C, ci.find((r) => r.entity === CA && day(r.ts_utc) === cd)!, "kg CO2/MWh");
  const q4: Question = {
    id: "a4", tables: [C],
    q: "On the latest day both are held, what was the carbon intensity of generation in ERCOT and in CAISO, and how much higher was ERCOT's?",
    answer: [`${cd}: ERCOT `, iE, ", CAISO ", iC, "; ERCOT's is higher by ", calc("diff", iE, iC, "kg CO2/MWh"), "."],
    steps: [["Read intensity_generation for each grid: the day's CO2 from generation over its net generation."], ["Subtract: ", iE, " - ", iC, " = ", calc("diff", iE, iC, "kg CO2/MWh"), "."]],
    why: "The same kilowatt-hour carries very different emissions depending on where and when it is made.",
  };
  const m0 = localMidnight(sd, "America/Chicago"), m1 = localMidnight(day(iso(m0 + 30 * 3_600_000)), "America/Chicago");
  const dem5 = await series(D, { entity: E, variable: "demand_mw", since: iso(m0) });
  const dd: V = { v: dem5.filter((r) => Date.parse(r.ts_utc) < m1).reduce((a, r) => a + r.value, 0), k: `series_sum|${D}|demand_mw|${iso(m0)}|${iso(m1)}|${E}`, u: "MWh" };
  const q5: Question = {
    id: "a5", tables: [S, D],
    q: `What share of ERCOT's demand on ${sd} (Central time) did its batteries' discharge equal?`,
    answer: [calc("pct", bE, dd, "%"), " of the day's demand."],
    steps: [["ERCOT's batteries discharged ", bE, " on that local day."], [`Add ERCOT's hourly demand_mw from ${iso(m0)} to ${iso(m1)} (the Central-time day in UTC): `, dd, "."], ["Divide: ", bE, " / ", dd, " x 100 = ", calc("pct", bE, dd, "%"), "."]],
    why: "Battery output is growing fast, but it is still a small share of all the energy a grid uses.",
  };
  return [q1, q2, q3, q4, q5];
}

// ---------------------------------------------------------------- set B: prices and your bill
async function setB(): Promise<Question[]> {
  const M = "cost_of_power_monthly", P = "cost_of_power_hourly_profile";
  const all = await series(M, {});
  const by = (e: string, v: string) => all.filter((r) => r.entity === e && r.variable === v);
  const E = "ercot:HB_HUBAVG";
  const hours = new Map(by(E, "rt_hours").map((r) => [day(r.ts_utc), r.value]));
  const full = by(E, "hours_in_month").filter((r) => hours.get(day(r.ts_utc)) === r.value).map((r) => r.ts_utc).sort();
  const m = full.at(-1)!;
  const lw = row(M, by(E, "rt_load_weighted").find((r) => r.ts_utc === m)!, "USD/MWh"), sm = row(M, by(E, "rt_simple_mean").find((r) => r.ts_utc === m)!, "USD/MWh");
  const q1: Question = {
    id: "b1", tables: [M],
    q: "For ERCOT's hub average in its latest complete month, what were the load-weighted and the simple average real-time prices, and what is the shape premium?",
    answer: [`${m.slice(0, 7)}: load-weighted `, lw, ", simple ", sm, ", shape premium ", calc("diff", lw, sm, "USD/MWh"), "."],
    steps: [["Load-weighted: each hour's price times ERCOT's demand that hour, over the month's demand: ", lw, "."], ["Simple: the plain mean of the same hours: ", sm, "."], ["Shape premium = load-weighted - simple = ", calc("diff", lw, sm, "USD/MWh"), "."]],
    why: "A grid's load uses power most when it is dear, so its average cost per MWh is above the simple average price.",
  };
  const ents = [...new Set(all.map((r) => r.entity))];
  const months = (e: string) => new Set(by(e, "rt_shape_premium").map((r) => r.ts_utc));
  const common = [...months(ents[0])].filter((t) => ents.every((e) => months(e).has(t))).sort().at(-1)!;
  const prem = ents.map((e) => by(e, "rt_shape_premium").find((r) => r.ts_utc === common)!);
  const top = pick(prem, "max"), low = pick(prem, "min");
  const name = (e: string) => ({ ercot: "ERCOT", caiso: "CAISO", isone: "ISO-NE", miso: "MISO", nyiso: "NYISO", spp: "SPP" } as Record<string, string>)[e.split(":")[0]] ?? e;
  const q2: Question = {
    id: "b2", tables: [M],
    q: "In the latest month all six ISO hubs hold, which had the largest shape premium, and which the smallest?",
    answer: [`${common.slice(0, 7)}: largest ${name(top.entity)}, `, row(M, top, "USD/MWh"), `; smallest ${name(low.entity)}, `, row(M, low, "USD/MWh"), " (months may be partial: see rt_hours)."],
    steps: [["Read rt_shape_premium of each hub for that month:"], ...prem.map((r) => [`${name(r.entity)}: `, row(M, r, "USD/MWh")] as Part[]), ["Rank them."]],
    why: "Where the premium is large, shifting use out of peak hours saves the most.",
  };
  const w = async (s: "CA" | "TX") => {
    const ent = bills.bills[s].wholesale_entity;
    const hs = new Map(by(ent, "rt_hours").map((r) => [r.ts_utc, r.value]));
    const fm = by(ent, "hours_in_month").filter((r) => hs.get(r.ts_utc) === r.value).map((r) => r.ts_utc).sort();
    const mm = fm.at(-1) ?? by(ent, "rt_load_weighted").map((r) => r.ts_utc).sort().at(-1)!;
    const price = by(ent, "rt_load_weighted").find((r) => r.ts_utc === mm)!;
    const b = s === "CA" ? billCA(bills, defaultsCA(bills)) : billTX(bills, defaultsTX(bills));
    const tot: V = { v: b.total, k: `bill|${s}|total`, u: "USD" };
    const wh: V = { v: (b.kwh * price.value) / 1000, k: `bill|${s}|wholesale|${price.ts_utc}`, u: "USD" };
    const sh: V = { v: (wh.v / b.total) * 100, k: `bill|${s}|share|${price.ts_utc}`, u: "%" };
    return { price: row(M, price, "USD/MWh"), tot, wh, sh, kwh: b.kwh, month: mm.slice(0, 7), partial: !fm.length };
  };
  const [ca, tx] = [await w("CA"), await w("TX")];
  const billQ = (id: string, s: "CA" | "TX", x: Awaited<ReturnType<typeof w>>, who: string): Question => ({
    id, tables: [M],
    q: `On the default ${who} bill of /learn/bill (${x.kwh} kWh), how many dollars are wholesale energy, and what share of the bill is that?`,
    answer: [x.wh, " of ", x.tot, ": ", x.sh, "."],
    steps: [[`The bill: `, x.tot, ` (the tariff lines on /learn/bill).`], [`Wholesale: ${x.kwh} kWh x `, x.price, ` / 1,000 (${x.month}${x.partial ? ", a partial month" : ""}) = `, x.wh, "."], ["Share: ", x.wh, " / ", x.tot, " x 100 = ", x.sh, "."]],
    why: "Most of a home's bill pays for wires, programs and fixed charges, not the power itself; how much differs by state.",
  });
  const q3 = billQ("b3", "CA", ca, "PG&E (California)");
  const q4 = billQ("b4", "TX", tx, "Oncor (Texas)");
  const prof = await series(P, { entity: E });
  const pm = [...new Set(prof.map((r) => r.ts_utc))].sort().at(-1)!;
  const cells = prof.filter((r) => r.ts_utc === pm && r.variable.startsWith("rt_mean_h"));
  const lo = pick(cells, "min"), hi = pick(cells, "max");
  const q5: Question = {
    id: "b5", tables: [P],
    q: "In the latest month of ERCOT's hour-of-day profile, which hour was cheapest and which dearest on average, and how far apart were they?",
    answer: [`${pm.slice(0, 7)}: cheapest ${lo.variable.slice(-2)}:00, `, row(P, lo, "USD/MWh"), `; dearest ${hi.variable.slice(-2)}:00, `, row(P, hi, "USD/MWh"), "; spread ", calc("diff", row(P, hi, "USD/MWh"), row(P, lo, "USD/MWh"), "USD/MWh"), "."],
    steps: [["Read the 24 values rt_mean_h00 to rt_mean_h23 for that month (Central time)."], ["The lowest is ", row(P, lo, "USD/MWh"), `, at ${lo.variable.slice(-2)}:00; the highest `, row(P, hi, "USD/MWh"), `, at ${hi.variable.slice(-2)}:00.`], ["Spread = ", row(P, hi, "USD/MWh"), " - ", row(P, lo, "USD/MWh"), " = ", calc("diff", row(P, hi, "USD/MWh"), row(P, lo, "USD/MWh"), "USD/MWh"), "."]],
    why: "The daily price swing is what a battery, or a flexible load, earns by moving use.",
  };
  return [q1, q2, q3, q4, q5];
}

// ---------------------------------------------------------------- set C: when the grid broke
async function setC(): Promise<Question[]> {
  const T = "event_window_daily";
  const ev = async (event: string, entity: string, variable: string) => series(T, { event, entity, variable });
  const r = (x: SeriesRow, event: string, u: string) => row(T, x, u, event);
  const uri = await ev("uri_2021", "ercot:HB_HUBAVG", "rt_max");
  const u21 = pick(uri.filter((x) => x.ts_utc.startsWith("2021")), "max"), ubase = pick(uri.filter((x) => !x.ts_utc.startsWith("2021")), "max");
  const U = r(u21, "uri_2021", "USD/MWh"), UB = r(ubase, "uri_2021", "USD/MWh");
  const q1: Question = {
    id: "c1", tables: [T],
    q: "Winter Storm Uri (ERCOT, February 2021): how many times the highest 15-minute real-time price on the same days of 2019 and 2020 was the highest price during the storm window?",
    answer: [`${day(u21.ts_utc)}: `, U, ", against ", UB, ` (${day(ubase.ts_utc)}): `, calc("ratio", U, UB, "times"), "."],
    steps: [["Read rt_max (event uri_2021, ercot:HB_HUBAVG) for every day; the highest in 2021 is ", U, "."], ["The highest on the 2019 and 2020 days is ", UB, "."], ["Divide: ", calc("ratio", U, UB, "times"), "."]],
    why: "Scarcity pricing lets the price rise to the cap when supply fails, which is the market's signal and the customer's risk.",
  };
  const cai = await ev("caiso_heat_2020", "eia930:CISO", "demand_max_pct_vs_baseline");
  const chi = pick(cai, "max"), c14 = cai.find((x) => day(x.ts_utc) === "2020-08-14")!;
  const CH = r(chi, "caiso_heat_2020", "%"), C14 = r(c14, "caiso_heat_2020", "%");
  const q2: Question = {
    id: "c2", tables: [T],
    q: "CAISO, August 2020: on which day was the peak hour furthest above the same weekdays of earlier years, and by how many percentage points did it exceed 2020-08-14, the first day of rotating outages?",
    answer: [`${day(chi.ts_utc)}, `, CH, "; ", calc("diff", CH, C14, "percentage points"), " above 2020-08-14 (", C14, ")."],
    steps: [["Read demand_max_pct_vs_baseline (event caiso_heat_2020) for each day and find the highest: ", CH, "."], ["2020-08-14: ", C14, "."], ["Subtract: ", calc("diff", CH, C14, "percentage points"), "."]],
    why: "The outages came before demand peaked: supply fell short, not demand alone.",
  };
  const pj = await ev("elliott_2022", "eia930:PJM", "demand_max_mw");
  const ptop = pick(pj.filter((x) => x.ts_utc >= "2022-12-19"), "max");
  const ppct = (await ev("elliott_2022", "eia930:PJM", "demand_max_pct_vs_baseline")).find((x) => x.ts_utc === ptop.ts_utc)!;
  const q3: Question = {
    id: "c3", tables: [T],
    q: "Winter Storm Elliott (December 2022): what was PJM's highest hour of demand served in the window, on which day, and how far above the same weekdays of 2021 and 2020 was that day's peak?",
    answer: [`${day(ptop.ts_utc)}: `, r(ptop, "elliott_2022", "MW"), ", ", r(ppct, "elliott_2022", "%"), " above the baseline."],
    steps: [["Read demand_max_mw (event elliott_2022, eia930:PJM) from 2022-12-19 on and find the highest: ", r(ptop, "elliott_2022", "MW"), "."], ["Read demand_max_pct_vs_baseline for that day: ", r(ppct, "elliott_2022", "%"), "."]],
    why: "Winter peaks can rival summer ones when a cold snap meets electric heating and failing plants.",
  };
  const e23 = await ev("ercot_heat_2023", "ercot:HB_HUBAVG", "rt_max");
  const etop = pick(e23.filter((x) => x.ts_utc >= "2023-08-01"), "max");
  const edem = pick((await ev("ercot_heat_2023", "eia930:ERCO", "demand_max_mw")).filter((x) => x.ts_utc >= "2023-08-01"), "max");
  const q4: Question = {
    id: "c4", tables: [T],
    q: "ERCOT, summer 2023: on which day was the highest 15-minute real-time price, and on which day the highest hour of demand? Were they the same day?",
    answer: [`Highest price ${day(etop.ts_utc)}, `, r(etop, "ercot_heat_2023", "USD/MWh"), `; highest demand ${day(edem.ts_utc)}, `, r(edem, "ercot_heat_2023", "MW"), day(etop.ts_utc) === day(edem.ts_utc) ? ": the same day." : ": different days."],
    steps: [["Read rt_max (event ercot_heat_2023) and find the highest: ", r(etop, "ercot_heat_2023", "USD/MWh"), "."], ["Read demand_max_mw and find the highest: ", r(edem, "ercot_heat_2023", "MW"), "."], ["Compare the dates."]],
    why: "Prices spike when supply is short, which is not always when demand is highest: wind and the solar ramp at sunset matter too.",
  };
  const U2: V = r(etop, "ercot_heat_2023", "USD/MWh");
  const q5: Question = {
    id: "c5", tables: [T],
    q: "Compare two ERCOT events: how many times the summer 2023 heat's highest 15-minute real-time price was Winter Storm Uri's?",
    answer: [U, " (Uri) / ", U2, " (2023) = ", calc("ratio", U, U2, "times"), "."],
    steps: [["Uri's highest rt_max: ", U, "."], ["The 2023 heat's highest rt_max: ", U2, "."], ["Divide: ", calc("ratio", U, U2, "times"), "."]],
    why: "Both hit the price cap's neighborhood, but Uri held prices there for days and cut power to millions.",
  };
  return [q1, q2, q3, q4, q5];
}

export const SETS: Omit<ProblemSet, "questions">[] = [
  { slug: "know-your-grid", title: "Know your grid: ERCOT and CAISO side by side", line: "Peak demand, generation mix, the battery cycle and carbon intensity, from the latest data.",
    teacher: "About 45 minutes. Prerequisites: MW against MWh, reading a daily and an hourly table. Students should open /grid/ercot, /grid/caiso, /mix, /storage and /emissions, and the tables linked under each question on /data.",
    pages: [{ href: "/grid/ercot", label: "ERCOT" }, { href: "/grid/caiso", label: "CAISO" }, { href: "/storage", label: "Storage" }, { href: "/emissions", label: "Emissions" }] },
  { slug: "prices-and-your-bill", title: "Prices and your bill", line: "Load-weighted against simple prices, the shape premium, the wholesale share of two real bills, and the cheapest and dearest hour.",
    teacher: "About 40 minutes. Prerequisites: a weighted average, USD per MWh against cents per kWh (divide by 10). Students should open /cost-of-power, /learn/bill and the method page for the cost of power.",
    pages: [{ href: "/cost-of-power", label: "Cost of power" }, { href: "/learn/bill", label: "What is on a bill" }, { href: "/data/methods/cost_of_power", label: "Method" }] },
  { slug: "when-the-grid-broke", title: "When the grid broke: four events", line: "Winter Storm Uri, CAISO's August 2020 heat, Winter Storm Elliott and ERCOT's 2023 heat, one question each and one comparing two.",
    teacher: "About 50 minutes. Prerequisites: percent change, a baseline (the same weekdays of earlier years). Students should open /events and the four event pages, and read each page's note on what contradicted the headline story.",
    pages: [{ href: "/events", label: "Events" }, { href: "/events/uri-2021", label: "Uri" }, { href: "/events/caiso-heat-2020", label: "CAISO 2020" }, { href: "/events/elliott-2022", label: "Elliott" }, { href: "/events/ercot-heat-2023", label: "ERCOT 2023" }] },
];

export async function problemSet(slug: string): Promise<ProblemSet | null> {
  const meta = SETS.find((s) => s.slug === slug);
  if (!meta) return null;
  const questions = slug === "know-your-grid" ? await setA() : slug === "prices-and-your-bill" ? await setB() : await setC();
  return { ...meta, questions };
}
