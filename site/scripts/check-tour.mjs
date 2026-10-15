// Energy Research Warehouse (ERW) site, session 292: the guided tour against today's pages (the heading check).
//
//   node scripts/check-tour.mjs [base-url]          (default http://localhost:3000)
//
// Opens the tour's first page and each stop of the guided path (/tour/1 to /tour/N, lib/tour.ts) and checks each has the
// progress bar, Back and Next and its link to the stop's page; then opens each stop's own page, following redirects, and
// checks that every heading its "what to look at" quotes (`headings` in lib/tour.ts) is one of the page's h1 to h3, in
// the internal view (the pages are in review: INTERNAL_COSTS_TOKEN from the environment or site/.env.local). A page that
// renames a heading fails the check, so the tour cannot send a reader to a heading that is gone (session 279's review,
// "Done for real users", item 4). Every request carries x-erw-check: 1. Exit 1 on any failure.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { STOPS, stopPath } from "../lib/tour.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const env = (k) => process.env[k] ?? (fs.readFileSync(path.join(here, "..", ".env.local"), "utf-8").match(new RegExp(`^${k}=(.*)$`, "m"))?.[1] ?? "").trim();
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

let cookie = "";
const tok = env("INTERNAL_COSTS_TOKEN");
if (tok) {
  const u = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(tok)}`, { redirect: "manual", headers: { "x-erw-check": "1" } });
  cookie = (u.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
}
check(cookie !== "", "the internal view opens (the pages are in review)");
const get = async (p) => {
  const r = await fetch(base + p, { headers: { cookie, "x-erw-check": "1" } });
  return { status: r.status, html: await r.text() };
};
const text = (h) => h.replace(/<!--.*?-->/gs, "").replace(/<[^>]+>/g, "").replace(/&#x27;|&#39;|&apos;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
const headings = (html) => {
  const main = html.match(/<main[\s\S]*?<\/main>/)?.[0] ?? html;
  return [...main.matchAll(/<h([123])[^>]*>([\s\S]*?)<\/h\1>/g)].map((m) => text(m[2]));
};

const first = await get("/tour");
check(first.status === 200 && first.html.includes('data-tour-bar="0"') && STOPS.every((s, i) => first.html.includes(`href="${stopPath(i + 1)}"`)), `/tour: the bar and a link to each of the ${STOPS.length} stops`);
for (const [i, s] of STOPS.entries()) {
  const k = i + 1;
  const t = await get(stopPath(k));
  const h = t.html;
  check(t.status === 200 && h.includes(`data-tour-bar="${k}"`), `${stopPath(k)}: the progress bar at stop ${k} of ${STOPS.length}`);
  check(h.includes('rel="prev"') && (k === STOPS.length || h.includes(`href="${stopPath(k + 1)}" rel="next"`) || h.includes('rel="next"')), `${stopPath(k)}: Back${k < STOPS.length ? " and Next" : ""}`);
  check(h.includes(`href="${s.href}"`) && h.includes("data-tour-open"), `${stopPath(k)}: opens ${s.href}`);
  const page = await get(s.href);
  const hs = headings(page.html);
  check(page.status === 200 && !page.html.includes('data-in-review="1"'), `${s.href}: answers in the internal view (HTTP ${page.status})`);
  for (const q of s.headings) check(hs.includes(q), `${s.href}: the heading "${q}" is on the page${hs.includes(q) ? "" : ` (its headings: ${hs.slice(0, 12).join(" | ")})`}`);
}
console.log(`the tour: ${n - bad} of ${n} checks pass`);
process.exit(bad ? 1 : 0);
