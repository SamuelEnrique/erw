// Energy Research Warehouse (ERW) site, session 163: "How long a large load waits", in the section "How soon" of "What a
// datacenter pays" (/cost-of-power, in review). Everything the block shows is decided here, from one site file,
// data/datacenter/how_soon.json (warehouse/derived/how_soon.py), which holds aggregates only: for each grid measured,
// the count of requests behind each stage, the bounds of the median, the range, the requests still waiting as a lower
// bound; and the entity's own stated figures with their documents. No request, name, queue position or megawatt is in
// it, and the page reads no table. This file imports nothing, so Node runs it as it is (scripts/test-howsoon.mjs).
// The summary sentence is written here, by code, from the file's numbers: no model writes a word of the block.

export type Stated = {
  stated_by: string; figure: string; basis: string; statistic?: string; covers: string; document: string; document_type?: string;
  date: string; date_basis?: string; page?: string; url: string; mark?: string; note?: string;
};
export type Measured = { n: number; form: "median" | "bounds" | "too few" | "none"; median_at_least?: number; median_at_most?: number; least?: number; most?: number; words?: string };
export type Waiting = { n: number; lower_bound: true; form: "range" | "too few" | "none"; least?: number; most?: number; words?: string };
export type Stage = {
  interval: string; label: string; phrase: string; requests: number; measured: Measured; waiting: Waiting;
  two_copies_only: { n: number; lower_bound: true }; ended_before_first_copy: { n: number }; stated: Stated[];
};
export type Copies = { n: number | null; first: string; last: string; requests_seen: number | null; requests_followed: number; what: string; read_from: string; retrieved?: string };
export type Reports = { n: number | null; first: string | null; last: string | null; requests_named: number | null; what: string; why: string; read_from: string };
export type WaitGrid = { state: string; entity?: string; place?: string; copies?: Copies; reports?: Reports; stages: Stage[]; stated: Stated[] };
export type HowSoonFile = {
  built_at_utc: string; unit: string; rule: { min_for_median: number; min_for_bounds: number; too_few: string };
  paused: string[]; grids: Record<string, WaitGrid>;
  /** the stage that leads the summary sentence, and the stages preferred for the stated figure beside a measured one */
  summary?: { service?: string; lead?: string[] };
  tables?: Record<string, { license?: string; rows?: number; retrieved?: string }>;
  left_out?: { entities?: number; interval_rows?: number; intervals?: string[] };
};

export const WAIT_GRIDS = ["ercot", "caiso", "nyiso", "isone", "spp", "miso", "pjm"] as const;
export const NOT_YET = "not measured yet";
export const NOT_HERE = "not measured here";
export const NOT_HELD = "not held yet";
export const NOT_HELD_WHY = "The file of measured waits is not in this page's files yet.";
export const PAUSED_WORDS = "paused while terms are reviewed";
export const PAUSED_WHY = "MISO's terms forbid automated access to its site; its pulls are paused. Nothing is measured or shown for MISO until a person lifts the pause.";
export const LOWER = "lower bound";
export const NONE_MEASURED = "none yet";
export const NONE_STATED = "none held";
/** The stage whose measured figure leads the summary sentence. */
export const SERVICE = "request to energized";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const isObj = (v: unknown): v is Record<string, unknown> => !!v && typeof v === "object" && !Array.isArray(v);

/** The file as read, or null when it is not a file of measured waits. Nothing is repaired. */
export function fileOf(v: unknown): HowSoonFile | null {
  if (!isObj(v) || !isObj(v.grids) || !isObj(v.rule) || typeof v.built_at_utc !== "string") return null;
  for (const g of Object.values(v.grids)) {
    if (!isObj(g) || typeof g.state !== "string" || !Array.isArray(g.stages) || !Array.isArray(g.stated)) return null;
    for (const st of g.stages) if (!isObj(st) || !isObj(st.measured) || !isObj(st.waiting) || !Array.isArray(st.stated) || typeof st.requests !== "number") return null;
  }
  return v as unknown as HowSoonFile;
}

/** "4 September 2014" from "2014-09-04" (or a longer stamp that begins so); null when it is not a day. */
export function dayWords(iso: unknown): string | null {
  const m = /^(\d{4})-(\d\d)-(\d\d)/.exec(typeof iso === "string" ? iso : "");
  if (!m) return null;
  const mo = Number(m[2]), d = Number(m[3]);
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
  return `${d} ${MONTHS[mo - 1]} ${m[1]}`;
}
/** A count or a number of days as the page writes it: 1,028; 760.5. Never rounded. */
export const num = (v: number): string => v.toLocaleString("en-US", { maximumFractionDigits: 2 });
const many = (n: number, one: string, more: string): string => `${num(n)} ${n === 1 ? one : more}`;

/** The grid whose waits an address shows: the one it names, when it is one of the seven (MISO and PJM too, which the
 * rest of the page does not open); else the grid the page opened. The same rule as the block "Rules in motion". */
export function waitsGrid(asked: string | undefined, opened: string): string {
  const a = (asked ?? "").trim().toLowerCase();
  return (WAIT_GRIDS as readonly string[]).includes(a) ? a : opened;
}

export type WaitBlock = { state: "measured" | "not measured here" | "not measured yet" | "paused" | "not held"; grid: string; entry: WaitGrid | null };
/** What the block is for a grid. MISO is paused whatever the file holds; a grid the file does not name is not measured
 * yet; a grid is measured only where the file says so and holds a stage. */
export function blockOf(file: HowSoonFile | null, grid: string): WaitBlock {
  if (grid === "miso" || (file?.paused ?? []).includes(grid)) return { state: "paused", grid, entry: null };
  if (!file) return { state: "not held", grid, entry: null };
  const entry = file.grids[grid] ?? null;
  if (!entry) return { state: "not measured yet", grid, entry: null };
  if (entry.state === "measured" && entry.stages.length && entry.copies) return { state: "measured", grid, entry };
  if (entry.state === "not measured here") return { state: "not measured here", grid, entry };
  return { state: "not measured yet", grid, entry };
}

/** Every stated figure of a grid: those beside a stage, then the rest. */
export function statedOf(g: WaitGrid | null): Stated[] {
  return g ? [...g.stages.flatMap((s) => s.stated), ...g.stated] : [];
}

const took = (m: Measured): string =>
  m.form === "median" ? `a median of at least ${num(m.median_at_least!)} and at most ${num(m.median_at_most!)} days` : `between ${num(m.least!)} and ${num(m.most!)} days`;

/** A stage's measured figure, as the face writes it. */
export function measuredWords(st: Stage): string {
  const m = st.measured;
  if (m.form === "median") return `median at least ${num(m.median_at_least!)}, at most ${num(m.median_at_most!)} days`;
  if (m.form === "bounds") return `between ${num(m.least!)} and ${num(m.most!)} days`;
  if (m.form === "too few") return m.words ?? "too few to show";
  return NONE_MEASURED;
}
/** The requests still waiting, as the face writes them: always beside the mark "lower bound". */
export function waitingWords(st: Stage): string {
  const w = st.waiting;
  if (w.form === "range") return `at least ${num(w.least!)} to ${num(w.most!)} days so far`;
  if (w.form === "too few") return w.words ?? "too few to show";
  return "none";
}
/** Where a grid's figures were read: the copies and their days. */
export function sourceWords(c: Copies): string {
  const a = dayWords(c.first), b = dayWords(c.last);
  return `Source: ${c.n === null ? "the" : num(c.n)} dated copies of ${c.what}${a && b ? `, ${a} to ${b}` : ""}, read from ${c.read_from}${c.requests_seen !== null ? `; ${many(c.requests_seen, "load request", "load requests")} seen, ${num(c.requests_followed)} followed from copy to copy` : ""}.`;
}
/** The hover of a measured figure: the count behind it, the bounds, and the copies it was read from. */
export function measuredTip(st: Stage, c: Copies, file: HowSoonFile): string {
  const m = st.measured, parts: string[] = [];
  parts.push(`${many(m.n, "request", "requests")} of the ${num(st.requests)} followed through this stage ${m.n === 1 ? "is" : "are"} measured: the stage's end lies between two dated copies that hold the request.`);
  if (m.form === "median") parts.push(`The median of their least possible durations is ${num(m.median_at_least!)} days and of their greatest ${num(m.median_at_most!)}; all lie within ${num(m.least!)} to ${num(m.most!)} days.`);
  if (m.form === "bounds") parts.push(`Fewer than ${file.rule.min_for_median}, so no median: the least any of them can have taken is ${num(m.least!)} days and the most ${num(m.most!)}.`);
  if (m.form === "too few") parts.push(`Fewer than ${file.rule.min_for_bounds}: a figure would be one request's own, and is not shown.`);
  if (m.form === "none") parts.push("No request has been seen to finish this stage between two copies.");
  parts.push("A duration is a range between two copies, never a midpoint.");
  if (st.two_copies_only.n) parts.push(`${many(st.two_copies_only.n, "request was", "requests were")} seen in two copies only.`);
  if (st.ended_before_first_copy.n) parts.push(`${many(st.ended_before_first_copy.n, "request", "requests")} had finished the stage before the first copy that holds ${st.ended_before_first_copy.n === 1 ? "it" : "them"}, so only the most ${st.ended_before_first_copy.n === 1 ? "it" : "they"} can have taken is known.`);
  parts.push(sourceWords(c));
  return parts.join(" ");
}
/** The hover of the requests still waiting: why the figure is a lower bound. */
export function waitingTip(st: Stage, c: Copies, file: HowSoonFile): string {
  const w = st.waiting;
  if (!w.n) return `No request followed through this stage is still waiting in the last copy that holds it. ${sourceWords(c)}`;
  return `${many(w.n, "request has", "requests have")} not reached the end of this stage in the last copy that holds ${w.n === 1 ? "it" : "them"}. ${w.form === "range" ? "Each has waited at least this long and is still waiting" : `Fewer than ${file.rule.min_for_bounds}: a figure would be one request's own, and is not shown`}: a lower bound, not a wait. Lower bounds are never averaged and never mixed with the measured figures. ${sourceWords(c)}`;
}
/** Whose figure a stated one is, in a few words for the face. */
export function basisWords(s: Stated): string {
  if (s.basis === "measured") return `measured by ${s.stated_by} itself${s.statistic ? `, ${s.statistic}` : ""}`;
  if (s.basis === "expected") return `expected by ${s.stated_by}`;
  return `stated by ${s.stated_by}`;
}
/** The hover of a stated figure: who stated it, what it covers, the document, its day and page, and what differs. */
export function statedTip(s: Stated): string {
  const d = dayWords(s.date), parts: string[] = [];
  parts.push(`${s.figure}: ${basisWords(s)}. Covers: ${s.covers}.`);
  if (s.basis === "measured") parts.push("The entity's own measurement, not one made here.");
  if (s.note) parts.push(s.note);
  parts.push(`Document: ${s.document}${d ? `, ${s.date_basis && s.date_basis !== "document" ? `read ${d}` : d}` : ""}${s.page ? `, page ${s.page}` : ""}.`);
  return parts.join(" ");
}
/** Why a grid's reports gave no measured wait. */
export function notHereWhy(g: WaitGrid): string {
  const r = g.reports;
  if (!r) return "No request of this grid could be followed from copy to copy.";
  const a = dayWords(r.first), b = dayWords(r.last);
  return `${r.n === null ? "The" : num(r.n)} ${r.what} of ${g.entity ?? "the operator"} were read${a && b ? ` (${a} to ${b})` : ""}${r.requests_named !== null ? `; ${num(r.requests_named)} name a request` : ""}. ${r.why}`;
}
export const notYetWhy = (name: string): string =>
  `No dated copies of a public list of large load requests have been read for ${name}, so no wait is measured. A search on 7 October 2026 found no public dataset of the time from a large load's request to its energization, for any grid. The interconnection queue in the table above is for generators, not loads.`;

/** The one summary sentence, written from the file's numbers. Every number in it is a number of the file. */
export function sentenceOf(file: HowSoonFile | null, grid: string, name: string): string {
  const b = blockOf(file, grid), place = b.entry?.place ?? name;
  if (b.state === "paused") return `${place}: ${PAUSED_WORDS}.`;
  if (b.state === "not held") return `${place}: ${NOT_HELD}.`;
  const shown = (st: Stage | undefined): st is Stage => !!st && (st.measured.form === "median" || st.measured.form === "bounds");
  if (b.state === "measured") {
    const g = b.entry!, parts: string[] = [];
    const svc = g.stages.find((s) => s.interval === (file!.summary?.service ?? SERVICE));
    const prefer = file!.summary?.lead ?? [];
    if (shown(svc)) {
      const w = svc.waiting;
      parts.push(`${many(svc.measured.n, "request", "requests")} followed ${svc.phrase} took ${took(svc.measured)}`
        + (w.n ? `, and ${num(w.n)} more ${w.n === 1 ? "is" : "are"} still waiting${w.form === "range" ? `, at least ${num(w.least!)} to ${num(w.most!)} days so far` : ""} (a ${LOWER})` : ""));
    }
    const lead = prefer.map((i) => g.stages.find((s) => s.interval === i)).find((s) => s !== svc && shown(s) && s!.stated.length)
      ?? g.stages.find((s) => s !== svc && shown(s) && s.stated.length) ?? (parts.length ? undefined : g.stages.find((s) => shown(s)));
    if (shown(lead)) {
      const s = lead.stated.find((x) => !x.mark) ?? lead.stated[0];
      parts.push(`${many(lead.measured.n, "request", "requests")} followed ${lead.phrase} took ${took(lead.measured)}${s ? `, where ${s.stated_by} itself states ${s.figure}` : ""}`);
    }
    if (!parts.length) return `${place}: ${many(g.copies!.requests_followed, "request is", "requests are")} followed here and no stage is measured yet.`;
    return `${place}: ${parts.join("; ")}.`;
  }
  const g = b.entry, r = g?.reports;
  let s = b.state === "not measured here"
    ? `${place}: no wait is measured here${r && r.n !== null && r.requests_named !== null ? ` (${many(r.requests_named, "request", "requests")} named in ${num(r.n)} of ${g!.entity ?? "the operator"}'s reports)` : ""}`
    : `${place}: ${NOT_YET}`;
  const own = (g?.stated ?? []).filter((x) => x.basis === "measured");
  if (own.length) {
    const by = [...new Set(own.map((x) => x.stated_by))];
    s += `; measured by the entities themselves: ${by.map((e) => `${e} ${own.filter((x) => x.stated_by === e).map((x) => `${x.figure}${x.statistic ? ` (${x.statistic})` : ""}`).join(" and ")}`).join(", ")}`;
  }
  return `${s}.`;
}
