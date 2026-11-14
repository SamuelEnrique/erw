// Energy Research Warehouse (ERW) site, session 6111 (chain 280): a column of prose is named, not listed. A module of its
// own with no imports (so `node --test` reads it without a build), as warehouse/chat/tools.py holds the same rule
// (split_long_text, LONG_TEXT, LONG_TEXT_NOTE).
//
// describe_table lists the values of every text column of a table of things or events that has 60 distinct values or
// fewer. The large-load research tables of 14 November 2026 (utility_large_load_rules, state_large_load_laws) are small
// and hold whole clauses as their source printed them (a law's requirements, a rule's exit fee): describing one through
// the Python tools returned 80 to 90 KB, most of it prose no question had asked for, read again by every later call of
// the answer. A column whose longest value is over LONG_TEXT characters is prose: the description gives its name, how
// many distinct values it has and the longest one's length, and the note says how one row's text is read.

export const LONG_TEXT = 200;
export const LONG_TEXT_NOTE = "columns of prose as the source printed it (a value is over 200 characters): their values are not listed here. " +
  "To read one row's text, call query with aggregation count, group_by set to the column, and where narrowed to that row " +
  "(by a short column listed above, such as a state, a status or an id); the text comes back as the group's key.";

export type LongColumn = { distinct: number; longest_chars: number };

/** The columns whose values are short, as given, and the columns of prose with the count of their distinct values and
 * the longest one's length. `values` maps a column to the values seen (a list here; a dict of counts in the Python tool). */
export function splitLongText<T extends string[] | Record<string, number>>(values: Record<string, T>, limit = LONG_TEXT): { short: Record<string, T>; long: Record<string, LongColumn> } {
  const short: Record<string, T> = {}, long: Record<string, LongColumn> = {};
  for (const [col, vals] of Object.entries(values)) {
    // the desk's fix (session 3976, chain 278): a list typed as one array, or Next's type check finds reduce not callable
    const list: string[] = Array.isArray(vals) ? (vals as string[]) : Object.keys(vals);
    const longest = list.reduce((m, v) => Math.max(m, String(v).length), 0);
    if (longest > limit) long[col] = { distinct: list.length, longest_chars: longest };
    else short[col] = vals;
  }
  return { short, long };
}
