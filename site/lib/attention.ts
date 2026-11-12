// Session 1880 (the attention faults of 12 November 2026, docs/reviews/attention-faults-2026-11-11.md): the pure part
// of /attention's view (app/attention/AttentionView.tsx). Every value comes from data/attention.json and the week files
// public/attention/stories/<monday>.json, both written by warehouse/derived/attention_index.py; nothing here computes
// an index. It chooses weeks (none after the build's week: row 3; the week that holds the build is partial: row 4; the
// chosen week kept among the cell's weeks: row 5), says a missing cell in one line (row 6), filters a cell's stories
// (row 1) and a place's (row 10), sums the places under All energy (row 11), names every figure's key and source (row
// 8) and gives the value a key names, for scripts/check-values.mjs (the keys of the rising rows, the places, the map's
// table and the footer). Tested by scripts/test-attention-view.mjs.

export type AttentionFile = {
  built: string; note: string; weeks: string[]; sectors: string[]; geos: string[]; states: string[];
  denominators: number[][];              // [week_i, stories_week, stories_judged, stories_classified, stories_unsent_zero]
  cells: number[][];                     // [sector_i, geo_i, week_i, stories, attention_index, opposition_stories, friction_index, tone_mean]
  kinds: Record<string, Record<string, number>>;   // "sector_i|geo_i|week_i" -> kind -> count
  places: (string | number)[][];         // [sector_i, place, state, week_i, stories, opposition]
  rising: (string | number)[][];         // [week_i, "sector" | "state", sector_i or state code, this, mean_before, change]
  counts: { stories: number; opposition: number; weeks_with_stories: number };
  model: string[]; tables: string[];
};
/** One story of a week file. `us` (0 or 1) when the week file carries it (faults row 2, the data machine's). */
export type Story = { id: string; date: string; outlet: string; url: string; headline: string; sector: string; state: string; opposition: number; kind: string; tone: number; place: string; us?: number };
export type Cell = { stories: number; attention: number; opposition: number; friction: number; tone: number };
export type Place = { place: string; state: string };

export const SECTOR_NAME: Record<string, string> = {
  datacenters: "Data centers", transmission: "Transmission and grid", gas: "Natural gas", nuclear: "Nuclear", solar_wind: "Solar and wind",
  storage: "Storage", oil_lng: "Oil and LNG", energy: "All energy",
};
export const KIND_NAME: Record<string, string> = {
  moratorium: "moratorium or ban", lawsuit: "lawsuit", protest: "protest", permit_denied: "permit denied", rate_case: "rate case",
  political_opposition: "political opposition", other_opposition: "other opposition",
};
export const ATT = "attention_index_weekly", FRI = "friction_index_weekly", LINKS = "attention_story_links";
export const BUILDER = "warehouse/derived/attention_index.py";
// two decimals: the value checker (scripts/check-values.mjs) reads a checked number as the raw value rounded to two decimals or a whole count
export const pct = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
export const day = (w: string) => (w ?? "").slice(0, 10);

const addDays = (d: string, n: number) => {
  const t = new Date(`${d}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() + n);
  return t.toISOString().slice(0, 10);
};
/** The Monday (UTC) of the week the file was built in. */
export function buildMonday(built: string): string {
  const b = new Date(built);
  return new Date(Date.UTC(b.getUTCFullYear(), b.getUTCMonth(), b.getUTCDate() - ((b.getUTCDay() + 6) % 7))).toISOString().slice(0, 10);
}
/** The day the file was built (UTC). */
export const builtDay = (built: string) => day(new Date(built).toISOString());
/** The Sunday that ends a week given by its Monday. */
export const weekEnd = (monday: string) => addDays(day(monday), 6);
/** Row 3: a week after the build's week is not offered, drawn or listed (a feed dates a few stories days ahead). */
export const inBuild = (f: AttentionFile, i: number) => i >= 0 && i < f.weeks.length && day(f.weeks[i]) <= buildMonday(f.built);
/** The week holds the build: its Sunday is after the day the file was built, so it holds only the days to the build (row 4). */
export const holdsBuild = (f: AttentionFile, i: number) => inBuild(f, i) && weekEnd(f.weeks[i]) > builtDay(f.built);
const denomOf = (f: AttentionFile, i: number) => f.denominators.find((d) => d[0] === i);
/** Fewer than nine in ten of the week's stories judged. */
export const partlyClassified = (f: AttentionFile, i: number) => { const d = denomOf(f, i); return !d || d[2] < d[1] * 0.9; };
/** Row 4: a week is partial when it is partly classified or holds the build (it was `the file's last week`, a week with no story). */
export const isPartial = (f: AttentionFile, i: number) => partlyClassified(f, i) || holdsBuild(f, i);
/** The words after a week in the picker: "(to 2026-11-06)", "(partly classified)", both, or none. */
export function weekWords(f: AttentionFile, i: number): string {
  const w: string[] = [];
  if (partlyClassified(f, i)) w.push("partly classified");
  if (holdsBuild(f, i)) w.push(`to ${builtDay(f.built)}`);
  return w.length ? ` (${w.join(", ")})` : "";
}
/** The weeks the charts draw: a classified story in them, none after the build's week. */
export const spanOf = (f: AttentionFile) => f.denominators.filter((d) => d[3] > 0 && inBuild(f, d[0])).map((d) => d[0]).sort((a, b) => a - b);
/** The weeks a cell (sector, place) has a row in, none after the build's week (rows 3 and 5). */
export const cellWeeks = (f: AttentionFile, sector: number, gi: number) =>
  [...new Set(f.cells.filter((c) => c[0] === sector && c[1] === gi && inBuild(f, c[2])).map((c) => c[2]))].sort((a, b) => a - b);
/** Row 5: the chosen week stays when the cell has it; else the cell's latest week; a cell with no week keeps it. */
export const chooseWeek = (weeks: number[], current: number) => (weeks.includes(current) || !weeks.length ? current : weeks[weeks.length - 1]);
/** The picker's options: the cell's weeks, and the chosen week marked "no story" where the cell lacks it. */
export const weekOptions = (weeks: number[], current: number) =>
  (weeks.includes(current) ? weeks : [...weeks, current].sort((a, b) => a - b)).map((i) => ({ i, none: !weeks.includes(i) }));
/** The week the page opens on: the latest with fifty classified stories or more, else the latest with any; none after the build. */
export function openingWeek(f: AttentionFile): number {
  const full = f.denominators.filter((d) => d[3] >= 50 && inBuild(f, d[0])).map((d) => d[0]);
  if (full.length) return Math.max(...full);
  const any = f.cells.map((c) => c[2]).filter((i) => inBuild(f, i));
  return any.length ? Math.max(...any) : f.weeks.length - 1;
}

/** A place of the picker in words. */
export const geoWords = (g: string, states: Record<string, string>) => (g === "all" ? "every story" : g === "US" ? "the United States" : states[g.slice(3)] ?? g);
/** Row 6: the one line where the cell has no row. */
export function noCellLine(sectorKey: string, geo: string, week: string, states: Record<string, string>): string {
  const what = sectorKey === "energy" ? "No energy story" : `No story of ${(SECTOR_NAME[sectorKey] ?? sectorKey).toLowerCase()}`;
  const where = geo === "all" ? "" : geo === "US" ? " about the United States" : ` named ${states[geo.slice(3)] ?? geo.slice(3)}`;
  return `${what}${where} in the week of ${day(week)}`;
}

/** Rows 1 and 10: a story is in the cell (sector, place), reports opposition when asked, and names the place when one is chosen.
 *  Under the United States: the story's `us` flag when the week file carries it, else a story that names a state. */
export function inCell(s: Story, sectorKey: string, geo: string, onlyOpposition = false, place: Place | null = null): boolean {
  const sectorOk = sectorKey === "energy" ? s.sector !== "not_energy" : s.sector === sectorKey;
  const geoOk = geo === "all" ? true : geo === "US" ? (typeof s.us === "number" ? s.us === 1 : s.state !== "") : s.state === geo.slice(3);
  const placeOk = !place || (s.place === place.place && s.state === place.state);
  return sectorOk && geoOk && placeOk && (!onlyOpposition || s.opposition === 1);
}
/** Row 1: whether the week file marks the stories about the United States. */
export const hasUsFlag = (rows: Story[]) => rows.length > 0 && rows.every((s) => typeof s.us === "number");

/** Row 11: a week's places named, for a sector; under All energy each place once, its sectors' rows summed. */
export function placesOf(f: AttentionFile, week: number, sector: number) {
  const all = f.sectors[sector] === "energy";
  const m = new Map<string, { place: string; state: string; stories: number; opposition: number }>();
  for (const p of f.places) {
    if (p[3] !== week || (!all && p[0] !== sector)) continue;
    const k = `${p[1]}|${p[2]}`;
    const r = m.get(k) ?? { place: p[1] as string, state: p[2] as string, stories: 0, opposition: 0 };
    r.stories += p[4] as number; r.opposition += p[5] as number;
    m.set(k, r);
  }
  return [...m.values()].sort((a, b) => b.stories - a.stories || b.opposition - a.opposition || a.place.localeCompare(b.place));
}

/** The week's rising rows: the sectors (All energy left out) and the states, largest change first. */
export function risingOf(f: AttentionFile, week: number) {
  const rows = f.rising.filter((r) => r[0] === week);
  const sectors = rows.filter((r) => r[1] === "sector" && f.sectors[r[2] as number] !== "energy")
    .map((r) => ({ index: r[2] as number, key: f.sectors[r[2] as number], this: r[3] as number, before: r[4] as number, change: r[5] as number }))
    .sort((a, b) => b.change - a.change);
  const states = rows.filter((r) => r[1] === "state")
    .map((r) => ({ key: r[2] as string, this: r[3] as number, before: r[4] as number, change: r[5] as number }))
    .sort((a, b) => b.change - a.change);
  return { sectors, states };
}

/** Row 9: the map's states as a table, for the chosen sector and week, largest value of the measure first. */
export function mapRows(f: AttentionFile, sector: number, week: number, measure: "attention" | "friction") {
  const out: { code: string; cell: Cell }[] = [];
  for (const st of f.states) {
    const gi = f.geos.indexOf("US-" + st);
    const c = f.cells.find((x) => x[0] === sector && x[1] === gi && x[2] === week);
    if (c) out.push({ code: st, cell: { stories: c[3], attention: c[4], opposition: c[5], friction: c[6], tone: c[7] } });
  }
  const v = (r: { cell: Cell }) => (measure === "attention" ? r.cell.attention : r.cell.friction);
  return out.sort((a, b) => v(b) - v(a) || b.cell.stories - a.cell.stories || a.code.localeCompare(b.code));
}

// The keys: a series key names the warehouse table, the entity, the variable and the week, as before. The rising rows,
// the places and the footer's counts are the file's own (data/attention.json), keyed so that scripts/check-values.mjs
// reads them back from it with attentionStat.
export const seriesKey = (table: string, entity: string, variable: string, week: string) => `series|${table}|${entity}|${variable}|${week}`;
export const risingKey = (week: string, kind: "sector" | "state", key: string, field: "this" | "mean_before" | "change") => `attention_rising|${day(week)}|${kind}|${key}|${field}`;
export const placeKey = (week: string, sectorKey: string, p: Place, field: "stories" | "opposition") => `attention_place|${day(week)}|${sectorKey}|${p.place}|${p.state}|${field}`;
export const fileKey = (field: "stories" | "opposition" | "weeks_with_stories") => `attention_file|${field}`;

const run = (built: string) => `${BUILDER}, run ${built.slice(0, 16).replace("T", " ")} UTC`;
/** Row 8: the words of a figure's source, drawn as its hover. */
export const seriesSource = (built: string, table: string, entity: string, variable: string, week: string) =>
  `${table}, ${entity}, ${variable}, week of ${day(week)}; ${run(built)}`;
export const risingSource = (built: string, week: string, kind: "sector" | "state", key: string, field: "this" | "mean_before" | "change") =>
  `${ATT}, attention_index of ${kind === "sector" ? `attention:${key}:all` : `attention:energy:US-${key}`}, week of ${day(week)}: ${
    field === "this" ? "this week" : field === "mean_before" ? "the mean of the four weeks before (data/attention.json, rising)" : "this week less the mean of the four weeks before (data/attention.json, rising)"}; ${run(built)}`;
export const placeSource = (built: string, week: string, sectorKey: string, p: Place, field: "stories" | "opposition") =>
  `${LINKS}: ${sectorKey === "energy" ? "energy" : SECTOR_NAME[sectorKey]?.toLowerCase() ?? sectorKey} stories naming ${p.place}${p.state ? `, ${p.state}` : ""}${field === "opposition" ? " that report opposition" : ""}, week of ${day(week)} (data/attention.json, places); ${run(built)}`;
export const fileSource = (built: string, field: "stories" | "opposition" | "weeks_with_stories") =>
  `${LINKS}: ${field === "stories" ? "the classified stories" : field === "opposition" ? "the classified stories reporting opposition" : "the weeks with a classified story"} (data/attention.json, counts); ${run(built)}`;

/** The value a key of this module names, read from the file; null when the file holds no such row. */
export function attentionStat(f: AttentionFile, check: string): number | null {
  const p = check.split("|");
  if (p[0] === "attention_file") {
    const v = (f.counts as Record<string, number>)[p[1]];
    return typeof v === "number" ? v : null;
  }
  const wi = f.weeks.findIndex((w) => day(w) === p[1]);
  if (wi < 0) return null;
  if (p[0] === "attention_rising") {
    const key = p[2] === "sector" ? f.sectors.indexOf(p[3]) : p[3];
    const r = f.rising.find((x) => x[0] === wi && x[1] === p[2] && x[2] === key);
    const col = { this: 3, mean_before: 4, change: 5 }[p[4] as "this" | "mean_before" | "change"];
    return r && col ? (r[col] as number) : null;
  }
  if (p[0] === "attention_place") {
    const si = f.sectors.indexOf(p[2]);
    if (si < 0) return null;
    const r = placesOf(f, wi, si).find((x) => x.place === p[3] && x.state === p[4]);
    if (!r) return null;
    return p[5] === "stories" ? r.stories : p[5] === "opposition" ? r.opposition : null;
  }
  return null;
}
