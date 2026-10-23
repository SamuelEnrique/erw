// Energy Research Warehouse (ERW) site, session 1153 (chain 077): a link of a picker that carries words of the address
// it is drawn in. The Grid tool's Gravity tab keeps the replay's day (net=day and t) when the reader picks another grid,
// so the day picked stays in the address. Pure, no imports, so a node test reads this file as it is
// (scripts/test-gravity.mjs); components/tool/CarryLink.tsx draws it.

/** Carry `words` from the address into a link when the address's `when` word reads `is` (net=day: carry net and t). */
export type Carry = { when: string; is: string; words: string[] };

/** The link `href` with the carried words of `search` set on it; unchanged when the address does not ask for it. */
export function carryWords(href: string, search: string, c: Carry): string {
  const from = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  if (from.get(c.when) !== c.is) return href;
  const at = href.indexOf("?");
  const path = at < 0 ? href : href.slice(0, at);
  const to = new URLSearchParams(at < 0 ? "" : href.slice(at + 1));
  let changed = false;
  for (const w of c.words) {
    const v = from.get(w);
    if (v) { to.set(w, v); changed = true; }
  }
  return changed ? `${path}?${to.toString()}` : href;
}

/** The Gravity tab's carry: the replay's day, net=day with its date t. */
export const KEEP_DAY: Carry = { when: "net", is: "day", words: ["net", "t"] };
