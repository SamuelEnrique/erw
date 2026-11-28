// Energy Research Warehouse (ERW) site, session 8490 (chain 503, part E): what the read of "The whole country" on
// /supply found on the data machine's real page files (docs/reviews/supply-regions-read-2026-11-19.md, rows 16 and
// on), fixed in the view and held here without a build and without the real files (they are not in git): the pairs'
// count of months (data request 325, in the contract since session 8004) and the storage hover. The section is drawn
// from session 8430's fixtures (scripts/regions-fixture-trade.mjs: values made by a rule, not data), with the two keys
// of the contract added to a copy of the matrix where a test needs them.
//   node --import ./scripts/tsx-register.mjs scripts/test-supply-regions-8490.mjs
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { fixtureReaders, matrixFixture } from "./regions-fixture-trade.mjs";

const S = await import("../components/supply/Country.tsx");
// session 11405 (decision 8 readied): drawn with the regions hold stood aside, so every region's arithmetic is checked; the hold itself is tests/test_ready_eia_held_regions.py's
S.REGIONS_HELD.splice(0);
const T = await import("../lib/countrytrade.ts");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const draw = (q, read = fixtureReaders()) => renderToStaticMarkup(createElement(S.Country, { q, read }));
const rowOf = (html, mark) => (new RegExp(`<tr[^>]*>(?:(?!</tr>)[\\s\\S])*${mark}[\\s\\S]*?</tr>`).exec(html) ?? [""])[0];
const seen = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-cn="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));

// a copy of the fixture's matrix whose pairs carry the contract's two counts as the real file does: a year of 2023
// held whole, 2026 held for 11 months, and one pair held for 9 of them
const withMonths = () => {
  const m = matrixFixture();
  const add = (r) => ({ ...r, months_in_year: String(r.year) === "2026" ? 11 : 12, months_held: `${r.a}-${r.b}` === "CAR-TEN" && String(r.year) === "2026" ? 9 : String(r.year) === "2026" ? 11 : 12 });
  m.region_pairs = m.region_pairs.map(add);
  m.ba_pairs = m.ba_pairs.map(add);
  return m;
};
const real = { ...fixtureReaders(), matrix: withMonths };

// ---- row 16: the pairs' year says how many months it holds
const p = T.pairsOfYear(withMonths().region_pairs, "2026").find((x) => x.key === "CAR-TEN");
ok(p && p.monthsHeld === 9 && p.monthsInYear === 11, "the view reads the pair's months held and the year's months in the file");
const q = T.pairsOfYear(matrixFixture().region_pairs, "2026").find((x) => x.key === "CAR-TEN");
ok(q && q.monthsHeld === null && q.monthsInYear === null, "a file without the two counts gives none (no count is made up)");
const half = withMonths(); half.region_pairs = half.region_pairs.map((r) => ({ ...r, months_in_year: null }));
ok(T.pairsOfYear(half.region_pairs, "2026").every((x) => x.monthsHeld === null), "a count of months without the year's months is not drawn");

const page = draw({ region: "ten", b: "car", year: "2026" }, real);
const pairs = page.slice(page.indexOf('id="wc-pairs"'), page.indexOf('data-wc-fold="bapairs"'));
ok((pairs.match(/data-wc-head="pair-months"/g) ?? []).length === 1 && /title="The months of the year that hold a report of this flow from either side, of the year&#x27;s months in the file: six in 2018, whose months begin in July, and fewer in the year still running\. A pair&#x27;s year is the sum of EIA&#x27;s Eastern months of that year, as in the net imports above\./.test(pairs),
  "the pairs of regions carry a column Months held whose hover says what a pair's year is (EIA's Eastern months, data request 326)");
const carTen = rowOf(pairs, 'data-wc-pair="CAR-TEN"');
ok(/<span data-cn="pair\|CAR-TEN\|2026\|months">9<\/span> of 11/.test(carTen), "the Carolinas and Tennessee in 2026: 9 of 11");
ok(/<span data-cn="pair\|SE-TEN\|2026\|months">11<\/span> of 11/.test(rowOf(pairs, 'data-wc-pair="SE-TEN"')), "a pair held in every month of the running year: 11 of 11");
const fold = page.slice(page.indexOf('data-wc-fold="bapairs"'), page.indexOf('data-wc-fold="partners"'));
ok((fold.match(/data-wc-head="pair-months"/g) ?? []).length === 1 && /<span data-cn="bapair\|DUK-TVA\|2026\|months">11<\/span> of 11/.test(fold), "the pairs of balancing authorities carry the same column");
// the figures script reads a count of months beside its "of" by this form (scripts/supply-regions-figures.mjs)
const read = [...page.matchAll(/<span data-cn="([^"]+\|months)">\d+<\/span> of (\d+)/g)].filter((m) => m[1].startsWith("pair|") || m[1].startsWith("bapair|"));
ok(read.length === withMonths().region_pairs.filter((r) => String(r.year) === "2026").length + withMonths().ba_pairs.filter((r) => String(r.year) === "2026").length, "every pair of the year is read by the figures script with its count of months");
const none = draw({ region: "ten", b: "car", year: "2026" });
const noneRow = rowOf(none.slice(none.indexOf('id="wc-pairs"')), 'data-wc-pair="CAR-TEN"');
ok(!/data-wc-head="pair-months"/.test(none) && !/\|months">/.test(noneRow) && !/count of the months it holds/.test(none), "a file without the counts (a build before session 8004): no column, the table as session 8430 drew it");
const some = withMonths(); some.region_pairs = some.region_pairs.map((r) => (`${r.a}-${r.b}` === "CAR-TEN" ? { ...r, months_held: null } : r));
const someRow = rowOf(draw({ region: "ten", b: "car", year: "2026" }, { ...fixtureReaders(), matrix: () => some }).split('id="wc-pairs"')[1], 'data-wc-pair="CAR-TEN"');
ok(/title="The file gives no count of the months it holds for this pair in 2026\."/.test(someRow) && /data-not-held="1"/.test(someRow), "a file with the counts but none for one pair: that cell reads not held yet, with the reason on hover");

// ---- row 17: storage
ok(/Form EIA-930 carries storage from 1 July 2024 \(UTC\)/.test(S.STORAGE_WORDS) && /not a count of the batteries on its ground/.test(S.STORAGE_WORDS), "the storage words say when Form EIA-930 begins storage and what a zero is");
const st = /<span title="([^"]*)" data-wc-head="mix-storage"/.exec(page);
ok(st && st[1].includes("Storage is below zero in a month it charged more than it discharged. Form EIA-930 carries storage from 1 July 2024 (UTC)") && (page.match(/data-wc-head="mix-storage"/g) ?? []).length === 2,
  "the hover of Storage in each region's mix table carries them");

// ---- row 18: a figure that rounds to zero reads "0.0", never "-0.0" or "+0.0" (Southwest and Central, December 2024;
// Tennessee's wind share in 2025, on the real files)
ok(S.gwh(-40) === "0.0" && S.gwh(40) === "0.0" && S.gwh(-50) === "-0.1" && S.gwh(1234567) === "1,234.6", "GWh: a flow under 50 MWh either way reads 0.0; others as before");
ok(S.signedGwh(-40) === "0.0" && S.signedGwh(40) === "0.0" && S.signedGwh(0) === "0.0" && S.signedGwh(60) === "+0.1" && S.signedGwh(-60) === "-0.1", "signed GWh: no sign on a figure that rounds to zero, the sign kept on every other");
ok(T.pct1(-0.04) === "0.0" && T.pct1(0.04) === "0.0" && T.pct1(-0.06) === "-0.1" && T.pct1(22.24) === "22.2", "a percent that rounds to zero reads 0.0; others as before");

// ---- row 19: the mean of a pair says what it is (it runs over the hours both reported, so it can stand outside the
// two reports: Tennessee and the Carolinas in 2025 on the real files, 94.2 and 91.1, a mean of 91.0)
const meanCell = (html, key) => (new RegExp(`<span title="([^"]*)"><span data-cn="${key.replace(/\|/g, "\\|")}">`).exec(html) ?? [])[1] ?? "";
const m1 = meanCell(page, "pair|CAR-TEN|2026|mean");
ok(m1.startsWith("The mean of ") && /reports of this flow in 2026, taken over the hours both reported \(\d[\d,]* hours\), as the file gives it\. Each report beside it runs over that side&#x27;s own hours, so the mean need not lie between them\. Source: EIA Form EIA-930/.test(m1),
  "the mean of a pair of regions carries a hover: over the hours both reported, and why it need not lie between the two reports");
const m2 = meanCell(page, "bapair|DUK-TVA|2026|mean");
ok(/taken over the hours both reported/.test(m2), "the mean of a pair of balancing authorities carries the same hover");
const pv = { fromReport: 5, toReport: null, hoursBoth: 0 };
ok(S.meanWords(pv, "California", "Mexico", "2025").startsWith("Only California reported this flow in 2025: the file gives that report as the mean."), "a pair one side alone reported: the mean is that side's report, and the hover says so");

// ---- row 20: when the two sides' hours differ, the percent's hover says the reports can differ by more than the gap
// (the Northwest and California in 2024: 9,622.6 GWh over 8,784 hours, 7,817.0 over 8,000, a gap of 4.7)
ok(S.hoursApart("Northwest", 8784, "California", 8000) === " Northwest's report runs over 8,784 hours and California's over 8,000: what Northwest reported in the hours California did not is in its report and not in the gap, so the two reports can differ by more than the gap.",
  "the sentence names each side's hours and which side reported the hours the other did not");
ok(S.hoursApart("Carolinas", 100, "Tennessee", 200).includes("Carolinas' report runs over 100 hours and Tennessee's over 200: what Tennessee reported in the hours Carolinas did not"), "the other way round, with the Carolinas' possessive");
ok(S.hoursApart("A", 10, "B", 10) === "" && S.hoursApart("A", null, "B", 10) === "" && S.hoursApart("A", 10, "B", null) === "", "the same hours, or hours not in the file: nothing is added");
const pctTips = [...page.matchAll(/<span class="cursor-help[^"]*"(?: data-gap-large="1")? title="([^"]*)"><span data-cn="(pair\|[^"]+\|gap_pct)">/g)];
ok(pctTips.length > 0 && pctTips.every((t) => /Source: EIA Form EIA-930, interchange as each side filed it\.( [^ ].* report runs over [\d,]+ hours and .* over [\d,]+: .*so the two reports can differ by more than the gap\.)?$/.test(t[1].replace(/&#x27;/g, "'"))),
  "every percent of a pair ends with the source, and any sentence on the hours stands after it (the hover session 8430's test holds is unchanged before it)");

// ---- row 21: a month of the mix file's span that it does not hold stands as a row, not held yet, with why
const carMix = T.mixGapMonths(S && fixtureReaders().mix("CAR"), "2025");
ok(JSON.stringify(carMix) === '["2025-06"]' && T.mixGapMonths(fixtureReaders().mix("TEN"), "2025").length === 0, "the months of a year the mix file leaves out (the fixture's Carolinas: June 2025)");
const cut = { ...fixtureReaders().mix("TEX"), first: "2018-07", upto: "2026-10" }; delete cut.months["2025-12"];
ok(JSON.stringify(T.mixGapMonths(cut, "2025")) === '["2025-12"]' && T.mixGapMonths(cut, "2018").length === 0 && T.mixGapMonths(cut, "2026").every((m) => m <= "2026-10"),
  "no month before the file's first or after its last is called missing (Texas without December 2025, as on the real files)");
const p25 = draw({ region: "ten", b: "car", year: "2025" });
const carMixHtml = p25.slice(p25.indexOf('data-wc-mix="b" data-wc-region="CAR"'));
const gapRow = rowOf(carMixHtml, 'data-wc-month-gap="2025-06"');
ok(gapRow && (gapRow.match(/data-not-held="1"/g) ?? []).length === 10 && /The file holds no generation by source for Carolinas in Jun 2025: the builder writes a month only when at least 90 percent of its days are complete/.test(gapRow) && !/data-cn=/.test(gapRow),
  "the Carolinas' June 2025 stands as a row: ten cells not held yet, the builder's rule on hover, no figure");
const order = [...carMixHtml.slice(0, carMixHtml.indexOf('data-wc-month="2025"')).matchAll(/data-wc-month(?:-gap)?="(2025-\d\d)"/g)].map((x) => x[1]);
ok(order.join(",") === "2025-01,2025-02,2025-03,2025-04,2025-05,2025-06,2025-07,2025-08,2025-09,2025-10,2025-11,2025-12", "the rows stand in the order of the months, the month not held in its place");
ok(/<span data-wc-month="2025" title="The year&#x27;s shares and net generation run over the 11 months of 2025 the file holds; Jun 2025 is not held, and nothing is filled for it\.">2025, 11 months<\/span>/.test(carMixHtml), "the year's row says on hover which month is not held; its face is as before");
ok(!/data-wc-month-gap/.test(p25.slice(p25.indexOf('data-wc-mix="a" data-wc-region="TEN"'), p25.indexOf('data-wc-mix="b"'))), "a region whose file holds every month of the year draws no such row");

// a year inside the file's span with no month held (the Southwest in 2024 on the real files): the hover says why
const sw = { ...fixtureReaders().mix("SW"), first: "2019-01", upto: "2026-10" };
for (const k of Object.keys(sw.months)) if (k.startsWith("2024")) delete sw.months[k];
const swPage = draw({ region: "sw", b: "none", year: "2024" }, { ...fixtureReaders(), mix: (c) => (c === "SW" ? sw : fixtureReaders().mix(c)) });
const swMix = swPage.slice(swPage.indexOf('data-wc-mix="a" data-wc-region="SW"'));
ok(/title="The file holds no month of 2024 for Southwest: its months run from Jan 2019 to [A-Z][a-z]{2} 20\d\d\. The builder writes a month only when at least 90 percent of its days are complete, [^"]*no month of 2024 inside that span is\. Nothing is filled\./.test(swMix),
  "a year the mix file holds no month of, inside its span: the hover gives the builder's rule");
const swOut = draw({ region: "sw", b: "none", year: "2018" });
ok(!/no month of 2018 inside that span/.test(swOut), "a year before the file's first month: the hover as before, no rule added");

// ---- nothing else moved
const base = draw({ region: "ten", b: "car" });
const f = figs(base);
ok(Object.keys(f).length === 451 && f["trade|TEN|2025|SE|gap_pct"] === "22.2" && f["pair|SE-TEN|2025|gap_pct"] === "66.7" && f["mix|TEN|2025|natural_gas"] === "3.6",
  "on the fixtures without the counts: the same 451 figures as session 8460's test, the same values");
ok(!/1 July 2024|Eastern months of that year/.test(seen(page)), "the words added stand on hovers, none on the section's face but the column's name");
for (const [name, h] of [["with the counts", page], ["without them", none]]) {
  ok(!dash.some((c) => h.includes(c)) && !/NaN|\bundefined\b|Infinity/.test(seen(h)) && !/\bnot held\b(?! yet)/i.test(seen(h)), `${name}: no dash, no NaN, and a value that is not held reads "not held yet"`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
