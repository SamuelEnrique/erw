// Energy Research Warehouse (ERW) site, session 369 (queue/todo/008, PRIORITIES.md layer 2, order 2): the date of every
// figure check-values.mjs reports for an event page.
//
// Session 58 read on /events/caiso-heat-2022 a key for 2022-09-01 (demand_max_mw 46,868 MW, demand_max_pct_vs_baseline
// 34.74 percent) while the page's headline named 2022-09-06 at 51,104 MW. Both were right (09-06 is the window's highest
// hour, 09-01 the day with the largest rise against its baseline), but the check's lines did not say which day each
// figure belonged to, and a key shared with /events was reported under /events only, so the page's own 51,104 MW line
// was missing from its lines. The check now:
//   - names the date (or the hour, or the event's window for a pooled estimate) of every key it reports for an event page;
//   - compares a key only with the table row of that same date (rowOfKey: never another day's row of the entity);
//   - fails a figure the page writes beside another date than its row's (writtenDate: "51,104 MW on 2022-09-06");
//   - reports a key under every event page that carries it.
// Pure functions: check-values.mjs reads the rows and the page; tests/test_session369.py runs them on real rows.

export const isEventPage = (page) => /^\/events(\/|\?|$)/.test(page);

/** The date a key's figure belongs to: { date, hour } (hour null for a day's row), { window: true } for an estimate
 * pooled over the event's window, or null when the key names neither. */
export function keyDate(check) {
  const p = check.split("|");
  if (p[0] === "series" && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(p[4] ?? "")) {
    const hour = p[4].slice(11, 16);
    return { date: p[4].slice(0, 10), hour: hour === "00:00" ? null : hour };
  }
  if (p[0] === "es") {   // es|<event>|<entity>|<variable>|<term>|<field>, term pooled, pooled_temp, weather_share or day|<date>
    if (p[4] === "day" && /^\d{4}-\d{2}-\d{2}$/.test(p[5] ?? "")) return { date: p[5], hour: null };
    if (["pooled", "pooled_temp", "weather_share"].includes(p[4])) return { window: true };
  }
  return null;
}

/** The words a line uses for a key's date. */
export const dateLabel = (kd) => (!kd ? "no date in its key" : kd.window ? "the event's window (pooled)" : kd.hour ? `${kd.date} ${kd.hour} UTC` : kd.date);

const DATE = /\b(\d{4}-\d{2}-\d{2})\b/g;
// a block boundary in the page (a paragraph, a cell, an item, a heading, a line break) ends a clause
const BLOCK = /<\/?(p|td|th|tr|li|ul|ol|h[1-6]|div|section|br|table|thead|tbody|caption|figcaption|summary|details)\b[^>]*>/gi;
const text = (html) => html.replace(BLOCK, "\n").replace(/<[^>]+>/g, "").replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"');

/** The date the page writes beside a figure, from the HTML between the previous figure and this one (`before`) and
 * between this one and the next (`after`): a date in the clause that follows the figure ("51,104 MW on 2022-09-06;"),
 * else the last date in the clause that leads to it ("rose most on 2022-09-01, 34.74%", "on 2022-09-01 (46,868 MW)").
 * A clause ends at a block boundary, a semicolon, a colon or a full stop; after the figure, at a comma or a bracket too.
 * null when no date stands beside it (a table's cell, whose day is its row's or its column's). */
export function writtenDate(beforeHtml, afterHtml) {
  const after = text(afterHtml).split(/[\n;:,()]|\.(?:\s|$)/)[0] ?? "";
  const a = [...after.matchAll(DATE)];
  if (a.length) return a[0][1];
  const parts = text(beforeHtml).split(/[\n;:]|\.(?:\s|$)/);
  const before = parts.at(-1) ?? "";
  const b = [...before.matchAll(DATE)];
  return b.length ? b.at(-1)[1] : null;
}

/** The date written beside the i-th figure of a page: `ms` are the page's data-check spans (matchAll), in order; the
 * text read is the page's between the figure and its neighbours, at most 400 characters each side. */
export function besideOf(html, ms, i) {
  const m = ms[i], end = m.index + m[0].length;
  const from = Math.max(i ? ms[i - 1].index + ms[i - 1][0].length : 0, m.index - 400);
  const to = Math.min(i + 1 < ms.length ? ms[i + 1].index : html.length, end + 400);
  return writtenDate(html.slice(from, m.index), html.slice(end, to));
}

/** The row of a key's own date (and hour) among rows of its entity and variable: never another date's row. */
export function rowOfKey(check, rows) {
  const kd = keyDate(check);
  if (!kd || kd.window) return undefined;
  const at = Date.parse(check.split("|")[0] === "series" ? check.split("|")[4] : `${kd.date}T00:00:00Z`);
  return rows.find((r) => Date.parse(r.ts_utc) === at);
}

/** One event-page figure against its rows: the row of its key's date must hold the page's value, and a date written
 * beside the figure must be that date. { pass, label, value, why }. */
export function compareDated({ check, raw, written }, rows) {
  const kd = keyDate(check);
  const label = dateLabel(kd);
  if (!kd || kd.window) return { pass: null, label, value: undefined, why: "" };   // compared by the check's own rule
  const r = rowOfKey(check, rows);
  if (!r) return { pass: false, label, value: undefined, why: `no row of ${label}` };
  const v = Number(r.value), x = Number(raw);
  if (!(Math.abs(v - x) < 1e-9 * Math.max(1, Math.abs(v)))) return { pass: false, label, value: v, why: `the row of ${label} holds ${v}, the page ${x}` };
  if (written && written !== kd.date) return { pass: false, label, value: v, why: `the page writes ${written} beside the figure of ${label}` };
  return { pass: true, label, value: v, why: "" };
}
