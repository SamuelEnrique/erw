// Energy Research Warehouse (ERW) site, session 292: the guided tour against today's pages (the heading check).
//
//   node scripts/check-tour.mjs [base-url]          (default http://localhost:3000)
//
// In a real browser (scripts/browser.mjs), in the internal view (the pages are in review; a link to a page in review is
// drawn as a link only once the browser knows the internal view, so the links are read from the page as it runs): opens
// the tour's first page and each stop of the guided path (/tour/1 to /tour/N, lib/tour.ts) and checks each has the
// progress bar, Back and Next and its link to the stop's page; then opens each stop's own page and checks that every
// heading its "what to look at" quotes (`headings` in lib/tour.ts) is one of the page's h1 to h3. A page that renames a
// heading fails the check, so the tour cannot send a reader to a heading that is gone (session 279's review, "Done for
// real users", item 4). Every request carries x-erw-check: 1. Exit 1 on any failure; "not proven" (exit 0) without a
// browser.
import { withBrowser, sleep } from "./browser.mjs";
import { STOPS, stopPath } from "../lib/tour.ts";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const LINKS = `[...document.querySelectorAll('main a[href]')].map((a) => ({ href: a.getAttribute('href'), rel: a.getAttribute('rel') ?? '', open: a.hasAttribute('data-tour-open'), text: a.innerText.trim() }))`;
const HEADS = `[...document.querySelectorAll('main h1, main h2, main h3')].map((h) => h.innerText.replace(/\\s+/g, ' ').trim())`;

const code = await withBrowser(async ({ go, evaluate, unlock, send }) => {
  await send("Network.setExtraHTTPHeaders", { headers: { "x-erw-check": "1" } });
  await unlock(base);
  await go(`${base}/tour`); await sleep(400);
  const first = await evaluate(LINKS);
  check(await evaluate(`!!document.querySelector('[data-tour-bar="0"]')`) && STOPS.every((_, i) => first.some((l) => l.href === stopPath(i + 1))), `/tour: the bar and a link to each of the ${STOPS.length} stops`);
  for (const [i, s] of STOPS.entries()) {
    const k = i + 1;
    await go(`${base}${stopPath(k)}`); await sleep(300);
    const links = await evaluate(LINKS);
    check(await evaluate(`!!document.querySelector('[data-tour-bar="${k}"]')`), `${stopPath(k)}: the progress bar at stop ${k} of ${STOPS.length}`);
    const back = links.find((l) => l.rel === "prev"), next = links.find((l) => l.rel === "next");
    check(!!back && back.href === (k === 1 ? "/tour" : stopPath(k - 1)) && (k === STOPS.length ? !next : next?.href === stopPath(k + 1)), `${stopPath(k)}: Back${k < STOPS.length ? " and Next" : ""}`);
    check(links.some((l) => l.open && l.href === s.href), `${stopPath(k)}: opens ${s.href}`);
    await go(`${base}${s.href}`); await sleep(800);
    const hs = await evaluate(HEADS);
    check(!(await evaluate(`!!document.querySelector('[data-in-review="1"]')`)), `${s.href}: answers in the internal view`);
    for (const q of s.headings) check(hs.includes(q), `${s.href}: the heading "${q}" is on the page${hs.includes(q) ? "" : ` (its headings: ${hs.slice(0, 12).join(" | ")})`}`);
  }
  return bad;
});
if (code === null) { console.log("check-tour: NOT PROVEN (no browser on this machine)"); process.exit(0); }
console.log(`the tour: ${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
