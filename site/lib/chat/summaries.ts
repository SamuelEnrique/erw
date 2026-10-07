// Energy Research Warehouse (ERW) site, session 143: what the planner needs to know about each table, held ready.
//
// Pure functions, no imports (Node runs this file as it is, for site/scripts/test-ask-speed.mjs). Before this session
// a question about numbers often spent a model call and a large read finding out what a table holds (describe_table
// reads up to 60,000 rows to list a table's variables) or how far its rows reach. Now each table's summary (its first
// and last date and its number of rows in the site's live set, and for the tables whose guide gives no names, its
// variables) is read once and kept in the server's memory for a short life, and every question is given the summaries.
//
// THE RISK IS A STALE LAST DATE (session 137's fault 4: the tool believed a date printed in its guide and refused
// yesterday's demand without a query). Three things keep a summary from hiding a newer day:
//   1. a summary lives LIFE_MS, ten minutes, and is then read again; a failed read is never kept;
//   2. the text the model is given says when it was read and that the tables grow: a query's own rows govern;
//   3. the rule of session 137 stands: no recent day is called "not held" without a query that came back empty.
// A summary only tells the planner where to look. Every number of an answer still comes from a tool result.

export const LIFE_MS = 600_000;          // a summary's dates and counts: ten minutes
export const NAMES_LIFE_MS = 21_600_000; // a table's variable names: six hours (a name changes only when the table's shape does)

/** held false: the table is not in this site's live set. dated false: a table of things or of events, with no row dates. */
export type Summary = { table: string; first: string | null; last: string | null; rows: number | null; variables?: string[]; held?: boolean; dated?: boolean; /** the read failed: the table is left out of the list */ unread?: boolean };

/** A cache of one value per key with a life: a value older than its life is read again; a read that fails is not kept
 * (the next question tries again) and is never an answer. Reads of one key in flight are shared. */
export function keep<T>(life: number, read: (key: string) => Promise<T>, now: () => number = Date.now) {
  const held = new Map<string, { at: number; value: Promise<T> }>();
  return {
    get(key: string): Promise<T> {
      const h = held.get(key);
      if (h && now() - h.at < life) return h.value;
      const value = read(key);
      const entry = { at: now(), value };
      held.set(key, entry);
      value.catch(() => { if (held.get(key) === entry) held.delete(key); });
      return value;
    },
    /** The age of what is held for a key, in milliseconds; null when nothing is held. */
    age(key: string): number | null { const h = held.get(key); return h ? now() - h.at : null; },
    clear(): void { held.clear(); },
  };
}

/** The first of the promise's value or null after `ms` milliseconds: a question never waits long for a summary. */
export function within<T>(p: Promise<T>, ms: number): Promise<T | null> {
  return new Promise((done) => {
    const t = setTimeout(() => done(null), ms);
    p.then((v) => { clearTimeout(t); done(v); }, () => { clearTimeout(t); done(null); });
  });
}

/** Names that differ only in an hour of the day ("avg_wind_mw_h00" to "avg_wind_mw_h23") written once. */
export function foldHours(names: string[]): string[] {
  const out: string[] = [], hours = new Map<string, string[]>();
  for (const n of names) {
    const m = /^(.*_h)(\d\d)$/.exec(n);
    if (!m) { out.push(n); continue; }
    if (!hours.has(m[1])) { hours.set(m[1], []); out.push(`\u0000${m[1]}`); }
    hours.get(m[1])!.push(m[2]);
  }
  return out.map((n) => {
    if (!n.startsWith("\u0000")) return n;
    const stem = n.slice(1), hh = hours.get(stem)!.sort();
    return hh.length > 2 ? `${stem}${hh[0]} to ${stem}${hh[hh.length - 1]}` : hh.map((h) => stem + h).join(", ");
  });
}

const day = (t: string | null) => (t ? t.slice(0, 10) : "none");

/** The summaries as the model is given them. `readAt` is the oldest moment any of them was read (an ISO time). */
export function summaryText(rows: Summary[], readAt: string): string {
  if (!rows.length) return "";
  const lines = rows.map((r) => (r.held === false ? `- ${r.table}: not in this site's live set (a query of it answers so)`
    : `- ${r.table}: ${r.dated === false ? "" : r.first || r.last ? `rows dated ${day(r.first)} to ${day(r.last)}` : "no rows"}${r.rows === null ? "" : `${r.dated === false ? "" : ", "}${r.rows} rows`}${r.variables?.length ? `. Variables: ${foldHours(r.variables).join(", ")}` : ""}`));
  return `THE TABLES NOW (read at ${readAt.slice(0, 16)}Z from the warehouse's catalogue: each table's first and last row as of its last load, all grids together; these dates are newer than the guide's and govern where the two differ). ` +
    "They say where to look, so go straight to query: do not call describe_table or list_tables for anything written here. " +
    "The tables grow every day, this list is up to ten minutes old and a table's last row for one grid can be a day off the table's: a query's own rows govern, and a day after a table's last date here is still queried before it is called not held.\n" +
    lines.join("\n");
}
