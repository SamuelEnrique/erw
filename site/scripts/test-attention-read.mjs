// Energy Research Warehouse (ERW) site, session 7563: the attention page read as a datacenter developer's
// community-relations lead would read it (docs/reviews/attention-read-2026-11-16.md, row 2). "What rose" now says how
// many stories the week holds beside the four classified weeks before it, on the site's own file
// (site/data/attention.json, built 2026-11-16), and the view drawn to HTML by its own component says it.
//   cd site && node --import ./scripts/tsx-register.mjs scripts/test-attention-read.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const A = await import("../lib/attention.ts");
const { AttentionView } = await import("../app/attention/AttentionView.tsx");
const f = JSON.parse(fs.readFileSync(new URL("../data/attention.json", import.meta.url), "utf-8"));

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };

const nov2 = f.weeks.findIndex((w) => w.startsWith("2026-11-02"));
const oct26 = f.weeks.findIndex((w) => w.startsWith("2026-10-26"));
const oct05 = f.weeks.findIndex((w) => w.startsWith("2026-10-05"));
const b = A.weekBesideBefore(f, nov2);
check(b && b.held === 631 && b.low === 1954 && b.high === 3146 && b.weeks === 4, `week of 2 November: 631 stories beside 1,954 to 3,146 in the 4 weeks before (${JSON.stringify(b)})`);
check(A.besideWords(b).includes("This week holds 631 stories; the 4 classified weeks before it held 1,954 to 3,146.") && A.besideWords(b).includes("thin"), "the words say so, and that the week is thin");
const c = A.weekBesideBefore(f, oct26);
check(c && c.weeks === 3 && !A.besideWords(c).includes("thin"), "week of 26 October: 3 classified weeks before, not thin");
check(A.weekBesideBefore(f, oct05) === null && A.besideWords(null) === "", "the first classified week has none before it: no words");

// the view as it opens draws the What rose note with the opening week's words
const html = renderToStaticMarkup(h(AttentionView, { file: f, statesGeo: { type: "FeatureCollection", features: [] } }));
const open = A.openingWeek(f);
const words = A.besideWords(A.weekBesideBefore(f, open));
check(words === "" || html.includes(words.trim().slice(0, 40)), `the opening week's What rose note carries the words (opening week ${f.weeks[open].slice(0, 10)})`);

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
