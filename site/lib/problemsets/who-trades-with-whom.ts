// Energy Research Warehouse (ERW) site, session 8901 (chain 507, part C): problem set "Who trades with whom". Every figure
// is read from a committed page file of the whole country and carries its pf| key (lib/pagefile.ts):
//   site/data/regions/trade/ten.json      Tennessee's net imports by neighbour and month, its own report and each
//                                          neighbour's report of the same flow, the gap and the hours behind each
//   site/data/regions/trade_matrix.json   each pair of regions by year, each side's report, their mean and the gap
// Both are drawn by "The whole country" on /supply (components/supply/Country.tsx). The month and the years are chosen
// by rules written beside them, from the files, never typed; a file rebuilt later gives the same questions on its newest
// month and years.
import type { Part, Question, V } from "@/lib/problems";
import { REGION_NAME } from "@/lib/countryfiles";
import { calc, fig, monthWords, open, type Built, type Meta, type SetGuide } from "./common";

const T = "regions/trade/ten.json", M = "regions/trade_matrix.json";
const PAIR_TABLE = "eia930_region_pair_hourly", YEAR_TABLE = "interchange_pair_monthly";
type Trade = { built: string; months: string[]; hours_in_month: number[]; net_imports_mwh: (number | null)[]; neighbors: Record<string, Record<string, (number | null)[]>> };
type Pair = { a: string; b: string; year: number; a_report_mwh: number | null; b_report_mwh: number | null; gap_mwh: number | null; hours_a: number; hours_b: number; months_held: number; months_in_year: number };
type Matrix = { region_pairs: Pair[] };

export const META: Meta = {
  slug: "who-trades-with-whom", title: "Who trades with whom: power between regions",
  line: "Tennessee's net imports from each neighbour in a month, two sides' reports of one flow and the gap between them, a pair of regions that disagreed about which way the power ran, and a border where only one side reports.",
  teacher: "About 45 minutes. Prerequisites: MWh, the sign of a flow (above zero an import), a ratio. Students should open /supply and its section The whole country (pick Tennessee), read the tables Net imports by month and by neighbour and Who trades with whom, and the method page of the regions. The page writes GWh: divide a file's MWh by 1,000.",
  pages: [{ href: "/supply#wc-trade", label: "The whole country on /supply" }, { href: "/data/methods/regions_pages", label: "Method: the regions' files" }, { href: "/data/methods/interchange_pairs", label: "Method: pairs of regions" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read a region's net imports by neighbour, compare two sides' reports of one flow, and say which report a quoted number is",
  grids: ["EIA's thirteen regions of the lower 48", "Canada", "Mexico"],
  tables: [PAIR_TABLE, YEAR_TABLE],
  skills: ["the sign of a flow", "two reports of one flow", "a gap over the hours both reported", "a ratio of two years", "hours held"],
  order: ["t1", "t6", "t2", "t7", "t5", "t3", "t4"],
  files: [T, M],
};

const name = (c: string) => REGION_NAME[c] ?? c;
/** Words for a net import as the file signs it: above zero the region imported, below zero it sent power out. */
const way = (x: V, region: string, other: string) => (x.v > 0 ? `${region} imported from ${other}` : x.v < 0 ? `${region} sent power to ${other}` : `no net flow between ${region} and ${other}`);

export async function build(): Promise<Built> {
  const t = open<Trade>(T);
  const mx = open<Matrix>(M);
  // the month: the newest month of the file that had ended when the file was built (its own `built` stamp)
  const i = t.months.map((m, j) => ({ m, j })).filter((x) => x.m < t.built.slice(0, 7)).at(-1)!.j;
  const mo = monthWords(t.months[i]);
  const nb = Object.keys(t.neighbors).sort();
  const own = (c: string, j = i) => fig(T, ["neighbors", c, "net_imports_mwh", j], "MWh");
  const their = (c: string, j = i) => fig(T, ["neighbors", c, "their_report_mwh", j], "MWh");
  const gap = (c: string, j = i) => fig(T, ["neighbors", c, "gap_mwh", j], "MWh");
  const hrs = (c: string, f: string, j = i) => fig(T, ["neighbors", c, f, j], "hours");

  // ---------------------------------------------------------------- worked example: the Southeast's two reports
  const xo = own("SE"), xt = their("SE"), xr = calc("ratio", xo, xt, "times");
  const example: Question = {
    id: "tx", tables: [PAIR_TABLE],
    q: `In ${mo}, how much power did Tennessee report receiving from the Southeast, how much did the Southeast report for the same flow, and how many times the Southeast's report was Tennessee's?`,
    answer: [`${mo}: Tennessee's report `, xo, ", the Southeast's ", xt, ": Tennessee's is ", xr, " the Southeast's. ",
      Math.sign(xo.v) === Math.sign(xt.v) ? `Both have the same sign, so both say ${way(xo, "Tennessee", "the Southeast")}.` : "The two have opposite signs: the sides disagree on the direction."],
    line: [xo, " / ", xt, " = ", xr],
    steps: [[`On /supply, The whole country, pick Tennessee and the year ${t.months[i].slice(0, 4)}; or open site/data/regions/trade/ten.json and take position ${i} of its months (${t.months[i]}).`],
      ["Under neighbors, SE: net_imports_mwh is Tennessee's own report, ", xo, "; their_report_mwh is the Southeast's report of the same flow, turned to Tennessee's side, ", xt, "."],
      ["Divide: ", xo, " / ", xt, " = ", xr, ". A ratio near one says the two sides agree."]],
    why: "Every flow between two regions is reported twice, once by each side, and the first thing to check before quoting one is whether the other agrees.",
  };

  // ---------------------------------------------------------------- t1: the month's total and each neighbour
  const tot = fig(T, ["net_imports_mwh", i], "MWh");
  const each = nb.map((c) => ({ c, v: own(c) }));
  const big = each.reduce((a, b) => (b.v.v > a.v.v ? b : a));
  const sum = each.reduce((a, x) => a + x.v.v, 0);
  const adds = Math.abs(sum - tot.v) < 0.5;
  const sent = each.filter((x) => x.v.v < 0).map((x) => name(x.c));
  const sentWords = sent.length ? `to ${sent.join(", ")} it sent power (below zero).` : "it imported from every one.";
  const bigAbs = each.reduce((a, b) => (Math.abs(b.v.v) > Math.abs(a.v.v) ? b : a)).c;
  const q1: Question = {
    id: "t1", tables: [PAIR_TABLE],
    q: `In ${mo}, what were Tennessee's net imports from all its neighbours together, by its own report, and from each of its ${nb.length} neighbours? From which did it import the most?`,
    answer: [`${mo}: in all `, tot, ". ", ...each.flatMap((x, j): Part[] => [`${j ? "; " : ""}${name(x.c)} `, x.v]), `. The most from ${name(big.c)}; ${sentWords}`],
    line: [...each.flatMap((x, j): Part[] => [j ? " + " : "", x.v]), adds ? " = " : "; the file's total: ", tot],
    steps: [[`Open the table Net imports by month and by neighbour for Tennessee, or site/data/regions/trade/ten.json at position ${i} (${t.months[i]}).`],
      ["Each neighbour's net_imports_mwh, Tennessee's own report: ", ...each.flatMap((x, j): Part[] => [`${j ? "; " : ""}${name(x.c)} `, x.v]), "."],
      ["The file's own total, net_imports_mwh: ", tot, adds ? ", the sum of the four." : ", which the file writes for itself; a month a neighbour holds fewer than half its hours is left out of it."],
      ["Above zero Tennessee imported; below zero it sent power out. The largest import: ", name(big.c), ", ", big.v, "."]],
    why: "A region's net imports are the sum of flows that run both ways at once: it can take power from one neighbour while it sends power to another.",
  };

  // ---------------------------------------------------------------- t2: the Midwest's two reports
  const wo = own("MIDW"), wt = their("MIDW"), wg = gap("MIDW"), wr = calc("ratio", wo, wt, "times");
  const q2: Question = {
    id: "t2", tables: [PAIR_TABLE],
    q: `In ${mo}, ${bigAbs === "MIDW" ? "Tennessee's largest flow, in size, was with the Midwest" : "take Tennessee's flow with the Midwest"}. What did Tennessee report, what did the Midwest report for the same flow, and how many times the Midwest's report was Tennessee's?`,
    answer: ["Tennessee ", wo, ", the Midwest ", wt, ": Tennessee's report is ", wr, " the Midwest's; the file's gap is ", wg, "."],
    line: [wo, " / ", wt, " = ", wr],
    steps: [["Under neighbors, MIDW: net_imports_mwh (Tennessee's report) ", wo, "; their_report_mwh (the Midwest's, turned to Tennessee's side) ", wt, "."],
      ["Divide: ", wo, " / ", wt, " = ", wr, "."], ["The file's gap_mwh, Tennessee's report less the Midwest's over the hours both reported: ", wg, "."]],
    why: "The two sides measure the same wires at different meters and with different rules, so a flow has two figures; which one a number is should be said when it is quoted.",
  };

  // ---------------------------------------------------------------- t3: the Mid-Atlantic, the difference against the gap
  const ao = own("MIDA"), at = their("MIDA"), ag = gap("MIDA"), ad = calc("diff", ao, at, "MWh");
  const ho = hrs("MIDA", "hours_own"), ht = hrs("MIDA", "hours_their"), hb = hrs("MIDA", "hours_both");
  const same = Math.abs(ad.v - ag.v) < 0.5;
  const q3: Question = {
    id: "t3", tables: [PAIR_TABLE],
    q: `In ${mo}, what did Tennessee and the Mid-Atlantic each report for the flow between them? Subtract the Mid-Atlantic's report from Tennessee's, and compare the result with the gap the file gives. Why can the two differ?`,
    answer: ["Tennessee ", ao, ", the Mid-Atlantic ", at, "; Tennessee's less the Mid-Atlantic's is ", ad, ", the file's gap ", ag, same ? ": the same, as both sides reported every hour." : `: not the same, because each report runs over its own side's hours and the gap over the hours both reported.`],
    line: [ao, " - ", at, " = ", ad, "; the file's gap_mwh = ", ag],
    steps: [["Under neighbors, MIDA: net_imports_mwh ", ao, " and their_report_mwh ", at, "."], ["Subtract: ", ao, " - ", at, " = ", ad, "."],
      ["The file's gap_mwh: ", ag, ". Tennessee reported ", ho, ", the Mid-Atlantic ", ht, ", both ", hb, ": the gap is taken over the hours both reported only."]],
    why: "A figure summed over different hours is not the same quantity: before two reports are subtracted, the hours behind each must match.",
  };

  // ---------------------------------------------------------------- t4: a year the two sides disagreed on the direction
  const whole = (p: Pair) => p.months_held === 12 && p.months_in_year === 12;
  const pairRows = (a: string, b: string) => mx.region_pairs.filter((p) => p.a === a && p.b === b && whole(p) && p.a_report_mwh !== null && p.b_report_mwh !== null && p.gap_mwh !== null);
  // the year of the Mid-Atlantic and Tennessee whose gap is largest in size, among the years both sides reported in full
  const midaTen = pairRows("MIDA", "TEN");
  const py = midaTen.reduce((a, b) => (Math.abs(b.gap_mwh!) > Math.abs(a.gap_mwh!) ? b : a)).year;
  const sel = (a: string, b: string, year: number) => ({ a, b, year });
  const pa = fig(M, ["region_pairs", sel("MIDA", "TEN", py), "a_report_mwh"], "MWh"), pb = fig(M, ["region_pairs", sel("MIDA", "TEN", py), "b_report_mwh"], "MWh");
  const pg = fig(M, ["region_pairs", sel("MIDA", "TEN", py), "gap_mwh"], "MWh"), pd = calc("diff", pa, pb, "MWh");
  const opposite = Math.sign(pa.v) !== Math.sign(pb.v);
  const dir = (x: V, who: string) => (x.v > 0 ? `${who} says the power ran from the Mid-Atlantic to Tennessee` : `${who} says it ran from Tennessee to the Mid-Atlantic`);
  const q4: Question = {
    id: "t4", tables: [YEAR_TABLE],
    q: `In the table Who trades with whom, find the Mid-Atlantic and Tennessee in ${py}, the year their two reports differ most. Which way did each side say the power ran over the year, and how far apart are their reports?`,
    answer: ["The Mid-Atlantic reported ", pa, ` (${dir(pa, "it")}); Tennessee reported `, pb, ` (${dir(pb, "it")})${opposite ? ": the two sides disagree on the direction." : "."} Apart by `, pd, "; the file's gap, over the hours both reported, is ", pg, "."],
    line: [pa, " - ", pb, " = ", pd, "; the file's gap_mwh = ", pg],
    steps: [[`In site/data/regions/trade_matrix.json, region_pairs, the row with a MIDA, b TEN, year ${py}. A report above zero is power from a (the Mid-Atlantic) to b (Tennessee).`],
      ["a_report_mwh, the Mid-Atlantic's: ", pa, ". b_report_mwh, Tennessee's: ", pb, "."], ["Subtract: ", pa, " - ", pb, " = ", pd, "; the file's gap_mwh: ", pg, "."],
      ["The page turns each pair to the direction of the mean and marks a report below zero as counting the flow the other way."]],
    why: "When two operators disagree even on which way power ran, a number quoted for that flow says more about whose meter it came from than about the flow; the mean of the two hides the disagreement.",
  };

  // ---------------------------------------------------------------- t5: a flow that grew, by either side's report
  const mw = pairRows("MIDW", "TEN").map((p) => p.year).sort((a, b) => a - b);
  const y0 = mw[0], y1 = mw[mw.length - 1];
  const g = (y: number, f: string) => fig(M, ["region_pairs", sel("MIDW", "TEN", y), f], "MWh");
  const ta0 = g(y0, "b_report_mwh"), ta1 = g(y1, "b_report_mwh"), wa0 = g(y0, "a_report_mwh"), wa1 = g(y1, "a_report_mwh");
  const rT = calc("ratio", ta1, ta0, "times"), rW = calc("ratio", wa1, wa0, "times");
  // the words of the comparison follow the two ratios (within 5 percent of each other is "about the same factor")
  const moved = rT.v > 1 && rW.v > 1 ? "grew" : rT.v < 1 && rW.v < 1 ? "shrank" : null;
  const near = Math.abs(rT.v - rW.v) <= 0.05 * Math.abs(rW.v);
  const growth = moved ? `The two sides' levels differ, but each says the flow ${moved}${near ? " by about the same factor" : ", by different factors"}.` : "The two sides do not agree on whether the flow grew.";
  const q5: Question = {
    id: "t5", tables: [YEAR_TABLE],
    q: `Power from the Midwest to Tennessee: by Tennessee's own report, how many times its ${y0} flow was its ${y1} flow? And by the Midwest's report?`,
    answer: [`By Tennessee's report `, rT, `; by the Midwest's `, rW, `. ${growth}`],
    line: [ta1, " / ", ta0, " = ", rT, "; ", wa1, " / ", wa0, " = ", rW],
    steps: [[`In region_pairs, the rows with a MIDW, b TEN, for ${y0} and ${y1}, the first and the latest years both sides reported in all twelve months.`],
      ["Tennessee's report (b_report_mwh): ", ta0, ` in ${y0}, `, ta1, ` in ${y1}; `, ta1, " / ", ta0, " = ", rT, "."],
      ["The Midwest's report (a_report_mwh): ", wa0, ` in ${y0}, `, wa1, ` in ${y1}; `, wa1, " / ", wa0, " = ", rW, "."]],
    why: "Two reports that disagree on a level can still agree on a change; comparing a region's report with itself across years removes the difference between the two meters.",
  };

  // ---------------------------------------------------------------- t6: a border with one report
  const cm = mx.region_pairs.filter((p) => p.a === "CAL" && p.b === "MEX" && p.months_in_year === 12).map((p) => p.year).sort((a, b) => a - b);
  const cy = cm[cm.length - 1];
  const ca = fig(M, ["region_pairs", sel("CAL", "MEX", cy), "a_report_mwh"], "MWh"), cha = fig(M, ["region_pairs", sel("CAL", "MEX", cy), "hours_a"], "hours");
  const chb = fig(M, ["region_pairs", sel("CAL", "MEX", cy), "hours_b"], "hours");
  const q6: Question = {
    id: "t6", tables: [YEAR_TABLE],
    q: `California and Mexico in ${cy}: how much power did California report sending to Mexico, over how many hours, and for how many hours does the file hold a report from Mexico's side? What does that leave out?`,
    answer: ["California reported ", ca, " over ", cha, "; Mexico's side: ", chb, ". With one report there is no second figure to compare, so no gap can be formed."],
    line: ["a_report_mwh = ", ca, "; hours_a = ", cha, "; hours_b = ", chb],
    steps: [[`In region_pairs, the row with a CAL, b MEX, year ${cy}. Above zero: power from California to Mexico.`],
      ["a_report_mwh, California's report: ", ca, ", over hours_a, ", cha, "."], ["hours_b: ", chb, ". b_report_mwh and gap_mwh are empty: Mexico's operators file nothing with EIA's Form EIA-930."]],
    why: "Flows across the borders with Canada and Mexico are known from the United States side only, so they cannot be checked against a second report.",
  };

  // ---------------------------------------------------------------- t7: a month reported over part of its hours
  const mn = t.neighbors.MIDW.hours_own;
  // among the months that had ended when the file was built (a month still running is short of hours by the calendar)
  const k7 = mn.map((h, j) => ({ j, share: typeof h === "number" && t.months[j] < t.built.slice(0, 7) ? h / t.hours_in_month[j] : Infinity }))
    .reduce((a, b) => (b.share < a.share ? b : a)).j;
  const h7 = fig(T, ["neighbors", "MIDW", "hours_own", k7], "hours"), n7 = fig(T, ["hours_in_month", k7], "hours"), o7 = own("MIDW", k7);
  const q7: Question = {
    id: "t7", tables: [PAIR_TABLE],
    q: `In ${monthWords(t.months[k7])}, the ended month of the file in which Tennessee reported its flow with the Midwest for the smallest share of the hours, for how many hours did it report, of how many in the month, and what share is that?`,
    answer: [`${monthWords(t.months[k7])}: `, h7, " of ", n7, ", or ", calc("pct", h7, n7, "%"), "; its net import from the Midwest that month, ", o7, ", sums only those hours."],
    line: [h7, " / ", n7, " x 100 = ", calc("pct", h7, n7, "%")],
    steps: [[`In site/data/regions/trade/ten.json, position ${k7} (${t.months[k7]}): neighbors, MIDW, hours_own, `, h7, "; hours_in_month, ", n7, "."],
      ["Divide and multiply by 100: ", h7, " / ", n7, " x 100 = ", calc("pct", h7, n7, "%"), "."], ["The month's net import, ", o7, ", is a sum over the hours reported: the missing hours are not filled."]],
    why: "A monthly total over part of the month is smaller than the true one; a figure should travel with the hours behind it.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6, q7] };
}
