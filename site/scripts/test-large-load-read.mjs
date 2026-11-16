// Chain 305 (session 7600): the large-load rules read in a browser at 1280 and 390 px on 16 November 2026
// (docs/reviews/large-load-on-site/browser-read-2026-11-16.md). Each site fault the read found is held here as fixed;
// the row numbers are the review's. The components are drawn to HTML without a build (scripts/tsx-loader.mjs), the
// placing of a hover's box is run on windows of both widths, and the style sheet is read for the rules a browser
// needs. No server, no network, no click: what only a browser shows is in the review's own measures.
//   node --import ./scripts/tsx-register.mjs scripts/test-large-load-read.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const L = await import("../lib/largeloadrules.ts");
const S = await import("../lib/siting.ts");
const { SITING_FILES } = await import("../lib/sitingdata.ts");
const { LargeLoadRules } = await import("../app/cost-of-power/LargeLoadRules.tsx");
const { LargeLoadSection, RuleLine, rulesOfRow } = await import("../app/cost-of-power/LargeLoadSection.tsx");
const { StateLaws } = await import("../app/policy/StateLaws.tsx");
const { RuleCard } = await import("../components/largeload/parts.tsx");
const file = JSON.parse(fs.readFileSync(new URL("../data/siting/large_load_rules.json", import.meta.url), "utf-8"));
const css = fs.readFileSync(new URL("../app/tokens.css", import.meta.url), "utf-8").replace(/\r\n/g, "\n");
const src = (p) => fs.readFileSync(new URL(p, import.meta.url), "utf-8");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<span role="tooltip"[\s\S]*?<\/span>(?=<\/span>)/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const NONE = { state: "", grid: "", status: "", find: "", sort: "", dir: "", a: "", b: "", rule: "", region: "" };
const X = S.sitingInputs ? S.sitingInputs({}) : undefined;

// ---- rows 1 and 2: where a hover's box is drawn (lib/largeloadrules.ts, placeTip; components/largeload/TipPlace.tsx)
const tipBox = { width: 416, height: 320 };            // the section's box: 26rem wide, at most 20rem high
for (const win of [{ width: 1280, height: 900 }, { width: 390, height: 844 }]) {
  const box = { width: Math.min(tipBox.width, win.width * 0.8), height: tipBox.height };
  let past = 0, tried = 0;
  for (let left = 0; left <= win.width - 20; left += 7) for (let top = 0; top <= win.height - 20; top += 37) {
    const p = L.placeTip({ left, top, right: left + 60, bottom: top + 18 }, box, win);
    const height = Math.min(box.height, p.maxHeight);
    tried += 1;
    if (p.left < 0 || p.left + box.width > win.width || p.top < 0 || p.top + height > win.height) past += 1;
  }
  ok(tried > 500 && past === 0, `rows 1 and 2: at ${win.width} px a hover's box is inside the window wherever its trigger stands (${tried} places tried, ${past} past an edge)`);
}
{
  const win = { width: 1280, height: 900 };
  const under = L.placeTip({ left: 100, top: 100, right: 160, bottom: 118 }, tipBox, win);
  ok(under.left === 100 && under.top === 120 && !under.above, "rows 1 and 2: with room, the box opens under its trigger, at the trigger's left edge");
  const right = L.placeTip({ left: 1200, top: 100, right: 1260, bottom: 118 }, tipBox, win);
  ok(right.left === 1280 - 8 - 416, "row 2: a trigger at the window's right edge has its box moved left to fit (at 1280 px it ran 12 to 248 px past the edge)");
  const low = L.placeTip({ left: 100, top: 860, right: 160, bottom: 878 }, tipBox, win);
  ok(low.above && low.top === 860 - 2 - 320 && low.maxHeight >= 320, "row 1: a trigger at the window's foot has its box above it");
  const phone = L.placeTip({ left: 300, top: 400, right: 360, bottom: 418 }, { width: 312, height: 320 }, { width: 390, height: 844 });
  ok(phone.left === 390 - 8 - 312 && phone.left + 312 <= 390, "row 2: at 390 px a box 312 px wide stands inside the window (144 of the table's 147 ran past its edge)");
  const tight = L.placeTip({ left: 10, top: 300, right: 60, bottom: 318 }, { width: 416, height: 900 }, { width: 390, height: 640 });
  ok(tight.maxHeight <= 640 && tight.left === 8, "a box taller than its room is given the room, and scrolls");
}
const placer = src("../components/largeload/TipPlace.tsx");
ok(/^"use client";/.test(placer) && placer.includes("placeTip(") && placer.includes('"pointerover"') && placer.includes('"focusin"') && placer.includes('position = "fixed"'), "rows 1 and 2: the placer sets the open box against the window on a hover and on a focus");
ok(placer.includes('"scroll"') && placer.includes("inBox(e.target)"), "the box follows its trigger when the page or a table's frame scrolls, and the box's own scroll moves nothing");
const sectionHtml = renderToStaticMarkup(h(LargeLoadSection, { q: { llrow: "ercot:LZ_AEN" }, x: X ?? S.DEFAULT_INPUTS ?? {} }));
{
  const win = { width: 390, height: 844 }, mark = { left: 123, top: 414, right: 139, bottom: 430 }, boxSize = { width: 288, height: 86 };
  const under = L.placeTip(mark, boxSize, win), over = L.placeTip(mark, boxSize, win, 8, 2, "above");
  ok(!under.above && over.above && over.top + 86 <= mark.top && over.left === under.left, `row 14: a headline's mark opens its box above it, clear of the figure under the label (its foot at ${over.top + 86}, the mark at ${mark.top})`);
  ok(!L.placeTip({ left: 123, top: 40, right: 139, bottom: 56 }, boxSize, win, 8, 2, "above").above, "row 14: with no room above for the whole box, it opens under the mark as any other");
  ok(/data-tip-open="above"/.test(src("../components/tool/ToolPage.tsx")) && src("../components/largeload/TipPlace.tsx").includes(`tip.closest('[data-tip-open="above"]')`), "row 14: the headline's slot says so, and the placer reads it");
}
// ---- row 15: the lease tab's table of flagged rules scrolls in its own frame (the page was 406 px wide on a 390 px screen)
ok(/<div className="overflow-x-auto" data-lease-flagged="1">\s*<table className="w-full text-left text-xs">\s*<thead><tr className="border-b border-rule"><th className="py-1">Well<\/th>/.test(src("../app/severance/lease/LeaseTool.tsx").replace(/\r\n/g, "\n")), "row 15: the lease tool's table of the rules a file may qualify for is inside a frame that scrolls sideways");
const layout = src("../app/layout.tsx");
ok((layout.match(/<TipPlace \/>/g) ?? []).length === 1 && !src("../app/cost-of-power/LargeLoadSection.tsx").includes("<TipPlace />") && !src("../app/policy/StateLaws.tsx").includes("<TipPlace />"), "the placer is mounted once, in the site's layout, so it is on both pages (and on every page that draws the shared mark)");
// the old laptop's rows 1, 7, 9, 10 and 12 (docs/state/browser_reads_wanted.md): the shared "i" mark's box, 288 px wide,
// ran past a phone's screen from any mark right of the first 100 px, and the page scrolled sideways while it was open
ok(/const TIP = "\[data-llr\] span\.tip, span\.tip\[data-tip\]";/.test(placer) && /const BOX = ':scope > \[role="tooltip"\]';/.test(placer), "row 14: the placer takes the large-load hovers and the site's shared mark, and no other");
const shared = src("../components/tool/ToolPage.tsx");
ok(/<span className="tip relative inline-block align-baseline" data-tip=\{id\}>\s*<button[^>]*aria-describedby=\{`tip-\$\{id\}`\}[\s\S]{0,200}<\/button>\s*<span role="tooltip" id=\{`tip-\$\{id\}`\}/.test(shared), "row 14: the shared mark is what the placer looks for: span.tip[data-tip], its button, and its box as a child");
{
  const phone = { width: 390, height: 844 }, mark = { left: 351, top: 400, right: 367, bottom: 416 };
  const p = L.placeTip(mark, { width: 288, height: 120 }, phone);
  ok(p.left + 288 <= 390 - 8 && p.left >= 8, `row 14: the shared mark at 351 px of a 390 px screen: its box stands at ${p.left} to ${p.left + 288} (it ran to 639)`);
  const wide = L.placeTip({ left: 1031, top: 440, right: 1047, bottom: 456 }, { width: 288, height: 86 }, { width: 1265, height: 900 });
  ok(wide.left + 288 <= 1265 - 8, `row 14: a mark in a page's right column at 1280 px: its box stands at ${wide.left} to ${wide.left + 288} (it ran to 1319, past the window)`);
}

// ---- row 3: a long address in a hover breaks; no sideways scroll bar in the box
const block = (re) => (css.match(re) ?? [""])[0];
ok(/\[data-llr\] span\.tip > \[role="tooltip"\]\[data-tp\],\n\.brand-a \[data-allgrids\] \[data-llr\] span\.tip > \[role="tooltip"\]\[data-tp\] \{\n  overflow-wrap: anywhere;\n  overflow-x: hidden;\n\}/.test(css), "row 3: a hover's words break anywhere and its box does not scroll sideways");

// ---- row 4: the first column, kept in place, is drawn above the cells that scroll under it
ok(/\.brand-a \[data-llr\] \.overflow-x-auto table th:first-child \{\n  z-index: 1;\n\}/.test(css), "row 4: the tables' first column has a level of its own");
ok(/\.brand-a \[data-llr\] \.overflow-x-auto table th:first-child:is\(:hover, :focus-within\) \{\n  z-index: 4;\n\}/.test(css), "row 4: a hover opened from the first column stands above the rows after it");
ok(/\.brand-a \[data-llr\] \.overflow-x-auto table td \.tip:is\(:hover, :focus-within\) \{\n  z-index: auto;\n\}/.test(css), "row 4: a hovered cell that has scrolled under the first column is not drawn over it");
const rulesHtml = renderToStaticMarkup(h(LargeLoadRules, { opened: { ...NONE, state: "VA", a: "coops_public_power-03", b: "dominion-04" }, address: "/cost-of-power?view=allgrids" }));
ok((rulesHtml.match(/class="overflow-x-auto"/g) ?? []).length === 3 && /<th scope="row"/.test(rulesHtml), "row 4: the rules, the changes and A and B are each a table in a frame that scrolls, with a first column of row heads");

// ---- row 5: a row's utilities are named once
ok(L.uniqueNames(["Austin Energy", "Austin Energy", "Bluebonnet Electric Coop, Inc", " Austin Energy "]).join("|") === "Austin Energy|Bluebonnet Electric Coop, Inc", "row 5: names are kept in the order met, each once");
const aen = S.rowOf(SITING_FILES, "ercot:LZ_AEN");
const names = rulesOfRow(aen).names;
ok(names.length === new Set(names).size && names.includes("Austin Energy"), `row 5: the Austin Energy load zone names each utility once (${names.length})`);
const panelWords = words((sectionHtml.match(/<section[^>]*data-llr-row-panel="ercot:LZ_AEN"[\s\S]*?<\/section>/) ?? [""])[0]);
ok(panelWords.includes(`(${names.join(", ")})`) && !/Austin Energy, Austin Energy/.test(panelWords), "row 5: the panel's line names them once");

// ---- row 6: a status with no date printed says so of the date
ok(L.statusWords("in effect", "2026-03-09") === "in effect, 2026-03-09" && L.statusWords("approved", "2026-06") === "approved, 2026-06", "row 6: a status with its day or its month");
ok(L.statusWords("in effect", "not published") === "in effect, date not published" && L.statusWords("in effect", "") === "in effect, date not published", "row 6: a status with no date printed reads \"in effect, date not published\"");
const undated = file.rules.filter((r) => !/^\d{4}/.test(r.status_date));
ok(undated.length > 0, `the file holds rules with no status date printed (${undated.length})`);
const cardOf = (r) => renderToStaticMarkup(h(RuleCard, { rule: r }));
ok(undated.every((r) => words(cardOf(r)).includes(`Status: ${r.status}, date not published`)), "row 6: every such rule's card says it of the date");
const np15 = S.rowOf(SITING_FILES, "caiso:TH_NP15_GEN-APND");
const lineHtml = renderToStaticMarkup(h(RuleLine, { r: np15, x: X ?? S.DEFAULT_INPUTS ?? {}, cell: "utility" }));
ok(!/in effect, not published/.test(ent(lineHtml)) && /date not published/.test(ent(lineHtml)), "row 6: the link of a hub row whose rule has no date says \"date not published\" in its title");
ok(!/in effect, not published|approved, not published|proposed, not published/.test(ent(rulesHtml)), "row 6: A and B say it too");

// ---- row 7: the card's status, docket and notes are a line each
const oncor = file.rules.find((r) => r.id === "texas-01" || /Oncor/.test(r.utility)) ?? file.rules.find((r) => r.docket.length > 80);
const longDocket = file.rules.filter((r) => r.docket && r.docket !== "not published" && r.notes);
ok(longDocket.length > 20, `rules with a docket and notes: ${longDocket.length}`);
ok(longDocket.every((r) => { const c = cardOf(r); return /<p[^>]*data-rule-status=/.test(c) && /<p[^>]*data-rule-docket=/.test(c) && /<p[^>]*data-rule-more=/.test(c) && !/<\/span>\. <span class="tip/.test(c); }), "row 7: the status, the docket and the notes are three lines, with no period left to open a line");
ok(file.rules.every((r) => { const c = words(cardOf(r)); return (!r.docket || r.docket === "not published" || c.includes(`Docket: ${r.docket.replace(/\s+/g, " ")}`)) && (!r.notes || c.includes("The ERW's notes")); }), "row 7: nothing the card held is dropped: every docket and every note is still drawn");
void oncor;

// ---- row 8: the changes, newest first by the date each row draws
const ordered = L.orderChanges(file.changes);
const drawnDate = (c) => (c.date_kind === "date read" || c.date_printed !== c.date ? c.date_printed || c.date : c.date);
const keyOf = (d) => (/^\d{4}-\d{2}$/.test(d) ? `${d}-99` : d);
ok(ordered.length === file.changes.length && new Set(ordered.map((c) => c.id)).size === file.changes.length, "row 8: every change is still a row (94)");
ok(ordered.every((c, i) => i === 0 || keyOf(drawnDate(ordered[i - 1])) >= keyOf(drawnDate(c))), "row 8: no row stands above a row with a later date drawn");
const months = file.changes.filter((c) => /^\d{4}-\d{2}$/.test(drawnDate(c)));
ok(months.length === 7 && months.every((c) => { const i = ordered.indexOf(c), before = ordered[i - 1]; return !before || drawnDate(before).slice(0, 7) >= drawnDate(c); }), `row 8: the ${months.length} changes printed as a month stand at the head of their month, not above 13 November`);
ok(/^\d{4}-\d{2}-\d{2}$/.test(drawnDate(ordered[0])) && drawnDate(ordered[0]) === "2026-11-13", `row 8: the first row is of ${drawnDate(ordered[0])}`);
const changesHtml = renderToStaticMarkup(h(LargeLoadRules, { opened: NONE, address: "/cost-of-power?view=allgrids" }));
const firstDrawn = (changesHtml.match(/data-llr-change="([^"]+)"/) ?? [])[1];
ok(firstDrawn === ordered[0].id, "row 8: the table draws that order");

// ---- row 9: the rows drawn are the rows counted, and the files carry them
const changesLine = words((changesHtml.match(/<p[^>]*data-llr-changes-shown[\s\S]*?<\/p>/) ?? [""])[0]);
ok(changesLine.startsWith(`${file.changes.length} of ${file.changes.length} changes, and ${file.held_changes.length} held`), `row 9: the changes' line counts the held rows it draws: "${changesLine.slice(0, 40)}"`);
ok((changesHtml.match(/<tr[^>]*data-llr-change="[^"]+"[^>]*data-llr-held="1"/g) ?? []).length === file.held_changes.length, "row 9: and draws as many");
const withState = renderToStaticMarkup(h(LargeLoadRules, { opened: { ...NONE, state: "TX" }, address: "/cost-of-power?view=allgrids" }));
ok(!/data-llr-changes-held/.test(withState), "row 9: with a state chosen no held change is drawn, and none is counted");
const csv = L.changesCsv(ordered, file, "/cost-of-power?view=allgrids", file.held_changes);
const csvRows = csv.trim().split("\n");
ok(csvRows.length === 2 + file.changes.length + file.held_changes.length && csvRows.filter((r) => r.includes(L.LICENSE_NEEDED)).length >= file.held_changes.length + 1, "row 9: the changes' file carries the held rows, marked license needed, as the rules' and the laws' files do");
ok(file.held_changes.every((hc) => { const row = csvRows.find((r) => r.startsWith(`${hc.id},`)); return row && row.split(L.LICENSE_NEEDED).length === 4; }), "row 9: a held change's row is its id, its utility and three cells marked license needed: no value");
ok(L.changesCsv(ordered, file, "x").trim().split("\n").length === 2 + file.changes.length, "the file of a state's changes holds no held row");
const lawsProp = { laws: file.laws, held: file.held_laws, built: file.built, retrieved: file.retrieved, searches: file.law_searches ?? [], rules: {}, changes: {} };
const lawsAll = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: [], clearStates: () => {} }));
const lawRows = (lawsAll.match(/<tr[^>]*data-law(-withheld)?="/g) ?? []).length;
const total = file.laws.length + file.held_laws.length;
const notShown = (file.law_searches ?? []).filter((s) => s.kind === "withheld").length;
ok(lawRows === total + notShown && notShown === 1, `row 9: the laws' table draws ${lawRows} rows: ${total} of the table and ${notShown} read and not shown`);
ok(words((lawsAll.match(/<p[^>]*data-laws-counts[\s\S]*?<\/p>/) ?? [""])[0]).includes(`${total} of ${total} shown, and ${notShown} read and not shown`), "row 9: and its line says so");
const lawsTx = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["TX"], clearStates: () => {} }));
ok(words((lawsTx.match(/<p[^>]*data-laws-counts[\s\S]*?<\/p>/) ?? [""])[0]).includes(`0 of ${total} shown, and 1 read and not shown`), "row 9: Texas alone: 0 of 28 shown, and 1 read and not shown");
const lawsMd = renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["MD"], clearStates: () => {} }));
ok(!/data-laws-not-shown/.test(lawsMd), "row 9: a state with no such bill says nothing of it");
ok(/enacted<\/button>[\s\S]{0,400}date not published/.test(renderToStaticMarkup(h(StateLaws, { file: lawsProp, states: ["VA"], clearStates: () => {} }))), "row 6: a law with no status date printed says so of the date");

// ---- row 10: targets a finger can meet (axe: target size)
ok(/\[data-llr="cell"\] :is\(a, button\[data-tip-trigger\]\),\n\.brand-a \[data-llr="laws"\] td :is\(a\[data-law-doc\], button\[data-tip-trigger\]\) \{\n  display: inline-block;\n  min-height: 24px;\n  line-height: 24px;\n\}/.test(css), "row 10: the hub cells' rule lines and the laws' documents are 24 px high");
ok(/button\[data-llr-set\] \{\n  min-width: 24px;\n  min-height: 24px;\n\}/.test(css) && /button\[data-llr-open\],\n\.brand-a \[data-allgrids\] tbody td \[data-util-name\] > button\[data-tip-trigger\] \{\n  min-height: 24px;\n\}/.test(css), "row 10: A and B, a rule's name and the hub table's utility names are 24 px high");
ok(/\[data-chart="policy-figures"\] tbody td \{\n  padding-block: 4px;\n\}/.test(css), "row 10: the policy monitor's table of figures by month keeps its links a finger apart");
void block;

console.log(`${n - failed} of ${n} passed`);
process.exit(failed ? 1 : 0);
