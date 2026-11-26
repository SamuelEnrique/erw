// Energy Research Warehouse (ERW) site, session 10404 (chain 720, part E): problem set "A forecast's report card". The
// ERW's own day-ahead forecast of demand, scored against what happened beside the operator's own forecast and two simple
// rules, every figure read from the committed page file site/data/predict/scores.json (written by
// warehouse/predict/backtest.py; contract docs/state/page_files_predict.md; method docs/methods/predict.md) with its
// pf| key (lib/pagefile.ts). The page that draws the file is /forecast.
//
// The file's rows are arrays in the order of its `rows_columns` (place, series, method, cut, key, hours, mae, mape,
// held). A question names a row by its place, series, method, cut and key; the row's position in the file is found by
// those five, never typed, and a figure's key is that position and its column.
//
// The set states what was forecast and how it scored. Where the ERW forecast scored worse it is written as it is: the
// rules below choose the places, the cuts and the hours, and none of them looks at who scored better.
//
// A waiting set (lib/problems.ts, WAITING_SETS): it has its page, and is in no index and no dated edition until the
// owner approves it.
import type { Question } from "@/lib/problems";
import { calc, fig, open, type Built, type Meta, type SetGuide } from "./common";

const F = "predict/scores.json";
type Cell = string | number | null;
type ScoresFile = {
  span: Record<string, { first_day: string | null; last_day: string | null }>;
  methods: { id: string; what: string }[]; cuts: Record<string, string>; rows_columns: string[]; rows: Cell[][];
};

/** The place the set asks about: the one /forecast opens on. And the second place of the last question. */
export const PLACE = "region-tex", PLACE_NAME = "Texas", SECOND = "region-cal", SECOND_NAME = "California";

export const META: Meta = {
  slug: "a-forecasts-report-card", title: "A forecast's report card: the ERW forecast against the operator's and two simple rules",
  line: "How far a day-ahead forecast of Texas's demand was from what happened, in megawatts and in percent, beside the grid operator's own forecast and two rules that need no model (the same hour of the latest day held, and of a week before): over every hour, over two years, by hour of the day, on the highest-demand days, and in a second region.",
  teacher: "About 45 minutes. Prerequisites: an absolute error, a mean, a percent of a value, a difference in percentage points, a ratio. Students open /forecast, read \"How it has done\" for Texas, and find each figure in site/data/predict/scores.json, the file the page draws. The ERW forecast is a model's output, not a published figure; the operator's forecast is the operator's own. The set asks how each scored and takes no side.",
  pages: [{ href: "/forecast", label: "ERW forecast" }, { href: "/data/methods/predict", label: "Method: the ERW forecast of demand" }],
};

export const GUIDE_ENTRY: SetGuide = {
  can: "read a forecast's score table, tell an error in megawatts from an error in percent, compare two forecasts on the same hours, and say where and when a forecast is furthest off",
  grids: ["Texas (EIA's region of the lower 48)", "California", "any region or balancing authority the file scores"],
  tables: [],
  skills: ["mean absolute error", "mean absolute percent error", "percentage points", "a ratio", "a share of a total", "a benchmark rule"],
  order: ["f1", "f2", "f6", "f3", "f4", "f5"],
  files: [F],
};

/** The choices that move this set's figures, in the form of the sets' decisions (app/learn/problems/Decisions.tsx). */
export const DECISIONS = [
  { key: "report-card-place", sets: [META.slug], text: `The set asks about ${PLACE_NAME}, and compares it with ${SECOND_NAME} in its last question.`,
    def: `${PLACE_NAME} (${PLACE}) and ${SECOND_NAME} (${SECOND}), fixed in the set's module.`, source: `${PLACE_NAME} is the place /forecast opens on; ${SECOND_NAME} is the first region in the file's own order. Neither was chosen by its score.`, session: "session 10404 (chain 720)" },
  { key: "report-card-hours", sets: [META.slug], text: "The hour of the day with the largest error and the one with the smallest are found from the file's 24 rows, the first on a tie.",
    def: "The largest and the smallest mean absolute percent error of the ERW forecast among the 24 rows of the cut \"hour\".", source: "site/data/predict/scores.json, the cut \"hour\" (over the last two years, in the place's own clock).", session: "session 10404 (chain 720)" },
  { key: "report-card-same-hours", sets: [META.slug], text: "Every method of a row is scored on the same hours, so two methods of one row can be set side by side.",
    def: "As the file is built: an hour enters a comparison only when every method in it has a forecast and what happened is held.", source: "docs/state/page_files_predict.md, section 3.", session: "session 10600 (chain 730), read here in session 10404" },
];

export async function build(): Promise<Built> {
  const d = open<ScoresFile>(F);
  const c = Object.fromEntries(d.rows_columns.map((n, i) => [n, i])) as Record<string, number>;
  const at = (place: string, method: string, cut: string, key = "", series = "demand"): number => {
    const i = d.rows.findIndex((r) => r[c.place] === place && r[c.series] === series && r[c.method] === method && r[c.cut] === cut && String(r[c.key] ?? "") === key);
    if (i < 0) throw new Error(`no row of ${F} for ${place}, ${series}, ${method}, ${cut}${key ? `, ${key}` : ""}`);
    return i;
  };
  const mape = (place: string, method: string, cut: string, key = "") => fig(F, ["rows", at(place, method, cut, key), c.mape], "%");
  const mae = (place: string, method: string, cut: string, key = "") => fig(F, ["rows", at(place, method, cut, key), c.mae], "MW");
  const hours = (place: string, method: string, cut: string, key = "") => fig(F, ["rows", at(place, method, cut, key), c.hours], "hours");
  const where = (method: string, cut: string, key = "", place = PLACE) => `the row of ${place}, demand, ${method}, ${cut}${key ? `, ${key}` : ""}`;
  const span = d.span.demand;
  const days = `${span.first_day} to ${span.last_day}`;
  const what = (id: string) => d.methods.find((m) => m.id === id)?.what ?? id;

  // ---------------------------------------------------------------- worked example: the two forecasts over every hour
  const xe = mape(PLACE, "erw", "all"), xo = mape(PLACE, "operator", "all"), xd = calc("diff", xe, xo, "percentage points");
  const example: Question = {
    id: "fx", tables: [],
    q: `Over every hour the file scores for ${PLACE_NAME} (${days}), what was the mean absolute percent error of the ERW forecast of demand, what was the operator's own forecast's, and how many percentage points apart are they?`,
    answer: ["The ERW forecast ", xe, ", the operator's ", xo, ": apart by ", xd, " (above zero, the ERW forecast was further off)."],
    line: [xe, " - ", xo, " = ", xd],
    steps: [[`In site/data/predict/scores.json, rows: ${where("erw", "all")}, and ${where("operator", "all")}. The column mape is the mean absolute percent error.`],
      ["The ERW forecast ", xe, "; the operator's ", xo, "."], ["Subtract: ", xe, " - ", xo, " = ", xd, "."]],
    why: "A percent error divides each hour's miss by that hour's demand, so a forecast of a large region and one of a small one can be read on one scale. Both methods of a row are scored on the same hours.",
  };

  // ---------------------------------------------------------------- f1: megawatts, over the last two years
  const e2 = mae(PLACE, "erw", "last_2_years"), o2 = mae(PLACE, "operator", "last_2_years"), r1 = calc("ratio", e2, o2, "times");
  const q1: Question = {
    id: "f1", tables: [],
    q: `Over the last two years of the backtest, what was the mean absolute error of the ERW forecast of ${PLACE_NAME}'s demand in megawatts, what was the operator's, and the first is how many times the second?`,
    answer: ["The ERW forecast ", e2, ", the operator's ", o2, ": ", r1, "."],
    line: [e2, " / ", o2, " = ", r1],
    steps: [[`rows: ${where("erw", "last_2_years")}, and ${where("operator", "last_2_years")}. The column mae is the mean absolute error, in MW.`], ["The ERW forecast ", e2, "; the operator's ", o2, "."],
      ["Divide: ", e2, " / ", o2, " = ", r1, "."]],
    why: `An error in megawatts says how much power was misjudged in an average hour. The cut is ${d.cuts.last_2_years ?? "the last 730 days of the backtest"}.`,
  };

  // ---------------------------------------------------------------- f2: the two simple rules
  const ye = mape(PLACE, "yesterday", "all"), we = mape(PLACE, "week_ago", "all"), d2 = calc("diff", we, ye, "percentage points");
  const q2: Question = {
    id: "f2", tables: [],
    q: `Two rules need no model. The file calls them yesterday (${what("yesterday")}) and week_ago (${what("week_ago")}). Over every hour scored for ${PLACE_NAME}, what was each rule's mean absolute percent error, and how many percentage points is the week-ago rule above the yesterday rule?`,
    answer: ["Yesterday ", ye, ", a week ago ", we, ": the week-ago rule is above by ", d2, "."],
    line: [we, " - ", ye, " = ", d2],
    steps: [[`rows: ${where("yesterday", "all")}, and ${where("week_ago", "all")}.`], ["Yesterday ", ye, "; a week ago ", we, "."], ["Subtract: ", we, " - ", ye, " = ", d2, "."]],
    why: "A forecast is read against what a rule with no model would have said. The nearer day is closer in weather; the day a week before is the same day of the week.",
  };

  // ---------------------------------------------------------------- f3: the hour of the day
  const byHour = Array.from({ length: 24 }, (_, h) => ({ h, i: at(PLACE, "erw", "hour", String(h)) })).map((x) => ({ ...x, v: d.rows[x.i][c.mape] as number }));
  const hi = byHour.reduce((a, b) => (b.v > a.v ? b : a)), lo = byHour.reduce((a, b) => (b.v < a.v ? b : a));
  const hh = (h: number) => `${String(h).padStart(2, "0")}:00`;
  const vh = mape(PLACE, "erw", "hour", String(hi.h)), vl = mape(PLACE, "erw", "hour", String(lo.h)), r3 = calc("ratio", vh, vl, "times");
  const q3: Question = {
    id: "f3", tables: [],
    q: `By hour of the day in ${PLACE_NAME}'s own clock, at which hour is the ERW forecast's mean absolute percent error largest and at which is it smallest, what are the two errors, and the largest is how many times the smallest?`,
    answer: [`Largest at ${hh(hi.h)}, `, vh, `; smallest at ${hh(lo.h)}, `, vl, ": ", r3, "."],
    line: [vh, " / ", vl, " = ", r3],
    steps: [[`rows of ${PLACE}, demand, erw, cut hour: 24 rows, key 0 to 23. Read the column mape of each.`], [`The largest is at key ${hi.h} (${hh(hi.h)}): `, vh, `; the smallest at key ${lo.h} (${hh(lo.h)}): `, vl, "."],
      ["Divide: ", vh, " / ", vl, " = ", r3, "."]],
    why: "A single mean hides when in the day a forecast misses most; the same forecast read hour by hour shows it. The 24 rows are hours of the place's own clock, scored over the last two years of the backtest.",
  };

  // ---------------------------------------------------------------- f4: the highest-demand days
  const et = mape(PLACE, "erw", "top10"), ot = mape(PLACE, "operator", "top10"), d4 = calc("diff", et, ot, "percentage points");
  const q4: Question = {
    id: "f4", tables: [],
    q: `On ${PLACE_NAME}'s ten highest-demand days of the backtest, what was the ERW forecast's mean absolute percent error, what was the operator's, and how many percentage points apart are they? Compare the ERW forecast's with its error over every hour.`,
    answer: ["On the ten days: the ERW forecast ", et, ", the operator's ", ot, ", apart by ", d4, ". Over every hour the ERW forecast's was ", xe, "."],
    line: [et, " - ", ot, " = ", d4, "; over every hour ", xe],
    steps: [[`rows: ${where("erw", "top10")}, and ${where("operator", "top10")}; and ${where("erw", "all")} from the worked example.`], ["The ERW forecast ", et, "; the operator's ", ot, "; over every hour ", xe, "."],
      ["Subtract: ", et, " - ", ot, " = ", d4, "."]],
    why: `The highest-demand days are the ones a grid is built for, so a forecast's error on them is read apart from its error on an ordinary day. The cut is ${d.cuts.top10 ?? "the place's ten highest-demand days"}.`,
  };

  // ---------------------------------------------------------------- f5: a second region
  const se = mape(SECOND, "erw", "all"), so = mape(SECOND, "operator", "all"), ds = calc("diff", se, so, "percentage points");
  const q5: Question = {
    id: "f5", tables: [],
    q: `Take the worked example again for ${SECOND_NAME}: over every hour scored, the ERW forecast's mean absolute percent error less the operator's. Set it beside ${PLACE_NAME}'s. In which of the two regions was the ERW forecast further from the operator's, and on which side?`,
    answer: [`${SECOND_NAME}: `, se, " - ", so, " = ", ds, `. ${PLACE_NAME}: `, xd, `. The two forecasts were further apart in ${Math.abs(xd.v) > Math.abs(ds.v) ? PLACE_NAME : SECOND_NAME}. Above zero the ERW forecast was further off than the operator's; below zero, closer.`],
    line: [se, " - ", so, " = ", ds, "; ", xe, " - ", xo, " = ", xd],
    steps: [[`rows: ${where("erw", "all", "", SECOND)}, and ${where("operator", "all", "", SECOND)}.`], [`${SECOND_NAME}: the ERW forecast `, se, ", the operator's ", so, ": ", ds, "."],
      [`${PLACE_NAME}, from the worked example: `, xd, "."]],
    why: "One method does not score alike everywhere: a region's weather, its size and how its operator forecasts all move the comparison, so a score is read place by place.",
  };

  // ---------------------------------------------------------------- f6: how many hours stand behind a score
  const ha = hours(PLACE, "erw", "all"), h2 = hours(PLACE, "erw", "last_2_years"), sh = calc("pct", h2, ha, "%");
  const q6: Question = {
    id: "f6", tables: [],
    q: `How many hours stand behind ${PLACE_NAME}'s score over the whole backtest, how many behind its score over the last two years, and what share of the first is the second?`,
    answer: ["The whole backtest ", ha, ", the last two years ", h2, ": ", sh, "."],
    line: [h2, " / ", ha, " x 100 = ", sh],
    steps: [[`rows: ${where("erw", "all")}, and ${where("erw", "last_2_years")}. The column hours is the count of hours scored.`], ["The whole backtest ", ha, "; the last two years ", h2, "."],
      ["Share: ", h2, " / ", ha, " x 100 = ", sh, "."]],
    why: "A mean is as steady as the count behind it, so a score is read with its hours. An hour is counted only when what happened and every method's forecast are held, so 730 days can hold fewer than their 17,520 hours.",
  };

  return { example, questions: [q1, q2, q3, q4, q5, q6] };
}
