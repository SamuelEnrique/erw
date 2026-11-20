// Energy Research Warehouse (ERW) site, chain 507 (session 8902): the tour's first page and each new stop drawn to HTML
// with the site's own code, without a build.
//   node --import ./scripts/events-page-register.mjs scripts/test-tour-render.mjs   (the site's loaders and the stand-in for next/font)
// Checks: the first page lists every stop of the path, the ruled seven first; each new stop has its title, its line,
// what to look at and its address; a held stop (landed: false) is on no page; no em dash. Exit 0
// when all hold, 1 otherwise. No network.
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { STOPS, RULED_STOPS, HELD_STOPS, stopPath } = await import("../lib/tour.ts");
const { default: Tour } = await import("../app/tour/page.tsx");
const fails = [];
const check = (ok, what) => { if (!ok) fails.push(what); };
const esc = (s) => s.replace(/&/g, "&amp;").replace(/'/g, "&#x27;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const dash = String.fromCharCode(0x2014);

const first = renderToStaticMarkup(h(Tour));
check(STOPS.length > RULED_STOPS.length, "no new stop on the path");
STOPS.forEach((s, i) => check(first.includes(`href="${stopPath(i + 1)}"`) && first.includes(esc(s.title)), `the first page: stop ${i + 1} (${s.title})`));
check(first.indexOf(esc(RULED_STOPS[6].title)) < first.indexOf(esc(STOPS[7].title)), "the ruled seven are not first");
for (const s of HELD_STOPS) check(!first.includes(esc(s.title)), `a held stop is listed: ${s.title}`);
check(!first.includes(dash), "an em dash on the first page");

// a stop's own page (app/tour/[stop]/page.tsx) imports next/navigation, which only a build serves: its words are held
// here from the stop's fields, and check-tour reads the page itself on a build (browser read)
for (const s of STOPS.slice(RULED_STOPS.length)) {
  check(s.title && s.line.length > 40 && s.look.length > 20 && s.href.startsWith("/"), `${s.title}: a field is missing`);
  check(![s.title, s.line, s.look].join(" ").includes(dash), `${s.title}: an em dash`);
}

if (fails.length) { console.log(`FAIL ${fails.length}:\n  ${fails.join("\n  ")}`); process.exitCode = 1; }
else console.log(`ok: ${STOPS.length} stops on the path (${STOPS.length - RULED_STOPS.length} new), ${HELD_STOPS.length} held until their pages land`);
