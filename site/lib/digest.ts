// Energy Research Warehouse (ERW) site, session 402: the Energy Digest's figures, each with the table and key it came
// from, and the days of its archive.
//
// The Digest is markdown (docs/digest/<date>.md, written by warehouse/news/brief.py), not Num spans, so until this
// session no figure on /digest or /digest/<date> carried a check key, scripts/check-values.mjs read none of them, and
// the license hold of 21 October (lib/license.ts) reached none: NYISO's and ISO-NE's prices were drawn as numbers.
// Here the numbers section is read as brief.py writes it (both of its forms: the table named in the row, until 27
// September 2026, and the footnote list, since), and every figure gets the key and the raw value a Num would carry:
//
//   digest_dam|<ISO>|<table>|<node>|<operating day>       the mean of the 24 hourly day-ahead prices of the ISO's day
//   digest_rt|<table>|<node>|<variable>|<ts_utc>          the highest real-time price, at its interval
//   digest_fuel|eia_fuel_spot_prices|<entity>|<date>      an EIA spot close on its trading day
//   digest_chart|<date>|<table>|<number>                  a figure of the chart of the day, from its record (session 315)
//
// The table is the one the Digest names (a table consolidated since, session 29, is read from its new table by the
// checkers, as the Roundup's are). A figure of a held table is drawn as Num draws one: "license needed", no data-check.
// This file imports nothing but lib/license.ts, so scripts can read it without building the site
// (scripts/digest-figures.mjs, scripts/test-digest-numbers.mjs).
import { LICENSE_FROM, LICENSE_NEEDED, licenseHeldRow, licenseNeeded, licenseTitle, utcDay } from "./license";

/** A grid's label in the Digest (the row's first cell, or the real-time line's parenthesis) and its entity prefix. */
const GRID: Record<string, string> = { ERCOT: "ercot", CAISO: "caiso", NYISO: "nyiso", MISO: "miso", SPP: "spp", "ISO-NE": "isone", ISONE: "isone", PJM: "pjm" };
/** The fuel lines' labels (brief.py FUELS) and their entities in eia_fuel_spot_prices. */
const FUEL: Record<string, string> = { "Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent" };
/** The US48 row of eia930_all_demand (session 804: the demand line). */
const US48 = "eia930:US48";
/** The day before a YYYY-MM-DD day, in UTC arithmetic. */
function dayBefore(day: string): string {
  const d = new Date(`${day}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() - 1);
  return d.toISOString().slice(0, 10);
}
/** The sections of stories: the news index's (news_index), held whole since 21 October when it is held. */
export const STORY_SECTIONS = ["Top of the industry", "By sector", "AI and power"];

export type Figure = {
  part: "dam" | "rt" | "fuel" | "chart" | "demand";
  key: string;
  raw: string;          // the value as the Digest wrote it (a chart figure: as its record holds it)
  text: string;         // the figure as written on the page
  table: string;        // the table the Digest names
  entity: string;       // the row's entity, for the hold by grid ("" when the figure has none)
  held: boolean;
  title: string;        // the hold's words, for the hover
};

/** The table a figure is held by and checked against: the consolidated table where the Digest names an old one. */
export function currentTable(table: string): string {
  const m = /^(caiso|ercot|miso|spp)_(dam|rtm)_hub_prices$/.exec(table);
  return m ? `iso_${m[2]}_hub_prices` : table;
}

function hold(table: string, entity: string | null, now: Date): { held: boolean; title: string } {
  const t = currentTable(table);
  const held = licenseHeldRow(t, entity, now);
  return { held, title: held ? licenseTitle(t) : "" };
}

/** The chart-maker's rounding (warehouse/analysis/findings/daily_chart.py nd_for and findings_common.fmt). */
export function chartText(v: number): string {
  const a = Math.abs(v);
  const nd = a >= 10000 ? 0 : a >= 100 ? 1 : a >= 1 ? 2 : 4;
  return v.toLocaleString("en-US", { minimumFractionDigits: nd, maximumFractionDigits: nd });
}

type Section = { title: string; start: number; end: number };   // line indexes: the heading, and one past the last line

function sectionsOf(lines: string[]): Section[] {
  const out: Section[] = [];
  let open = false;
  lines.forEach((l, i) => {
    const m = /^## (.+?)\s*$/.exec(l);
    if (m) {
      if (open) out[out.length - 1].end = i;
      out.push({ title: m[1], start: i, end: lines.length });
      open = true;
    } else if (l.trim() === "---" && open) {   // the Digest's closing rule: what follows it belongs to no section
      out[out.length - 1].end = i;
      open = false;
    }
  });
  return out;
}
const isNumbers = (t: string) => /^(ERW's )?Numbers today$/i.test(t);
const isChart = (t: string) => /^ERW's Chart of the Day$/i.test(t);

const NUM = "-?\\d[\\d,]*\\.\\d+|-?\\d[\\d,]*";
const plain = (s: string) => s.replace(/,/g, "");

type Place = { line: number; from: string; unit: string; cell?: number };   // where a figure sits: its line, the text replaced, the unit kept after it; a table figure's cell

/** The figures of one Digest, with where each sits in its markdown. chart: the day's chart record (docs.json
 *  digest_charts), when the Digest has one. */
function read(md: string, date: string, chart: { table: string; numbers: Record<string, number | string> } | null, now: Date) {
  const lines = md.split("\n");
  const figs: (Figure & Place)[] = [];
  const secs = sectionsOf(lines);
  const num = secs.find((s) => isNumbers(s.title));
  let summary: number[] = [];
  if (num) {
    const foot: Record<string, string> = {};
    for (let i = num.start; i < num.end; i++) {
      if (lines[i].startsWith("Tables: ")) for (const m of lines[i].matchAll(/\[(\d+)\] `([a-z0-9_]+)`/g)) foot[m[1]] = m[2];
    }
    const tableOf = (cell: string) => {
      const mk = /\[(\d+)\]/.exec(cell);
      if (mk) return foot[mk[1]] ?? "";
      return /`([a-z0-9_]+)`/.exec(cell)?.[1] ?? "";
    };
    let seenTable = false;
    for (let i = num.start + 1; i < num.end; i++) {
      const l = lines[i];
      if (l.startsWith("**Day-ahead average")) seenTable = true;
      if (!seenTable && l.trim() && !l.startsWith("Every number below")) summary.push(i);
      if (l.startsWith("| ")) {
        const c = l.split("|").slice(1, -1).map((x) => x.trim());
        if (c.length >= 5 && GRID[c[0]] && /^\d{4}-\d{2}-\d{2}$/.test(c[2])) {
          const table = tableOf(c[4]), entity = `${GRID[c[0]]}:${c[1]}`;
          if (!table) continue;
          if (/^-?[\d,]+\.\d{2}$/.test(c[3])) {
            figs.push({ part: "dam", key: `digest_dam|${c[0]}|${table}|${c[1]}|${c[2]}`, raw: plain(c[3]), text: c[3], table, entity, ...hold(table, entity, now),
              line: i, from: c[3], unit: "", cell: 4 });
          }
          // session 804: the day before, in the sixth cell, is the same figure of the operating day before
          if (c.length >= 7 && /^-?[\d,]+\.\d{2}$/.test(c[5])) {
            figs.push({ part: "dam", key: `digest_dam|${c[0]}|${table}|${c[1]}|${dayBefore(c[2])}`, raw: plain(c[5]), text: c[5], table, entity, ...hold(table, entity, now),
              line: i, from: c[5], unit: "", cell: 6 });
          }
        }
        continue;
      }
      const rt = /^\*\*Highest real-time price[^*]*:\*\* (-?[\d,]+\.\d{2}) USD\/MWh at (.+?) \(([A-Z-]+)\), interval starting .*?\((\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC\), \S+ `([a-z0-9_]+)`(.*)$/.exec(l);
      if (rt && GRID[rt[3]]) {
        const rest = rt[7];
        const marks = [...rest.matchAll(/\[(\d+)\]/g)];
        const table = marks.length ? foot[marks[marks.length - 1][1]] ?? "" : (/`([a-z]+_rtm_[a-z_]+)`/.exec(rest)?.[1] ?? "");
        if (table) {
          const entity = `${GRID[rt[3]]}:${rt[2]}`;
          figs.push({ part: "rt", key: `digest_rt|${table}|${rt[2]}|${rt[6]}|${rt[4]}T${rt[5]}:00Z`, raw: plain(rt[1]), text: rt[1], table, entity, ...hold(table, entity, now),
            line: i, from: `${rt[1]} USD/MWh`, unit: " USD/MWh" });
        }
        continue;
      }
      // session 804: a mover line, "<label>: <newest> <unit> on <day>, up|down <change> (<pct>%) from <previous> on <day> [n]":
      // two figures of the label's table (a fuel's closes; a hub's day-ahead averages)
      const mv = /^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2}), (?:up|down) [\d,.]+ \S+ \([\d.]+%\) from (-?[\d,]+\.\d{2}) \S+ on (\d{4}-\d{2}-\d{2}) \[(\d+)\]/.exec(l);
      if (mv) {
        const hub = /^(ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) (\S+) day-ahead$/.exec(mv[1]);
        if (FUEL[mv[1]]) {
          const table = "eia_fuel_spot_prices", entity = FUEL[mv[1]];
          for (const [v, d] of [[mv[2], mv[4]], [mv[5], mv[6]]]) {
            figs.push({ part: "fuel", key: `digest_fuel|${table}|${entity}|${d}`, raw: plain(v), text: v, table, entity, ...hold(table, entity, now),
              line: i, from: v, unit: "" });
          }
        } else if (hub && GRID[hub[1]]) {
          const table = foot[mv[7]] ?? "", entity = `${GRID[hub[1]]}:${hub[2]}`;
          if (table) {
            for (const [v, d] of [[mv[2], mv[4]], [mv[5], mv[6]]]) {
              figs.push({ part: "dam", key: `digest_dam|${hub[1]}|${table}|${hub[2]}|${d}`, raw: plain(v), text: v, table, entity, ...hold(table, entity, now),
                line: i, from: v, unit: "" });
            }
          }
        }
        continue;
      }
      // session 804: US48 demand's peak hour, and the same weekday a year before where held
      if (/^\*\*US48 demand/.test(l)) {
        for (const m of l.matchAll(/peaked at (-?[\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC/g)) {
          const table = "eia930_all_demand", entity = US48;
          figs.push({ part: "demand", key: `digest_demand|${table}|${entity}|demand_mw|${m[2]}T${m[3]}:00Z`, raw: plain(m[1]), text: m[1], table, entity,
            ...hold(table, entity, now), line: i, from: `${m[1]} MW`, unit: " MW" });
        }
        continue;
      }
      const fu = /^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2})\b/.exec(l);
      if (fu && FUEL[fu[1]]) {
        const table = "eia_fuel_spot_prices", entity = FUEL[fu[1]];
        figs.push({ part: "fuel", key: `digest_fuel|${table}|${entity}|${fu[4]}`, raw: plain(fu[2]), text: fu[2], table, entity, ...hold(table, entity, now),
          line: i, from: `${fu[2]} ${fu[3]}`, unit: ` ${fu[3]}` });
      }
    }
  }
  const ch = secs.find((s) => isChart(s.title));
  if (ch && chart) {
    // the record's own figures, the day's value and the old record first (two figures written alike take the first key)
    const order = Object.keys(chart.numbers).sort((a, b) => (a === "value" ? -2 : a === "old_record" ? -1 : 0) - (b === "value" ? -2 : b === "old_record" ? -1 : 0));
    const taken = new Set<string>();
    for (let i = ch.start + 1; i < ch.end; i++) {
      const l = lines[i];
      if (l.startsWith("![")) continue;   // the picture's words are an attribute of the image, not text
      for (const k of order) {
        const v = Number(chart.numbers[k]);
        if (!Number.isFinite(v)) continue;
        const t = chartText(v);
        if (taken.has(`${i}|${t}`)) continue;
        const re = new RegExp(`(?<![\\d.,])${t.replace(/[.]/g, "\\.")}(?![\\d]|[.,]\\d)`);
        if (!re.test(l)) continue;
        taken.add(`${i}|${t}`);
        figs.push({ part: "chart", key: `digest_chart|${date}|${chart.table}|${k}`, raw: String(chart.numbers[k]), text: t, table: chart.table, entity: "",
          ...hold(chart.table, null, now), line: i, from: t, unit: "" });
      }
    }
  }
  return { lines, figs, secs, summary, num, ch };
}

/** The figures of one Digest, each with its key (scripts/digest-figures.mjs prints them for scripts/check_digest.py). */
export function digestFigures(md: string, date: string, chart: { table: string; numbers: Record<string, number | string> } | null = null, now: Date = new Date()): Figure[] {
  return read(md, date, chart, now).figs.map((f) => ({ part: f.part, key: f.key, raw: f.raw, text: f.text, table: f.table, entity: f.entity, held: f.held, title: f.title }));
}

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** The span a figure is drawn as: Num's (components/Num.tsx), with its key, or the hold's words. */
export function figureSpan(f: Pick<Figure, "key" | "raw" | "text" | "table" | "held" | "title">): string {
  if (f.held) return `<span data-license-held="${esc(currentTable(f.table))}" class="text-muted" title="${esc(f.title)}">${LICENSE_NEEDED}</span>`;
  return `<span data-check="${esc(f.key)}" data-raw="${esc(f.raw)}">${esc(f.text)}</span>`;
}

const day = (iso: string) => new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

/**
 * The Digest's markdown with each figure replaced by a placeholder, and the HTML each placeholder stands for; the page
 * renders the markdown (lib/markdown.ts render) and puts the spans in with fillDigest. Placeholders are letters and
 * digits, which markdown leaves as they are. Held since 21 October (lib/license.ts): a figure of a held table; the
 * numbers' summary when it names one (the model's sentence compares the grids: a held grid's figure, or its place
 * among the others, is the held table's); and, while news_index is held, the sections of stories, but for the policy
 * actions (policy_actions, the Federal Register and agency news) that brief.py adds under Policy.
 */
export function digestMarkdown(md: string, date: string, chart: { table: string; numbers: Record<string, number | string> } | null = null, now: Date = new Date()) {
  const { lines, figs, secs, summary } = read(md, date, chart, now);
  const out = [...lines];
  const spans: string[] = [];
  const token = (html: string) => { spans.push(html); return `ERWDIGESTFIG${spans.length - 1}Z`; };
  for (const f of figs) {
    const at = out[f.line];
    if (f.part === "dam" && f.cell) {   // a table cell (session 804: the day before sits in its own cell)
      const c = at.split("|");
      c[f.cell] = ` ${token(figureSpan(f))} `;
      out[f.line] = c.join("|");
    } else {
      const i = at.indexOf(f.from);
      if (i < 0) continue;
      out[f.line] = at.slice(0, i) + token(figureSpan(f)) + (f.held ? "" : f.unit) + at.slice(i + f.from.length);
    }
  }
  // the summary above the numbers: held whole when it names a held figure, else each figure it names carries its key
  const numFigs = figs.filter((f) => f.part !== "chart");
  for (const i of summary) {
    const l = lines[i];
    const named = (f: Figure) => new RegExp(`(?<![\\d.,])${f.text.replace(/[.]/g, "\\.")}(?![\\d]|[.,]\\d)`).test(l);
    const heldOnes = numFigs.filter((f) => f.held && named(f));
    if (heldOnes.length) {
      const tables = [...new Set(heldOnes.map((f) => currentTable(f.table)))];
      out[i] = `${token(`<span data-license-held="${esc(tables.join(" "))}" class="text-muted" title="${esc(tables.map(licenseTitle).join("; "))}">${LICENSE_NEEDED}</span>`)}: `
        + `the summary of these numbers names figures of ${tables.length === 1 ? "a table" : "tables"} held since ${day(LICENSE_FROM)}.`;
      continue;
    }
    let s = l;
    for (const f of numFigs) {
      const re = new RegExp(`(?<![\\d.,A-Za-z])${f.text.replace(/[.]/g, "\\.")}(?![\\d]|[.,]\\d)`);
      if (re.test(s)) s = s.replace(re, token(figureSpan(f)));
    }
    out[i] = s;
  }
  if (licenseNeeded("news_index", now)) {
    for (const s of [...secs].reverse()) {
      if (!STORY_SECTIONS.includes(s.title)) continue;
      const body = lines.slice(s.start + 1, s.end);
      // keep the policy actions (and their group's label) of "By sector"
      const kept: string[] = [];
      let label = "";
      for (const l of body) {
        if (/^\*\*[^*]+\*\*\s*$/.test(l)) { label = l; continue; }
        if (/, policy action\): /.test(l)) {
          if (label) { kept.push("", label, ""); label = ""; }
          kept.push(l);
        }
      }
      const line = `${token(`<span data-license-held="news_index" class="text-muted" title="${esc(licenseTitle("news_index"))}">${LICENSE_NEEDED}</span>`)}: `
        + `the stories of this section come from the news index, whose outlets ask for permission; held since ${day(LICENSE_FROM)}.`;
      out.splice(s.start + 1, s.end - s.start - 1, "", line, ...kept, "");
    }
  }
  // the chart of a held table: the picture and its sentence go with it (the chart-maker passes over held tables since
  // session 232; a chart drawn before a hold is held here). Done last: the chart follows the sections above.
  const ch = secs.find((s) => isChart(s.title));
  if (ch && chart && licenseHeldRow(currentTable(chart.table), null, now)) {
    const shift = out.length - lines.length;   // the story sections above it may have changed length
    const line = `${token(`<span data-license-held="${esc(currentTable(chart.table))}" class="text-muted" title="${esc(licenseTitle(currentTable(chart.table)))}">${LICENSE_NEEDED}</span>`)}: `
      + `the chart of the day is drawn from \`${chart.table}\`, held since ${day(LICENSE_FROM)}.`;
    out.splice(ch.start + 1 + shift, ch.end - ch.start - 1, "", line, "");
  }
  return { md: out.join("\n"), spans };
}

/** Puts the spans into the rendered HTML. */
export function fillDigest(html: string, spans: string[]): string {
  return html.replace(/ERWDIGESTFIG(\d+)Z/g, (all, i: string) => spans[Number(i)] ?? all);
}

// ---------------------------------------------------------------------------------------------------------------------
// the days of the archive
// ---------------------------------------------------------------------------------------------------------------------

/** Is a YYYY-MM-DD date a Saturday or Sunday? */
export function weekendDay(date: string): boolean {
  const d = new Date(`${date}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && (d.getUTCDay() === 0 || d.getUTCDay() === 6);
}

/** What the Digest holds for a day: its Digest; none, a weekend (no weekend issue); none yet (today, before the run that
 *  writes it); none, a weekday that passed without one; or null, a day outside the archive (before the first Digest,
 *  after today, or not a date). */
export type DayKind = "digest" | "weekend" | "pending" | "missed";
export function dayKind(date: string, have: string[], today: string = utcDay()): DayKind | null {
  if (have.includes(date)) return "digest";
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || Number.isNaN(new Date(`${date}T00:00:00Z`).getTime())) return null;
  const first = [...have].sort()[0];
  if (!first || date < first || date > today) return null;
  if (weekendDay(date)) return "weekend";
  return date === today ? "pending" : "missed";
}

/** Every day from the first Digest to today, newest first: the Digests, and the days without one (weekends, the
 *  weekdays that passed without one, and today before it is written). */
export function archiveOf(have: string[], today: string = utcDay()): { date: string; kind: DayKind }[] {
  const first = [...have].sort()[0];
  const out: { date: string; kind: DayKind }[] = [];
  if (!first) return out;
  for (let d = new Date(`${first}T00:00:00Z`); d.toISOString().slice(0, 10) <= today; d.setUTCDate(d.getUTCDate() + 1)) {
    const s = d.toISOString().slice(0, 10);
    out.push({ date: s, kind: dayKind(s, have, today) as DayKind });
  }
  return out.reverse();
}

/** "Wednesday 21 October 2026". */
export function dayWords(date: string): string {
  const d = new Date(`${date}T00:00:00Z`);
  return `${d.toLocaleDateString("en-GB", { weekday: "long", timeZone: "UTC" })} ${day(date)}`;
}
