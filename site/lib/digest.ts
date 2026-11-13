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
import { LICENSE_FROM, LICENSE_NEEDED, gridName, gridPrefix, licenseHeldGrids, licenseHeldRow, licenseNeeded, licenseTitle, utcDay } from "./license";

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
export const STORY_SECTIONS = ["Top of the industry", "By sector", "AI and power", "What moved", "The rest of the top ten"];   // session 2703: the v2 order's

export type Figure = {
  part: "dam" | "rt" | "fuel" | "chart" | "demand" | "story";   // session 1450: the block's story rows
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
    const m = /^###? (.+?)\s*$/.exec(l);   // session 2703: the v2 Digest's fold holds its parts under "### " headings
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
const isFullNumbers = (t: string) => /^(ERW's )?Numbers today$/i.test(t);
// session 2703: the v2 Digest's opening number and numbers block carry figures in the same forms, each with its own list of tables
const isNumbers = (t: string) => isFullNumbers(t) || /^The (opening number|numbers)$/i.test(t);
/** A v2 line read as the older forms: a block row's bold label ("- **Market price.** ") and the opening's bold off. */
const asOld = (l: string) => l.replace(/^- \*\*[^*]+\*\* /, "- ").replace(/^\*\*(?=[A-Z])/, "- ");
const isChart = (t: string) => /^ERW's Chart of the Day$/i.test(t);

const NUM = "-?\\d[\\d,]*\\.\\d+|-?\\d[\\d,]*";
const plain = (s: string) => s.replace(/,/g, "");

type Place = { line: number; from: string; unit: string; cell?: number; label?: string };   // where a figure sits: its line, the text replaced, the unit kept after it; a table figure's cell; the row's name

/** Session 2207 (Samuel's ruling of 23 October 2026, item 7 of docs/reviews/deals-rulings-2026-10-23.md): a figure the
 *  warehouse holds at another value than the stored issue printed. The issue keeps its figure; the page adds one line
 *  under the numbers saying the publisher revised it after the issue was written, with the value held now
 *  (lib/digestLive.ts reads them). Every check reads the note as a note: scripts/check-values.mjs passes a figure whose
 *  page carries its revision at the live value, scripts/check_digest.py marks it "revised". */
export type Revision = { key: string; value: number; retrieved: string | null };

/** The figures of one Digest, with where each sits in its markdown. chart: the day's chart record (docs.json
 *  digest_charts), when the Digest has one. */
function read(md: string, date: string, chart: { table: string; numbers: Record<string, number | string> } | null, now: Date) {
  const lines = md.split("\n");
  const figs: (Figure & Place)[] = [];
  const secs = sectionsOf(lines);
  const num = secs.find((s) => isNumbers(s.title));
  let summary: number[] = [];
  for (const num of secs.filter((s) => isNumbers(s.title))) {   // session 2703: every numbers section, each with its own tables
    const foot: Record<string, string> = {};
    // session 1450: the stories a block row reads ("[3] `news_stories`; story news:abc (mw); story news:def (price)")
    const stories: Record<string, string> = {};
    for (let i = num.start; i < num.end; i++) {
      if (lines[i].startsWith("Tables: ")) {
        for (const m of lines[i].matchAll(/\[(\d+)\] `([a-z0-9_]+)`/g)) foot[m[1]] = m[2];
        for (const m of lines[i].matchAll(/story (news:[0-9a-f]+) \((mw|price)\)/g)) if (!stories[m[2]]) stories[m[2]] = m[1];
      }
    }
    const tableOf = (cell: string) => {
      const mk = /\[(\d+)\]/.exec(cell);
      if (mk) return foot[mk[1]] ?? "";
      return /`([a-z0-9_]+)`/.exec(cell)?.[1] ?? "";
    };
    let seenTable = !isFullNumbers(num.title);   // the summary is the model's sentences above the full section's table only
    for (let i = num.start + 1; i < num.end; i++) {
      const l = isFullNumbers(num.title) ? lines[i] : asOld(lines[i]);   // session 2703: the v2 forms only in the v2 sections
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
      if (/^\*\*US48 demand/.test(l) || /US48 demand peaked at /.test(l)) {
        for (const m of l.matchAll(/peaked at (-?[\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC/g)) {
          const table = "eia930_all_demand", entity = US48;
          figs.push({ part: "demand", key: `digest_demand|${table}|${entity}|demand_mw|${m[2]}T${m[3]}:00Z`, raw: plain(m[1]), text: m[1], table, entity,
            ...hold(table, entity, now), line: i, from: `${m[1]} MW`, unit: " MW" });
        }
        continue;
      }
      // session 1450 (chain 149, fault 6): a story row of the v2 block, keyed to its story's scored field
      // read on the line as written (asOld takes the bold label off the v2 rows)
      const st = /^- \*\*(Project or capacity|Policy, capital or reliability)\.\*\* [^:]+: (?:(USD [\d,.]+(?: (?:billion|million|trillion|thousand))?)|([\d,]+) MW) \(.*?\) \[(\d+)\]\./.exec(lines[i]);
      if (st && foot[st[4]] === "news_stories") {
        const field = st[3] ? "mw" : "price", id = stories[field];
        if (id) {
          const text = st[3] ?? st[2];
          figs.push({ part: "story", key: `digest_story|news_stories|${id}|${field}`, raw: plain(st[3] ?? st[2].replace(/^USD /, "")), text, table: "news_stories", entity: id,
            held: false, title: "", line: i, from: text, unit: "" });
        }
        continue;
      }
      const fu = /^- (.+?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2})\b/.exec(l);
      if (fu && FUEL[fu[1]]) {
        const table = "eia_fuel_spot_prices", entity = FUEL[fu[1]];
        figs.push({ part: "fuel", key: `digest_fuel|${table}|${entity}|${fu[4]}`, raw: plain(fu[2]), text: fu[2], table, entity, ...hold(table, entity, now),
          line: i, from: `${fu[2]} ${fu[3]}`, unit: ` ${fu[3]}`, label: fu[1] });
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
export function digestMarkdown(md: string, date: string, chart: { table: string; numbers: Record<string, number | string> } | null = null, now: Date = new Date(),
                               revisions: Record<string, Revision> = {}) {
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
        // session 1980 (faults file row 85): a policy action whose why line failed closes on "). " since then
        if (/, policy action\)[:.] /.test(l)) {
          if (label) { kept.push("", label, ""); label = ""; }
          kept.push(l);
        }
      }
      const line = `${token(`<span data-license-held="news_index" class="text-muted" title="${esc(licenseTitle("news_index"))}">${LICENSE_NEEDED}</span>`)}: `
        + `the stories of this section come from the news index, whose outlets ask for permission; held since ${day(LICENSE_FROM)}.`;
      out.splice(s.start + 1, s.end - s.start - 1, "", line, ...kept, "");
    }
  }
  // session 4010: the revision notes go in after the news index's hold below. The hold rewrites the story sections by
  // their first lines' places in the issue as written, and "What moved" begins where the notes went in, so its splice
  // began on the notes and removed them (the issue of 12 November lost its revised US48 demand line on every build).
  // The hold changes only lines after "The numbers", so num.end is still the notes' place once it has run.
  // session 2207: the revision notes, one line a revised figure, at the end of the numbers section (before any splice
  // of the sections above it moves the lines); the figure keeps its span and its key, and the note names the value held
  const num = secs.find((s) => s.title === "The numbers") ?? secs.find((s) => isNumbers(s.title));   // session 2703: under the v2 block
  // session 4010: one note a key (the US48 demand line is printed twice in an issue, under one key)
  const revised = figs.filter((f, i, all) => f.part !== "chart" && revisions[f.key] && !f.held && all.findIndex((g) => g.key === f.key) === i);
  if (num && revised.length) {
    const notes = revised.map((f) => {
      const r = revisions[f.key];
      const who = f.part === "fuel" ? "EIA" : "The publisher";
      const when = /\|(\d{4}-\d{2}-\d{2})(?:T|$)/.exec(f.key.slice(f.key.lastIndexOf("|")))?.[1] ?? "";
      // session 4009: US48 demand's peak hour is a revised figure too, said in whole MW
      const demand = f.part === "demand";
      const what = demand ? "US48 demand" : f.label ?? `${currentTable(f.table)} ${f.entity}`;
      const noun = f.part === "fuel" ? "close" : demand ? "peak hour" : "price";
      const held = demand ? Math.round(r.value).toLocaleString("en-US") : shownTwo(r.value);
      const words = `${who} revised the ${what} ${noun}${when ? ` for ${day(when)}` : ""} after this issue was written: `
        + `the warehouse now holds ${held}${f.unit}; the issue printed ${f.text}${f.unit} and keeps it as its record.`;
      return token(`<span data-revised="${esc(f.key)}" data-revised-value="${r.value}" data-revised-printed="${esc(f.raw)}" class="text-muted">${esc(words)}</span>`);
    });
    out.splice(num.end, 0, "", ...notes.flatMap((n, i) => (i ? ["", n] : [n])));
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
// session 1449 (chain 149, faults 18 and 26 on the page): the source trail close at hand, not in the way
// ---------------------------------------------------------------------------------------------------------------------

/** The "Tables: [1] `iso_dam_hub_prices` (...); [2] `eia930_all_demand` ..." paragraphs of a rendered issue become a
 *  closed <details class="digest-tables"> (its summary "Sources"), and each [n] mark in the text gets a hover naming
 *  its table (an <abbr title>): the owner's rule that explanatory text is a hover tip, never visible grey text, with the
 *  trail one click away for a reader without a hover. The markdown keeps every line: the parser and the tracer read it. */
export function sourceTrail(html: string): string {
  const tables: Record<string, string> = {};
  const out = html.replace(/<p>(Tables: (?:.|\n)*?)<\/p>/g, (all, body: string) => {
    for (const m of body.matchAll(/\[(\d+)\] <code>([a-z0-9_]+)<\/code>/g)) tables[m[1]] = m[2];
    return `<details class="digest-tables"><summary>Sources</summary><p>${body}</p></details>`;
  });
  if (!Object.keys(tables).length) return out;
  // the marks outside the details and outside tags: "[n]" as text, after a space or a quote
  return out.split(/(<details class="digest-tables">(?:.|\n)*?<\/details>)/).map((part, i) => {
    if (i % 2) return part;
    return part.replace(/(^|[\s>(])\[(\d+)\](?=[\s.,;:)<]|$)/g, (all, before: string, n: string) =>
      tables[n] ? `${before}<abbr class="digest-mark" title="${tables[n]}">[${n}]</abbr>` : all);
  }).join("");
}

/** The Roundup's five numbers: the row that is the opening number word for word says so instead (the markdown keeps
 *  both; scripts/check_roundup.py traces the five by their form). */
/** Session 1989 (docs/reviews/periodicals-faults-2026-11-05.md row 94): a stored Roundup's table row of a grid held for
 *  license on the day: each price cell reads "license needed". The Roundups of W44 and W45 printed NYISO's and ISO-NE's
 *  weekly means (row 93, fixed in the writer since); a stored issue is not rewritten, so the page holds them, as
 *  digestMarkdown holds a held table's figures on the Digest's page. A cell with no figure is kept as written. */
export function holdRoundupGrids(md: string, now: Date = new Date()): string {
  const held = new Set(licenseHeldGrids(now));
  if (!held.size) return md;
  // session 3319 (row 108): the held grids by the names a stored Roundup's sentences give them
  const names = [...held].map((p) => gridName(p)).filter((n) => n && !/^[a-z]/.test(n));
  const namesHeld = names.length ? new RegExp(`\\b(?:${names.map((n) => n.replace(/[-]/g, "\\-")).join("|")})\\b`) : null;
  let inNumbers = false;
  return md.split("\n").map((l) => {
    if (/^#{2,3} /.test(l)) inNumbers = /ERW's Numbers This Week|^## Numbers of the week/.test(l);   // W39's older heading too
    // session 3319 (row 108): the week's highest real-time price, when it was a held grid's (W43: LONGIL, NYISO)
    const rt = /^\*\*Highest real-time price of the week:\*\* -?[\d,]+\.\d+ USD\/MWh at .+? \(([A-Z-]+)\)/.exec(l);
    if (rt && held.has(gridPrefix(rt[1]))) {
      return `**Highest real-time price of the week:** ${LICENSE_NEEDED}: the week's highest interval held was ${rt[1]}'s, a grid held since ${day(LICENSE_FROM)}.`;
    }
    // session 3319 (row 108): the numbers' summary sentence, when it names a held grid beside a price (W43: "dearest at
    // NYISO's N.Y.C., 47.64 USD/MWh")
    if (inNumbers && namesHeld && /^[A-Z]/.test(l) && !/^Tables?:/.test(l) && namesHeld.test(l) && /\d\.\d{2}\b/.test(l)) {
      return `${LICENSE_NEEDED}: the summary of these numbers names figures of a grid held since ${day(LICENSE_FROM)}.`;
    }
    if (!l.startsWith("| ")) return l;
    const c = l.split("|");
    const p = gridPrefix((c[1] ?? "").trim());
    if (!p || !held.has(p)) return l;
    return c.map((x, i) => (i >= 3 && i < c.length - 1 && /^\s*[+-]?[\d,]+\.\d+(?: \([+-]?[\d.]+%\))?\s*$/.test(x) ? ` ${LICENSE_NEEDED} ` : x)).join("|");
  }).join("\n");
}

export function dedupeOpening(html: string): string {
  const op = /<h2 id="the-opening-number">(?:.|\n)*?<p><strong>([^<]+?)\.?<\/strong>/.exec(html);
  if (!op) return html;
  const text = op[1].trim();
  if (text.length < 20) return html;
  const esc = text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return html.replace(new RegExp(`(<li><strong>[^<]+:<\\/strong> )${esc}\\.?((?:\\s*<abbr[^>]*>\\[\\d+\\]<\\/abbr>|\\s*\\[\\d+\\])?\\.?)(</li>)`), "$1the opening number, above.$3");
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
/** A revised value as the Digest writes a close: two decimals, thousands separated. */
function shownTwo(v: number): string {
  return v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** Session 2701 (rulings item 8, the default of 24 October 2026): an issue kept as it was written, with one line on its
 *  page saying why. A corrected archive is not a record, so the stored markdown is never rewritten. */
export const ISSUE_NOTES: Record<string, string> = {
  "2026-10-14": "This issue is kept as it was written. Its fun fact's second half is a colliery disaster, which the fun fact has not allowed since 21 October 2026.",
};

export function dayWords(date: string): string {
  const d = new Date(`${date}T00:00:00Z`);
  return `${d.toLocaleDateString("en-GB", { weekday: "long", timeZone: "UTC" })} ${day(date)}`;
}

// ---------------------------------------------------------------------------------------------------------------------
// session 1461 (chain 150, fault 41): the chart of the day drawn on the page from its record's points, a hover on each
// ---------------------------------------------------------------------------------------------------------------------

/** The plotted series a chart record keeps since session 1461 (daily_chart.chart_points): the x labels, each series'
 *  values (null where the series has none), the unit and the chart's count of decimals. */
export type ChartPoints = { x: string[]; series: { name: string; values: (number | null)[] }[]; unit?: string; decimals?: number };

const SVG_COLORS = ["var(--chart-ink, #2E2D29)", "var(--chart-blue, #3C6E9E)", "var(--chart-grey, #6B675F)", "var(--chart-light, #8F8A80)"];

function svgEscape(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/** A number with the chart's own decimals and a thousands separator, as the picture prints it. */
export function chartNumber(v: number, decimals = 2): string {
  return v.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

/** The chart of the day as an inline SVG (role img, named by the alt text): one line a series, and on each point a
 *  circle whose title is the hover ("2026-06: 251.00 kbbl", the series' name first when there are two or more). The
 *  axis shows the lowest and highest value and the first and last label. "" when the points cannot be drawn (no x, no
 *  value), so the caller draws the picture instead. No script and no style attribute: the page's CSP holds. */
export function chartSvg(p: ChartPoints | undefined | null, alt: string): string {
  if (!p || !Array.isArray(p.x) || !p.x.length || !Array.isArray(p.series) || !p.series.length) return "";
  const vals = p.series.flatMap((s) => (s.values || []).filter((v): v is number => typeof v === "number" && Number.isFinite(v)));
  if (!vals.length) return "";
  const nd = typeof p.decimals === "number" ? p.decimals : 2, unit = p.unit ? ` ${p.unit}` : "";
  const W = 640, H = 300, L = 64, R = 16, T = 16, B = 36;
  let lo = Math.min(...vals), hi = Math.max(...vals);
  if (lo === hi) { lo -= 1; hi += 1; }
  const n = p.x.length;
  const X = (i: number) => L + (n === 1 ? (W - L - R) / 2 : (i * (W - L - R)) / (n - 1));
  const Y = (v: number) => T + ((hi - v) * (H - T - B)) / (hi - lo);
  const f = (v: number) => v.toFixed(1);
  const parts: string[] = [
    `<svg class="digest-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${svgEscape(alt)}" xmlns="http://www.w3.org/2000/svg">`,
    `<title>${svgEscape(alt)}</title>`,
    `<line x1="${L}" y1="${H - B}" x2="${W - R}" y2="${H - B}" stroke="var(--color-rule, #E3DED1)"/>`,
    `<text x="${L - 6}" y="${f(Y(hi)) }" text-anchor="end" dominant-baseline="middle" font-size="12" fill="var(--color-muted, #6B675F)">${svgEscape(chartNumber(hi, nd))}</text>`,
    `<text x="${L - 6}" y="${f(Y(lo))}" text-anchor="end" dominant-baseline="middle" font-size="12" fill="var(--color-muted, #6B675F)">${svgEscape(chartNumber(lo, nd))}</text>`,
    `<text x="${L}" y="${H - 12}" font-size="12" fill="var(--color-muted, #6B675F)">${svgEscape(String(p.x[0]))}</text>`,
    `<text x="${W - R}" y="${H - 12}" text-anchor="end" font-size="12" fill="var(--color-muted, #6B675F)">${svgEscape(String(p.x[n - 1]))}</text>`,
  ];
  p.series.forEach((s, k) => {
    const color = SVG_COLORS[k % SVG_COLORS.length];
    const pts: string[] = [];
    const dots: string[] = [];
    (s.values || []).slice(0, n).forEach((v, i) => {
      if (typeof v !== "number" || !Number.isFinite(v)) return;
      pts.push(`${f(X(i))},${f(Y(v))}`);
      const hover = `${p.series.length > 1 ? `${s.name}, ` : ""}${p.x[i]}: ${chartNumber(v, nd)}${unit}`;
      dots.push(`<circle cx="${f(X(i))}" cy="${f(Y(v))}" r="3" fill="${color}"><title>${svgEscape(hover)}</title></circle>`);
    });
    if (pts.length > 1) parts.push(`<polyline points="${pts.join(" ")}" fill="none" stroke="${color}" stroke-width="1.8"${k ? ' stroke-dasharray="5 3"' : ""}/>`);
    parts.push(...dots);
  });
  parts.push("</svg>");
  return parts.join("");
}
