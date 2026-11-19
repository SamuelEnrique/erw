// Energy Research Warehouse (ERW) site, ruling alternative 2 of /supply (wip/alt-supply-2, not a default on main),
// session 8401 (chain 503), browser row 366: at 390 px the page was 490 px wide. The box under the burn table drew its
// table of the two grids (six cells a row, each figure on one line) in no frame, while every other table of the page
// scrolls inside its own. The page is drawn whole by its own function (scripts/supply-read-page.mjs) on the site's own
// file, with two grids chosen and with none; only the frames are read, and no figure is printed.
//   node --import ./scripts/battery-awards-page-register.mjs scripts/test-alt-supply-ab-frame.mjs
// Exit 1 on a failure. Nothing is written. No server, no network, no click; no width is measured here.
import { drawSupply } from "./supply-read-page.mjs";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const count = (h, re) => (h.match(re) ?? []).length;

const two = await drawSupply("a=pjm&b=miso");
const box = (/<div id="ab"[^>]*data-burn-ab="pjm\|miso">([\s\S]*?)<\/table>/.exec(two) ?? ["", ""])[1];
ok(box !== "" && count(box, /data-burn-ab-row=/g) === 2, "with two grids chosen the box draws its table, a row for gas and a row for coal");
ok(/<\/form><div class="overflow-x-auto"><table\b/.test(box), "browser row 366: the box's table stands inside a frame that scrolls sideways");
ok(count(two, /<table\b/g) === 10 && count(two, /overflow-x-auto"><table\b/g) === count(two, /<table\b/g), `browser row 366: no table of the page stands outside a scrolling frame (${count(two, /overflow-x-auto"><table\b/g)} of ${count(two, /<table\b/g)})`);

const none = await drawSupply("");
ok(/data-burn-ab="none"/.test(none) && count(none, /<table\b/g) === 9 && count(none, /overflow-x-auto"><table\b/g) === 9, "with no grid chosen the box draws no table, and the page's nine tables keep their frames");
// the form's two lists and its button wrap (flex-wrap), so the box is no wider than the screen without its table
ok(/<form class="mb-2 flex flex-wrap items-end gap-2"/.test(none), "the box's form wraps its lists and its button");

console.log(`\n${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
