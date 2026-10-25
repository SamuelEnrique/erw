// Session 2702 (docs/reviews/periodicals-rulings-2026-10-23.md, item 19, the default of 24 October 2026): a figure the
// license holds of 21 October draws "license needed" where its number was (lib/license.ts LICENSE_NEEDED; components/Num
// and NoData mark it with data-license-held). Each such mark counts toward the page's floor in check-values.mjs, so the
// gate fails on a lost figure and not on a held one. Standard library only, so a test can import it without the site.

/** The held figures a page draws: its data-license-held marks, or where a page draws none, the times its visible text
 *  says "license needed" (tags and attribute values left out). */
export function heldMarks(html) {
  const marks = (String(html).match(/data-license-held=/g) || []).length;
  if (marks) return marks;
  const text = String(html).replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]*>/g, " ");
  return (text.match(/license needed/gi) || []).length;
}

/** The floor's verdict for a page: { counted, fail } where counted is the checked numbers and the held marks together. */
export function floorVerdict(count, held, floor) {
  const counted = count + held;
  return { counted, fail: floor !== undefined && counted < floor };
}
