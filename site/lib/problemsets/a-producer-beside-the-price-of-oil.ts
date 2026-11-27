// Energy Research Warehouse (ERW) site, session 10412 (chain 720, part E): problem set "A producer beside the price of
// oil". What a listed oil and gas producer filed with the SEC (its revenue, income, capital spending and debt, period by
// period), set beside the spot price of the fuel it sells on the same days. Every figure is read from the committed
// equities page files (site/data/equities/series/<ticker>.json and energy_prices.json, written by the data machine's
// warehouse/derived/equity_page_files.py; contract docs/state/page_files_equities.md; method docs/methods/equities.md)
// with its pf| key (lib/pagefile.ts). The page that draws the files is /equities.
//
// The chain asked for "a segment beside an energy price". No segment has a line: a segment's line is built from share
// prices, and every share price is held ("license needed"). What the files do hold since 27 November 2026 is what each
// company filed, which is public. So the set is a company beside an energy price, and it uses no share price at all.
//
// A filed period is a row of the file's `quarterly` (columns in `quarterly_columns`); a question names a row by its
// period's end, its length in months and the column, and the row's position in the file is found by those, never
// typed. Where a period was filed twice the later filing's row is the one, the page's own rule (lib/equities.ts
// figureLine). A price is the row of the price's `daily` for the day named, found by the day.
//
// The set states what was filed and what a fuel cost. It gives no view of a company and no advice.
//
// A waiting set (lib/problems.ts, WAITING_SETS): it has its page, and is in no index and no dated edition until the
// owner approves it.
import type { Question } from "@/lib/problems";
import { calc, fig, monthWords, open, type Built, type Meta, type SetGuide } from "./common";

const PRICES = "equities/energy_prices.json";
type Cell = string | number | null;
type SeriesFile = { name: string | null; ticker: string | null; quarterly_columns: string[]; quarterly: Cell[][]; concepts?: Record<string, string | null> };
type PricesFile = { series: { id: string; label: string; unit: string }[]; daily: Record<string, [string, number | null][]> };

/** The producer the set asks about, and the second of its last question. Chosen by size, not by how an answer comes out: among
 *  the companies of the segment "Exploration and production" whose file holds every period the set reads, the one with
 *  the largest revenue filed for the three months to 30 September 2026; and, for the last question, the largest of them
 *  whose production is mostly natural gas by its own name of business (Expand Energy). The first is checked against
 *  the files by the set's test; the second is a choice, written in the set's decisions. */
export const TICKER = "EOG", SECOND = "EXE";
/** The segment of the list of companies (site/data/equities/index.json) the rule reads. */
export const SEGMENT = "exploration_production";
/** The period ends the set reads, and the days the prices are read on. */
export const Q3 = "2026-09-30", Q2 = "2026-06-30", Q3_BEFORE = "2025-09-30";
const fileOf = (ticker: string) => `equities/series/${ticker}.json`;

export const META: Meta = {
  slug: "a-producer-beside-the-price-of-oil", title: "A producer beside the price of oil: what a company filed, and what its fuel cost",
  line: "What a listed oil and gas producer reported to the SEC for a quarter (revenue, net income, capital spending, debt), read period by period from its own filings, and set beside the spot price of crude oil and of natural gas on the same days.",
  teacher: "About 45 minutes. Prerequisites: a percent of a value, a share of a total, a difference, a ratio; a quarter and a year to date. Students open /equities, choose the company, and find each figure in the company's file under site/data/equities/series, the file the page draws; each period links to its filing on the SEC's site. No share price is used: the ERW holds none it may show. The set says what was filed and what a fuel cost, and draws no conclusion about a company.",
  pages: [{ href: `/equities?a=${TICKER}`, label: "Energy equities" }, { href: "/data/methods/equities", label: "Method: energy equities" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read a company's filed figures period by period, tell a quarter from a year to date and a sum over a period from a figure at a day, and set a company's revenue beside the price of what it sells",
  grids: [],
  tables: [],
  skills: ["a percent of a value", "a share of a total", "a difference", "a ratio", "a quarter and a year to date", "a figure at a day and a sum over a period"],
  order: ["p1", "p2", "p3", "p4", "p5", "p6"],
  files: [fileOf(TICKER), fileOf(SECOND), PRICES],
};

/** The choices that move this set's figures, in the form of the sets' decisions (app/learn/problems/Decisions.tsx). */
export const DECISIONS = [
  { key: "producer-company", sets: [META.slug], text: `The set asks about one producer (${TICKER}) and, in its last question, a second (${SECOND}).`,
    def: `${TICKER}: of the companies of the segment "Exploration and production" whose file holds every period the set reads, the one with the largest revenue filed for the three months to ${Q3}. ${SECOND}: a producer of mostly natural gas, set beside the price of gas.`, source: "site/data/equities/index.json and the companies' files, read on 27 November 2026; the rule reads a company's size, not how any answer comes out.", session: "session 10412 (chain 720)" },
  { key: "producer-days", sets: [META.slug], text: "A price is read on the last day of the period a filing reports.",
    def: `The spot price on ${Q2}, ${Q3} and ${Q3_BEFORE}, each a day the price's series holds.`, source: "site/data/equities/energy_prices.json, the series' daily rows.", session: "session 10412 (chain 720)" },
  { key: "producer-filed-twice", sets: [META.slug], text: "Where a period was filed twice (an amended form), the later filing's figure is read.",
    def: "The row filed last among the rows of one period that hold the figure.", source: "The page's own rule: site/lib/equities.ts, figureLine.", session: "session 10408 (chain 720), read here in session 10412" },
];

export async function build(): Promise<Built> {
  const prices = open<PricesFile>(PRICES);
  const files = new Map<string, SeriesFile>();
  const file = (ticker: string) => { if (!files.has(ticker)) files.set(ticker, open<SeriesFile>(fileOf(ticker))); return files.get(ticker) as SeriesFile; };
  /** The position of the row of a period that holds a column, the later filing where there are two. */
  const rowOf = (ticker: string, end: string, months: number | null, column: string): { i: number; c: number } => {
    const d = file(ticker);
    const c = Object.fromEntries(d.quarterly_columns.map((n, i) => [n, i])) as Record<string, number>;
    let best = -1;
    d.quarterly.forEach((r, i) => {
      if (r[c.period_end] !== end || (months !== null && r[c.months] !== months) || typeof r[c[column]] !== "number") return;
      if (best < 0 || String(r[c.filed] ?? "") > String(d.quarterly[best][c.filed] ?? "")) best = i;
    });
    if (best < 0) throw new Error(`no row of ${fileOf(ticker)} for ${column}, ${months ?? "any"} months to ${end}`);
    return { i: best, c: c[column] };
  };
  const filed = (ticker: string, end: string, months: number | null, column: string, u = "USD") => { const at = rowOf(ticker, end, months, column); return fig(fileOf(ticker), ["quarterly", at.i, at.c], u); };
  const price = (id: string, day: string) => {
    const rows = prices.daily[id] ?? [];
    const i = rows.findIndex((r) => r[0] === day && typeof r[1] === "number");
    if (i < 0) throw new Error(`no price of ${id} on ${day} in ${PRICES}`);
    return fig(PRICES, ["daily", id, i, 1], prices.series.find((s) => s.id === id)?.unit);
  };
  const name = (ticker: string) => file(ticker).name ?? ticker;
  const A = name(TICKER), B = name(SECOND);
  const where = (end: string, months: number | null, column: string) => `the row whose period ends ${end}${months !== null ? ` and is ${months} months long` : ""}, column ${column}`;
  const inFile = (ticker: string) => `In site/data/${fileOf(ticker)}`;
  const label = (id: string) => prices.series.find((s) => s.id === id)?.label ?? id;
  /** A day in words, from the set's own constants: "30 September 2026" for "2026-09-30". No date is typed in an answer. */
  const dayWords = (d: string) => `${Number(d.slice(8, 10))} ${monthWords(d)}`;
  const D3 = dayWords(Q3), D2 = dayWords(Q2), DY = dayWords(Q3_BEFORE);

  // ---------------------------------------------------------------- worked example: one quarter's revenue beside the one before
  const r3 = filed(TICKER, Q3, 3, "revenue"), r2 = filed(TICKER, Q2, 3, "revenue"), xr = calc("pct", r3, r2, "%");
  const example: Question = {
    id: "px", tables: [],
    q: `${A} (${TICKER}) filed its revenue for the three months to ${Q3} and for the three months to ${Q2}. What are the two, and the later quarter's revenue is what percent of the earlier one's?`,
    answer: [`The three months to ${D3} `, r3, `, the three months to ${D2} `, r2, ": the later is ", xr, " of the earlier."],
    line: [r3, " / ", r2, " x 100 = ", xr],
    steps: [[`${inFile(TICKER)}: ${where(Q3, 3, "revenue")}, and ${where(Q2, 3, "revenue")}.`],
      [`The quarter to ${D3} `, r3, `; the quarter to ${D2} `, r2, "."], ["Divide and multiply by 100: ", r3, " / ", r2, " x 100 = ", xr, "."]],
    why: "A quarterly report (form 10-Q) gives the three months and, beside them, the year to date. The set reads a sum over a period from the row of exactly that length: a quarter is compared with a quarter. Above 100 percent the later quarter's revenue was the larger.",
  };

  // ---------------------------------------------------------------- p1: the price of oil on the same two days
  const w3 = price("wti", Q3), w2 = price("wti", Q2), xw = calc("pct", w3, w2, "%");
  const q1: Question = {
    id: "p1", tables: [],
    q: `${label("wti")}: what was the price on ${Q3} and on ${Q2}, and the later is what percent of the earlier? Set it beside the worked example's percent for ${A}'s revenue.`,
    answer: [`On ${D3} `, w3, `, on ${D2} `, w2, ": the later is ", xw, " of the earlier. The company's revenue: ", xr, "."],
    line: [w3, " / ", w2, " x 100 = ", xw, "; revenue ", xr],
    steps: [[`In site/data/${PRICES}, daily, the series wti: the rows of ${Q3} and ${Q2}.`], [`${D3} `, w3, `; ${D2} `, w2, "."], ["Divide and multiply by 100: ", w3, " / ", w2, " x 100 = ", xw, "."],
      ["From the worked example, the revenue's percent: ", xr, "."]],
    why: "A price on one day is not the price a company sold at over three months: a quarter's revenue follows the prices of every day of the quarter and the volume sold. The two percents are read side by side, and neither explains the other on its own.",
  };

  // ---------------------------------------------------------------- p2: net income as a share of revenue
  const n3 = filed(TICKER, Q3, 3, "net_income"), s2 = calc("pct", n3, r3, "%");
  const q2: Question = {
    id: "p2", tables: [],
    q: `For the three months to ${Q3}, what net income did ${A} file, and what share of the quarter's revenue is it?`,
    answer: ["Net income ", n3, " of revenue ", r3, ": ", s2, "."],
    line: [n3, " / ", r3, " x 100 = ", s2],
    steps: [[`${inFile(TICKER)}: ${where(Q3, 3, "net_income")}. The revenue is the worked example's.`], ["Net income ", n3, "; revenue ", r3, "."], ["Share: ", n3, " / ", r3, " x 100 = ", s2, "."]],
    why: "Net income is what is left of revenue after every cost, interest and tax of the period. As a share of revenue it can be read across companies of different sizes.",
  };

  // ---------------------------------------------------------------- p3: capital spending over the year to date
  const c9 = filed(TICKER, Q3, 9, "capex"), r9 = filed(TICKER, Q3, 9, "revenue"), s3 = calc("pct", c9, r9, "%");
  const q3: Question = {
    id: "p3", tables: [],
    q: `A quarterly report gives capital spending for the year to date, not for the quarter. For the nine months to ${Q3}, what capital spending and what revenue did ${A} file, and what share of the revenue is the spending?`,
    answer: ["Capital spending ", c9, " of revenue ", r9, " over the nine months: ", s3, "."],
    line: [c9, " / ", r9, " x 100 = ", s3],
    steps: [[`${inFile(TICKER)}: ${where(Q3, 9, "capex")}, and ${where(Q3, 9, "revenue")}: the same row, the nine months.`], ["Capital spending ", c9, "; revenue ", r9, "."], ["Share: ", c9, " / ", r9, " x 100 = ", s3, "."]],
    why: "The statement of cash flows in a 10-Q runs from the start of the year, so its lines are for six or nine months. A share is taken of a revenue of the same length: nine months of spending over nine months of revenue.",
  };

  // ---------------------------------------------------------------- p4: debt, a figure at a day
  const d3 = filed(TICKER, Q3, null, "debt"), d0 = filed(TICKER, Q3_BEFORE, null, "debt"), dd = calc("diff", d3, d0, "USD");
  // which way the debt moved is read from the two figures, never typed
  const moved = dd.v > 0 ? "above zero, the debt rose" : dd.v < 0 ? "below zero, the debt fell" : "the debt is the same";
  const q4: Question = {
    id: "p4", tables: [],
    q: `Debt is a figure at a day, not a sum over a period. What debt did ${A} report at ${Q3} and at ${Q3_BEFORE}, and what is the later less the earlier?`,
    answer: [`At ${D3} `, d3, `, at ${DY} `, d0, ": the later less the earlier is ", dd, ` (${moved}).`],
    line: [d3, " - ", d0, " = ", dd],
    steps: [[`A row whose period ends ${Q3} and holds debt, and one whose period ends ${Q3_BEFORE}: the column debt is the same in every row of one period end.`], [`${D3} `, d3, `; ${DY} `, d0, "."], ["Subtract: ", d3, " - ", d0, " = ", dd, "."]],
    why: `A balance sheet is a count at the period's last day, so its lines are read by the day, whatever the length of the period reported. The file's column debt is the concept ${file(TICKER).concepts?.debt ?? "the company reports as long-term debt"}.`,
  };

  // ---------------------------------------------------------------- p5: the same quarter a year before, beside the price
  const ry = filed(TICKER, Q3_BEFORE, 3, "revenue"), xy = calc("pct", r3, ry, "%"), wy = price("wti", Q3_BEFORE), xwy = calc("pct", w3, wy, "%");
  const q5: Question = {
    id: "p5", tables: [],
    q: `Take the same quarter a year apart. ${A}'s revenue for the three months to ${Q3} is what percent of its revenue for the three months to ${Q3_BEFORE}? And the price of ${label("wti")} on ${Q3} is what percent of its price on ${Q3_BEFORE}?`,
    answer: ["Revenue ", r3, " against ", ry, ": ", xy, ". The price ", w3, " against ", wy, ": ", xwy, "."],
    line: [r3, " / ", ry, " x 100 = ", xy, "; ", w3, " / ", wy, " x 100 = ", xwy],
    steps: [[`${inFile(TICKER)}: ${where(Q3_BEFORE, 3, "revenue")}. In site/data/${PRICES}, daily, the series wti: the rows of ${Q3_BEFORE} and ${Q3}.`], ["Revenue: ", r3, " / ", ry, " x 100 = ", xy, "."], ["The price: ", w3, " / ", wy, " x 100 = ", xwy, "."]],
    why: "The same quarter of two years leaves the season out of the comparison. A producer's revenue also moves with how much it produced, what else it sold and what it bought or sold of other companies, none of which a price shows.",
  };

  // ---------------------------------------------------------------- p6: a second producer, beside the price of gas
  const b3 = filed(SECOND, Q3, 3, "revenue"), b2 = filed(SECOND, Q2, 3, "revenue"), xb = calc("pct", b3, b2, "%");
  const g3 = price("henry_hub", Q3), g2 = price("henry_hub", Q2), xg = calc("pct", g3, g2, "%");
  const q6: Question = {
    id: "p6", tables: [],
    q: `Take the worked example for ${B} (${SECOND}), a producer of mostly natural gas: its revenue for the three months to ${Q3} as a percent of the three months to ${Q2}. Then ${label("henry_hub")} on the same two days. Set the four percents of the set side by side: the two companies' and the two fuels'.`,
    answer: [`${B}: `, b3, " / ", b2, ": ", xb, ". The price of gas: ", g3, " / ", g2, ": ", xg, `. ${A}: `, xr, "; the price of oil: ", xw, "."],
    line: [b3, " / ", b2, " x 100 = ", xb, "; ", g3, " / ", g2, " x 100 = ", xg],
    steps: [[`${inFile(SECOND)}: ${where(Q3, 3, "revenue")}, and ${where(Q2, 3, "revenue")}. In site/data/${PRICES}, daily, the series henry_hub: the rows of ${Q3} and ${Q2}.`],
      [`${B}: `, b3, " / ", b2, " x 100 = ", xb, "."], ["The price of gas: ", g3, " / ", g2, " x 100 = ", xg, "."], [`From the worked example and question 1: ${A} `, xr, ", the price of oil ", xw, "."]],
    why: "Two producers sell different fuels, and the two fuels' prices need not move together. Which price a company's revenue is read beside depends on what it sells, which its filings say and a ticker does not.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6] };
}
