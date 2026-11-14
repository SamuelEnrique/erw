// Energy Research Warehouse (ERW) site, session 5267 (chain 256): whether a window of a series is whole.
//
// A query bounded by a start and an end returns the rows it matched, their count and the first and last time. It did
// not say how many steps the window should hold, so the chat found a short day, week or month by counting the rows
// itself and by grouping them again: 79 of the 257 tool calls made after the figure was in hand on 13 November 2026
// (docs/reviews/ask-eval-2026-11-13.md, "The calls after the figure, by class"). windowOf says it with the first
// result: the steps the window holds, the steps it has at the table's step, and the steps that are missing.
//
// A pure function of the times read and the table's steps: it reads no table, asks the database nothing and fills
// nothing. As warehouse/chat/window.py, line for line; tests/fixtures/session5267/window_cases.json holds both to the
// same answers (tests/test_session5267_ask.py, site/scripts/test-ask-window.test.mjs). Kept apart from tools.ts, with
// no imports, so that `node --test site/scripts/test-ask-window.test.mjs` runs it without the site's build.
//
//   start, end   the window as the query read it, two UTC instants, start included, end not
//   steps        the steps the rows may have. The site's loop reads no freq with its rows, so it gives the steps the
//                catalogue lists for the table; one step is taken as it is, and of several the step is the smallest gap
//                between two neighbouring rows of a series, when that gap is one of them; else not known
//   series       {"entity|variable": [the UTC instants of its rows in the window]}

export const MISSING_SHOWN = 6;
export const MOST_LABELS = 2400;   // the months or years of a window counted one by one; a longer window is not judged
const FIXED: Record<string, number> = { P1D: 86400, P1W: 604800 };
const CALENDAR = ["P1M", "P1Y"];

export type Run = { from: string; until: string; steps: number };
export type Window = {
  from: string; until: string; step: string | null; series?: number;
  steps_held: number | { least: number; most: number }; steps_in_window: number | null; steps_missing?: number;
  whole: boolean | null; first_held: string | null; last_held: string | null; missing?: Run[]; missing_runs?: number; note: string;
};

/** The seconds of a step of fixed length ("PT5M" 300, "PT1H" 3600, "P1D" 86400, "P1W" 604800); null for a month, a year
 *  or a step this does not read. */
export function secondsOf(step: string | null | undefined): number | null {
  if (step && step in FIXED) return FIXED[step];
  const m = /^PT(\d+)([MH])$/.exec(step ?? "");
  if (!m || Number(m[1]) <= 0) return null;
  return Number(m[1]) * (m[2] === "M" ? 60 : 3600);
}

const epoch = (t: string | number): number => {
  if (typeof t === "number") return Math.trunc(t);
  const s = t.trim();
  return Math.floor(Date.parse(/^\d{4}-\d{2}-\d{2}$/.test(s) ? `${s}T00:00:00Z` : /(Z|[+-]\d{2}:?\d{2})$/.test(s) ? s : `${s}Z`) / 1000);
};
const iso = (sec: number) => new Date(sec * 1000).toISOString().replace(/\.\d{3}Z$/, "Z");
const mod = (x: number, n: number) => ((x % n) + n) % n;

/** The month or year starts t with a <= t < b, as seconds; null when there are more than MOST_LABELS. */
function labels(step: string, a: number, b: number): number[] | null {
  const d = new Date(a * 1000);
  let y = d.getUTCFullYear(), m = step === "P1M" ? d.getUTCMonth() + 1 : 1;
  const out: number[] = [];
  for (;;) {
    const t = Date.UTC(y, m - 1, 1) / 1000;
    if (t >= b) return out;
    if (t >= a) { out.push(t); if (out.length > MOST_LABELS) return null; }
    if (step === "P1M") { if (m === 12) { y += 1; m = 1; } else m += 1; } else y += 1;
  }
}

/** The one step the rows are counted at, or null: the only step given, or of several the smallest gap between two
 *  neighbouring rows of a series when it is one of them (a month's or a year's rows are told by their gap of 28 to 31
 *  days, or 365 or 366). */
export function stepOf(steps: (string | null | undefined)[], series: Record<string, number[]>): string | null {
  const uniq = Array.from(new Set(steps.filter((s): s is string => !!s))).sort();
  if (uniq.length === 1) return uniq[0];
  if (!uniq.length) return null;
  let gap: number | null = null;
  for (const times of Object.values(series)) for (let i = 1; i < times.length; i++) {
    const g = times[i] - times[i - 1];
    if (g > 0 && (gap === null || g < gap)) gap = g;
  }
  if (gap === null) return null;
  for (const s of uniq) {
    const sec = secondsOf(s);
    if (sec === gap || (s === "P1M" && 28 * 86400 <= gap && gap <= 31 * 86400) || (s === "P1Y" && (gap === 365 * 86400 || gap === 366 * 86400))) return s;
  }
  return null;
}

type Grid = { first: number; sec: number; n: number };
function expected(step: string, a: number, b: number, held: number[]): number[] | Grid | null {
  if (CALENDAR.includes(step)) return labels(step, a, b);
  const sec = secondsOf(step);
  if (sec === null) return null;
  let anchor = 0;
  if (step === "P1W") {
    if (!held.length) return null;      // a week's row is dated the day its week begins, which only a row says
    anchor = held[0] % sec;
  }
  const first = a + mod(anchor - a, sec);
  return { first, sec, n: first >= b ? 0 : Math.floor((b - 1 - first) / sec) + 1 };
}

/** [steps held on the step's grid, steps in the window, the runs of missing steps] for one series; [n, null, null] when
 *  the step is not known or a row sits off the step's grid. */
function one(step: string | null, a: number, b: number, times: number[]): [number, number | null, Run[] | null] {
  const held = Array.from(new Set(times)).sort((x, y) => x - y);
  const exp = step ? expected(step, a, b, held) : null;
  if (exp === null) return [held.length, null, null];
  const runs: Run[] = [];
  if (Array.isArray(exp)) {
    const have = new Set(held), all = new Set(exp);
    if (held.some((t) => !all.has(t))) return [held.length, null, null];
    let run: [number, number] | null = null;
    for (const t of exp) {
      if (have.has(t)) { if (run) { runs.push({ from: iso(run[0]), until: iso(t), steps: run[1] }); run = null; } }
      else run = run === null ? [t, 1] : [run[0], run[1] + 1];
    }
    if (run) runs.push({ from: iso(run[0]), until: iso(b), steps: run[1] });
    return [held.length, exp.length, runs];
  }
  const { first, sec, n } = exp;
  if (held.some((t) => mod(t - first, sec) !== 0)) return [held.length, null, null];
  let prev = first - sec;
  for (const t of held) {
    if (t - prev > sec) runs.push({ from: iso(prev + sec), until: iso(t), steps: Math.floor((t - prev) / sec) - 1 });
    prev = t;
  }
  const last = first + (n - 1) * sec;
  if (n && prev < last) runs.push({ from: iso(prev + sec), until: iso(b), steps: Math.floor((last - prev) / sec) });
  return [held.length, n, runs];
}

export const WINDOW_WHOLE = "the window holds every step it has: steps_held of steps_in_window at the table's step. No count and no regrouping is needed to check it";
export const WINDOW_WHOLE_ROWS = "every row of the window is held: steps_held of steps_in_window, one row a day, a week, a month or a year. No count and no regrouping is needed to check it. Whether a row covers its whole period is the table's own to say, in a variable that counts the hours or days behind the row where it has one (da_hours, days_held and the like)";
export const WINDOW_PART = "the window is held in part: steps_held of steps_in_window. The steps under missing are not held and nothing is filled. Say so in the answer: a figure over this window is over the steps held, not over the whole window";
export const WINDOW_NONE_HELD = "no step of the window is held for these filters: steps_in_window steps, none of them in the table. When the entity and the variable are right (the same query with no start and no end finds their rows), the table holds the series and not this window: say which window is missing and state no figure of it";
export const WINDOW_NONE_HELD_ANY_STEP = "no row of the window is held for these filters. The table's rows come at more than one step, so the steps the window has are not counted here (steps_in_window is null); it has some at each of them, and none is in the table. When the entity and the variable are right (the same query with no start and no end finds their rows), the table holds the series and not this window: say which window is missing and state no figure of it";
export const WINDOW_UNKNOWN ="whether the window is whole cannot be told from the rows read (the table's step is not one a window is counted by, or the rows do not sit on one step): steps_held is the rows held";
export const WINDOW_SEVERAL = "more than one series matched: steps_held gives the least and the most rows any one of them holds in the window. For the steps a series is missing, ask it alone (one entity, one variable)";
export const WINDOW_EMPTY = "the window has no step of the table inside it (it is shorter than the table's step, or starts and ends between two steps)";

/** What a bounded window of a series holds beside what it has. null when no series is given. */
export function windowOf(start: string | number, end: string | number, steps: (string | null | undefined)[], series: Record<string, (string | number)[]>): Window | null {
  const keys = Object.keys(series);
  if (!keys.length) return null;
  const a = epoch(start), b = epoch(end);
  const rows: Record<string, number[]> = {};
  for (const k of keys) rows[k] = series[k].map(epoch).sort((x, y) => x - y).filter((t) => a <= t && t < b);
  const step = stepOf(steps, rows);
  const every = keys.flatMap((k) => rows[k]).sort((x, y) => x - y);
  let held: number, n: number | null, runs: Run[] | null;
  const out: Record<string, unknown> = { from: iso(a), until: iso(b), step };
  if (keys.length === 1) {
    [held, n, runs] = one(step, a, b, rows[keys[0]]);
    out.steps_held = held;
    out.steps_in_window = n;
    if (n !== null) out.steps_missing = n - held;
  } else {
    const each = keys.map((k) => one(step, a, b, rows[k]));
    const ns = new Set(each.map((e) => e[1]));
    n = ns.size === 1 ? each[0][1] : null;
    runs = null;
    held = Math.min(...each.map((e) => e[0]));
    out.series = keys.length;
    out.steps_held = { least: held, most: Math.max(...each.map((e) => e[0])) };
    out.steps_in_window = n;
  }
  out.whole = n === null || n === 0 ? null : held === n;
  // session 5276: no row at all in the window of a table of more than one step. The steps the window has cannot be
  // counted (at which step?), but when it has some at every step the table may have, none of them is held, and that is
  // said: the live set's SP15 real-time prices on a missing day read "not told" where "none held" is plain (gp02)
  let noneAtAnyStep = false;
  if (n === null && step === null && !every.length) {
    const counts = Array.from(new Set(steps.filter((s): s is string => !!s))).sort().map((s) => { const e = expected(s, a, b, []); return e === null ? null : Array.isArray(e) ? e.length : e.n; });
    if (counts.length && counts.every((c) => c !== null && c > 0)) { noneAtAnyStep = true; out.whole = false; }
  }
  out.first_held = every.length ? iso(every[0]) : null;
  out.last_held = every.length ? iso(every[every.length - 1]) : null;
  if (runs && runs.length) { out.missing = runs.slice(0, MISSING_SHOWN); out.missing_runs = runs.length; }
  const note = noneAtAnyStep ? WINDOW_NONE_HELD_ANY_STEP : n === null ? WINDOW_UNKNOWN : n === 0 ? WINDOW_EMPTY : out.whole ? (step !== null && (step in FIXED || CALENDAR.includes(step)) ? WINDOW_WHOLE_ROWS : WINDOW_WHOLE) : !every.length ? WINDOW_NONE_HELD : WINDOW_PART;
  out.note = note + (keys.length > 1 ? `. ${WINDOW_SEVERAL}` : "");
  return out as Window;
}
