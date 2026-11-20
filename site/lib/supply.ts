// Energy Research Warehouse (ERW) site, session 134: Supply and trade (/supply).
//
// The question the page answers: is the market tighter or looser than last week, last year and normal for the season.
// Every figure is in the site's own file (data/supply.json, written by warehouse/derived/supply_page.py from tables in
// the warehouse); the functions here only choose and write them. A figure that is not held is null and the page shows
// a short placeholder. Method, sources and gaps: docs/methods/supply_and_trade.md.

// Session 7541: "held" is a row of a grid held for a license on the day (holdRows below); its figures never reach the page.
export type Status = "ok" | "paused" | "licensed" | "not_held" | "working" | "held";
export type Row = {
  id: string; group: string; label: string; at: string; unit: string; freq: "W" | "M" | ""; sense: -1 | 0 | 1; status: Status; note?: string; source?: number;
  last?: { t: string; v: number };
  prev?: { t: string; v: number; ch: number } | null;
  year?: { t: string; v: number; ch: number; pct: number | null } | null;
  avg5?: { v: number; lo: number; hi: number; ch: number; pct: number | null; outside: boolean } | null;
  change?: { v: number; avg5: number | null; lo: number | null; hi: number | null; surprise: number | null; outside: boolean } | null;
  spark?: { t: string[]; v: number[] };
  season?: { t: string[]; cur: (number | null)[]; last: (number | null)[]; avg: (number | null)[]; lo: (number | null)[]; hi: (number | null)[] };
  long?: number; short?: number; open_interest?: number; net_share_pct?: number | null; three_year?: { lo: number; hi: number; pos: number | null; n: number };
};
export type Group = { id: string; title: string; band?: boolean };
export type Release = {
  id: string; name: string; publisher: string; page: string; covers: string; rule: string; read: string; next: string; moved: string | null;
  weekday?: number; time?: string; exceptions?: { date: string; time: string; holiday: string }[];
};
export type SupplyFile = {
  built: string; years: number; near_days: number; heat_rate: Record<string, number>; heat_content: Record<string, { mmbtu_per_unit: number; unit: string }>;
  groups: Group[]; sources: string[]; rows: Row[]; calendar: { retrieved_at: string | null; timezone?: string; reports: Release[] };
};

export const PLACEHOLDER: Record<Exclude<Status, "ok">, string> = {
  paused: "paused while terms are reviewed", licensed: "licensed source needed", not_held: "not held yet", working: "working on it",
  held: "license needed",
};

/** Session 7541 (the read of /supply, docs/reviews/supply-read-2026-11-16.md, row 1): the day-ahead cleared rows are
 *  each grid operator's own figures. A grid held for a license on the day (lib/license.ts, licenseHeldGrids: the
 *  operators whose own page asks for permission) has its row drawn "license needed", as the price board draws a held
 *  grid's rows (lib/board.ts, holdRows): the row keeps its name and loses every figure, on the server, before the page
 *  draws, so none reaches the browser. The hold itself is lib/license.ts's; this only applies it. */
export const CLEARED_GRID: Record<string, string> = {
  "cleared-ercot": "ercot", "cleared-caiso": "caiso", "cleared-nyiso": "nyiso", "cleared-iso-ne": "isone",
  "cleared-spp": "spp", "cleared-spp-west": "spp", "cleared-miso": "miso", "cleared-pjm": "pjm",
};
export function holdRows(file: SupplyFile, heldGrids: string[], title: (grid: string) => string): SupplyFile {
  const held = new Set(heldGrids.map((g) => g.toLowerCase()));
  return {
    ...file,
    rows: file.rows.map((r) => {
      const g = CLEARED_GRID[r.id];
      if (!g || !held.has(g) || r.status !== "ok") return r;
      return { id: r.id, group: r.group, label: r.label, at: r.at, unit: r.unit, freq: "", sense: 0, status: "held", note: title(g) };
    }),
  };
}

/** Session 7541 (row 7): the units in words, for the hover on each unit the page writes short. */
export const UNIT_LONG: Record<string, string> = {
  "kb/d": "thousand barrels a day", "Bcf/d": "billion cubic feet a day", Bcf: "billion cubic feet", "million bbl": "million barrels",
  "k short tons/d": "thousand short tons a day", "MWh/d": "megawatt-hours a day", contracts: "futures contracts", "%": "percent",
};
export const unitTitle = (unit: string) => UNIT_LONG[unit] ?? unit;

/** Session 7541 (row 12): the states the builder writes short in a place ("Sabine Pass, LA, monthly"), in full, as the
 *  price board names the same terminals ("Sabine Pass, Louisiana"). Only the words change. */
export const STATE_WORDS: Record<string, string> = { LA: "Louisiana", TX: "Texas", MD: "Maryland", GA: "Georgia" };
export const placeWords = (at: string) => at.replace(/, (LA|TX|MD|GA)(?=,|$)/g, (_m, s: string) => `, ${STATE_WORDS[s]}`);
export const withPlaceWords = (file: SupplyFile): SupplyFile => ({ ...file, rows: file.rows.map((r) => ({ ...r, at: placeWords(r.at) })) });

const MONTH_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
/** Session 7541 (rows 11 and 14): the hover of a row's latest value, where the figure needs a word a reader would ask
 *  for. A monthly gas trade figure (the month's volume over its days, in Bcf a day) is also written as the month's
 *  volume, the unit the price board uses for the same month. A net import below zero is a net export. */
export function latestTitle(r: Row): string | undefined {
  if (!r.last) return undefined;
  const v = r.last.v;
  if (r.group === "gastrade" && r.freq === "M" && r.unit === "Bcf/d") {
    const [y, m] = r.last.t.slice(0, 10).split("-").map(Number);
    const days = new Date(Date.UTC(y, m, 0)).getUTCDate();
    const bcf = (v * days).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const mmcf = (Math.round(v * days * 10) * 100).toLocaleString("en-US");
    return `${fmt(v, r.unit)} Bcf a day over the ${days} days of ${MONTH_LONG[m - 1]} ${y}: ${bcf} Bcf in the month, about ${mmcf} MMcf (million cubic feet), the unit the price board writes the month's volume in`;
  }
  if (/net imports/i.test(r.label) && v < 0) {
    return `Below zero: the United States exported ${fmt(-v, r.unit)} ${r.unit} more than it imported (net exports)`;
  }
  return undefined;
}

/** Session 7541 (row 6): fuel burned for power, a row whose newest whole week is older than another grid's of the same
 *  fuel. "The seven grids together" is the sum only when all seven hold the week, so it stops at the oldest grid's
 *  newest week; the hover names the grids that hold the newer week and those that do not. Null when the row is current. */
export function burnWeekWords(file: SupplyFile, r: Row): string | null {
  const m = /^burn-([a-z]+)-(.+)$/.exec(r.id);
  if (!m || !r.last) return null;
  const fuel = m[2];
  const grids = file.rows.filter((x) => x.group === "burn" && x.status === "ok" && x.last && x.id !== `burn-all-${fuel}` && x.id.endsWith(`-${fuel}`));
  if (!grids.length) return null;
  const newest = grids.map((x) => x.last!.t).sort().at(-1)!;
  if (r.last.t >= newest) return null;
  const at = (x: Row) => x.at;
  const ahead = grids.filter((x) => x.last!.t >= newest).map(at);
  const behind = grids.filter((x) => x.last!.t < newest).map(at);
  const week = dateWords(newest);
  if (m[1] === "all") {
    return `The newest week all seven grids hold whole. The week ending ${week} is held for ${ahead.join(", ")}; not yet for ${behind.join(", ")}, whose hours of that week are not all held yet in the hourly generation by fuel the rows are built from`;
  }
  return `This grid's newest whole week. The week ending ${week} is held for ${ahead.join(", ")}; this grid's hours of that week are not all held yet in the hourly generation by fuel the rows are built from`;
}
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
/** "25 Sep 2026" from a day; a monthly value is written "Jul 2026". */
export function dateWords(t: string, freq = "W"): string {
  const [y, m, d] = t.slice(0, 10).split("-").map(Number);
  return freq === "M" ? `${MON[m - 1]} ${y}` : `${d} ${MON[m - 1]} ${y}`;
}
export const shortDate = (t: string, freq = "W") => (freq === "M" ? MON[Number(t.slice(5, 7)) - 1] : `${Number(t.slice(8, 10))} ${MON[Number(t.slice(5, 7)) - 1]}`);
/** Decimals by size: positions and barrels whole, small rates to two places. */
export function places(v: number, unit: string): number {
  if (unit === "contracts") return 0;
  if (unit === "percent" || unit === "%") return 1;
  const a = Math.abs(v);
  return a >= 1000 ? 0 : a >= 100 ? 1 : 2;
}
export const fmt = (v: number, unit: string, ref = v) => v.toLocaleString("en-US", { minimumFractionDigits: places(ref, unit), maximumFractionDigits: places(ref, unit) });
const sign = (v: number, written: string) => (Number(written.replace(/,/g, "")) === 0 ? "" : v > 0 ? "+" : v < 0 ? "−" : "");
/** A difference with its sign; one that is written as zero carries none. */
export const signed = (v: number, unit: string, ref = v) => { const t = fmt(Math.abs(v), unit, ref); return `${sign(v, t)}${t}`; };
export const pct = (v: number) => { const t = Math.abs(v).toFixed(1); return `${sign(v, t)}${t}%`; };
/** The unit as a desk writes it. The file keeps the long words; the page shows these. */
export const UNIT_WORDS: Record<string, string> = { "thousand bbl/d": "kb/d", "kbbl/d": "kb/d", "thousand short tons/d": "k short tons/d", percent: "%", bcf: "Bcf", "bcf/d": "Bcf/d" };
export const withUnitWords = (file: SupplyFile): SupplyFile => ({ ...file, rows: file.rows.map((r) => ({ ...r, unit: UNIT_WORDS[r.unit] ?? r.unit })) });

/** Tighter or looser than the thing compared with, for a series whose direction has a reading: more stocks, production
 *  or imports is looser; more exports or burn is tighter. Null when the series has no reading or the difference is nil. */
export function reading(sense: number, diff: number | null | undefined): "tighter" | "looser" | null {
  if (!sense || diff === null || diff === undefined || diff === 0) return null;
  return diff * sense > 0 ? "looser" : "tighter";
}
/** The rows a group shows. */
export const rowsOf = (file: SupplyFile, group: string) => file.rows.filter((r) => r.group === group);
/** The surprises of the newest reports: the rows whose latest change is outside the five years' changes, largest first
 *  by how far the change stands from the five-year average change, in units of that range. */
export function surprises(file: SupplyFile): Row[] {
  const far = (r: Row) => { const c = r.change!; const span = (c.hi ?? 0) - (c.lo ?? 0); return span > 0 ? Math.abs(c.surprise ?? 0) / span : 0; };
  return file.rows.filter((r) => r.status === "ok" && r.change?.outside && r.change.surprise !== null).sort((a, b) => far(b) - far(a));
}
/** Ruling alternative 2 of /supply (session 7726, branch wip/alt-supply-2; not a default on main): two grids' burn rows
 *  side by side over the weeks both hold (the rows' own weekly series, `spark`), for each fuel both hold: the newest common
 *  week, each grid's value then and A less B, and the means over the common weeks. On main the table sets each grid's own
 *  newest week in one column. */
export type BurnPair = { fuel: string; unit: string; weeks: number; week: string; a: number; b: number; meanA: number; meanB: number };
export function burnPair(file: SupplyFile, a: string, b: string): BurnPair[] {
  const out: BurnPair[] = [];
  for (const fuel of ["natural-gas", "coal", "oil"]) {
    const ra = file.rows.find((r) => r.id === `burn-${a}-${fuel}`), rb = file.rows.find((r) => r.id === `burn-${b}-${fuel}`);
    if (!ra?.spark || !rb?.spark || ra.status !== "ok" || rb.status !== "ok") continue;
    const sa = new Map(ra.spark.t.map((t, i) => [t, ra.spark!.v[i]])), sb = new Map(rb.spark.t.map((t, i) => [t, rb.spark!.v[i]]));
    const weeks = [...sa.keys()].filter((t) => sb.has(t) && sa.get(t) !== null && sb.get(t) !== null).sort();
    if (!weeks.length) continue;
    const w = weeks[weeks.length - 1], mean = (m: Map<string, number>) => weeks.reduce((x, t) => x + (m.get(t) as number), 0) / weeks.length;
    out.push({ fuel, unit: ra.unit, weeks: weeks.length, week: w, a: sa.get(w) as number, b: sb.get(w) as number, meanA: mean(sa), meanB: mean(sb) });
  }
  return out;
}
/** The headline answers: for the stock series a desk reads first, tighter or looser against each of the three. */
export const HEADLINE = ["eia-nw2-epg0-swo-r48-bcf", "eia-wcestus1", "eia-w-epc0-sax-ycuok-mbbl", "eia-wgtstus1", "eia-wdistus1"];

export type Choice = { groups: string[]; s: string | null };
type Query = Record<string, string | string[] | undefined>;
const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
/** What an address asks for: the groups shown (all when none is named) and the series whose seasonal chart is open. */
export function choiceOf(q: Query, file: SupplyFile): Choice {
  const ids = file.groups.map((g) => g.id);
  const groups = [...new Set((one(q.g) ?? "").split(",").filter((g) => ids.includes(g)))];
  const s = one(q.s);
  return { groups, s: s && file.rows.some((r) => r.id === s && r.status === "ok") ? s : null };
}
export function hrefOf(c: Choice, patch: Partial<Choice> = {}): string {
  const n = { ...c, ...patch };
  const q = new URLSearchParams();
  if (n.groups.length) q.set("g", n.groups.join(","));
  if (n.s) q.set("s", n.s);
  const s = q.toString();
  return s ? `/supply?${s}` : "/supply";
}
/** A group added to or taken from the selection; an empty selection is every group. */
export const toggled = (groups: string[], id: string) => (groups.includes(id) ? groups.filter((g) => g !== id) : [...groups, id]);
/** "Wed 7 Oct, 10:30 Eastern" from a release's next date. */
export function releaseWords(next: string): string {
  const d = new Date(`${next}:00Z`);
  return `${["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][d.getUTCDay()]} ${d.getUTCDate()} ${MON[d.getUTCMonth()]}, ${next.slice(11, 16)} Eastern`;
}
/** The wall clock in New York as "YYYY-MM-DDTHH:MM": the reports are released on Eastern time. */
export function easternNow(now: Date): string {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(now).map((x) => [x.type, x.value]));
  return `${p.year}-${p.month}-${p.day}T${p.hour}:${p.minute}`;
}
/** A report's next release as of an Eastern wall clock: this week's standing day, or the date its publisher moved this
 *  week's to; when that has passed, the same for the week after. The file's own "next" (worked out when the file was
 *  built, by the same rule: warehouse/derived/supply_page.py) stands in when the file carries no rule. */
export function nextRelease(r: Release, eastern: string): { next: string; moved: string | null } {
  if (r.weekday === undefined || !r.time) return { next: r.next, moved: r.moved };
  const day = (t: string) => new Date(`${t.slice(0, 10)}T00:00:00Z`);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  const plus = (d: Date, n: number) => new Date(d.getTime() + n * 86400000);
  const today = day(eastern);
  let monday = plus(today, -((today.getUTCDay() + 6) % 7));
  for (let i = 0; i < 60; i += 1) {
    const from = iso(monday), to = iso(plus(monday, 6));
    const alt = (r.exceptions ?? []).find((e) => e.date >= from && e.date <= to);
    const next = alt ? `${alt.date}T${alt.time}` : `${iso(plus(monday, r.weekday))}T${r.time}`;
    if (next > eastern) return { next, moved: alt ? `moved from the standing day for ${alt.holiday}` : null };
    monday = plus(monday, 7);
  }
  return { next: r.next, moved: r.moved };
}
