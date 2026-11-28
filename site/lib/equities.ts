// Energy Research Warehouse (ERW) site, session 10402 (chain 720, part D): energy equities.
//
// Two things read the equities page files (site/data/equities/, the data machine's warehouse/derived/equity_pages.py;
// contract docs/state/page_files_equities.md; method docs/methods/equities.md): a group on the price board (/board),
// one row a segment line and one an index, and the group's analyzer, /equities (every company by segment, a company,
// an index or a segment as a line with an energy price laid over it, a company's filed figures by quarter, two side by
// side). This module holds the files' shapes and the pure functions the board, the page, its download routes and its
// tests share. The files carry levels and plain changes: no score, no signal, no view, and neither do the pages.
// Nothing is filled: a value a file holds as null is a blank with the file's own reason, never a zero.
import { WINDOWS, windowed, type BoardFile, type Group, type Point, type Row, type Status } from "@/lib/board";

export type Cell = string | number | null;
export type EqMove = { t: string; v: number; ch: number; pct: number | null } | null;
export type MoveKey = "d" | "w" | "m" | "ytd" | "y";
export type EqMoves = Partial<Record<MoveKey, EqMove>>;
/** The moves in the contract's order, with the words of each. */
export const MOVE_WORDS: [MoveKey, string][] = [["d", "Day"], ["w", "Week"], ["m", "Month"], ["ytd", "Year to date"], ["y", "Year"]];

// ---- The board's group (file 3) -------------------------------------------------------------------------------------

export type EqBoardRow = {
  id: string; group: string; label: string; unit: string; freq?: string; tags?: Record<string, string | null>; source?: number;
  status: string; note?: string; basis?: string; last?: { t: string; v: number }; moves?: EqMoves; spark?: { t0: string; d: number[]; v: number[] }; file?: string;
  // session 10405 (chain 720, part E): the board's other cells in the board's own forms, on each `ok` row once the
  // equity side holds one (the contract's dated line of 26 November, data request 572); no row carries them yet
  avg7?: Row["avg7"]; avg30?: Row["avg30"]; avg365?: Row["avg365"]; lo30?: number; hi30?: number; range?: Row["range"];
};
/** Session 10405: the board's cells a row may carry beyond its latest value, its moves and its trend. */
const WIDE_CELLS = ["avg7", "avg30", "avg365", "lo30", "hi30", "range"] as const;
/** A row that holds a figure and at least one of the board's other cells. */
export const hasWideCells = (r: EqBoardRow): boolean => r.status === "ok" && WIDE_CELLS.some((k) => r[k] !== undefined && r[k] !== null);
export type EqBoardFile = { built: string; example?: boolean; method?: string; contract?: string; group: Group; sources: string[]; rows: EqBoardRow[] };
export const EQUITIES_GROUP = "equities";
const BOARD_STATUS: readonly string[] = ["ok", "paused", "licensed", "license", "not_held", "working"];

/** A series' id from the path a file gives it: "series/segment-refining.json" is "segment-refining"; null for any
 *  other shape. The id is what /equities takes in its address. */
export function seriesIdOf(file: string | null | undefined): string | null {
  const m = /^series\/([A-Za-z0-9][A-Za-z0-9._-]*)\.json$/.exec(file ?? "");
  return m ? m[1] : null;
}

/** One row of the contract's file as a row of the board (lib/board.ts Row). A row that is not `ok`, or that is `ok`
 *  and holds no latest value, carries its name, its unit, its status and its note, and no figure, as the board's held
 *  rows do. A row with a value opens its series on /equities. `offset` is where the file's sources start in the
 *  board's list. */
export function boardRow(r: EqBoardRow, offset: number): Row {
  const tags = Object.fromEntries(Object.entries(r.tags ?? {}).filter((e): e is [string, string] => typeof e[1] === "string"));
  const freq = r.freq === "D" || r.freq === "W" || r.freq === "M" || r.freq === "Q" ? r.freq : "";
  const status = (BOARD_STATUS.includes(r.status) ? r.status : "not_held") as Status;
  const base: Row = { id: r.id, group: EQUITIES_GROUP, label: r.label, at: "", code: "", unit: r.unit ?? "", freq, tags, status };
  if (status !== "ok" || !r.last || typeof r.last.v !== "number") {
    return { ...base, status: status === "ok" ? "not_held" : status, note: r.note ?? "The file holds no figure for this row." };
  }
  const id = seriesIdOf(r.file);
  return {
    ...base, basis: r.basis, last: r.last, moves: r.moves as Row["moves"], spark: r.spark,
    // session 10405: the board's other cells, where the file holds them (a cell it does not hold is left out, never a nought)
    ...Object.fromEntries(WIDE_CELLS.filter((k) => r[k] !== undefined && r[k] !== null).map((k) => [k, r[k]])),
    ...(typeof r.source === "number" ? { source: offset + r.source } : {}),
    ...(id ? { open: `/equities?a=${encodeURIComponent(id)}` } : {}),
  };
}

/** The board's file with the equities group after its own groups and the group's rows after its own rows: nothing the
 *  board has is dropped, moved or changed. With no equities file the board is as it was. With the contract's example
 *  file (every value null) the group is one blank row that says so: nothing of an example is shown as real, its rows'
 *  names included. A board file that already holds a group of this id is left alone. */
export function withEquities(file: BoardFile, eq: EqBoardFile | null): BoardFile {
  if (!eq || !eq.group || eq.group.id !== EQUITIES_GROUP || !Array.isArray(eq.rows)) return file;
  if (file.groups.some((g) => g.id === EQUITIES_GROUP)) return file;
  // lean while no row carries the board's other cells (session 10405): with the first row that does, the group's table
  // takes the board's full set of columns, and a row without them shows blanks there as any board row does
  const group: Group = { ...eq.group, lean: eq.example === true || !eq.rows.some(hasWideCells) };
  if (eq.example === true) {
    const blank: Row = { id: "equities-not-built", group: EQUITIES_GROUP, label: "Segments and indices", at: "", code: "", unit: "", freq: "", tags: {}, status: "not_held",
      note: "The equities files on the site are the contract's examples: no figure has been written yet (docs/state/page_files_equities.md)." };
    return { ...file, groups: [...file.groups, group], rows: [...file.rows, blank] };
  }
  const offset = file.sources.length;
  return { ...file, sources: [...file.sources, ...(eq.sources ?? [])], groups: [...file.groups, group], rows: [...file.rows, ...eq.rows.map((r) => boardRow(r, offset))] };
}

// ---- The list (file 1), a series (file 2), the energy prices (file 4) ------------------------------------------------

/** `rule_why` (in the files as built on 26 November 2026, not yet in the contract's text): why `rule` is null. */
export type EqSegment = { id: string; label: string; rule: string | null; rule_why?: string | null; n_companies: number | null };
export type EqCompany = {
  id: string; cik: string | null; name: string | null; ticker: string; exchange: string | null; sic: string | null; sic_label: string | null;
  segments: string[]; segments_note: string | null; directory_id: string | null;
  price_status: string; price_why: string | null; fundamentals_status: string; fundamentals_why: string | null;
  first: string | null; last: string | null; file: string;
  // session 10405 (chain 720, part E): a company's last close, its changes and its market value (the contract's dated
  // line of 26 November, data request 571), each null where its price or share count is held; no company carries them yet
  last_close?: { t: string; v: number } | null; moves?: EqMoves | null; market_value?: { t: string; v: number } | null;
  // session 10414 (chain 720, part E): the newest period the company filed, as the list carries it since the contract's
  // dated line of 27 November (data requests 578 and 579); null when nothing is filed, absent in an older list
  newest_filed?: NewestFiled | null;
};
/** Session 10414: the newest period a company filed, by the page's own rule (newestOf): a sum over a period is the
 *  shortest period to that end with its length in months, debt and shares are at the end; the later filing where a
 *  period was filed twice. */
export type FiledSum = { months: number | null; v: number };
export type NewestFiled = { period_end: string; form: string | null; filed: string | null; url: string | null; revenue: FiledSum | null; net_income: FiledSum | null; capex: FiledSum | null; debt: number | null; shares_outstanding: number | null };
/** Session 10405: whether any company of a list carries a close, a change or a market value (the table has the columns
 *  only then: a list with none of them is the table as it was). */
export const companiesPriced = (rows: EqCompany[]): boolean => rows.some((c) => !!c.last_close || !!c.market_value || (!!c.moves && Object.values(c.moves).some(Boolean)));
/** A sum of dollars as the site's value check writes a figure: whole with commas, or two decimals. */
export const wholeWords = (v: number) => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
export type EqIndexEntry = { id: string; name: string | null; publisher: string | null; kind: string; proxy_for: string | null; status: string; why: string | null; first: string | null; last: string | null; file: string };
export type EqList = {
  built: string; example?: boolean; method?: string; contract?: string; license?: string; tables?: string[]; last_day: string | null;
  segments: EqSegment[]; companies: EqCompany[]; indices: EqIndexEntry[]; segment_series: { id: string; segment: string; file: string }[];
  /** as built on 26 November 2026: why the companies, the indices and the prices are not in the list, each in words */
  held?: Record<string, string>;
};
export type EqSeries = {
  built: string; example?: boolean; method?: string; contract?: string; license?: string;
  id: string; kind: "company" | "index" | "segment"; name: string | null; cik?: string | null; ticker?: string | null; exchange?: string | null; segments?: string[] | null;
  status: string; why: string | null; source: string | null; units: Record<string, string>; held: Record<string, string>;
  daily_columns: string[]; daily: Cell[][]; last: { t: string; v: number } | null; last_value_weight?: { t: string; v: number } | null;
  moves: EqMoves; moves_value_weight?: EqMoves;
  quarterly_columns?: string[]; quarterly?: Cell[][]; concepts?: Record<string, string | null>;
};
export type EqPrice = {
  id: string; label: string; unit: string; freq: string; table: string | null; entity: string | null; variable: string | null; source: string | null; license: string | null;
  status: string; why: string | null; first: string | null; last: string | null; last_value: { t: string; v: number } | null; moves?: EqMoves;
};
export type EqPrices = { built: string; example?: boolean; method?: string; contract?: string; since?: string; series: EqPrice[]; daily: Record<string, [string, number | null][]> };
/** A change the file writes for a step the series does not have: a monthly price's "day" and "week" are its month's
 *  (the contract measures `d` from the previous value held), and a quarterly one's "month" is its quarter's. The page
 *  says the series' step there instead of repeating the figure (the price board's own rule, lib/board.ts noMove). */
export const noStep = (freq: string, k: MoveKey): boolean => (freq === "W" && k === "d") || (freq === "M" && (k === "d" || k === "w")) || (freq === "Q" && k !== "y" && k !== "ytd");
export const FREQ_WORDS: Record<string, string> = { D: "daily", W: "weekly", M: "monthly", Q: "quarterly" };

/** A series is drawn only when its file is not an example and its status is "shown". */
export const isShown = (f: { example?: boolean; status?: string } | null | undefined): boolean => !!f && f.example !== true && f.status === "shown";
/** The words a blank carries on the page, by the file's status. "license needed" is the catalogue's own phrase. */
export function blankWords(status: string | null | undefined, example = false): string {
  if (example) return "not built yet";
  switch (status) {
    case "license needed": return "license needed";
    case "source needed": return "source needed";
    case "not filed": return "not filed";
    case "paused": return "paused";
    default: return "not held";
  }
}
/** The words of a reason, short enough for a cell or a blank's face: what stands before its first colon ("source
 *  needed" of "source needed: the segment rule reads ..."); the whole reason stays in the hover. */
export function shortWhy(reason: string | null | undefined, dflt = "not held"): string {
  const head = (reason ?? "").split(":")[0].trim();
  return head && head.length <= 24 ? head : dflt;
}
/** The list's reasons, each once, as one hover. */
export const heldWhy = (list: Pick<EqList, "held"> | null, keys: string[]): string =>
  [...new Set(keys.map((k) => list?.held?.[k]).filter((x): x is string => !!x))].map((x) => (/[.!?]$/.test(x) ? x : `${x}.`)).join(" ");
/** The hover of a blank: the file's own reason, else the status in a sentence. Never empty. */
export function blankWhy(status: string | null | undefined, why: string | null | undefined, example = false): string {
  if (example) return "The file on the site is the contract's example: no figure has been written yet (docs/state/page_files_equities.md).";
  const w = (why ?? "").trim();
  if (status === "license needed") return w ? (/^license needed/i.test(w) ? w.replace(/^license needed/i, "License needed") : `License needed: ${w}`) : "License needed: the ERW holds this series and may not show it (docs/licenses.md).";
  if (status === "source needed") return w ? (/^source needed/i.test(w) ? w.replace(/^source needed/i, "Source needed") : `Source needed: ${w}`) : "Source needed: no source has been found that the ERW may read for this series.";
  if (status === "paused") return w ? `Paused: ${w}` : "Paused: the publisher is paused (warehouse/metadata/paused_sources.csv).";
  return w || (status ? `${status}.` : "The file of this series is not on the site.");
}

// ---- What a reader can choose ---------------------------------------------------------------------------------------

export type Choice = { id: string; kind: "segment" | "index" | "company"; label: string; file: string };
/** Everything /equities can draw, in the list's own order: the segments' lines, the indices, the companies. */
export function picksOf(list: EqList | null): Choice[] {
  if (!list || list.example === true) return [];
  const out: Choice[] = [];
  for (const s of list.segment_series ?? []) {
    const id = seriesIdOf(s.file);
    if (id) out.push({ id, kind: "segment", label: `Segment: ${list.segments.find((g) => g.id === s.segment)?.label ?? s.segment}`, file: s.file });
  }
  for (const x of list.indices ?? []) {
    const id = seriesIdOf(x.file);
    if (id) out.push({ id, kind: "index", label: `${x.kind === "proxy" ? "Index proxy" : "Index"}: ${x.name ?? x.id}`, file: x.file });
  }
  for (const c of list.companies ?? []) {
    const id = seriesIdOf(c.file);
    if (id) out.push({ id, kind: "company", label: `${c.ticker}: ${c.name ?? c.ticker}`, file: c.file });
  }
  return out;
}
export const segmentLabel = (list: EqList | null, id: string) => list?.segments.find((g) => g.id === id)?.label ?? id.replace(/_/g, " ");

// ---- Lines ----------------------------------------------------------------------------------------------------------

const numOf = (v: Cell | undefined): number | null => (typeof v === "number" && Number.isFinite(v) ? v : null);
const dayMs = (day: string) => Date.parse(`${day}T00:00:00Z`);
/** One column of a series' daily rows as points in time; a day the column does not hold has no point. */
export function pointsOf(s: Pick<EqSeries, "daily_columns" | "daily">, col: string): Point[] {
  const i = s.daily_columns.indexOf(col), d = s.daily_columns.indexOf("day");
  if (i < 0 || d < 0) return [];
  const out: Point[] = [];
  for (const r of s.daily ?? []) { const v = numOf(r[i]); if (v !== null && typeof r[d] === "string") out.push({ t: dayMs(r[d] as string), v }); }
  return out;
}

export type Line = { col: string; name: string; unit: string; what: string };
/** The lines a series is drawn as. A segment has two, each named plainly: every company counting the same, and each
 *  company counting by its market value. */
export function linesOf(s: EqSeries): Line[] {
  const u = (c: string, d: string) => s.units?.[c] ?? d;
  if (s.kind === "segment") return [
    { col: "equal_weight", name: "Every company counts the same", unit: u("equal_weight", "index, first day = 100"), what: "Equal weight: the mean of the segment's companies' daily returns, chained from 100 on the first day held." },
    { col: "value_weight", name: "Larger companies count more", unit: u("value_weight", "index, first day = 100"), what: "Weighted by market value: the same, each company's return weighted by its market value the day before, from 100 on the first day held." },
  ];
  if (s.kind === "index") return [{ col: "level", name: "Level", unit: u("level", "points"), what: "The index's level as its publisher prints it." }];
  return [{ col: "close", name: "Close", unit: u("close", "USD/share"), what: "The day's closing price, as the source prints it." }];
}
/** An energy price's points; a monthly or weekly price keeps its own dates. */
export function pricePoints(prices: EqPrices | null, id: string | null): Point[] {
  if (!prices || prices.example === true || !id) return [];
  return (prices.daily?.[id] ?? []).filter((r) => typeof r[1] === "number").map((r) => ({ t: dayMs(r[0]), v: r[1] as number }));
}
export const WINDOW_KEYS = WINDOWS.map((w) => w[0]);
export const windowWords = (w: string) => WINDOWS.find((x) => x[0] === w)?.[1] ?? w;
/** Points inside a window counted back from the newest point of `anchor` (the series a price is laid over), so both
 *  lines cover the same days. */
export function windowLike(p: Point[], w: string, anchor: Point[]): Point[] {
  const a = windowed(anchor, w);
  if (!a.length) return [];
  return p.filter((x) => x.t >= a[0].t && x.t <= a[a.length - 1].t);
}
export { windowed };

// ---- Filed figures --------------------------------------------------------------------------------------------------

export type Filing = {
  i: number; period_start: string | null; period_end: string | null; months: number | null; fy: Cell; fp: Cell; form: string | null; filed: string | null;
  revenue: number | null; net_income: number | null; capex: number | null; debt: number | null; shares_outstanding: number | null; accession: string | null; url: string | null;
};
export const STATEMENT: [keyof Filing & string, string, string][] = [
  ["revenue", "Revenue", "USD million"], ["net_income", "Net income", "USD million"], ["capex", "Capital spending", "USD million"],
  ["debt", "Debt", "USD million"], ["shares_outstanding", "Shares outstanding", "million"],
];
/** A company's filed periods, in the file's own order (newest first), by the file's column names. A row with no
 *  period end is not a filing (the example's row of nulls). */
export function filingsOf(s: EqSeries): Filing[] {
  const cols = s.quarterly_columns ?? [];
  const at = (n: string) => cols.indexOf(n);
  const str = (r: Cell[], n: string) => { const v = r[at(n)]; return typeof v === "string" && v ? v : null; };
  const num = (r: Cell[], n: string) => (at(n) < 0 ? null : numOf(r[at(n)]));
  return (s.quarterly ?? []).map((r, i): Filing => ({
    i, period_start: str(r, "period_start"), period_end: str(r, "period_end"), months: num(r, "months"), fy: at("fy") < 0 ? null : r[at("fy")], fp: at("fp") < 0 ? null : r[at("fp")],
    form: str(r, "form"), filed: str(r, "filed"), revenue: num(r, "revenue"), net_income: num(r, "net_income"), capex: num(r, "capex"), debt: num(r, "debt"),
    shares_outstanding: num(r, "shares_outstanding"), accession: str(r, "accession"), url: str(r, "url"),
  })).filter((f) => f.period_end !== null);
}
// Session 10408 (chain 720, part E; the SEC's company figures are in the files since 27 November 2026): one filed
// figure over the periods a company filed, and the newest period's rows side by side. A point of figureLine is
// a figure as filed, for the period its filing reports; a period not filed on its own (often the fourth quarter,
// which a 10-K reports inside its 12 months) has none there, and fourthQuarters (session 11408) works it out apart.
export type FigureKey = "revenue" | "net_income" | "capex" | "debt" | "shares_outstanding";
export const FIGURES = STATEMENT.map((x) => x[0]) as FigureKey[];
export const FIGURE_DEFAULT: FigureKey = "revenue";
/** Debt and shares are a filing's figures at its period's end; the others are sums over the period. */
export const AT_PERIOD_END: readonly FigureKey[] = ["debt", "shares_outstanding"];
export const PERIOD_KEYS = ["3", "12"] as const;
export type PeriodKey = (typeof PERIOD_KEYS)[number];
export const PERIOD_DEFAULT: PeriodKey = "3";
export const PERIOD_WORDS: Record<PeriodKey, string> = { "3": "3 months", "12": "12 months" };
export const figureWords = (col: FigureKey) => STATEMENT.find((x) => x[0] === col)?.[1] ?? col;
export const figureUnit = (col: FigureKey) => (col === "shares_outstanding" ? "million shares" : "USD million");
export type FiledPoint = { f: Filing; v: number };
const later = (a: Filing, b: Filing | undefined) => !b || (a.filed ?? "") > (b.filed ?? "");
/** One figure over the periods filed, oldest first, one point a period end. A sum over a period (revenue, net income,
 *  capital spending): the rows whose period is `per` months long. A figure at a period's end (debt, shares): every
 *  period end for "3", the period ends of the annual reports (10-K) for "12". Where one period was filed more than
 *  once (an amended form), the figure of the filing made last that holds one. */
export function figureLine(fs: Filing[], col: FigureKey, per: PeriodKey): FiledPoint[] {
  const atEnd = AT_PERIOD_END.includes(col), months = Number(per);
  const best = new Map<string, FiledPoint>();
  for (const f of fs) {
    const v = f[col];
    if (v === null || f.period_end === null) continue;
    if (atEnd ? per === "12" && !/^10-K/.test(f.form ?? "") : f.months !== months) continue;
    if (later(f, best.get(f.period_end)?.f)) best.set(f.period_end, { f, v });
  }
  return [...best.values()].sort((a, b) => (a.f.period_end as string).localeCompare(b.f.period_end as string));
}
/** Ready branch of session 11408 (weekend page of 28 November 2026, part 3.5: a fourth quarter worked out): a quarter
 *  filed only inside a year's total is the year less its first nine months, where a 12-month figure and a 9-month
 *  figure of one fiscal year (the same period start, the nine months ending three months before the year) are both
 *  filed and the quarter itself is not. Each point names the two filings it is worked out from (`nine`); a sum only
 *  (revenue, net income, capital spending), never debt or shares. The chart draws them beside the quarters filed; the
 *  headline figure and the tables stay the filed figures. */
export type WorkedPoint = FiledPoint & { nine: Filing };
const monthsBefore = (end: string, n: number) => {
  const d = new Date(`${end}T00:00:00Z`);
  const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - n + 1, 0));
  return t.toISOString().slice(0, 10);
};
export function fourthQuarters(fs: Filing[], col: FigureKey): WorkedPoint[] {
  if (AT_PERIOD_END.includes(col)) return [];
  const filed = new Set(figureLine(fs, col, "3").map((p) => p.f.period_end));
  const year = figureLine(fs, col, "12");
  const nines = new Map<string, Filing>();
  for (const f of fs) {
    if (f.months !== 9 || f[col] === null || f.period_start === null || f.period_end === null) continue;
    const k = `${f.period_start}|${f.period_end}`;
    if (later(f, nines.get(k))) nines.set(k, f);
  }
  const out: WorkedPoint[] = [];
  for (const y of year) {
    const end = y.f.period_end as string;
    if (filed.has(end) || y.f.period_start === null) continue;
    const nine = nines.get(`${y.f.period_start}|${monthsBefore(end, 3)}`);
    if (!nine) continue;
    out.push({ f: y.f, v: y.v - (nine[col] as number), nine });
  }
  return out;
}
export type NewestColumn = { months: number | null; head: Filing; cells: Record<FigureKey, FiledPoint | null> };
/** The newest period end a company filed, one column for each length of period its filing reports to that day (a
 *  10-Q for September: the 3 months and the 9 months), shortest first. In a column, a sum is the figure filed for
 *  exactly that period; debt and shares are the figures at the period's end. An amended filing's figure stands in
 *  place of the first filing's where it holds one. No period filed: no column. */
export function newestOf(fs: Filing[]): NewestColumn[] {
  const end = fs[0]?.period_end ?? null;
  if (end === null) return [];
  const rows = fs.filter((f) => f.period_end === end);
  const lengths = [...new Set(rows.map((f) => f.months).filter((m): m is number => m !== null))].sort((a, b) => a - b);
  const pick = (among: Filing[], col: FigureKey): FiledPoint | null => {
    let best: FiledPoint | null = null;
    for (const f of among) { const v = f[col]; if (v !== null && later(f, best?.f)) best = { f, v }; }
    return best;
  };
  const column = (months: number | null): NewestColumn => {
    const own = rows.filter((f) => f.months === months);
    let head = own[0] ?? rows[0];
    for (const f of own) if (later(f, head)) head = f;
    return { months, head, cells: Object.fromEntries(FIGURES.map((col) => [col, pick(AT_PERIOD_END.includes(col) ? rows : own, col)])) as Record<FigureKey, FiledPoint | null> };
  };
  return lengths.length ? lengths.map(column) : [column(null)];
}
/** Only an address of the SEC's own site is made a link. */
export const secUrl = (url: string | null | undefined): string | null => (url && /^https:\/\/www\.sec\.gov\//.test(url) ? url : null);

// ---- Numbers as the page writes them ------------------------------------------------------------------------------

const fixed = (v: number, d: number) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
/** A level or a price: two decimals. */
export const levelWords = (v: number) => fixed(v, 2);
/** A statement line in millions, whole; shares in millions with one decimal. The exact figure is in the hover. */
export const millions = (v: number, shares = false) => fixed(v / 1e6, shares ? 1 : 0);
export const exact = (v: number) => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
export const signedPct = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${fixed(Math.abs(v), 2)}%`;
export const signedLevel = (v: number) => `${v > 0 ? "+" : v < 0 ? "-" : ""}${fixed(Math.abs(v), 2)}`;

// ---- The table of every company -------------------------------------------------------------------------------------

/** `filed` (session 10414): by the end of the newest period filed, then the day it was filed; a company with none last. */
export const SORTS = ["name", "ticker", "segment", "exchange", "first", "last", "filed"] as const;
export type Sort = (typeof SORTS)[number];
/** `filed` (session 10408): only the companies whose filed figures are shown. */
export type Filter = { seg: string | null; q: string; shown: boolean; filed?: boolean; sort: Sort | null; desc: boolean };
/** The companies a filter lets through, in the list's own order unless a column is chosen to sort by. A company in two
 *  segments is one row. */
export function companiesOf(list: EqList | null, f: Filter): EqCompany[] {
  if (!list || list.example === true) return [];
  const q = f.q.trim().toLowerCase();
  let rows = list.companies.filter((c) => (!f.seg || c.segments.includes(f.seg)) && (!f.shown || c.price_status === "shown") && (!f.filed || c.fundamentals_status === "shown")
    && (!q || `${c.name ?? ""} ${c.ticker} ${c.sic_label ?? ""} ${c.cik ?? ""}`.toLowerCase().includes(q)));
  if (f.sort) {
    const key = (c: EqCompany): string => (f.sort === "name" ? c.name ?? c.ticker : f.sort === "ticker" ? c.ticker : f.sort === "segment" ? segmentLabel(list, c.segments[0] ?? "") : f.sort === "exchange" ? c.exchange ?? "" : f.sort === "first" ? c.first ?? "" : f.sort === "filed" ? `${c.newest_filed?.period_end ?? ""} ${c.newest_filed?.filed ?? ""}` : c.last ?? "");
    // session 10414: by the newest period filed, a company with none is last in either direction, in the list's order
    const last = f.sort === "filed" ? rows.filter((c) => !c.newest_filed) : [];
    if (f.sort === "filed") rows = rows.filter((c) => c.newest_filed);
    rows = [...rows].sort((a, b) => key(a).localeCompare(key(b), "en", { sensitivity: "base" }) || a.ticker.localeCompare(b.ticker));
    if (f.desc) rows.reverse();
    rows = [...rows, ...last];
  }
  return rows;
}

// ---- The address ---------------------------------------------------------------------------------------------------

/** `fig` and `per` (session 10408): the filed figure drawn over the periods filed, and the length of its periods. */
export type Query = { a: string | null; b: string | null; p: string | null; win: string; fig: FigureKey; per: PeriodKey } & Filter;
type Raw = Record<string, string | string[] | undefined>;
const one = (q: Raw, k: string) => (typeof q[k] === "string" ? (q[k] as string) : undefined);
export const NONE = "none";
export const WINDOW_DEFAULT = "1y";
/** What the address asks for, held to what the files offer. A opens on the first thing the list can draw (its first
 *  segment's line); B and the price laid over are none unless named. */
export function queryOf(q: Raw, list: EqList | null, prices: EqPrices | null): Query {
  const picks = picksOf(list);
  const has = (id: string | undefined) => !!id && picks.some((p) => p.id === id);
  const a = has(one(q, "a")) ? (one(q, "a") as string) : picks[0]?.id ?? null;
  const bRaw = one(q, "b");
  const b = has(bRaw) && bRaw !== a ? (bRaw as string) : null;
  const pRaw = one(q, "p");
  const p = pRaw && prices && prices.example !== true && prices.series.some((x) => x.id === pRaw) ? pRaw : null;
  const win = WINDOW_KEYS.includes(one(q, "win") ?? "") ? (one(q, "win") as string) : WINDOW_DEFAULT;
  const segRaw = one(q, "seg");
  const seg = segRaw && list?.segments.some((s) => s.id === segRaw) ? segRaw : null;
  const sortRaw = one(q, "sort");
  const sort = (SORTS as readonly string[]).includes(sortRaw ?? "") ? (sortRaw as Sort) : null;
  const figRaw = one(q, "fig"), perRaw = one(q, "per");
  const fig = (FIGURES as readonly string[]).includes(figRaw ?? "") ? (figRaw as FigureKey) : FIGURE_DEFAULT;
  const per = (PERIOD_KEYS as readonly string[]).includes(perRaw ?? "") ? (perRaw as PeriodKey) : PERIOD_DEFAULT;
  return { a, b, p, win, fig, per, seg, q: (one(q, "q") ?? "").slice(0, 60), shown: one(q, "shown") === "1", filed: one(q, "filed") === "1", sort, desc: one(q, "dir") === "desc" };
}
/** The page's address for a state, leaving out what is the default. `first` is the id A opens on. */
export function hrefOf(q: Query, patch: Partial<Query> = {}, first: string | null = null, hash = ""): string {
  const x = { ...q, ...patch };
  const p = new URLSearchParams();
  if (x.a && x.a !== first) p.set("a", x.a);
  if (x.b) p.set("b", x.b);
  if (x.p) p.set("p", x.p);
  if (x.win !== WINDOW_DEFAULT) p.set("win", x.win);
  if (x.fig && x.fig !== FIGURE_DEFAULT) p.set("fig", x.fig);
  if (x.per && x.per !== PERIOD_DEFAULT) p.set("per", x.per);
  if (x.seg) p.set("seg", x.seg);
  if (x.q) p.set("q", x.q);
  if (x.shown) p.set("shown", "1");
  if (x.filed) p.set("filed", "1");
  if (x.sort) p.set("sort", x.sort);
  if (x.sort && x.desc) p.set("dir", "desc");
  const s = p.toString();
  return `/equities${s ? `?${s}` : ""}${hash}`;
}

// ---- Downloads -----------------------------------------------------------------------------------------------------

const cell = (c: Cell | undefined) => (c === null || c === undefined ? "" : /[",\n]/.test(String(c)) ? `"${String(c).replace(/"/g, '""')}"` : String(c));
const lines = (head: string[], rows: (Cell | undefined)[][]) => [head, ...rows].map((r) => r.map(cell).join(",")).join("\n") + "\n";

/** A series' daily rows as a CSV, with the provenance first: the file's own columns, a held column empty and named in
 *  the header with its reason. A series that is not shown has its header and no row. */
export function seriesCsv(s: EqSeries, url: string): string {
  const shown = isShown(s);
  const head = [
    `# Energy Research Warehouse (ERW): ${s.kind === "company" ? `${s.ticker ?? s.id}, ${s.name ?? ""}` : s.name ?? s.id}, day by day, as /equities draws it (site/lib/equities.ts seriesCsv)`,
    `# Built: ${s.built} (site/data/equities/series/${s.id}.json, written by warehouse/derived/equity_pages.py from the ERW's tables); method: ${s.method ?? "docs/methods/equities.md"}`,
    `# Source: ${s.source ?? "not named in the file"}`,
    `# License: ${s.license ?? "not said"}. Status: ${s.status}${s.why ? ` (${s.why})` : ""}`,
    `# Units: ${Object.entries(s.units ?? {}).filter(([k]) => s.daily_columns.includes(k)).map(([k, v]) => `${k} in ${v}`).join("; ") || "not said"}`,
    ...Object.entries(s.held ?? {}).filter(([k]) => s.daily_columns.includes(k)).map(([k, v]) => `# Held: ${k} is empty in every row: ${v}`),
    ...(shown ? [] : [`# No row: the series is not shown. ${blankWhy(s.status, s.why, s.example === true)}`]),
    `# From: ${url}`,
  ];
  return `${head.join("\n")}\n${lines(s.daily_columns, shown ? s.daily : [])}`;
}
/** A company's filed periods as a CSV, in the file's own columns, with the provenance first. */
export function filedCsv(s: EqSeries, url: string): string {
  const cols = s.quarterly_columns ?? [];
  const head = [
    `# Energy Research Warehouse (ERW): ${s.ticker ?? s.id}, ${s.name ?? ""}: the figures it filed, period by period, as /equities draws them (site/lib/equities.ts filedCsv)`,
    `# Built: ${s.built} (site/data/equities/series/${s.id}.json); method: ${s.method ?? "docs/methods/equities.md"}`,
    "# Source: the company's own filings with the SEC (EDGAR, a US government source); each row's url is the filing's address and accession its number",
    "# months: 3, 6, 9 or 12 as the filing reports the period (a 10-Q's cash flow is often year to date). A value not filed for that exact period is empty",
    `# Units: ${["revenue", "net_income", "capex", "debt", "shares_outstanding"].map((k) => `${k} in ${s.units?.[k] ?? (k === "shares_outstanding" ? "shares" : "USD")}`).join("; ")}`,
    ...Object.entries(s.concepts ?? {}).filter(([, v]) => !!v).map(([k, v]) => `# Concept: ${k} is ${v}`),
    `# From: ${url}`,
  ];
  const rows = s.example === true ? [] : (s.quarterly ?? []).filter((r) => r[cols.indexOf("period_end")] !== null);
  return `${head.join("\n")}\n${lines(cols, rows)}`;
}
/** Session 10414: the newest filed period's columns of the list's CSV: the period's end, its form, the day filed and
 *  the filing's address, then each sum with the months it covers, and debt and shares at the period's end. In USD and
 *  in shares, as filed (the page draws millions). Empty where the company filed none, or the list is an older one. */
export const LIST_FILED_FIGURES = ["newest_revenue", "newest_revenue_months", "newest_net_income", "newest_net_income_months", "newest_capex", "newest_capex_months", "newest_debt", "newest_shares_outstanding"];
export const LIST_HEAD = ["ticker", "name", "cik", "exchange", "sic", "sic_label", "segments", "price_status", "price_why", "fundamentals_status", "fundamentals_why", "first_day", "last_day",
  "newest_period_end", "newest_form", "newest_filed_day", "newest_filing", ...LIST_FILED_FIGURES];
/** The list of companies as a CSV: every company the list holds, whatever the page's filter, with the provenance first. */
export function listCsv(list: EqList, url: string): string {
  const head = [
    "# Energy Research Warehouse (ERW): the listed energy companies by segment, as /equities lists them (site/lib/equities.ts listCsv)",
    `# Built: ${list.built} (site/data/equities/index.json, written by warehouse/derived/equity_pages.py from ${(list.tables ?? []).join(", ") || "the ERW's tables"}); method: ${list.method ?? "docs/methods/equities.md"}`,
    `# License of the list: ${list.license ?? "not said"}. first_day and last_day are the first and last trading day of the prices shown; empty where the price is held`,
    "# newest_*: the newest period the company filed with the SEC (a 10-Q or a 10-K): its end, form, the day filed and the filing's address; revenue, net income and capital spending in USD as filed, each with the months its period covers; debt in USD and shares outstanding at the period's end. Empty where the company filed none",
    ...(list.segments ?? []).map((s) => `# Segment ${s.id}: ${s.label}${s.rule ? `: ${s.rule}` : ""}`),
    `# From: ${url}`,
  ];
  const rows = list.example === true ? [] : list.companies.map((c) => [c.ticker, c.name, c.cik, c.exchange, c.sic, c.sic_label, c.segments.join(" "), c.price_status, c.price_why, c.fundamentals_status, c.fundamentals_why, c.first, c.last,
    c.newest_filed?.period_end, c.newest_filed?.form, c.newest_filed?.filed, c.newest_filed?.url, c.newest_filed?.revenue?.v, c.newest_filed?.revenue?.months, c.newest_filed?.net_income?.v, c.newest_filed?.net_income?.months,
    c.newest_filed?.capex?.v, c.newest_filed?.capex?.months, c.newest_filed?.debt, c.newest_filed?.shares_outstanding]);
  return `${head.join("\n")}\n${lines(LIST_HEAD, rows)}`;
}
