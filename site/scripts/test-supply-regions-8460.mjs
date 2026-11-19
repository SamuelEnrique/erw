// Energy Research Warehouse (ERW) site, session 8460 (chain 503, part E): the faults the reader's read of "The whole
// country" on /supply found and fixed at their cause (docs/reviews/supply-regions-read-2026-11-19.md, rows 1 to 4),
// held without a build. The section is drawn to HTML with the site's own code from session 8430's fixtures
// (scripts/regions-fixture-trade.mjs: values made by a rule, not data). Each fix is words on a hover; nothing on the
// section's face and no figure moved, which this test holds too. Session 8430's own tests are not changed.
//   node --import ./scripts/tsx-register.mjs scripts/test-supply-regions-8460.mjs
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { fixtureReaders, indexFixture, matrixFixture, pairOf } from "./regions-fixture-trade.mjs";

const S = await import("../components/supply/Country.tsx");

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const dash = [String.fromCharCode(0x2014), String.fromCharCode(0x2013)];
const draw = (q, read = fixtureReaders()) => renderToStaticMarkup(createElement(S.Country, { q, read }));
const rowOf = (html, mark) => (new RegExp(`<tr[^>]*>(?:(?!</tr>)[\\s\\S])*${mark}[\\s\\S]*?</tr>`).exec(html) ?? [""])[0];
const seen = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
const figs = (html) => Object.fromEntries([...html.matchAll(/<span data-cn="([^"]+)">([^<]*)<\/span>/g)].map((m) => [m[1], m[2]]));
const ABROAD = (place) => `No balancing authority of ${place} files Form EIA-930: a flow across the border stands by the report of the balancing authorities of the United States alone.`;

// ---- row 1: a flow across the border says why the other side's report is never held
ok(S.abroadWhy("MEX") === ` ${ABROAD("Mexico")}` && S.abroadWhy("CAN") === ` ${ABROAD("Canada")}` && S.abroadWhy("SE") === "" && S.abroadWhy("TVA") === "", "the reason is given for Canada and Mexico and for no region of the lower 48");
const tex = draw({ region: "tex", b: "nw", year: "2023" });
const mex = rowOf(tex, 'data-wc-nb="MEX"');
ok((mex.match(/data-not-held="1"/g) ?? []).length === 3 && (mex.match(/No balancing authority of Mexico files Form EIA-930/g) ?? []).length === 3 && /title="The file holds no report by Mexico of its flow with Texas in 2023\. No balancing authority of Mexico files Form EIA-930: a flow across the border stands by the report of the balancing authorities of the United States alone\."/.test(mex),
  "Texas and Mexico in a year: the neighbour's report, the gap and its percent read not held yet, each with the reason on hover");
const can = rowOf(tex, 'data-wc-nb="CAN"');
ok((can.match(/No balancing authority of Canada files Form EIA-930/g) ?? []).length === 3, "the Northwest and Canada, the same");
ok(/title="Texas reported [^"]* of net imports from Mexico in Jan 2023[^"]*Mexico&#x27;s report of the same flow is not held\. No balancing authority of Mexico files Form EIA-930[^"]*"><span data-cn="trade\|TEX\|2023-01\|MEX">/.test(tex), "a month's hover of a flow across the border says it too");
const ten = draw({ region: "ten", b: "none", year: "2026" });
ok(/Midwest&#x27;s report of the same flow is not held\. Source: EIA Form EIA-930/.test(ten) && !/No balancing authority of/.test(ten.slice(0, ten.indexOf('id="wc-pairs"'))), "a neighbour of the lower 48 whose report a month lacks carries no such reason");
const calMex = rowOf(tex, 'data-wc-pair="CAL-MEX"'), nwSw = rowOf(tex, 'data-wc-pair="NW-SW"'), canNw = rowOf(tex, 'data-wc-pair="CAN-NW"');
ok(/The file holds no report by Mexico of this flow in 2023\. No balancing authority of Mexico files Form EIA-930/.test(calMex) && /The file holds no report by Canada of this flow in 2023\. No balancing authority of Canada files Form EIA-930/.test(canNw)
  && /The file holds no report by Southwest of this flow in 2023\."/.test(nwSw) && !/No balancing authority of/.test(nwSw), "in the pairs: Mexico's and Canada's missing report gives the reason; a region of the lower 48 that reported nothing does not");

// ---- row 2: a balancing authority the index does not list
const withAbroad = () => { const m = matrixFixture(); m.ba_pairs = [...m.ba_pairs, ...m.years.map((y) => pairOf(["CAN", "BPAT"], 15, y)).map((r) => ({ ...r, a: "BCHA" }))]; return m; };
const listed = draw({ region: "nw", b: "none", year: "2025" }, { ...fixtureReaders(), matrix: withAbroad });
const bcha = rowOf(listed, 'data-wc-pair="BCHA-BPAT"');
ok(bcha !== "" && /title="Balancing authority BCHA, by its EIA-930 code\. The index of the regions \(site\/data\/regions\/index\.json\) lists the balancing authorities of the lower 48 and does not list this one\."/.test(bcha) && !/Its name stands here once the index/.test(bcha),
  "with the index on the site, an authority it does not list says so on hover (it no longer says its name will come with the index)");
ok(/The file holds no report by BCHA of this flow in 2025\. The index of the regions lists the balancing authorities of the lower 48 and does not list BCHA; an authority outside the lower 48 files no Form EIA-930\./.test(bcha) && (bcha.match(/data-not-held="1"/g) ?? []).length === 3,
  "its missing report, the gap and the percent read not held yet, and the report's hover gives the reason");
ok(/title="Bonneville Power Administration, balancing authority BPAT, in EIA&#x27;s region Northwest\."/.test(bcha) && !/does not list/.test(rowOf(listed, 'data-wc-pair="DUK-TVA"')), "an authority the index lists keeps its name and region");
const unlistedNoIndex = draw({ region: "nw", b: "none", year: "2025" }, { ...fixtureReaders({ without: ["index"] }), matrix: withAbroad });
ok(/Balancing authority BCHA, by its EIA-930 code\. Its name stands here once the index/.test(rowOf(unlistedNoIndex, 'data-wc-pair="BCHA-BPAT"')) && !/does not list/.test(unlistedNoIndex), "without the index file nothing is said of what it lists");
ok(indexFixture().bas.every((b) => b.code !== "BCHA"), "the fixture's index does not list the authority the test adds");

// ---- rows 3 and 4: the mix's months and its shares
const car = draw({ region: "car", b: "sw", year: "2025" });
ok(/data-wc-head="mix-net"/.test(car) && (car.match(/A month here is Carolinas&#x27; own local month \(time zone America\/New_York\); the net imports above run by EIA&#x27;s Eastern months\./g) ?? []).length === 1 && (car.match(/A month here is Southwest&#x27;s own local month \(time zone America\/New_York\)/g) ?? []).length === 1,
  "the mix table's net generation says whose local month a month is, with the file's time zone, and that net imports run by EIA's Eastern months");
const noTz = draw({ region: "car", b: "none", year: "2025" }, { ...fixtureReaders(), mix: (c) => { const f = fixtureReaders().mix(c); if (f) delete f.tz; return f; } });
ok(/A month here is Carolinas&#x27; own local month; the net imports above run by EIA&#x27;s Eastern months\./.test(noTz), "a mix file with no time zone names none");
ok(/The file holds an hour when its sources add up to its net generation within 5 percent, so a month&#x27;s shares need not add up to exactly 100\. A month of the mix is the region&#x27;s own local month; a month of the net imports above is EIA&#x27;s Eastern month\./.test(car),
  "the hover beside the mix's heading says why a month's shares need not add up to 100, and the two kinds of month");

// ---- nothing on the face moved, and no figure
const base = draw({ region: "ten", b: "car" });
ok(!/files Form EIA-930|does not list|local month|within 5 percent/.test(seen(tex)) && !/files Form EIA-930|does not list|local month|within 5 percent/.test(seen(car)) && !/local month|within 5 percent/.test(seen(base)), "every word added stands on a hover, none on the section's face");
const f = figs(base);
ok(Object.keys(f).length === 451 &&f["trade|TEN|2025|SE|gap_pct"] === "22.2" && f["pair|SE-TEN|2025|gap_pct"] === "66.7" && f["mix|TEN|2025|natural_gas"] === "3.6" && (base.match(/data-gap-large="1"/g) ?? []).length === 14,
  "Tennessee and the Carolinas in 2025: the same figures, the same marks of a large gap");
for (const [name, h] of [["Texas and the Northwest", tex], ["an authority not listed", listed], ["the Carolinas and the Southwest", car]]) {
  ok(!dash.some((c) => h.includes(c)) && !/\b(should|recommend|we advise)\b/i.test(seen(h)) && !/NaN|\bundefined\b|Infinity/.test(seen(h)) && !/\bnot held\b(?! yet)/i.test(seen(h)), `${name}: no dash, no advice, no NaN, and a value that is not held reads "not held yet"`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
