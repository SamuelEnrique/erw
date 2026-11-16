// Chain 304, part B (session 7519): "What a battery earns" (/cost-of-power/battery) read as a merchant battery developer
// choosing between two ERCOT nodes, for five cases (docs/reviews/battery-read-2026-11-16.md). The page's view is drawn to
// HTML without a build (scripts/tsx-loader.mjs) from real months: the default case's public download, hour by hour
// (public/battery/erw_2026_battery_dispatch.csv, ERCOT, 4 hours, perfect foresight, 36 months), added up by local month
// as the table holds them. Each site fault the read found is held here as fixed; the row numbers are the review's. Where
// the warehouse's table is on the machine (ERW_OUTPUT_DIR, else ../warehouse/output) the two real cases that showed rows
// 3 and 5 are drawn as well. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-battery-read.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const B = await import("../lib/batterystack.ts");
const F = await import("../lib/battery/finance.ts");
const VW = await import("../lib/battery/view.ts");
const P = await import("../app/cost-of-power/battery/place.ts");
const S = await import("../app/cost-of-power/battery/Scenarios.tsx");
const { Income } = await import("../app/cost-of-power/battery/Income.tsx");
const here = path.dirname(fileURLToPath(import.meta.url));
const read = (...p) => fs.readFileSync(path.join(here, "..", ...p), "utf-8");
const steps = JSON.parse(read("data", "battery_scenario_steps.json"));

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const two = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// ---- the default case's months, from the public download: the table's variables, per MW
function dispatchRows() {
  const lines = read("public", "battery", "erw_2026_battery_dispatch.csv").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(","), ix = (k) => head.indexOf(k);
  const streams = ["energy", "regup", "regdn", "rrs", "ecrs", "nspin", "ancillary", "total"];
  const by = new Map();
  for (const l of lines.slice(1)) {
    const c = l.split(","), m = c[ix("local_month")];
    if (!by.has(m)) by.set(m, { days: new Set(), sums: Object.fromEntries(streams.map((s) => [s, 0])) });
    const t = by.get(m);
    t.days.add(c[ix("local_day")]);
    for (const s of streams) t.sums[s] += Number(c[ix(`revenue_${s}_usd`)]);
  }
  const rows = [];
  for (const [m, t] of by) {
    const ts = `${m}-01T00:00:00Z`, inMonth = new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 0)).getUTCDate();
    for (const s of streams) rows.push({ variable: `foresight_4h_revenue_${s}_usd_per_mw`, ts_utc: ts, value: t.sums[s] });
    rows.push({ variable: "foresight_4h_days_held", ts_utc: ts, value: t.days.size }, { variable: "foresight_4h_days_in_month", ts_utc: ts, value: inMonth }, { variable: "foresight_4h_days_left_out", ts_utc: ts, value: inMonth - t.days.size });
  }
  return rows;
}
const rows = dispatchRows();
const ms = B.monthsOf(rows, "foresight", 4);
const l12 = B.lastTwelve(ms);
ok(ms.length === 36 && ms.every((r) => r.held) && l12 && l12.length === 12, `the public download gives 36 held months, the last twelve ${l12?.[0].m} to ${l12?.[11].m}`);

// the page's client view for one address, on months given (the server's part is page.tsx, read as source below)
function draw(query, months = ms, dur = 4, strat = "foresight") {
  const q = Object.fromEntries(new URLSearchParams(query));
  const asked = B.inputsOf({ ...q, dur: String(dur), strat }, false);
  const costs = B.COSTS[asked.dur], d = F.defaultsOf(costs);
  const offered = F.ONLY_DEFAULT;
  const A = F.parseScenarios(q, d, offered, asked.mw).a;
  const x = { ...asked, fom: A.fom, ds: F.debtUsd(A, asked.mw) };
  const scenarioParams = Object.fromEntries(Object.entries(q).filter(([k]) => F.isScenarioParam(k) || F.isOldParam(k)));
  const stepMeta = { built: steps.built, rte_steps: steps.rte_steps, cycle_steps: steps.cycle_steps };
  return renderToStaticMarkup(
    h(S.BatteryDecisions, { ms: months, mw: x.mw, costs, stepCase: null, stepMeta, initial: scenarioParams, view: VW.parseView(q), peak: null, hours: x.dur, years: [] },
      h(S.BatteryHeadline, { ms: months, x, gridName: "ERCOT", gridFrom: "2018" }),
      h(S.BatteryCharts, { ms: months, x, ys: B.years(months), upper: "", strategyLine: "", brokenNote: null }),
      h(Income, { ms: months, x, pre: B.inputsKey(x), gridName: "ERCOT", products: B.PRODUCTS.ercot, capacityWords: B.CAPACITY_WORDS.ercot, em: {}, events: [] }),
      h(S.Scenarios, { x })));
}

const plainDrawHas = (s) => draw("").includes(s);

// ---- rows 1 and 2 (case 1: two ERCOT nodes): a place the address names is said, and the node list is linked
const ercot = B.gridOf("ercot"), caiso = B.gridOf("caiso");
const west = P.placeNotes({ grid: "ercot", hub: "HB_WEST" }, ercot);
ok(west.length === 1 && west[0].includes("its HB_HUBAVG hub") && west[0].includes("is not held here") && !west[0].includes("HB_WEST"), "row 1: an address naming another ERCOT hub is told the hub average is shown, and the name typed is not repeated");
ok(P.placeNotes({ node: "ANY_RN", region: "LZ_WEST" }, ercot).length === 1 && P.placeNotes({ node: "ANY_RN" }, ercot)[0].includes("node list"), "row 1: a node or a zone named gets the same one sentence, which names the node list for ERCOT");
ok(P.placeNotes({}, ercot).length === 0 && P.placeNotes({ hub: "hb_hubavg" }, ercot).length === 0 && P.placeNotes({ hub: "SP15" }, caiso).length === 0 && P.placeNotes({ node: "TH_SP15_GEN-APND" }, caiso).length === 0, "row 1: no place named, or the grid's own place named, says nothing");
const np15 = P.placeNotes({ hub: "NP15" }, caiso);
ok(np15.length === 1 && np15[0].includes("in CAISO, its SP15 hub") && !np15[0].includes("node list"), "row 1: CAISO's sentence names SP15 and no ERCOT list");
const page = read("app", "cost-of-power", "battery", "page.tsx");
ok(page.includes("asItWas.push(...placeNotes(q, g));") && page.includes("const asItWas = [...typedNotes(q, asked), ...scenarioNotes(q, defaultsOf(COSTS[asked.dur]), offered)];"), "row 1: the page's status line carries the sentence, after session 263's");
ok(P.NODE_LIST === "/cost-of-power?view=allgrids&rows=nodes" && /x\.grid === "ercot" \? <span data-node-list="1">[^<]*<Link href=\{NODE_LIST\}>the ERCOT node list<\/Link>/.test(page), "row 2: under the income table ERCOT's page links the site's list of settlement points by name");
ok(read("app", "cost-of-power", "AllGridsView.tsx").includes('rows: "nodes"') && read("app", "cost-of-power", "AllGridsView.tsx").includes("data-node-pair"), "row 2: the All grids tab still holds the node list and its two nodes side by side");
// row 6 (a ruling, the default taken): the line beside ERCOT's awards does not link the awards page. Sessions 115, 116,
// 120 and 178 hold that this page names nothing of it (tests/test_session178.py and three more); the rule is the owner's
ok(!page.includes("battery/awards") && page.includes("data-awards-beside"), "row 6: the awards line is drawn and the page still names nothing of the awards page (the rule of sessions 115 to 178, left to the owner)");
// row 8: ECRS is spelled out on hover, as every other service is in place
ok(read("app", "cost-of-power", "battery", "Income.tsx").includes('ecrs: "ERCOT Contingency Reserve Service"') && plainDrawHas('title="ERCOT Contingency Reserve Service"'), "row 8: the income table's ECRS row gives the service's name on hover");

// ---- row 3: no figure is written "-0"
const zeroYear = ms.map((r) => (r.m.startsWith("2024") ? { ...r, energy: -300 / 12, total: r.ancillary - 300 / 12 } : r));   // a hand case: a year whose energy is USD -0.30 per kW
const zero = draw("", zeroYear);
ok(B.years(zeroYear).find((y) => y.y === "2024").energy / 1000 > -0.5 && B.years(zeroYear).find((y) => y.y === "2024").energy < 0, "row 3: the hand case's 2024 energy is between USD -0.50 and 0 per kW");
ok(!/[>\s:]-0[<\s,]/.test(zero) && zero.includes("2024: energy 0, ancillary"), "row 3: a figure that rounds to zero is written 0 in the year chart's hover, on its axis and in its table");
const plainDraw = draw("");
ok(!/[>\s:]-0[<\s,]/.test(plainDraw), "row 3: the default case draws no \"-0\"");

// ---- row 5: an energy row below zero says how, on hover, and only then
const belowTip = "over that span the battery paid more for the energy it charged than it was paid for the energy it sold";
ok(!plainDraw.includes('data-energy-below-zero="1"') && plainDraw.includes("Energy (charge low, sell high)"), "row 5: with every energy figure above zero the row is as it was");
ok(zero.includes('data-energy-below-zero="1"') && words(zero).includes(belowTip) && words(zero).includes("returns 86 percent of what it charges"), "row 5: an energy figure below zero says how on hover, with the model's round trip");

// ---- row 4 (case 4: a toll against merchant): the contract's income and the months above its price
const price = 12.08;
const toll = draw(`bn=100&bp=${price}`);
const line = (toll.match(/<p[^>]*data-contract-line="b"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1];
const attr = (k) => Number((toll.match(new RegExp(`data-${k}="([^"]*)"`)) ?? [])[1]);
const market = B.sumOf(l12, "total") / 1000;
const above12 = l12.filter((r) => r.total / 1000 > price).length, aboveAll = ms.filter((r) => r.total / 1000 > price).length;
ok(!plainDraw.includes("data-contract-line"), "row 4: with no contract the line is not drawn (the default page is what it was)");
ok(line !== "" && Math.abs(attr("contract-year") - price * 12) < 1e-9 && attr("contract-rest") === 0, `row 4: scenario B's toll on the whole battery pays USD ${two(price * 12)} per kW a year and leaves nothing to the market`);
ok(words(line).includes(`USD ${two(price * 12)} in all, beside USD ${two(market)} for the same battery with no contract`), `row 4: the two incomes stand side by side (${two(price * 12)} and ${two(market)})`);
ok(attr("above-twelve") === above12 && attr("above-held") === aboveAll && attr("months-held") === 36 && words(line).includes(`In ${above12} of the last twelve months`) && words(line).includes(`in ${aboveAll} of the 36 months held`), `row 4: the months the market paid more than the toll's price, counted from the download (${above12} of 12, ${aboveAll} of 36)`);
const half = draw("an=50&ap=10&bn=100&bp=4.19");
const halfLine = words((half.match(/<p[^>]*data-contract-line="a\+b"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1]);
ok(halfLine.includes(`Scenario A's contract pays USD ${two(0.5 * 10 * 12)} per kW of the battery a year (50 percent of its power at USD 10 per kW-month, twelve months), and the market on the rest USD ${two(0.5 * market)}`) && halfLine.includes("Scenario B's contract pays USD 50.28"), "row 4: a half contract counts the market on the other half, and both scenarios are said when both hold one");
ok(!/should|better|worse|recommend|prefer/i.test(words(line) + halfLine), "row 4: the line states figures and takes no view");

// ---- the warehouse's table, where the machine has it: the two real cases of rows 3 and 5
const dir = process.env.ERW_OUTPUT_DIR ?? path.join(here, "..", "..", "warehouse", "output");
const file = path.join(dir, "battery_stack_monthly.csv");
if (fs.existsSync(file)) {
  const real = fs.readFileSync(file, "utf-8").split(/\r?\n/).filter((l) => l.startsWith("ercot:HB_HUBAVG,dayahead_2h_")).map((l) => { const c = l.split(","); return { variable: c[1], ts_utc: c[2], value: Number(c[3]) }; });
  const rm = B.monthsOf(real, "dayahead", 2);
  const y18 = B.years(rm).find((y) => y.y === "2018");
  const html = draw("", rm, 2, "dayahead");
  ok(y18 && y18.energy < 0 && html.includes('data-energy-below-zero="1"'), `rows 3 and 5, the table: ERCOT, 2 hours, the day-ahead schedule, 2018 energy USD ${y18 ? two(y18.energy / 1000) : "?"} per kW is below zero and the row says how`);
  ok(!/[>\s:]-0[<\s,]/.test(html), "row 3, the table: the same view draws no \"-0\"");
} else console.log(`skip the table's two cases: ${file} is not on this machine`);

// ---- row 7: the method note's worked example of a stress repeat, beside what the page draws from the stress table
const note = fs.readFileSync(path.join(here, "..", "..", "docs", "methods", "battery_earns_algorithm.md"), "utf-8");
ok(note.includes("### 11.4 The page read as its reader (session 7519, 16 November 2026)") && note.includes("USD 3,105.51 per kW, so a repeat adds USD 155.28 per kW a year and takes NPV from USD -697.80 to +462.02 per kW") && note.includes("+583.43"), "row 7: the note gives the stress repeat as the page draws it, and keeps session 297's three figures as written");
const stressFile = path.join(dir, "battery_stack_stress_daily.csv");
if (fs.existsSync(stressFile)) {
  const uri = fs.readFileSync(stressFile, "utf-8").split(/\r?\n/).filter((l) => l.startsWith("ercot:HB_HUBAVG,foresight_4h_revenue_total_usd_per_mw,") && l.endsWith(",uri_2021")).map((l) => Number(l.split(",")[3]));
  const peak = uri.reduce((a, v) => a + v, 0) / 1000;
  const d = F.defaultsOf(B.COSTS[4]);
  const base = F.resultOf(d, market, { peak, hours: 4 }), one = F.resultOf({ ...d, stress: 1 }, market, { peak, hours: 4 });
  ok(uri.length === 18 && two(peak) === "3,105.51" && two(peak / d.life) === "155.28" && two(base.npv) === "-697.80" && two(one.npv) === "462.02", `row 7, the table: Uri's window is USD ${two(peak)} per kW over ${uri.length} days, and one repeat takes NPV from ${two(base.npv)} to ${two(one.npv)}`);
} else console.log(`skip the stress table's case: ${stressFile} is not on this machine`);

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
