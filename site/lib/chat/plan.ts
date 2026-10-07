// Energy Research Warehouse (ERW) site, session 148: a plan made by rule, for the commonest shapes of question.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-speed.mjs). Session 143 left a
// number question at two model calls: a reading turn of about 2.7 seconds in which the model decides what to read, and
// a writing turn. For three shapes of question the read is the same every time, and code can write it:
//
//   hub price    a price at one named ERCOT hub, in a named market (day-ahead, real-time or both), over a named
//                period: one figure (the average, the highest or the lowest) or a series by day, month or year.
//                Read from ercot_hub_prices_daily.
//   generation   the electricity ERCOT generated from one named source (solar, wind, coal, natural gas, nuclear,
//                hydro): a month's or a year's total, a source's share of a month, or a series by month or year.
//                Read from generation_mix_hourly_profile.
//   reserve      the day-ahead price of one named reserve product (ECRS, regulation up or down, responsive reserve,
//                non-spin) over a named period: one figure or a series by day, month or year. Read from the two
//                tables of session 148, ercot_as_prices_monthly and ercot_as_prices_daily, and only when the site
//                holds them.
//
// HOW A NEAR-MISS IS KEPT OUT. The rule does not look for a shape inside a question: it must account for every word.
// The question is cut into the phrases the rule knows (a period, a grain, a market, a statistic, a hub or a product or
// a source) and what is left must be words from a short closed list for that shape ("what", "was", "the", "price",
// "show"). One word outside the list (a clock hour, "now", "last week", "capacity", "forecast", another grid's name,
// a second hub) and the rule returns null: the question goes to the model exactly as before. So does a question whose
// hub, market or period is not named outright (the rule never fills a default), one that names two periods, a period
// in the future, more groups than a result shows, and every question that continues a conversation (lib/chat/ercot.ts
// asks the rule only for a first question). The rule writes the read only: the model still writes the answer, and the
// answer passes every check it always passed. If the writing turn cannot answer from what the rule read, the model is
// given the question with its tools, as before, and told what was already read.
//
// Behind the server switch ASK_RULE_PLAN=on (lib/chat/ask.ts). Unset, no question is planned by rule.

export type PlannedCall = { name: "query"; input: Record<string, unknown> };
export type RulePlan = { shape: "hub price" | "generation" | "reserve"; calls: PlannedCall[] };

const MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"];
const MONTH = `(${MONTHS.join("|")})`;
const HUBS: [RegExp, string][] = [
  [/\bhub average\b/, "ercot:HB_HUBAVG"], [/\bbus average\b/, "ercot:HB_BUSAVG"], [/\bnorth hub\b/, "ercot:HB_NORTH"], [/\bsouth hub\b/, "ercot:HB_SOUTH"],
  [/\bwest hub\b/, "ercot:HB_WEST"], [/\bhouston hub\b/, "ercot:HB_HOUSTON"],
];
const PRODUCTS: [RegExp, string][] = [
  [/\b(ecrs|contingency reserve service|contingency reserve)\b/, "ercot:ECRS"], [/\b(regulation up|reg up|regup)\b/, "ercot:REGUP"], [/\b(regulation down|reg down|regdn)\b/, "ercot:REGDN"],
  [/\b(responsive reserve service|responsive reserve|rrs)\b/, "ercot:RRS"], [/\b(non-spinning reserve|non-spin reserve|non-spin|nspin)\b/, "ercot:NSPIN"],
];
const FUELS: [RegExp, string][] = [
  [/\bnatural gas\b/, "natural_gas"], [/\bsolar\b/, "solar"], [/\bwind\b/, "wind"], [/\bcoal\b/, "coal"], [/\bnuclear\b/, "nuclear"], [/\bhydro\b/, "hydro"],
];
// what may be left of a question once its phrases are taken out: the words that carry no meaning the read depends on
const COMMON = ["what", "was", "were", "is", "the", "ercot", "texas", "show", "chart", "how", "has", "have", "did", "does", "a", "of", "in", "at", "on", "over", "for", "me", "and"];
const FILLER: Record<RulePlan["shape"], Set<string>> = {
  "hub price": new Set([...COMMON, "price", "prices", "moved", "move", "changed", "change", "compare"]),
  generation: new Set([...COMMON, "generation", "generate", "generated", "electricity", "much", "from", "grown", "grow", "changed", "change", "came", "come"]),
  reserve: new Set([...COMMON, "price", "prices", "reserve", "reserves", "moved", "move", "changed", "change"]),
};
const NEEDS: Record<RulePlan["shape"], RegExp> = { "hub price": /\bprices?\b/, generation: /\b(generation|generate|generated|electricity)\b/, reserve: /\bprices?\b/ };
/** The first day each table holds, for the count of groups a series without a start would have. */
const FIRST: Record<RulePlan["shape"], string> = { "hub price": "2015-01-01", generation: "2019-01-01", reserve: "2018-01-01" };
export const MAX_PLAN_GROUPS = 120;   // the rows one grouped result shows (lib/chat/spec_ercot.json, max_groups)

type Period = { kind: "day" | "month" | "year" | "span" | "open"; start?: string; end?: string };
const pad = (n: number) => String(n).padStart(2, "0");
const iso = (y: number, m: number, d: number) => `${y}-${pad(m)}-${pad(d)}`;
/** A calendar date as its ISO day, or null when it is not one (31 June, a month 13). */
function day(y: number, m: number, d: number): string | null {
  const t = new Date(Date.UTC(y, m - 1, d));
  return t.getUTCFullYear() === y && t.getUTCMonth() === m - 1 && t.getUTCDate() === d ? iso(y, m, d) : null;
}
const addDays = (d: string, n: number) => new Date(Date.parse(`${d}T00:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10);
const nextMonth = (y: number, m: number) => (m === 12 ? iso(y + 1, 1, 1) : iso(y, m + 1, 1));
const daysBetween = (a: string, b: string) => Math.round((Date.parse(`${b}T00:00:00Z`) - Date.parse(`${a}T00:00:00Z`)) / 86_400_000);
const monthsBetween = (a: string, b: string) => (Number(b.slice(0, 4)) - Number(a.slice(0, 4))) * 12 + Number(b.slice(5, 7)) - Number(a.slice(5, 7)) + (b.slice(8, 10) > "01" ? 1 : 0);

/** Take every match of `re` out of the text; the matches, and the text without them. */
function take(text: string, re: RegExp): { hits: RegExpMatchArray[]; rest: string } {
  const g = new RegExp(re.source, "g");
  const hits = Array.from(text.matchAll(g));
  return { hits, rest: hits.length ? text.replace(g, " ") : text };
}

/** The read for a question, when the question is one of the three shapes and every word of it is accounted for; null
 * otherwise. `today` is the UTC date the model is given; `rollup`: whether the site holds the two reserve tables. */
export function rulePlan(question: string, today: string, opts: { rollup?: boolean } = {}): RulePlan | null {
  if (typeof question !== "string" || question.length > 200 || !/^\d{4}-\d{2}-\d{2}$/.test(today)) return null;
  let s = ` ${question.toLowerCase().replace(/[‘’]/g, "'").replace(/\bercot's\b/g, "ercot").replace(/[?.!,]/g, " ").replace(/\s+/g, " ").trim()} `;
  if (/[^a-z0-9 '\-]/.test(s)) return null;                                  // a sign the rule does not read
  const thisYear = Number(today.slice(0, 4)), thisMonth = Number(today.slice(5, 7));

  // ---- the period: at most one, named outright
  const periods: Period[] = [];
  let bad = false;
  const grab = (re: RegExp, f: (m: RegExpMatchArray) => Period | null) => {
    const t = take(s, re);
    s = t.rest;
    for (const m of t.hits) { const p = f(m); if (p) periods.push(p); else bad = true; }
  };
  const oneDay = (d: string | null): Period | null => (d ? { kind: "day", start: d, end: addDays(d, 1) } : null);
  grab(new RegExp(`\\b(?:on )?(\\d{1,2}) ${MONTH} (\\d{4})\\b`), (m) => oneDay(day(Number(m[3]), MONTHS.indexOf(m[2]) + 1, Number(m[1]))));
  grab(new RegExp(`\\b(?:on )?${MONTH} (\\d{1,2}) (\\d{4})\\b`), (m) => oneDay(day(Number(m[3]), MONTHS.indexOf(m[1]) + 1, Number(m[2]))));
  grab(/\b(?:on )?(\d{4})-(\d{2})-(\d{2})\b/, (m) => oneDay(day(Number(m[1]), Number(m[2]), Number(m[3]))));
  grab(new RegExp(`\\b(?:in|for|during) ${MONTH} (\\d{4})\\b`), (m) => { const y = Number(m[2]), mo = MONTHS.indexOf(m[1]) + 1; return { kind: "month", start: iso(y, mo, 1), end: nextMonth(y, mo) }; });
  grab(/\b(?:in|for|during) (\d{4})\b/, (m) => ({ kind: "year", start: iso(Number(m[1]), 1, 1), end: iso(Number(m[1]) + 1, 1, 1) }));
  grab(/\bthrough (\d{4})\b/, (m) => ({ kind: "open", end: iso(Number(m[1]) + 1, 1, 1) }));
  grab(/\bsince (\d{4})\b/, (m) => ({ kind: "open", start: iso(Number(m[1]), 1, 1) }));
  grab(/\b(?:over|in|during|for) the (?:last|past) (\d{1,3}) days\b/, (m) => (Number(m[1]) >= 2 ? { kind: "span", start: addDays(today, -Number(m[1])), end: today } : null));
  grab(/\bthis year\b/, () => ({ kind: "span", start: iso(thisYear, 1, 1), end: today }));
  grab(/\blast month\b/, () => { const y = thisMonth === 1 ? thisYear - 1 : thisYear, mo = thisMonth === 1 ? 12 : thisMonth - 1; return { kind: "month", start: iso(y, mo, 1), end: nextMonth(y, mo) }; });
  grab(/\byesterday\b/, () => oneDay(addDays(today, -1)));
  if (bad || periods.length > 1) return null;
  const period: Period | null = periods[0] ?? null;
  if (period?.start && (period.start > today || period.start < "2010-01-01")) return null;      // a period that has not begun is a forecast: the model's to refuse
  if (period?.end && period.end < "2010-01-02") return null;

  // ---- the subject: one hub, or one reserve product, or one source of generation, and nothing of another shape
  // (taken out before the statistic: "Hub Average" is a hub's name, not a request for an average)
  const found = (list: [RegExp, string][]) => { const out: string[] = []; for (const [re, id] of list) { const t = take(s, re); s = t.rest; if (t.hits.length) out.push(id); } return out; };
  const products = found(PRODUCTS), hubs = found(HUBS), fuels = found(FUELS);
  if (products.length + hubs.length + fuels.length !== 1) return null;
  const shape: RulePlan["shape"] = hubs.length ? "hub price" : products.length ? "reserve" : "generation";

  // ---- the grain, the market, the statistic
  const grains: string[] = [];
  for (const [re, g] of [[/\b(day by day|by day)\b/, "day"], [/\b(month by month|by month|monthly)\b/, "month"], [/\b(year by year|by year)\b/, "year"]] as [RegExp, string][]) {
    const t = take(s, re); s = t.rest; if (t.hits.length) grains.push(g);
  }
  if (grains.length > 1) return null;
  const grain = grains[0] ?? null;
  const markets: string[] = [];
  for (const [re, m] of [[/\bday[- ]ahead\b/, "da"], [/\breal[- ]time\b/, "rt"]] as [RegExp, string][]) { const t = take(s, re); s = t.rest; if (t.hits.length) markets.push(m); }
  const stats: string[] = [];
  for (const [re, st] of [[/\b(average|mean)\b/, "mean"], [/\bhighest\b/, "highest"], [/\blowest\b/, "lowest"], [/\bshare\b/, "share"]] as [RegExp, string][]) { const t = take(s, re); s = t.rest; if (t.hits.length) stats.push(st); }
  if (stats.length > 1) return null;
  const stat = stats[0] ?? "mean";

  // ---- what is left: the shape's own noun must be there, and every other word must be one that changes nothing
  if (!NEEDS[shape].test(s)) return null;
  const left = s.split(" ").filter(Boolean);
  if (left.some((w) => !FILLER[shape].has(w))) return null;                   // a word the rule cannot account for: the model's question

  // ---- how many groups a series would have: more than a result shows is not planned by rule
  const bounded = !!(period?.start && period.end);
  const groups = (): number => {
    const a = period?.start ?? FIRST[shape], b = period?.end && period.end < addDays(today, 1) ? period.end : addDays(today, 1);
    return grain === "day" ? daysBetween(a, b) : grain === "month" ? monthsBetween(a, b) : Number(b.slice(0, 4)) - Number(a.slice(0, 4)) + 1;
  };
  if (grain && (groups() > MAX_PLAN_GROUPS || groups() < 3)) return null;      // fewer than three rows is no series (spec_ercot.json, min_rows)
  const when = { ...(period?.start ? { start: period.start } : {}), ...(period?.end ? { end: period.end } : {}) };
  const q = (input: Record<string, unknown>): PlannedCall => ({ name: "query", input });

  if (shape === "hub price") {
    if (!markets.length || stat === "share") return null;
    if (!grain && !bounded) return null;                                       // one figure needs its period
    if (grain === "day" && !bounded) return null;
    const table = "ercot_hub_prices_daily", entity = hubs[0];
    const [aggregation, tail] = stat === "highest" ? ["max", "max"] : stat === "lowest" ? ["min", "min"] : ["mean", "mean"];
    return { shape, calls: markets.map((m) => q({ table, aggregation, entity, variable: `${m}_${tail}`, ...when, ...(grain ? { group_by: grain } : {}) })) };
  }

  if (shape === "generation") {
    if (markets.length || stat === "highest" || stat === "lowest" || stats[0] === "mean") return null;
    const table = "generation_mix_hourly_profile", entity = "iso:ercot", fuel = fuels[0];
    if (grain === "day") return null;                                          // the table is monthly
    if (stat === "share") {
      if (grain || period?.kind !== "month") return null;                      // a share is a month's own row; a year's share is not held
      return { shape, calls: [q({ table, aggregation: "mean", entity, variable: `${fuel}_share_pct`, ...when }), q({ table, aggregation: "sum", entity, variable: "days_held", ...when }),
        q({ table, aggregation: "sum", entity, variable: "days_in_month", ...when })] };
    }
    if (grain) {
      if (period && period.kind !== "year" && period.kind !== "open" && period.kind !== "span") return null;
      return { shape, calls: [q({ table, aggregation: "sum", entity, variable: `${fuel}_mwh`, ...when, group_by: grain })] };
    }
    if (period?.kind !== "month" && period?.kind !== "year") return null;      // one total is a month's or a year's
    return { shape, calls: [q({ table, aggregation: "sum", entity, variable: `${fuel}_mwh`, ...when }), q({ table, aggregation: "sum", entity, variable: "days_held", ...when }),
      q({ table, aggregation: "sum", entity, variable: "days_in_month", ...when })] };
  }

  // reserve prices: only from the two tables of session 148, so only when the site holds them
  if (!opts.rollup || markets.includes("rt") || stat === "share") return null;
  const entity = products[0], daily = "ercot_as_prices_daily", monthly = "ercot_as_prices_monthly";
  const [aggregation, variable] = stat === "highest" ? ["max", "mcpc_dam_max"] : stat === "lowest" ? ["min", "mcpc_dam_min"] : ["mean", "mcpc_dam_mean"];
  if (grain) {
    if (grain !== "year" && !bounded) return null;
    return { shape, calls: [q({ table: grain === "month" ? monthly : daily, aggregation, entity, variable, ...when, group_by: grain })] };
  }
  if (!bounded) return null;
  if (period!.kind === "month" && stat === "mean")                             // a month's mean is its own row, with the hours it rests on
    return { shape, calls: [q({ table: monthly, aggregation, entity, variable, ...when }), q({ table: monthly, aggregation: "sum", entity, variable: "mcpc_dam_hours", ...when }),
      q({ table: monthly, aggregation: "sum", entity, variable: "mcpc_dam_hours_in_month", ...when })] };
  return { shape, calls: [q({ table: daily, aggregation, entity, variable, ...when })] };
}
