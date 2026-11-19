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
