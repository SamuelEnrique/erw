// Energy Research Warehouse (ERW) site, session 7504 (chain 304): /battery/customer drawn to HTML without a build.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-customer-page.mjs
// 1. The decisions block (app/battery/customer/Decisions.tsx): one line a choice, each with its default and its source
//    in a tip that has its target, closed to start, no grey note, no dash of the long kinds, no way to send or store.
// 2. The calculator (app/battery/customer/Calc.tsx) drawn with numbers in its fields: a typed number is printed back
//    as typed (the fault this session fixed: a demand charge of 5.36 read "At $5 per kW", a 13.5 kWh battery "14 kWh"),
//    whole numbers read as they did, and a refused number is told its range in words.
// 3. The page as it opens: three starting values, six fields empty, no figure.
// No network, no file written. A draw runs no effect and no click: the fields' starting values are set for the draw
// and put back after, as scripts/battery-customer-figures.mjs does.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1");
const read = (rel) => fs.readFileSync(new URL(rel, import.meta.url), "utf-8");

// 1. the decisions block
const { CustomerBatteryDecisions, CUSTOMER_BATTERY_DECISIONS: D } = await import("../app/battery/customer/Decisions.tsx");
const block = renderToStaticMarkup(h(CustomerBatteryDecisions));
const ids = [...block.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
const asked = [...block.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
ok(D.length === 10 && new Set(D.map((d) => d.key)).size === D.length, `the list holds ${D.length} choices, each key once`);
ok((block.match(/data-decision="/g) ?? []).length === D.length && block.includes(`data-decision-count="${D.length}"`), "the block draws one line a choice and says how many");
ok((block.match(/data-decision-default="/g) ?? []).length === D.length && (block.match(/data-decision-source="/g) ?? []).length === D.length, "every choice has its default and its source");
ok(asked.length === D.length && asked.every((id) => ids.filter((x) => x === id).length === 1), `the ${asked.length} tips each have their one target`);
ok(/<details[^>]*data-decisions="7504"/.test(block) && !/<details[^>]* open/.test(block), "the fold is closed to start");
// the tip's own mark (the small "i" button of components/tool/ToolPage.tsx) is grey; no words of the block are
ok(!block.replace(/<button\b[\s\S]*?<\/button>/g, "").includes("text-muted"), "no grey note in the block: a default and a source are in the tip");
ok(D.every((d) => d.text && d.def && d.source), "no choice has an empty text, default or source");
ok(![0x2014, 0x2013].some((c) => block.includes(String.fromCharCode(c))), "no em dash and no en dash in the block");
ok(/methods\/battery_customer/.test(block) || /the method note/.test(block), "the block points to the method note");
const src = read("../app/battery/customer/Decisions.tsx");
const code = src.split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");
ok(!["use client", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage", "sessionStorage", "indexedDB", "document.cookie", "useState", "useEffect", "useRouter", "useSearchParams", "onChange", "onClick", "<form", "<input"].some((w) => code.includes(w)),
  "the block's file names no way to send, store or take what a reader types");
ok(code.includes("prefetch={false}") && (code.match(/href=/g) ?? []).length === 1, "its one link is to the method note and does not prefetch");
const page = read("../app/battery/customer/page.tsx");
ok(page.includes("<CustomerBatteryDecisions />") && page.includes("<Brand noUsage>") && page.includes('export const dynamic = "force-static"'), "the page mounts the block, stays static and keeps its promise that nothing is counted");
ok(page.indexOf("<Calc />") < page.indexOf("<CustomerBatteryDecisions />") && page.indexOf("<CustomerBatteryDecisions />") < page.indexOf("Source: none."), "the block is under the calculator and its two folds, above the source line");
for (const w of ["This page uses your own numbers, not ERW data.", "Nothing you type is sent or stored.", "What this assumes", "What it leaves out", "Source: none."]) ok(page.includes(w), `the page still says: ${w}`);

// the starting values the block states are the fields'
const lib = await import("../lib/customerbattery.ts");
const start = Object.fromEntries(lib.FIELDS.map((f) => [f.key, f.start]));
const def = (k) => D.find((d) => d.key === k).def;
ok(def("peak-hours").startsWith(`${start.peakHours} hours`) && def("days").startsWith(`${start.days} days`) && def("round-trip").startsWith(`${start.roundTrip} percent`),
  `the three defaults the block states are the fields' starting values (${start.peakHours}, ${start.days}, ${start.roundTrip})`);
ok(lib.FIELDS.filter((f) => f.start !== undefined).length === 3 && lib.FIELDS.length === 9, "nine fields, three with a starting value: no number is assumed for the reader's bill or battery");

// 2. the calculator with numbers in its fields
const { Calc } = await import("../app/battery/customer/Calc.tsx");
function draw(typed) {
  const kept = lib.FIELDS.map((f) => f.start);
  lib.FIELDS.forEach((f) => { f.start = typed[f.key] ?? ""; });
  try { return text(renderToStaticMarkup(h(Calc))); } finally { lib.FIELDS.forEach((f, i) => { f.start = kept[i]; }); }
}
const seattle = draw({ peakKw: "400", demandCharge: "5.36", peakRate: "0.1218", offPeakRate: "0.0609", batteryKw: "100", batteryKwh: "400", peakHours: "4", days: "26", roundTrip: "86" });
// ruling alternative 3 (wip/alt-battery-customer-3): 85 percent of 536 reaches the bill; main: $536
ok(seattle.includes("At $5.36 per kW that is $456 a month.") && !seattle.includes("At $5 per kW"), "a demand charge of 5.36 is printed as $5.36 beside the $456 it makes (it read $5)");
const dec = draw({ peakKw: "62.5", demandCharge: "5.36", peakRate: "0.1218", offPeakRate: "0.0609", batteryKw: "5", batteryKwh: "13.5", peakHours: "1.5", days: "25.6", roundTrip: "86" });
ok(dec.includes("a 5 kW battery holding 13.5 kWh (2.7 hours)") && !dec.includes("holding 14 kWh"), "a 13.5 kWh battery is printed as 13.5 kWh (it read 14)");
ok(dec.includes("kW off a 62.5 kW peak") && dec.includes("your peak is 62.5 kW") && !dec.includes("63 kW"), "a 62.5 kW peak is printed as 62.5 kW in both places (it read 63)");
ok(dec.includes("discharge through all 1.5 hours of it") && dec.includes("off-peak rate, 25.6 days.") && dec.includes("over 25.6 days."), "1.5 hours and 25.6 days are printed as typed (the days read 26)");
const whole = draw({ peakKw: "500", demandCharge: "18", peakRate: "0.22", offPeakRate: "0.09", batteryKw: "200", batteryKwh: "800", peakHours: "4", days: "22", roundTrip: "85" });
ok(whole.includes("a 200 kW battery holding 800 kWh (4.0 hours) lowers the bill by $5,068 a month, $60,822 a year: $3,060 a month from a lower peak and $2,008 a month from moving energy.")
  && whole.includes("At $18 per kW that is $3,060 a month.") && whole.includes("your peak is 500 kW") && whole.includes("over 22 days."), "whole numbers read as they did: the browser proof's case, $5,068 a month (alternative 3; main: $5,608)");
const big = draw({ peakKw: "12,500", demandCharge: "18", peakRate: "0.22", offPeakRate: "0.09", batteryKw: "2000", batteryKwh: "8000", peakHours: "4", days: "22", roundTrip: "85" });
ok(big.includes("a 2,000 kW battery holding 8,000 kWh") && big.includes("off a 12,500 kW peak"), "a typed number is still grouped by thousands");
ok(lib.typed(13.5) === "13.5" && lib.typed(2000) === "2,000" && lib.rate(18) === "$18" && lib.rate(5.36) === "$5.36" && lib.rate(15.5) === "$15.50" && lib.rate(4.375) === "$4.375",
  "typed and rate: 13.5, 2,000, $18, $5.36, $15.50, $4.375");
const f = Object.fromEntries(lib.FIELDS.map((x) => [x.key, x]));
ok(lib.range(f.peakKw) === "more than 0, up to 1,000,000" && lib.range(f.demandCharge) === "0 to 500" && lib.range(f.roundTrip) === "1 to 100" && lib.range(f.peakHours) === "more than 0, up to 24",
  "a field's range in words: one that refuses zero says so");
const zero = draw({ peakKw: "0", demandCharge: "18", peakRate: "0.22", offPeakRate: "0.09", batteryKw: "200", batteryKwh: "800", peakHours: "4", days: "22", roundTrip: "85" });
ok(zero.includes("Not a number this page can use (more than 0, up to 1,000,000).") && zero.includes("1 of 9 still needed.") && !zero.includes("Saved a year"), "a peak of 0 is refused with its range in words, and no figure is shown");
const flat = draw({ peakKw: "200", demandCharge: "15.35", peakRate: "0.06797", offPeakRate: "0.06797", batteryKw: "50", batteryKwh: "100", peakHours: "2", days: "21", roundTrip: "86" });
ok(flat.includes("At your rates moving energy does not pay") && flat.includes("At $15.35 per kW that is $652 a month.")   /* alternative 3 (wip/alt-battery-customer-3): 85 percent of $768 */ && flat.includes("is a cost: -$23 a month."), "one price for every hour: moving energy does not pay, and the loss is shown as a cost");

// 3. the page as it opens
const opens = text(renderToStaticMarkup(h(Calc)));
ok(opens.includes("Fill in every field to see what the battery saves. 6 of 9 still needed. No number is assumed for you.") && !/\$\d/.test(opens), "as it opens: six of nine fields still needed and no figure");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
