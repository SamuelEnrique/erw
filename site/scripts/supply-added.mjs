// Energy Research Warehouse (ERW) site, session 8430 (chain 503, part D): what the session added to /supply stands
// between two marks, so a test can cut it out and hold the rest of the page to what it was (scripts/test-supply-pin.mjs).
// The section "The whole country" opens with <section data-whole-country="supply"> and is followed by
// <span data-whole-country-end="1"></span>, the marks session 8410 gave the same section of the event pages. Here too
// are the two stand-ins a draw of the whole page needs to be the same on any day: a clock that stands still, and an
// answer for the one read the page makes of the live set (the catalogue, for its line of downloads).

/** The page without what session 8430 added. */
export function withoutSupplyAdded(html) {
  return html.replace(/<section data-whole-country="supply"[\s\S]*?<span data-whole-country-end="1"><\/span>/g, "");
}

/** The section alone, or "" when the page has none. */
export function supplyAdded(html) {
  return (/<section data-whole-country="supply"[\s\S]*?<span data-whole-country-end="1"><\/span>/.exec(html) ?? [""])[0];
}

/** The count of the page's own checked figures (its data-n marks) in a piece of HTML. */
export const figureCount = (html) => (html.match(/ data-n="/g) ?? []).length;

/** `new Date()` and `Date.now()` answer `iso` from here on (a date built from a value is untouched). The page works out
 *  its next releases and the day's license holds from the clock, so a pin needs it to stand still. Returns the undo. */
export function fixClock(iso) {
  const Real = globalThis.Date;
  const at = Real.parse(iso);
  if (!Number.isFinite(at)) throw new Error(`fixClock: ${iso} is not a time`);
  class Fixed extends Real {
    constructor(...a) { if (a.length) super(...a); else super(at); }
    static now() { return at; }
  }
  globalThis.Date = Fixed;
  return () => { globalThis.Date = Real; };
}

/** The page's one read of the live set, answered here and never sent. `read` true: the catalogue answers with one row
 *  that is none of the page's tables (a stand-in, not data), so the line of downloads is drawn as read; false: no
 *  database is named, so the line says the catalogue was not read. Returns the undo. */
export function standInCatalogue(read) {
  const real = globalThis.fetch;
  const url = process.env.SUPABASE_URL, key = process.env.SUPABASE_ANON_KEY;
  if (read) {
    process.env.SUPABASE_URL = "http://localhost:9/";
    process.env.SUPABASE_ANON_KEY = "stand-in";
  } else {
    delete process.env.SUPABASE_URL;
    delete process.env.SUPABASE_ANON_KEY;
  }
  globalThis.fetch = async () => new Response(JSON.stringify([{ table_name: "stand_in_not_a_table", license: "public", in_live_set: "yes" }]), { status: 200, headers: { "content-type": "application/json" } });
  return () => {
    globalThis.fetch = real;
    if (url === undefined) delete process.env.SUPABASE_URL; else process.env.SUPABASE_URL = url;
    if (key === undefined) delete process.env.SUPABASE_ANON_KEY; else process.env.SUPABASE_ANON_KEY = key;
  };
}
