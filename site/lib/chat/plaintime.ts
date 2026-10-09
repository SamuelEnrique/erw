// Energy Research Warehouse (ERW) site, session 168: times in an answer in plain local words, and a question without a
// stray quote mark. Pure functions, no imports: the server (lib/chat/tools.ts, lib/chat/ask.ts, app/api/ask) and the
// panel (components/ask/AskPanel.tsx) share them; scripts/test-ask-168.mjs tests them.
//
// WHERE THE STAMP CAME FROM. The query tool gives each time it reports (the hour of a maximum, the newest row) as the
// table holds it, a UTC stamp such as 2026-10-03T21:00:00Z, and the answer's rule is that every number in it must be
// in a tool result. So the model copied the stamp: it was the only way to write the hour that passed the number check.
// Since session 168 the tool gives the same moment in the grid's own local words beside it ("at_local": "4 pm
// Central, 3 October 2026"), computed here with the zone database (daylight saving included), so the words the model
// copies are in a tool result and pass the same check. A stamp the model writes anyway is turned into the same words
// before the reader sees it (plainTimes), after the check has run on the text as written.

/** The plain word for a grid's zone. */
export const ZONE_WORD: Record<string, string> = {
  "America/Chicago": "Central", "America/New_York": "Eastern", "America/Los_Angeles": "Pacific", "America/Denver": "Mountain", "America/Phoenix": "Mountain",
};

/** The zone of a series' entity, by its grid; null where the entity names no grid of the ERW's seven. */
export function zoneOfEntity(entity: string | null | undefined): string | null {
  const e = String(entity ?? "").toLowerCase();
  if (/^(ercot|miso|spp):|^eia930:(erco|miso|swpp)\b/.test(e)) return "America/Chicago";
  if (/^caiso:|^eia930:ciso\b/.test(e)) return "America/Los_Angeles";
  if (/^(nyiso|isone|iso-ne|pjm):|^eia930:(nyis|isne|pjm)\b/.test(e)) return "America/New_York";
  return null;
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const STAMP = /\b(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?(Z|[+-]\d{2}:?\d{2})/g;
const DATE = /(?<![\dA-Za-z:-])(\d{4})-(\d{2})-(\d{2})(?![\dT:]|-\d)/g;

/** "3 October 2026" for a date label (YYYY-MM-DD, or the 00:00Z stamp a table of days labels its day with). */
export function plainDate(label: string): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(label);
  if (!m) return null;
  const mo = Number(m[2]), d = Number(m[3]);
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
  return `${d} ${MONTHS[mo - 1]} ${m[1]}`;
}

/** "4 pm Central, 3 October 2026" for an instant, in the zone given (the zone database decides daylight saving);
 * "4:15 pm" when the minute is not zero; "12 am" is midnight and "12 pm" noon. null for a stamp that is not a time. */
export function plainTime(iso: string, zone: string): string | null {
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return null;
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: zone, year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "2-digit", hourCycle: "h23" })
    .formatToParts(new Date(t)).map((x) => [x.type, x.value]));
  const h = Number(p.hour) % 24, mi = Number(p.minute);
  const clock = `${h % 12 === 0 ? 12 : h % 12}${mi ? `:${String(mi).padStart(2, "0")}` : ""} ${h < 12 ? "am" : "pm"}`;
  const word = ZONE_WORD[zone] ?? zone;
  return `${clock} ${word}, ${Number(p.day)} ${MONTHS[Number(p.month) - 1]} ${p.year}`;
}

/** The local words of every time a tool result gives, beside it: `at` gains `at_local`, `newest_row_at` gains
 * `newest_row_at_local`, a time span's `first` and `last` gain `first_local` and `last_local`. On a table of days or
 * longer (`dated`) a time is the label of a local day, so it reads as a date. Returns the pairs added, stamp to words. */
export function addLocalTimes(out: Record<string, unknown>, dated: boolean, zone: string | null): Map<string, string> {
  const added = new Map<string, string>();
  const words = (v: unknown): string | null => {
    if (typeof v !== "string" || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(v)) return null;
    if (dated) return plainDate(v);
    return zone ? plainTime(v, zone) : null;
  };
  const mark = (o: Record<string, unknown>, keys: string[]) => {
    for (const k of keys) {
      const w = words(o[k]);
      if (w && !(`${k}_local` in o)) { o[`${k}_local`] = w; added.set(String(o[k]), w); }
    }
  };
  for (const r of Array.isArray(out.result) ? out.result : []) if (r && typeof r === "object") mark(r as Record<string, unknown>, ["at"]);
  if (out.newest && typeof out.newest === "object") mark(out.newest as Record<string, unknown>, ["newest_row_at"]);
  if (out.week && typeof out.week === "object") mark(out.week as Record<string, unknown>, ["newest_row_at"]);
  if (out.time_span && typeof out.time_span === "object") mark(out.time_span as Record<string, unknown>, ["first", "last"]);
  if (zone && !dated && Object.keys(out).length) {
    const z = ZONE_WORD[zone];
    if (z && added.size) out.times_local = `each time with "_local" beside it is the same moment in ${z} time (${zone}, daylight saving included): write that, not the UTC stamp`;
  }
  return added;
}

/** An answer's text with every UTC stamp in plain local words: a stamp a tool result gave words for takes those words;
 * any other stamp is read in the zone given, except a 00:00Z stamp, which on the ERW's tables of days is a day's label
 * and reads as a date. A bare date (2026-10-03) reads as "3 October 2026". */
export function plainTimes(text: string, zone: string | null, known: Map<string, string> = new Map()): string {
  if (!text) return text;
  let s = text.replace(STAMP, (m) => {
    if (known.has(m)) return known.get(m)!;
    const norm = m.replace(/\.\d+(?=Z)/, "").replace(/(T\d{2}:\d{2})(Z)$/, "$1:00$2");
    if (known.has(norm)) return known.get(norm)!;
    if (/T00:00(:00)?(\.0+)?Z$/.test(m)) return plainDate(m) ?? m;
    return zone ? plainTime(m, zone) ?? m : m;
  });
  s = s.replace(DATE, (m) => plainDate(m) ?? m);
  return s;
}

/** A question as asked, without the quote marks it was pasted with: a pair around the whole question, or one quote mark
 * left at either end with no partner (`What was ERCOT's peak demand yesterday?"`). An apostrophe inside is kept. */
export function cleanQuestion(q: string): string {
  let s = String(q ?? "").trim();
  const open = /^["“”„]/, close = /["“”]$/;
  for (let i = 0; i < 3; i += 1) {
    const before = s;
    const n = (s.match(/["“”„]/g) ?? []).length;
    if (open.test(s) && close.test(s) && s.length > 1) s = s.slice(1, -1).trim();
    else if (n % 2 === 1 && close.test(s)) s = s.slice(0, -1).trim();
    else if (n % 2 === 1 && open.test(s)) s = s.slice(1).trim();
    if (s === before) break;
  }
  return s;
}
