// Energy Research Warehouse (ERW) site, session 7533 (chain 304): /learn/bill at the done line, drawn to HTML with the
// site's own code, no build. The faults this session fixed, each held here, and the decisions fold.
//   node --import ./scripts/tsx-register.mjs scripts/test-bill-render.mjs
// tests/test_session7533_bill.py runs it. Exits 1 on any failed check.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const rules = JSON.parse(fs.readFileSync(new URL("../data/bill_rules.json", import.meta.url), "utf-8"));
const { BillCalc } = await import("../app/learn/bill/BillCalc.tsx");
const { BILL_DECISIONS, BillDecisions } = await import("../app/learn/bill/Decisions.tsx");
const { Num, heldBy, BILL_GRID } = await import("../components/Num.tsx");
const lib = await import("../lib/bill.ts");

let pass = 0, fail = 0;
const check = (ok, what) => { ok ? pass++ : fail++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const W = { price: 40, month: "2026-09", partial: false };
const wholesale = Object.fromEntries(lib.BILL_KEYS.map((k) => [k, W]));
const clone = (o) => JSON.parse(JSON.stringify(o));
const draw = (r, first) => renderToStaticMarkup(h(BillCalc, { rules: r, wholesale, ...(first ? { first } : {}) }));
// the visible words only (the bar's width in its style attribute is not printed)
const noisy = (html) => (html.replace(/<[^>]+>/g, " ").match(/\d+\.\d{7,}/g) ?? []);

// 1. A bill's figures are not held for a license: no bill is in a held grid, and a total reads no table
for (const k of lib.BILL_KEYS) {
  check(heldBy(`bill|${k}|total`) === null, `bill|${k}|total is not held`);
  check(heldBy(`bill|${k}|wholesale|2026-09-01T00:00:00Z`) === null, `bill|${k}|wholesale is not held (${BILL_GRID[k]})`);
  check(heldBy(`bill|${k}|share|2026-09-01T00:00:00Z`) === null, `bill|${k}|share is not held`);
  check(BILL_GRID[k] === rules.bills[k].iso, `BILL_GRID of ${k} is the rules file's iso (${rules.bills[k].iso})`);
  const html = renderToStaticMarkup(h(Num, { check: `bill|${k}|total`, raw: 229.6299 }, "229.63"));
  check(html.includes(`data-check="bill|${k}|total"`) && !html.includes("license needed"), `the ${k} total draws as a checked number`);
}
check(heldBy("bill|ZZ|share|2026-09-01T00:00:00Z") !== null, "a bill of no known grid is held, as before");
check(heldBy("series|cost_of_power_monthly|isone:.H.INTERNAL_HUB|rt_load_weighted|2026-09-01T00:00:00Z") !== null, "an ISO-NE row of cost_of_power_monthly is still held");
check(heldBy("series|cost_of_power_monthly|ercot:HB_HUBAVG|rt_load_weighted|2026-09-01T00:00:00Z") === null, "an ERCOT row of cost_of_power_monthly is shown");

// 2. A computed kWh in a line's words is printed to a tenth (16.9 x 30 printed 506.99999999999994)
check(lib.kwhs(16.9 * 30) === "507" && lib.kwhs(333 * 1.3) === "432.9" && lib.kwhs(195) === "195", "kwhs prints to a tenth");
{
  const r = clone(rules);
  r.bills.SCE.defaults.season = "summer";
  const html = draw(r, "SCE");
  check(html.includes("507 kWh within the Region 9 baseline"), "SCE, summer, Region 9: 507 kWh within the baseline");
  check(noisy(html).length === 0, `SCE, summer, Region 9: no floating-point noise (${noisy(html).join(", ")})`);
}
{
  const r = clone(rules);
  r.bills.SDGE.defaults.baseline_kwh = 333;
  const html = draw(r, "SDGE");
  check(html.includes("432.9 kWh (up to 130 percent of your 333 kWh allowance)"), "SDG&E, a 333 kWh allowance: 432.9 kWh");
  check(noisy(html).length === 0, "SDG&E: no floating-point noise");
}
let worst = [];
for (const season of ["summer", "winter"]) {
  for (const t of Object.keys(rules.bills.CA.baseline_quantities.code_B)) for (const kwh of [150, 600, 1234]) {
    const r = clone(rules); Object.assign(r.bills.CA.defaults, { season, territory: t, kwh });
    worst = worst.concat(noisy(draw(r)));
  }
  for (const g of Object.keys(rules.bills.SCE.baseline_quantities.basic)) for (const kwh of [150, 600, 1234]) {
    const r = clone(rules); Object.assign(r.bills.SCE.defaults, { season, region: g, kwh });
    worst = worst.concat(noisy(draw(r, "SCE")));
  }
}
check(worst.length === 0, `every PG&E territory and SCE region, both seasons, three uses: no floating-point noise (${worst.slice(0, 3).join(", ")})`);

// 3. SCE's summer has no super off-peak hours: the field says so in summer, and only there
{
  const r = clone(rules);
  r.bills.SCE.defaults.season = "summer";
  check(draw(r, "SCE").includes('data-sce-summer-super="1"'), "SCE, summer: the line under the super off-peak share");
  check(!draw(rules, "SCE").includes("data-sce-summer-super"), "SCE, winter: no such line");
  r.bills.SDGE.defaults.season = "summer";
  check(!draw(r, "SDGE").includes("data-sce-summer-super"), "SDG&E, summer: no such line (its super off-peak hours run all year)");
  const a = lib.billTOU(rules, "SCE", { ...lib.defaultsTOU(rules, "SCE"), season: "summer", superShare: 0 }).total;
  const b = lib.billTOU(rules, "SCE", { ...lib.defaultsTOU(rules, "SCE"), season: "summer", superShare: 0.5 }).total;
  check(Math.abs(a - b) < 1e-9, "SCE, summer: the super off-peak share moves nothing (as the line says)");
}

// 4. The calculator opens on PG&E unless told otherwise
check(draw(rules).includes("Base Services Charge (Income Tier 3)"), "the calculator opens on PG&E");
check(draw(rules, "TXC").includes("Delivery (CenterPoint)"), "first=TXC opens on CenterPoint");

// 5. The decisions fold
{
  const html = renderToStaticMarkup(h(BillDecisions));
  check(html.includes('data-decisions="7533"') && !/<details[^>]* open/.test(html), "the fold is drawn, closed to start");
  check((html.match(/data-decision="/g) ?? []).length === BILL_DECISIONS.length && BILL_DECISIONS.length === 14, `14 choices (${BILL_DECISIONS.length})`);
  check(BILL_DECISIONS.every((d) => html.includes(`data-decision-default="${d.key}"`) && html.includes(`data-decision-source="${d.key}"`)), "each choice has its default and its source in a tip");
  check(html.includes('href="/data/methods/bill"'), "the fold links the method note");
  check(!/—/.test(html), "no em dash in the fold");
  for (const d of BILL_DECISIONS.filter((x) => /Change it in the field "([^"]+)"/.test(x.text))) {
    const field = d.text.match(/Change it in the field "([^"]+)"/)[1];
    const any = lib.BILL_KEYS.some((k) => draw(rules, k).includes(field.replace(/'/g, "&#x27;")));
    check(any, `the field "${field}" the fold names is on the calculator`);
  }
}
const page = fs.readFileSync(new URL("../app/learn/bill/page.tsx", import.meta.url), "utf-8");
check(/<BillDecisions \/>\s*\n\s*<TableDownloads/.test(page), "the page mounts the fold above the downloads");

console.log(`${pass} of ${pass + fail} passed`);
if (fail) process.exitCode = 1;
