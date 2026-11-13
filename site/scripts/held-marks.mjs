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

/** Session 4000: the reason a page says it has no issue today, "pending" (the Digest is written by the daily run from
 *  14:00 UTC) or "weekend" (no weekday Digest), else null. /digest is today's issue only (session 402), so before the
 *  daily run and at weekends it carries no checked number by design and its floor is not judged; "missed" (no issue
 *  after the run) is not a reason and still fails the floor. */
export function noIssueToday(html) {
  const m = /data-digest-none="(pending|weekend)"/.exec(String(html));
  return m ? m[1] : null;
}

/** The floor's verdict for a page: { counted, fail } where counted is the checked numbers and the held marks together. */
export function floorVerdict(count, held, floor) {
  const counted = count + held;
  return { counted, fail: floor !== undefined && counted < floor };
}
