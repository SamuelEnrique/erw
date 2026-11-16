// Energy Research Warehouse (ERW) site, session 7513 (chain 304, part B): /battery/customer read as the energy manager
// of a grocery chain would read it (docs/reviews/battery-customer-read-2026-11-16.md), drawn to HTML without a build.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-customer-read.mjs
// The store of every case is real: 27,625 square feet, a peak of about 247 kW in 2012 (EnerNOC facility 384, a grocery
// store in Los Angeles, in NREL/TP-6A20-64987, page 7). The rates are the published ones of
// replication/battery_customer/cases.json. The batteries are published sizes: 55 kW and 110 kWh (the size that report
// found best for the store, its table 9) and 100 kW and 400 kWh (a 4 hour commercial unit).
// 1. The five cases: the figures the read states are the ones the page's own calculator draws.
// 2. Row 1 of the read: a rate typed as a sheet prints it, in cents, is refused with the unit as well as the range.
// 3. Row 2: the line under "How long your peak lasts" says whose hours; what the three spans called peak do.
// 4. Row 3: the round trip on the site's three battery pages, as the decisions block now says.
// 5. The promise: no way to send or store was added.
// No network, no file written. A draw runs no effect and no click: the fields' starting values are set for the draw and
// put back after, as scripts/test-battery-customer-page.mjs does.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1");
const read = (rel) => fs.readFileSync(new URL(rel, import.meta.url), "utf-8");

const lib = await import("../lib/customerbattery.ts");
const { Calc } = await import("../app/battery/customer/Calc.tsx");
const KEYS = ["peakKw", "demandCharge", "peakRate", "offPeakRate", "batteryKw", "batteryKwh", "peakHours", "days", "roundTrip"];
const T = (...v) => Object.fromEntries(KEYS.map((k, i) => [k, String(v[i])]));
function draw(typed) {
  const kept = lib.FIELDS.map((f) => f.start);
  lib.FIELDS.forEach((f) => { f.start = typed[f.key] ?? ""; });
  try { return text(renderToStaticMarkup(h(Calc))); } finally { lib.FIELDS.forEach((f, i) => { f.start = kept[i]; }); }
}
const exact = (typed) => lib.saving(Object.fromEntries(Object.entries(typed).map(([k, v]) => [k, Number(v)])));
const cents = (v) => Math.round(v * 100) / 100;

// the published rates of the cases, read from the replication's file: a rate changed there fails here
const cases = Object.fromEntries(JSON.parse(read("../../replication/battery_customer/cases.json")).cases.map((c) => [c.id, c]));
const rates = (id) => ["demandCharge", "peakRate", "offPeakRate"].map((k) => cases[id].typed[k]);
const P = 247;

// 1. the five cases
const c1 = draw(T(P, ...rates("seattle-md-city-tou"), 55, 110, 4, 26, 86));
ok(c1.includes("a 55 kW battery holding 110 kWh (2.0 hours) lowers the bill by $293 a month, $3,519 a year: $147 a month from a lower peak and $146 a month from moving energy.")
  && c1.includes("27.5 kW off a 247 kW peak; the demand charge was $1,324 a month."), "case 1, Seattle City Light, medium, City: 55 kW and 110 kWh, $3,519 a year");
const c1b = draw(T(P, ...rates("seattle-md-city-tou"), 100, 400, 4, 26, 86));
ok(c1b.includes("lowers the bill by $1,066 a month, $12,795 a year"), "case 1, the 100 kW and 400 kWh unit: $12,795 a year");
const c2 = draw(T(P, ...rates("seattle-md-downtown-tou"), 55, 110, 4, 26, 86));
const c2b = draw(T(P, ...rates("seattle-md-downtown-tou"), 100, 400, 4, 26, 86));
ok(c2.includes("$498 a month, $5,977 a year") && c2b.includes("$1,811 a month, $21,733 a year") && c2.includes("At $12.19 per kW that is $335 a month."), "case 2, the Downtown Network: $5,977 and $21,733 a year");
const srp = ["srp-e32-summer-peak", "srp-e32-summer", "srp-e32-winter"].map((id) => T(P, ...rates(id), 100, 400, 5, 22, 86));
const srpDrawn = srp.map(draw), srpMonth = srp.map((t) => exact(t).monthSaved);
const srpYear = 2 * srpMonth[0] + 4 * srpMonth[1] + 6 * srpMonth[2];
ok(srpDrawn[0].includes("$1,115 a month, $13,376 a year") && srpDrawn[1].includes("$743 a month, $8,917 a year") && srpDrawn[2].includes("$597 a month, $7,164 a year")
  && srpDrawn.every((d) => d.includes("80.0 kW off a 247 kW peak") && d.includes("set by the battery's energy")), "case 3, Salt River Project E-32, the three seasons typed in turn: $13,376, $8,917 and $7,164 a year, 80 kW off in each");
ok(cents(srpYear) === 8783.57 && cents(12 * srpMonth[0] - srpYear) === 4592.85 && cents(srpYear - 12 * srpMonth[2]) === 1619.6,
  `case 3, the year by the plan's seasons is $${cents(srpYear)}: twelve Julys are $4,592.85 over, twelve winter months $1,619.60 under (part A, row 3)`);
const c4 = draw(T(P, ...rates("austin-sv2"), 55, 110, 2, 21, 86));
ok(c4.includes("$819 a month, $9,824 a year: $844 a month from a lower peak and -$26 a month from moving energy.") && c4.includes("At your rates moving energy does not pay")
  && c4.includes("the demand charge was $3,791 a month"), "case 4, Austin Energy, one price for every hour: $9,824 a year, the energy a cost of $26 a month");
const sce = (hours) => T(P, ...rates("sce-tou-gs-2-b-2013-summer"), 55, 110, hours, 21, 86);
const c5 = [2, 4, 6].map((hh) => draw(sce(hh)));
ok(c5[0].includes("$1,840 a month, $22,080 a year") && c5[0].includes("that is $1,658 a month") && c5[1].includes("that is $829 a month") && c5[2].includes("that is $553 a month") && c5[2].includes("$735 a month, $8,819 a year"),
  "case 5, the store's own 2013 rate as NREL prints it: $1,658, $829 and $553 a month off the demand charge at 2, 4 and 6 hours typed");
// the winter months of the same sheet (NREL/TP-5400-63162, table 1): no on-peak demand charge, 8.59 and 5.47 cents
const sceWinter = exact(T(P, 13.94, 0.0859, 0.0547, 55, 110, 2, 21, 86)).monthSaved, sceSummer = exact(sce(2)).monthSaved;
ok(cents(4 * sceSummer + 8 * sceWinter) === 13905.69 && cents(12 * sceSummer) === 22080.22, "case 5, the year by the sheet's seasons (4 summer, 8 winter months) is $13,905.69 against twelve summer months, $22,080.22");
// part A's ruling 6 (the demand saving is an upper bound): 85 percent of a 4 hour battery's power, in dollars a year
const upper = (t) => cents(exact(t).demandSaved * 0.15 * 12);
ok(upper(T(P, ...rates("seattle-md-city-tou"), 100, 400, 4, 26, 86)) === 964.8 && upper(T(P, ...rates("seattle-md-downtown-tou"), 100, 400, 4, 26, 86)) === 2194.2,
  "part A, row 6, on the 4 hour unit: at NREL's 85 percent the year is $964.80 lower in the City and $2,194.20 lower Downtown");

// the read's two smaller figures: the days left at the starting 21, and the mid-peak rate when the peak is outside 5 to 9 p.m.
const yearOf = (...v) => exact(T(P, ...v)).yearSaved;
const city = rates("seattle-md-city-tou"), mid = cases["seattle-md-city-tou"].printed.mid_peak_energy_usd_per_kwh;
ok(Math.round(yearOf(...city, 55, 110, 4, 26, 86) - yearOf(...city, 55, 110, 4, 21, 86)) === 337, "case 1: the days left at the starting 21 take $337 off the small battery's year");
ok(Math.round(yearOf(...city, 55, 110, 4, 26, 86) - yearOf(city[0], mid, city[2], 55, 110, 4, 26, 86)) === 522 && Math.round(yearOf(...city, 100, 400, 4, 26, 86) - yearOf(city[0], mid, city[2], 100, 400, 4, 26, 86)) === 1897,
  "row 6: discharged at the mid-peak rate the year is $522 lower for the small battery and $1,897 lower for the unit");
ok(lib.usd(247 * 6.75) === "$1,667" && (247 - 5) * 6.75 === 1633.5, "row 5: the page's demand charge before, $1,667, against the plan's own (all kW over 5 kW), $1,633.50");
const cent = draw(T(P, ...[city[0]], 4.9, 2.5, 55, 110, 4, 26, 86));
ok(cent.includes("$5,847 a month, $70,169 a year"), "row 4 (a ruling, not changed): 4.9 and 2.5 typed for cents are taken as dollars, $70,169 a year");

// 2. a rate typed in cents
const asPrinted = draw(T(P, 30.14, 14.66, 5.82, 55, 110, 2, 21, 86));
const said = "Not a number this page can use (0 to 5). The rate is typed in dollars: 12 cents is 0.12.";
ok(asPrinted.split(said).length === 3 && asPrinted.includes("2 of 9 still needed.") && !asPrinted.includes("Saved a year"), "row 1: 14.66 and 5.82 (cents, as the sheet prints them) are each refused with the unit as well as the range, and no figure is shown");
const kw = draw(T(0, 30.14, 0.1466, 0.0582, 55, 110, 2, 21, 86));
ok(kw.includes("Not a number this page can use (more than 0, up to 1,000,000).") && !kw.includes("typed in dollars"), "a refused size is told its range alone, as it was");
const f = Object.fromEntries(lib.FIELDS.map((x) => [x.key, x]));
ok(lib.inDollars(f.peakRate) === " The rate is typed in dollars: 12 cents is 0.12." && lib.inDollars(f.offPeakRate) === lib.inDollars(f.peakRate) && lib.FIELDS.filter((x) => lib.inDollars(x) !== "").length === 2,
  "the two rates per kWh, and no other field, are told dollars when refused");
const charge = draw(T(P, 3014, 0.1466, 0.0582, 55, 110, 2, 21, 86));
ok(charge.includes("Not a number this page can use (0 to 500).") && !charge.includes("typed in dollars"), "a refused demand charge is told its range alone");
ok(f.peakRate.hint.includes("In dollars") && f.offPeakRate.hint.includes("in dollars"), "both rate fields say dollars under the field before anything is typed");

// 3. whose hours
const opens = text(renderToStaticMarkup(h(Calc)));
ok(opens.includes("How long your own demand stays near its highest, in the hours your demand charge counts. The battery must hold its discharge this long to lower the peak."), "row 2: the line under \"How long your peak lasts\" says whose hours they are");
const span = [2, 4, 18].map((hh) => draw(T(P, ...rates("seattle-md-city-tou"), 55, 110, hh, 26, 86)));
ok(span[0].includes("that is $295 a month") && span[1].includes("that is $147 a month") && span[2].includes("6.1 kW off a 247 kW peak") && span[2].includes("that is $33 a month"),
  "row 2: on Seattle City Light's medium rate the same battery takes $295, $147 or $33 a month off the demand charge at 2, 4 and 18 hours typed");
ok(/"Peak" is defined|6 a\.m\. to midnight/.test(cases["seattle-md-city-tou"].printed.peak_demand_hours) && cases["seattle-md-city-tou"].printed.peak_energy_hours.startsWith("5 p.m. to 9 p.m."),
  "the two spans the rate itself calls peak are the published ones: 6 a.m. to midnight for the demand charge, 5 p.m. to 9 p.m. for the energy rate");

// 4. the round trip on three pages
const { CustomerBatteryDecisions, CUSTOMER_BATTERY_DECISIONS: D } = await import("../app/battery/customer/Decisions.tsx");
const block = text(renderToStaticMarkup(h(CustomerBatteryDecisions)));
const earns = Number(read("../lib/battery/finance.ts").match(/export const MODEL = \{ rte: (\d+)/)[1]);
const game = read("../lib/battery.ts").match(/rte: \{ label: "Round-trip efficiency", unit: "percent", def: ([\d.]+),[^}]*source: "([^"]+)"/);
const rt = D.find((d) => d.key === "round-trip");
ok(f.roundTrip.start === String(earns) && rt.def === `${earns} percent.` && rt.source.includes(`the same ${earns} percent as on What a battery earns`), `row 3: the round trip starts at ${earns} percent here and on What a battery earns, and the block says so`);
ok(Number(game[1]) * 100 === 90 && game[2].includes("88 to 91 percent") && rt.source.includes("The home battery game of this site starts at 90 percent, inside the 88 to 91 percent"), "row 3: the home battery game's 90 percent and its 88 to 91 percent are named beside it");
ok(!rt.source.includes("no figure for a customer's battery was read") && rt.source.includes("No figure for a commercial customer's battery was read."), "row 3: the block no longer says no customer's battery figure was read while another page of the site cites one");
ok(D.find((d) => d.key === "peak-hours").source.includes("Seattle City Light's peak demand charge counts 6 a.m. to midnight, Monday to Saturday") && block.includes("your own demand stays near its highest inside them"), "row 2: the block's line on the hours names the longer span a demand charge counts");
ok(D.length === 10 && (block.match(/Default:/g) ?? []).length === 10 && (block.match(/Source:/g) ?? []).length === 10, "the block still draws 10 choices, each with its default and its source");

// 5. the promise, and the dashes
const code = (rel) => read(rel).split("\n").filter((l) => !l.trim().startsWith("//") && !l.trim().startsWith("*") && !l.trim().startsWith("/**")).join("\n");
const WAYS = ["fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage", "sessionStorage", "indexedDB", "document.cookie", "useRouter", "useSearchParams", "<form", "history.", "location."];
ok(!WAYS.some((w) => code("../app/battery/customer/Calc.tsx").includes(w) || code("../lib/customerbattery.ts").includes(w) || code("../app/battery/customer/Decisions.tsx").includes(w)),
  "the calculator, its arithmetic and the block still name no way to send, store or put in the address what a reader types");
ok(!/^import /m.test(code("../lib/customerbattery.ts")) && (code("../app/battery/customer/Calc.tsx").match(/^import /gm) ?? []).length === 2, "the arithmetic still imports nothing, and the calculator only React and the arithmetic");
const long = [0x2014, 0x2013].map((c) => String.fromCharCode(c));
ok(["../lib/customerbattery.ts", "../app/battery/customer/Calc.tsx", "../app/battery/customer/Decisions.tsx", "../../docs/reviews/battery-customer-read-2026-11-16.md", "../../docs/methods/battery_customer.md"].every((p) => !long.some((c) => read(p).includes(c))),
  "no em dash and no en dash in the files this session wrote or changed");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
