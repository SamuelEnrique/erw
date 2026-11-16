// Energy Research Warehouse (ERW) site, session 7502 (chain 304): the severance page's parts drawn to HTML without a
// build, and the calculator's default price.
//   node --import ./scripts/tsx-register.mjs scripts/test-severance-page.mjs
// 1. The decisions block (app/severance/Decisions.tsx): one line a choice, each with its default and its source in a
//    tip that has its target, closed to start, no grey note, no dash of the long kinds.
// 2. The calculator (app/severance/Calculator.tsx) as it opens, drawn with a price given: Texas, oil, 1,000 bbl, and
//    the three figures a reader first sees, to the cent.
// 3. The default price (lib/leaseprices.ts latestMonthMean): the read begins on a month's first day, so the latest
//    complete month is averaged whole when the table runs weeks behind (it began 75 days back until this session, and a
//    table three weeks behind then lost the month's first days). The rows are a fixture made for the test (each day's
//    value is its day of the month), answered by a stand-in for fetch: no network.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");

// 1. the decisions block
const { SeveranceDecisions, SEVERANCE_DECISIONS } = await import("../app/severance/Decisions.tsx");
const block = renderToStaticMarkup(h(SeveranceDecisions));
const ids = [...block.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
const asked = [...block.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
ok(SEVERANCE_DECISIONS.length >= 10 && new Set(SEVERANCE_DECISIONS.map((d) => d.key)).size === SEVERANCE_DECISIONS.length, `the list holds ${SEVERANCE_DECISIONS.length} choices, each key once`);
ok((block.match(/data-decision="/g) ?? []).length === SEVERANCE_DECISIONS.length && block.includes(`data-decision-count="${SEVERANCE_DECISIONS.length}"`), "the block draws one line a choice and says how many");
ok((block.match(/data-decision-default="/g) ?? []).length === SEVERANCE_DECISIONS.length && (block.match(/data-decision-source="/g) ?? []).length === SEVERANCE_DECISIONS.length, "every choice has its default and its source");
ok(asked.length === SEVERANCE_DECISIONS.length && asked.every((id) => ids.filter((x) => x === id).length === 1), `the ${asked.length} tips each have their one target`);
ok(/<details[^>]*data-decisions="7502"/.test(block) && !/<details[^>]* open/.test(block), "the fold is closed to start");
// the tip's own mark (the small "i" button of components/tool/ToolPage.tsx) is grey; no words of the block are
ok(!block.replace(/<button\b[\s\S]*?<\/button>/g, "").includes("text-muted"), "no grey note in the block: a default and a source are in the tip");
ok(SEVERANCE_DECISIONS.every((d) => d.text && d.def && d.source), "no choice has an empty text, default or source");
ok(![0x2014, 0x2013].some((c) => block.includes(String.fromCharCode(c))), "no em dash and no en dash in the block");
ok(/href="[^"]*\/data\/methods\/severance"|data-review-link|methods\/severance/.test(block), "the block points to the method note");
const page = fs.readFileSync(new URL("../app/severance/page.tsx", import.meta.url), "utf-8");
ok(page.includes("<SeveranceDecisions />") && page.includes("<Brand noUsage>"), "the page mounts the block under both tabs and keeps its promise that nothing is counted");
const rules = JSON.parse(fs.readFileSync(new URL("../data/severance_rules.json", import.meta.url), "utf-8"));
const lpGas = rules.states.TX.products.gas.options.find((o) => o.id === "tx_lp_gas").certified, lpOil = rules.states.TX.products.oil.options.find((o) => o.id === "tx_lp_oil").certified;
const cert = SEVERANCE_DECISIONS.find((d) => d.key === "certified-price").def;
ok(cert.includes(String(lpGas.prices[0].price)) && cert.includes(String(lpOil.prices[0].price)), "the certified prices the block states are the rules file's latest");
const districts = rules.states.NM.products.oil.base.find((b) => b.rate === "district").districts.list;
const nm = SEVERANCE_DECISIONS.find((d) => d.key === "nm-district").def;
ok(nm.includes(String(districts.length)) && nm.includes((Math.min(...districts.map((d) => d.rate)) * 100).toFixed(4)) && nm.includes((Math.max(...districts.map((d) => d.rate)) * 100).toFixed(4)), "the district count and range the block states are the rules file's");
ok(SEVERANCE_DECISIONS.find((d) => d.key === "la-gas-rate").def.includes(String(rules.states.LA.products.gas.base[0].rate * 100)), "the Louisiana gas rate the block states is the rules file's");

// 2. the calculator as it opens
const { Calculator } = await import("../app/severance/Calculator.tsx");
const calc = text(renderToStaticMarkup(h(Calculator, { rules, prices: { oil: 102.07, gas: 2.99, label: { oil: "the label", gas: "the label" } } })));
ok(calc.includes("$102,070.00") && calc.includes("$4,695.22") && calc.includes("$6.25"), "the calculator opens on Texas oil, 1,000 bbl: gross $102,070.00, tax $4,695.22, the fee $6.25");
const none = text(renderToStaticMarkup(h(Calculator, { rules, prices: { oil: null, gas: null, label: { oil: "not held: enter a price", gas: "not held: enter a price" } } })));
ok(none.includes("Enter a volume and a price.") && !none.includes("$0.00"), "with no price held it asks for one and shows no figure");

// 3. the default price
const days = (month, last) => Array.from({ length: last }, (_, i) => i + 1)
  .filter((d) => ![0, 6].includes(new Date(`${month}-${String(d).padStart(2, "0")}T00:00:00Z`).getUTCDay()))
  .map((d) => ({ entity: "eia:wti_cushing", variable: "spot_price", ts_utc: `${month}-${String(d).padStart(2, "0")}T00:00:00Z`, value: d, unit: "USD/bbl", freq: "P1D" }));
let table = [], calls = [];
process.env.SUPABASE_URL = "http://localhost:9/rest/v1/";
process.env.SUPABASE_ANON_KEY = "stand-in";
globalThis.fetch = async (url) => {
  const q = new URL(String(url)).searchParams;
  calls.push(q.get("ts_utc"));
  const since = (q.get("ts_utc") ?? "gte.").replace(/^gte\./, "");
  const rows = table.filter((r) => r.ts_utc >= since);
  return new Response(JSON.stringify(rows.slice(Number(q.get("offset") ?? 0), Number(q.get("offset") ?? 0) + Number(q.get("limit") ?? 1000))), { status: 200 });
};
const P = await import("../lib/leaseprices.ts");
ok(P.latestMonthSince(Date.parse("2026-11-16T12:00:00Z")) === "2026-08-01T00:00:00Z" && P.latestMonthSince(Date.parse("2027-01-05T00:00:00Z")) === "2026-10-01T00:00:00Z",
  "the read begins on the first day of the month three months before: 1 August for 16 November, 1 October for 5 January");
const july = days("2026-07", 31), august = days("2026-08", 31), september = days("2026-09", 11);
const mean = (xs) => Math.round((xs.reduce((a, r) => a + r.value, 0) / xs.length) * 100) / 100;
table = [...july, ...august, ...september];
let m = await P.latestMonthMean("eia:wti_cushing", Date.parse("2026-09-20T12:00:00Z"));
ok(m && m.month === "2026-08" && m.n === august.length && m.value === mean(august), `a table current to the month: August whole, ${august.length} days`);
table = [...july, ...august];
calls = [];
m = await P.latestMonthMean("eia:wti_cushing", Date.parse("2026-09-20T12:00:00Z"));
const from7 = july.filter((r) => r.ts_utc >= "2026-07-07");
ok(m && m.month === "2026-07" && m.n === july.length && m.value === mean(july) && mean(july) !== mean(from7),
  `a table three weeks behind: July whole, ${july.length} days at ${mean(july)} (from 75 days back it was ${from7.length} days at ${mean(from7)})`);
ok(calls.length > 0 && calls.every((c) => c === "gte.2026-06-01T00:00:00Z"), "the request asks from 1 June, a month's first day");
table = [...days("2026-05", 31)];
m = await P.latestMonthMean("eia:wti_cushing", Date.parse("2026-09-20T12:00:00Z"));
ok(m === null, "a table four months behind gives no default price: the page says to enter one");
table = [...september];
m = await P.latestMonthMean("eia:wti_cushing", Date.parse("2026-09-20T12:00:00Z"));
ok(m === null, "one month held, not yet complete: no default price");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
