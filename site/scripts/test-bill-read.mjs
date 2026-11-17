// Energy Research Warehouse (ERW) site, session 7547 (chain 304, part B): /learn/bill read as a household with its own
// bill in hand (docs/reviews/bill-read-2026-11-16.md). The site rows the read fixed, each held here, drawn to HTML with
// the site's own code, no build; and the figures this page shares with /learn/problems/prices-and-your-bill.
//   node --import ./scripts/tsx-register.mjs scripts/test-bill-read.mjs
// tests/test_session7547_bill_read.py runs it. Exits 1 on any failed check.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const rules = JSON.parse(fs.readFileSync(new URL("../data/bill_rules.json", import.meta.url), "utf-8"));
const { BillCalc, POWER_LINE } = await import("../app/learn/bill/BillCalc.tsx");
const { BILL_DECISIONS } = await import("../app/learn/bill/Decisions.tsx");
const lib = await import("../lib/bill.ts");

let pass = 0, fail = 0;
const check = (ok, what) => { ok ? pass++ : fail++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
const words = (html) => ent(html.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1");
// the rows of cost_of_power_monthly the page read on 16 November 2026 (replication/bill/source_rows.csv), as the server hands them
const W = { CA: { price: 44.8469, month: "2026-09", partial: false }, SCE: { price: 38.5228, month: "2026-09", partial: false }, SDGE: { price: 38.5228, month: "2026-09", partial: false },
  TX: { price: 39.5037, month: "2026-09", partial: false }, TXC: { price: 39.5037, month: "2026-09", partial: false } };
const caMonths = [{ month: "2026-10", price: 50.1104, partial: true }, { month: "2026-09", price: 44.8469, partial: false }, { month: "2026-08", price: 46.9855, partial: false }, { month: "2026-04", price: 12.5221, partial: false }];
const txMonths = [{ month: "2026-10", price: 42.6257, partial: true }, { month: "2026-09", price: 39.5037, partial: false }, { month: "2026-08", price: 36.6951, partial: false }];
const history = { CA: caMonths, SCE: [], SDGE: [], TX: txMonths, TXC: txMonths };
const draw = (first, extra = {}) => renderToStaticMarkup(h(BillCalc, { rules, wholesale: W, first, history, ...extra }));

// Row 1 (cases 1 and 3): the month of the bill in hand. A field lists every month held, newest first; the default is the cards'
{
  const html = draw("CA");
  check(html.includes('data-bill-month="7547"'), "the month field is drawn when months are held");
  const opts = [...html.matchAll(/<option value="(\d{4}-\d{2})"[^>]*>([^<]*)<\/option>/g)].map((m) => m[1]);
  check(opts.join(",") === "2026-10,2026-09,2026-08,2026-04", `the options are every month held, newest first (${opts.join(",")})`);
  check(/<option value="" selected="">2026-09, the default<\/option>/.test(html), "the first option is the cards' month, selected");
  check(html.includes("2026-10: $50.11 per MWh (partial)"), "a partial month is said to be partial in its option");
  check(words(html).includes("$44.85 per MWh in 2026-09"), "with no month chosen the bar is the cards' month, as before");
  check(!renderToStaticMarkup(h(BillCalc, { rules, wholesale: W, first: "CA" })).includes('data-bill-month="7547"'), "no months handed, no field (the calculator as session 7533 drew it)");
}
{
  const t = words(draw("CA", { firstMonth: "2026-04" }));
  check(t.includes("Wholesale energy $7.51, 3 percent") && t.includes("$12.52 per MWh in 2026-04."), "the default PG&E bill set against April 2026: $7.51, 3 percent (case 3)");
  check(t.includes("Total $229.63"), "the bill's lines do not move with the month (the total stays 229.63)");
  const p = words(draw("TXC", { firstMonth: "2026-10" }));
  check(p.includes("$42.63 per MWh in 2026-10 (a partial month).") && !p.includes("the latest held"), "a partial month chosen is said to be partial, not 'the latest held'");
  const q = words(draw("TXC", { firstMonth: "2025-01" }));
  check(q.includes("$39.50 per MWh in 2026-09"), "a month not held for the bill falls back to the default");
  const tip = draw("CA");
  check(words(tip).includes("every line of the bill stays at the tariff's rates as read"), "the field's tip says the lines stay at the rates as read");
}
// the reset puts the month back too
{
  const src = fs.readFileSync(new URL("../app/learn/bill/BillCalc.tsx", import.meta.url), "utf-8");
  check(/const reset = \(\) => \{\s*setMonth\(null\);/.test(src), "Reset this bill to its defaults puts the month back to the default");
  const page = fs.readFileSync(new URL("../app/learn/bill/page.tsx", import.meta.url), "utf-8");
  check(page.includes("<BillCalc rules={rules} wholesale={wholesale} history={history} />"), "the page hands the calculator every month held");
}

// Row 2 (cases 1 and 2): the bill's own power line beside the wholesale energy; "Everything else" holds the rest of it
{
  const ca = words(draw("CA"));
  check(ca.includes("The bill's own power line: Generation $69.45, 30 percent of the bill, beside the wholesale energy's $26.91."), "PG&E: Generation $69.45, 30 percent, beside $26.91");
  check(ca.includes("Everything else, $202.72: the rest of the bill's power line (below), the wires"), "PG&E: 'Everything else' names the rest of the power line");
  const sce = words(draw("SCE"));
  check(/The bill's own power line: Generation \$[\d.]+, \d+ percent of the bill/.test(sce), "SCE: its Generation line");
  const sd = draw("SDGE");
  check(sd.includes('data-power-line="none"') && words(sd).includes("the rest of the power, inside SDG&E's one line"), "SDG&E: no power line, said, and 'Everything else' says the power is inside its one line");
  const hou = words(draw("TXC"));
  check(hou.includes("The bill's own power line: Energy charge (your retail electric provider) $51.18, 54 percent of the bill"), "CenterPoint: the retailer's energy charge, $51.18, 54 percent");
  for (const k of lib.BILL_KEYS) {
    const p = POWER_LINE[k];
    if (!p) continue;
    const r = JSON.parse(JSON.stringify(rules));
    const b = k === "CA" ? lib.billCA(r, lib.defaultsCA(r)) : k === "SCE" ? lib.billTOU(r, k, lib.defaultsTOU(r, k)) : k === "TX" ? lib.billTX(r, lib.defaultsTX(r)) : lib.billTDSP(r, k, lib.defaultsTDSP(r, k));
    check(b.lines.filter((l) => l.id === p.id).length === 1, `the power line of ${k} (${p.id}) is one line of the bill`);
  }
}

// Row 4 (case 2): in Texas the wires company's lines together, on the group's row
for (const k of ["TX", "TXC"]) {
  const html = draw(k);
  const b = k === "TX" ? lib.billTX(rules, lib.defaultsTX(rules)) : lib.billTDSP(rules, k, lib.defaultsTDSP(rules, k));
  const sum = b.lines.filter((l) => l.group && l.group.startsWith("Delivery")).reduce((a, l) => a + l.amount, 0);
  const energy = b.lines.find((l) => l.id === POWER_LINE[k].id).amount;
  const shown = html.match(/data-group-sum="Delivery \([^)]*\)">\$([\d,.]+)</);
  check(!!shown && Math.abs(Number(shown[1]) - sum) < 0.005 && Math.abs(sum - (b.total - energy)) < 1e-9, `${k}: the delivery lines together (${shown && shown[1]}) are the total less the energy charge`);
}
check(!draw("CA").includes("data-group-sum"), "no group sum on a California bill (unchanged)");

// Row 5 (case 1): where a reader outside San Francisco finds the territory letter
{
  const ex = rules.bills.CA.default_territory.examples;
  check(ex.cite === "pge_prelim_a" && ex.quote === "FRESNO* Under 3,500' R 3,501'-6,500' Y Over 6,500' Z" && ex.words.startsWith("Fresno County below 3,500 feet is Territory R"), "the rules file holds Preliminary Statement Part A's Fresno passage");
  const t = words(draw("CA"));
  check(t.includes("Fresno County below 3,500 feet is Territory R") && t.includes("Sheet No. 34601-E"), "the territory field's tip names Fresno's territory and the sheet");
  check(t.includes("Territory R: 17.7 kWh a day in summer, 10.4 in winter"), "territory R is in the list with Sheet 5's quantities");
}

// The decisions fold: the month line says it is a field now; still 14 choices
{
  const d = BILL_DECISIONS.find((x) => x.key === "wholesale-month");
  check(d.text.includes("\"Wholesale price, month\"") && BILL_DECISIONS.length === 14, "the fold's month line names the new field; 14 choices");
}

// The figures shared with /learn/problems/prices-and-your-bill (questions b3 and b4): the same keys, the same functions
{
  const prob = fs.readFileSync(new URL("../lib/problems.ts", import.meta.url), "utf-8");
  check(prob.includes("k: `bill|${s}|total`") && prob.includes("k: `bill|${s}|share|${price.ts_utc}`"), "the problem set keys its bill figures as the cards do");
  const ca = lib.defaultBill(rules, "CA").total, tx = lib.defaultBill(rules, "TX").total;
  check(Math.abs(ca - lib.billCA(rules, lib.defaultsCA(rules)).total) < 1e-9 && Math.abs(tx - lib.billTX(rules, lib.defaultsTX(rules)).total) < 1e-9, `the problem set's bills equal the cards' (${ca.toFixed(2)}, ${tx.toFixed(2)})`);
  const ed = JSON.parse(fs.readFileSync(new URL("../data/problem_editions/2026-10-15.json", import.meta.url), "utf-8"));
  const vals = (k) => [...new Set(JSON.stringify(ed).match(new RegExp(`\\{"v":([\\d.]+),"k":"${k.replace(/[|]/g, "\\|")}"`, "g")) ?? [])].map((s) => Number(s.match(/"v":([\d.]+)/)[1]));
  const ec = vals("bill|CA|total"), et = vals("bill|TX|total");
  check(ec.length === 1 && Math.abs(ec[0] - ca) < 0.005 && et.length === 1 && Math.abs(et[0] - tx) < 0.005, `the frozen edition of 15 October holds the same totals (${ec}, ${et})`);
}

// No row or figure of a license-held table in what this session commits (site/data/license_status.json: cost_of_power_monthly
// is held by grid, ISO-NE, MISO and NYISO; the page reads CAISO and ERCOT only)
{
  const held = /\b(isone|miso|nyiso):/;
  for (const f of ["source_rows.csv", "page_figures.csv", "page_figures.json", "cases.json"]) {
    const t = fs.readFileSync(new URL(`../../replication/bill/${f}`, import.meta.url), "utf-8");
    check(!held.test(t), `replication/bill/${f} holds no row of a held grid`);
  }
}
// no em dash in the files this session wrote or changed
for (const f of ["../app/learn/bill/BillCalc.tsx", "../app/learn/bill/page.tsx", "../app/learn/bill/Decisions.tsx", "../data/bill_rules.json", "./bill-figures.mjs", "./test-bill-read.mjs"]) {
  check(!fs.readFileSync(new URL(f, import.meta.url), "utf-8").includes(String.fromCharCode(0x2014)), `no em dash in ${f}`);
}

console.log(`${pass} of ${pass + fail} checks pass`);
if (fail) process.exitCode = 1;
