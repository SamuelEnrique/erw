// Energy Research Warehouse (ERW) site, session 7510 (chain 304, part B): /contracts read as the reader it is for
// (docs/reviews/contracts-read-2026-11-16.md). The page is drawn to HTML with its own code, without building the site,
// on rows made up for this test (the real table is internal: no name and no row of it is in this file); its two
// database functions are answered by a stand-in for fetch, so no request leaves the machine. It holds what the read
// fixed, by the row of the review file:
//   1. a quarter's link and a product's link keep the balancing authority chosen;
//   2. the rows beside each quarter say on hover that they are every product's, delivered anywhere;
//   3. the authority chosen stays in the panel when it has no row in the quarter, with its count;
//   4. an address that names a quarter the page does not list says so;
//   5. one row is "1 row ... was signed": one agreement, one seller, one buyer;
//   6. a term under one year also gives its days;
//   7. a number filed with no unit says "no unit filed";
//   8. the fold "What a row is" names the quantity and the price units, the rows that differ only in their price,
//      and a market operator as the buyer;
//   9. a grid's balancing authority code that is not its name says the name on hover;
//  10. the megawatts view gives no advice.
//   node --import ./scripts/tsx-register.mjs scripts/test-contracts-read.mjs
import { register } from "node:module";
import { renderToStaticMarkup } from "react-dom/server";

register(`data:text/javascript,${encodeURIComponent(`
const SRC = "const f = (o) => ({ variable: o?.variable ?? '', className: '', style: { fontFamily: 'stand-in' } }); export const IBM_Plex_Mono = f, IBM_Plex_Sans = f, Source_Serif_4 = f;";
export async function resolve(s, c, next) { return s === "next/font/google" ? { url: "erw-font-stub:google", shortCircuit: true } : next(s, c); }
export async function load(u, c, next) { return u === "erw-font-stub:google" ? { format: "module", source: SRC, shortCircuit: true } : next(u, c); }
`)}`);

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");

// ---- made-up rows: two quarters of execution, 2026 Q2 and 2026 Q1
const row = (i, day, over = {}) => ({ event_id: `made-up:${i}`, event_date: day, status: "in_force", mw: null, price: null, seller: `Example Seller ${i}`, buyer: `Example Buyer ${i}`,
  affiliate: "N", agreement: `A-${i}`, product_type: "MB", product: "ENERGY", class: "F", term: "LT", commencement: "20260701", termination: "20410630", quantity: "", units: "",
  rate: "", rate_units: "", rate_description: "Market Based", pod_ba: "", pod_location: "", quarter: "2026_Q2", ...over });
const Q2 = [
  row(1, "2026-06-20", { pod_ba: "SWPP", rate: "31.5", rate_units: "$/MWH", rate_description: "" }),                                       // 15.0 years, a price with its unit
  row(2, "2026-06-12", { pod_ba: "CISO", product: "CAPACITY", term: "ST", commencement: "20260801", termination: "20260831", quantity: "10", units: "MW-MO", rate: "3000", rate_units: "$/MW-MO", rate_description: "" }),   // one month
  row(3, "2026-06-11", { pod_ba: "CISO", product: "CAPACITY", term: "ST", commencement: "20261001", termination: "20261014", rate: "11.24", rate_units: "", rate_description: "" }),   // 14 days, a number with no unit
  row(4, "2026-05-02", { pod_ba: "CISO", product: "CAPACITY", commencement: "20260101", termination: "20261231", rate: "3", rate_units: "$/KW-MO", rate_description: "" }),              // 1.0 years: no days
  row(5, "2026-04-20", { pod_ba: "PJM" }),
  row(6, "2026-04-03", { pod_ba: "DUK", commencement: "20260403", termination: "20260403" }),                                              // a term of one day
];
const Q1 = [row(20, "2026-02-11", { pod_ba: "SWPP" }), row(21, "2026-01-30", { pod_ba: "SWPP" }), row(22, "2026-01-15", { pod_ba: "NYIS", product: "CAPACITY" })];
const all = [...Q2, ...Q1];
const priced = all.filter((r) => r.rate !== "").length;
const months = [...new Set(all.map((r) => r.event_date.slice(0, 7)))].sort();
const summary = {
  rows: all.length, priced, first: "2026-01-01", last: "2026-06-20", quarters: ["2026_Q2"],
  by_month: months.map((m) => ({ month: m, rows: all.filter((r) => r.event_date.startsWith(m)).length, priced: all.filter((r) => r.event_date.startsWith(m) && r.rate !== "").length })),
  by_product: [{ product: "ENERGY", rows: 5, priced: 1 }], by_ba: [{ ba: "CISO", rows: 3 }],
};
process.env.SUPABASE_URL = "https://rows.invalid";
process.env.SUPABASE_ANON_KEY = "stand-in";
process.env.INTERNAL_COSTS_TOKEN = "stand-in-token-of-the-read-test";
globalThis.fetch = async (url, init) => {
  const fn = String(url).split("/rpc/")[1] ?? "", args = JSON.parse(init?.body ?? "{}");
  const body = fn === "internal_eqr_summary" ? summary : fn === "internal_eqr_contracts" ? all.filter((r) => r.event_date >= args.p_from && r.event_date < args.p_to) : null;
  return new Response(JSON.stringify(body ?? { message: "the stand-in answers nothing else" }), { status: body ? 200 : 404, headers: { "Content-Type": "application/json" } });
};
const { default: Page } = await import("../app/contracts/page.tsx");
const C = await import("../lib/contracts.ts");
const { GRID_CHOICES } = await import("../lib/gridtool.ts");
const draw = async (q) => renderToStaticMarkup(await Page({ searchParams: Promise.resolve(q) }));
const marked = (html, key) => (html.match(new RegExp(`data-n="${key}">([^<]*)<`)) ?? [])[1];
const nav = (html, label) => html.match(new RegExp(`<nav aria-label="${label}"[\\s\\S]*?</nav>`))?.[0] ?? "";
const sentence = (html) => text(html.match(/<p[^>]*data-summary="1"[^>]*>([\s\S]*?)<\/p>/)?.[1] ?? "").trim();

// ---- the library
const R = (over) => row(0, "2026-06-01", over);
ok(C.termDays(R({ commencement: "20260801", termination: "20260831" })) === 31 && C.termDays(R({ commencement: "20260601", termination: "20260630" })) === 30 && C.termDays(R({ commencement: "20261001", termination: "20261014" })) === 14
  && C.termDays(R({ commencement: "20260403", termination: "20260403" })) === 1, "row 6: a term under one year has its days, the first and the last both counted (31, 30, 14, 1)");
ok(C.termDays(R({ commencement: "20260101", termination: "20261231" })) === null && C.termDays(R({})) === null && C.termDays(R({ termination: "" })) === null && C.termDays(R({ commencement: "20260601", termination: "20260501" })) === null,
  "row 6: a term drawn as 1.0 years or more, a term with no end and a term that ends before it starts have no days");
ok(C.termDays(R({ commencement: "20260101", termination: "20261115" })) === 319 && C.termYears(R({ commencement: "20260101", termination: "20261115" })).toFixed(1) === "0.9", "row 6: the longest term that still gives its days is one drawn as 0.9 years");
ok(C.some(1, "row") === "row" && C.some(0, "row") === "rows" && C.some(2, "row") === "rows" && C.some(1, "was", "were") === "was" && C.some(3, "was", "were") === "were", "row 5: a count's noun is singular for one only");
ok(C.baName("CISO", GRID_CHOICES) === "California Independent System Operator (CAISO)" && C.baName("SWPP", GRID_CHOICES) === "Southwest Power Pool (SPP)" && C.baName("PJM", GRID_CHOICES) === null && C.baName("DUK", GRID_CHOICES) === null && C.baName("not stated", GRID_CHOICES) === null,
  "row 9: a grid's code that is not its name has the name the site gives it; a code that is the name, and a code the site names nowhere, have none");
ok(C.quarterNotListed("2025", ["2026-Q2"]) === "2025" && C.quarterNotListed("2026-Q2", ["2026-Q2"]) === null && C.quarterNotListed(undefined, ["2026-Q2"]) === null && C.quarterNotListed("<b>", ["2026-Q2"]) === null,
  "row 4: a quarter named and not listed is told; one listed, none named, and one that is not plain characters are not");

// ---- row 1: the links keep the balancing authority chosen
const ciso = await draw({ q: "2026-Q2", product: "capacity", ba: "CISO" });
const quarters = nav(ciso, "Quarter signed"), products = nav(ciso, "Product");
ok(/href="\/contracts\?q=2026-Q1&amp;product=capacity&amp;ba=CISO"/.test(quarters) && /href="\/contracts\?q=2026-Q2&amp;product=capacity&amp;ba=CISO"/.test(quarters), "row 1: each quarter's link keeps the product and the balancing authority chosen");
ok(/href="\/contracts\?q=2026-Q2&amp;product=energy&amp;ba=CISO"/.test(products) && /href="\/contracts\?q=2026-Q2&amp;product=all&amp;ba=CISO"/.test(products), "row 1: each product's link keeps the quarter and the balancing authority chosen");
const open = await draw({});
ok(/href="\/contracts\?q=2026-Q1&amp;product=power"/.test(nav(open, "Quarter signed")) && !/&amp;ba=/.test(nav(open, "Quarter signed")) && !/&amp;ba=/.test(nav(open, "Product")), "row 1: with no authority chosen the links name none");
ok(/href="\/contracts\?q=2026-Q2&amp;product=capacity"[^>]*>Every balancing authority/.test(nav(ciso, "Delivered in")), "row 1: \"Every balancing authority\" still drops the choice");

// ---- row 2: what the count beside a quarter is
ok(/data-quarter-rows="1"/.test(open) && /id="tip-contracts-quarter-rows"/.test(open) && /The rows beside each quarter are every product's, delivered anywhere/.test(text(open)), "row 2: the rows beside each quarter say on hover that they are every product's, delivered anywhere");

// ---- row 3: the authority chosen stays in the panel
const swppQ1 = await draw({ q: "2026-Q1", product: "capacity", ba: "SWPP" });
ok(/data-ba-chosen="SWPP"/.test(nav(swppQ1, "Delivered in")) && />SWPP<\/a>\s*<span[^>]*>0<\/span>/.test(nav(swppQ1, "Delivered in")) && marked(swppQ1, "rows") === "0", "row 3: an authority with no row in the quarter stays in the panel as the choice, with 0");
ok(!/data-ba-chosen=/.test(ciso) && (nav(ciso, "Delivered in").match(/>CISO<\/a>/g) ?? []).length === 1, "row 3: an authority the panel lists is listed once");
ok(/^Among the contracts filed with FERC, 0 rows of capacity delivered in SWPP were signed in 2026 Q1: 0 agreements between 0 sellers and 0 buyers\. 0 of the rows state a price as a number\.$/.test(sentence(swppQ1)), "row 3: no row reads \"0 rows ... were signed\"");

// ---- row 4: a quarter that is not listed
const year = await draw({ q: "2025", product: "energy", ba: "SWPP" });
ok(/data-quarter-not-listed="2025"/.test(year) && /Quarter signed: "2025" is not listed here, so 2026 Q2 is shown\./.test(text(year)), "row 4: an address that names a year says it is not listed and which quarter is shown");
ok(!/data-quarter-not-listed/.test(open) && !/data-quarter-not-listed/.test(ciso) && !/data-quarter-not-listed/.test(await draw({ q: "<script>" })) && !/data-quarter-not-listed/.test(await draw({ view: "terms", q: "2025" })), "row 4: nothing is said for no quarter, a listed one, one that is no plain word, or another view");

// ---- row 5: one row, one agreement
const one = await draw({ q: "2026-Q2", product: "energy", ba: "SWPP" });
ok(/^Among the contracts filed with FERC, 1 row of energy delivered in SWPP was signed in 2026 Q2: 1 agreement between 1 seller and 1 buyer\. 1 of the rows states a price as a number\.$/.test(sentence(one)), "row 5: one row reads \"1 row ... was signed: 1 agreement between 1 seller and 1 buyer\"");
ok(/1 agreement; one row per product of an agreement\./.test(text(one)) && /The other 0 give words/.test(text(one)), "row 5: the headline's notes count one agreement, and the other 0 give words");
ok(/3 rows of capacity delivered in CISO were signed in 2026 Q2: 3 agreements between 3 sellers and 3 buyers\. 3 of the rows state a price/.test(sentence(ciso)), "row 5: three rows read as before");
const pjm = await draw({ q: "2026-Q2", product: "energy", ba: "PJM" });
ok(/The other 1 gives words/.test(text(pjm)) && /0 of the rows state a price/.test(sentence(pjm)), "row 5: \"The other 1 gives words\"");

// ---- row 6: a term under one year also gives its days
ok(/\(0\.1 years<span data-term-days="31">: 31 days<\/span>\)/.test(ciso) && /\(0\.0 years<span data-term-days="14">: 14 days<\/span>\)/.test(ciso) && /\(1\.0 years\)/.test(ciso) && (ciso.match(/data-term-days=/g) ?? []).length === 2, "row 6: one month reads \"0.1 years: 31 days\", fourteen days \"0.0 years: 14 days\", a year \"1.0 years\" alone");
ok(/\(15\.0 years\)/.test(one) && !/data-term-days=/.test(one), "row 6: a term of fifteen years gives no days");
ok(/\(0\.0 years<span data-term-days="1">: 1 day<\/span>\)/.test(await draw({ q: "2026-Q2", product: "energy", ba: "DUK" })), "row 6: a term of one day reads \"1 day\"");

// ---- row 7: a number filed with no unit
ok((ciso.match(/data-no-unit="1"/g) ?? []).length === 1 && /11\.24<span[^>]*data-no-unit="1"> \(no unit filed\)<\/span>/.test(ciso) && />3000 \$\/MW-MO</.test(ciso) && />3 \$\/KW-MO</.test(ciso), "row 7: a number filed with no unit says so; a number with its unit is as before");
ok(!/data-no-unit/.test(pjm) && />Market Based</.test(pjm), "row 7: a rate filed as words is as before");

// ---- row 8: the fold names what the cells hold
const t = text(open);
ok(/data-fold-quantity="1"/.test(open) && /megawatts by the month, the day or the year \(MW-MO, MW-DAY, MW-YR\)/.test(t), "row 8: the fold says what a quantity's units are");
ok(/3 \$\/KW-MO and 3,000 \$\/MW-MO are the same price/.test(t) && /is not converted/.test(t), "row 8: the fold says a price filed in two units is not converted");
ok(/data-fold-repeat="1"/.test(open) && /one agreement can file a row for each year, month or peak period of its price/.test(t) && /is not shown here yet/.test(t), "row 8: the fold says why rows of one agreement differ only in their price, and that the period is not shown");
ok(/data-fold-operator="1"/.test(open) && /a sale into an organized market is filed with the operator as its customer/.test(t), "row 8: the fold says what a market operator as the buyer is");
ok(/A term under one year also gives its days, the first and the last both counted/.test(t), "row 6: the fold says how the days are counted");

// ---- row 9: a grid's code says its name on hover
const dn = nav(ciso, "Delivered in");
ok(/id="tip-contracts-ba-CISO"/.test(dn) && /data-ba-name="CISO"/.test(dn) && /CISO is the balancing authority code of California Independent System Operator \(CAISO\)/.test(text(dn)), "row 9: CISO says on hover that it is CAISO's code");
const dnOpen = nav(open, "Delivered in");
ok(/data-ba-name="SWPP"/.test(dnOpen) && />PJM<\/a>/.test(dnOpen) && />DUK<\/a>/.test(dnOpen) && !/data-ba-name="PJM"/.test(dnOpen) && !/data-ba-name="DUK"/.test(dnOpen), "row 9: SWPP has its name; PJM, whose code is its name, and a code the site does not name have no tip");

// ---- row 10: no advice, and every tip sound on every page drawn
const mwSummary = { ...summary, terms: { quarter: "2026_Q2", top: 25, rows: 9, mw_ceiling: 6809, mw: { rows_stated: 1, rows_over: 0, by_product: { energy: { contracts: 5, contracts_with_mw: 0, contracts_over: 0 }, capacity: { contracts: 4, contracts_with_mw: 0, contracts_over: 0 }, tolling: { contracts: 0, contracts_with_mw: 0, contracts_over: 0 } } },
  prices: { filed_number: 4, none: 0, words_only: 5, read: 0, read_usd_per_mwh: 0, read_by_unit: {}, unread: {} }, buyers: { rows_merged: 0 }, tags: { tolling_rows: 0, tolling_contracts: 0, storage_rows: 0, storage_words_elsewhere: {}, storage_words_rows: 0 },
  by_mw: { buyer: { energy: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] }, capacity: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] }, tolling: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] } },
    seller: { energy: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] }, capacity: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] }, tolling: { parties: 0, mw: 0, contracts_with_mw: 0, top: [] } } }, changes: [] } };
Object.assign(summary, mwSummary);
const mw = await draw({ view: "mw" });
ok(/data-mw="1"/.test(mw) && /The contract itself, not its row here, is the record of its size\./.test(text(mw)) && !/\b(should|recommend|we advise)\b/i.test(text(mw).split("Decisions on this page")[0]), "row 10: the megawatts view states what a row is and gives no advice");
for (const [what, html] of [["the page as it opens", open], ["capacity in CISO", ciso], ["an authority with no row", swppQ1], ["a year named", year], ["the megawatts view", mw]]) {
  const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
  const twice = ids.filter((id, i) => ids.indexOf(id) !== i);
  const lost = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]).filter((id) => !ids.includes(id));
  ok(!twice.length && !lost.length, `${what}: every tip has its one target${twice.length ? `; an id twice: ${twice[0]}` : ""}${lost.length ? `; a tip with no target: ${lost[0]}` : ""}`);
  ok(!html.includes(String.fromCharCode(0x2014)) && !html.includes(String.fromCharCode(0x2013)), `${what}: no em dash and no en dash`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
