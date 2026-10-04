// Energy Research Warehouse (ERW) site: warm the live pages (session 90).
//
//   node scripts/warm-live.mjs [base-url]     (default http://localhost:3000)
//
// Asks for every live page once, as a visitor, one at a time: the pages scripts/snapshot-live.mjs reads (the six live
// pages, with the battery page for both grids at 2, 4 and 8 hours under both strategies, the seller tab's California
// solar and wind, /terms and the four live methods pages). The first request for a page after a build or a deploy finds the database's tables cold and is the
// slow one; three deploys in a row lost one read of the home page that way (sessions 77, 87, 88). The workflow runs
// this against the build it has just started, before the route check, so the check and the deploy that follows the
// merge find the tables warm.
//
// A page that does not answer 200 is asked again, up to three times, ten seconds apart. Prints one line per page with
// its status, its time and how many "no data" blocks it shows; exits 1 if a page never answered 200. It judges
// nothing else: the route check and the snapshot comparison do that.
import { LIVE_PAGES } from "./snapshot-live.mjs";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const REQUEST_MS = Number(process.env.WARM_REQUEST_S ?? 60) * 1000;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let failed = 0;
const started = Date.now();
for (const page of LIVE_PAGES) {
  let line = "";
  let ok = false;
  for (let attempt = 1; attempt <= 3 && !ok; attempt++) {
    const t = Date.now();
    try {
      const res = await fetch(base + page, { redirect: "manual", signal: AbortSignal.timeout(REQUEST_MS) });
      const html = await res.text();
      const noData = (html.match(/<span class="font-semibold[^"]*">no data<\/span>/g) ?? []).length;
      const notHeld = (html.match(/>not held</g) ?? []).length;
      ok = res.status === 200;
      line = `${res.status} ${page}: ${((Date.now() - t) / 1000).toFixed(1)} s, ${noData} "no data", ${notHeld} "not held"${attempt > 1 ? `, try ${attempt}` : ""}`;
    } catch (e) {
      line = `FAILED ${page}: ${String(e?.message ?? e)}${attempt > 1 ? `, try ${attempt}` : ""}`;
    }
    if (!ok && attempt < 3) await sleep(10_000);
  }
  console.log(line);
  if (!ok) failed++;
}
console.log(`warmed ${LIVE_PAGES.length - failed} of ${LIVE_PAGES.length} live pages at ${base} in ${((Date.now() - started) / 1000).toFixed(0)} s${failed ? `; ${failed} never answered 200` : ""}`);
process.exit(failed ? 1 : 0);
