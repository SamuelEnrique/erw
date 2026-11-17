// Energy Research Warehouse (ERW) site, session 7501 (chain 304): /contracts drawn to HTML with the page's own code,
// without building the site, on rows made up for this test (the real table is internal: no name and no row of it is
// in this file). The page's default export is called for each view; its two database functions are answered by a
// stand-in for fetch, so no request leaves the machine. It holds the five faults fixed in session 7501 and the
// decisions block:
//   1. the panel's "not stated" lists the rows that file no balancing authority (it listed none);
//   2. a balancing authority filed in two capitalisations is one entry of the panel;
//   3. the limits box counts the rows that file no number and says so, and says on hover which rows are "held here";
//   4. a last execution date after today is "as filed" in the panel's note, and the oldest quarter listed says on
//      hover that it is held in part;
//   5. the tolling tag says on hover how many of its contracts are in force;
//   and the decisions: every choice with its default and its source on hover, the same list as the method note's,
//   drawn with and without the internal token; without the token no figure and no row is drawn.
//   node --import ./scripts/tsx-register.mjs scripts/test-contracts-render.mjs
import fs from "node:fs";
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

// ---- made-up rows: one quarter (2026 Q2) of nine rows, an older quarter held in part, one row dated in 2101
const row = (i, day, over = {}) => ({ event_id: `made-up:${i}`, event_date: day, status: "in_force", mw: null, price: null, seller: `Example Seller ${1 + (i % 3)}`, buyer: `Example Buyer ${1 + (i % 4)}`,
  affiliate: "N", agreement: `A-${i}`, product_type: "MB", product: "ENERGY", class: "F", term: "LT", commencement: "20260501", termination: "20360501", quantity: "", units: "",
  rate: "", rate_units: "", rate_description: "Market Based", pod_ba: "", pod_location: "", quarter: "2026_Q2", ...over });
const Q2 = [
  row(1, "2026-06-20", { pod_ba: "PSCO", rate: "41.5", rate_units: "$/MWH", rate_description: "" }),
  row(2, "2026-06-19", { pod_ba: "PSCo" }),
  row(3, "2026-06-18", { pod_ba: " PSCO " }),
  row(4, "2026-06-10"), row(5, "2026-06-09"), row(6, "2026-05-30", { rate_description: "" }), row(7, "2026-05-02", { affiliate: "Y" }),
  row(8, "2026-04-15", { pod_ba: "CISO", product: "Capacity" }),
  row(9, "2026-04-02", { pod_ba: "CISO", product: "POINT-TO-POINT AGREEMENT" }),
];
const OLD = [row(20, "2024-02-11"), row(21, "2024-01-30", { pod_ba: "CISO" })];
const LATER = [row(30, "2101-01-01")];
const all = [...Q2, ...OLD, ...LATER];
const priced = all.filter((r) => r.rate !== "").length;
const months = [...new Set(all.map((r) => r.event_date.slice(0, 7)))].sort();
const party = (rank) => ({ rank, name: `Example Party ${rank}`, contracts: 10 - rank, rows: 12 - rank, counterparties: 3, mw_filed: rank === 1 ? 120.5 : 0, rows_with_mw: rank === 1 ? 2 : 0 });
const list = { parties: 2, contracts: 17, rows: 21, top: [party(1), party(2)] };
const mwList = { parties: 1, mw: 120.5, contracts_with_mw: 1, top: [{ rank: 1, name: "Example Party 1", mw: 120.5, contracts_with_mw: 1, contracts: 9, rank_contracts: 1, contracts_over: 0 }] };
const three = (v) => ({ energy: v, capacity: v, tolling: v });
const change = (quarter, product, inForce, more = {}) => ({ quarter, product, contracts_in_force: inForce, rows_in_force: inForce + 2, ...more });
const summary = {
  rows: all.length, priced, first: "2024-01-21", last: "2101-01-01", quarters: ["2026_Q2"],
  by_month: months.map((m) => ({ month: m, rows: all.filter((r) => r.event_date.startsWith(m)).length, priced: all.filter((r) => r.event_date.startsWith(m) && r.rate !== "").length })),
  by_product: [{ product: "ENERGY", rows: 10, priced }], by_ba: [{ ba: "not stated", rows: 6 }, { ba: "ERCO", rows: 2 }, { ba: "Erco", rows: 1 }],
  largest: { quarter: "2026_Q2", top: 25, names: { filed: 40, after_rules: 31, merged_groups: 4, merged_names: 13, doubtful_pairs: 3 }, lists: { buyer: three(list), seller: three(list) } },
  terms: { quarter: "2026_Q2", top: 25, rows: 60, mw_ceiling: 6809, mw: { rows_stated: 5, rows_over: 1, by_product: three({ contracts: 17, contracts_with_mw: 1, contracts_over: 0 }) },
    prices: { filed_number: 20, none: 2, words_only: 38, read: 3, read_usd_per_mwh: 2, read_by_unit: { "$/MWH": 2, "$/KW-MO": 1 }, unread: { no_dollar_amount: 30, several_amounts: 2, no_unit: 1, conditional: 1, other_numbers: 1, units_disagree: 0 } },
    buyers: { rows_merged: 22 }, tags: { tolling_rows: 7, tolling_contracts: 5, storage_rows: 0, storage_words_elsewhere: { seller_name: 2, rate_description: 1, agreement_id: 0, tariff_reference: 0 }, storage_words_rows: 3 },
    by_mw: { buyer: three(mwList), seller: three(mwList) },
    changes: [change("2026_Q1", "all", 50), change("2026_Q1", "energy", 20), change("2026_Q1", "capacity", 10), change("2026_Q1", "tolling", 3),
      ...["all", "energy", "capacity", "tolling"].map((p, i) => change("2026_Q2", p, [52, 21, 11, 4][i], { contracts_new: 4, contracts_gone: 2, contracts_kept: [48, 17, 7, 0][i] }))] },
};

process.env.SUPABASE_URL = "https://rows.invalid";
process.env.SUPABASE_ANON_KEY = "stand-in";
process.env.INTERNAL_COSTS_TOKEN = "stand-in-token-of-the-render-test";
let asked = 0;
globalThis.fetch = async (url, init) => {
  asked++;
  const fn = String(url).split("/rpc/")[1] ?? "", args = JSON.parse(init?.body ?? "{}");
  const body = fn === "internal_eqr_summary" ? summary : fn === "internal_eqr_contracts" ? all.filter((r) => r.event_date >= args.p_from && r.event_date < args.p_to) : null;
  return new Response(JSON.stringify(body ?? { message: "the stand-in answers nothing else" }), { status: body ? 200 : 404, headers: { "Content-Type": "application/json" } });
};
const { default: Page } = await import("../app/contracts/page.tsx");
const C = await import("../lib/contracts.ts");
const { CONTRACTS_DECISIONS } = await import("../app/contracts/Decisions.tsx");
const draw = async (q) => renderToStaticMarkup(await Page({ searchParams: Promise.resolve(q) }));
const marked = (html, key) => (html.match(new RegExp(`data-n="${key}">([^<]*)<`)) ?? [])[1];
function sound(html, what) {
  const ids = [...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1]);
  const twice = ids.filter((id, i) => ids.indexOf(id) !== i);
  const lost = [...html.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]).filter((id) => !ids.includes(id));
  const buttons = [...html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)];
  const nameless = buttons.filter((b) => !/aria-label="[^"]+"/.test(b[1]) && !text(b[2]).trim());
  ok(!twice.length && !lost.length && !nameless.length, `${what}: every tip has its one target and every button a name${twice.length ? `; an id twice: ${twice[0]}` : ""}${lost.length ? `; a tip with no target: ${lost[0]}` : ""}`);
  ok(!html.includes(String.fromCharCode(0x2014)) && !html.includes(String.fromCharCode(0x2013)), `${what}: no em dash and no en dash`);
}

// ---- the library
ok(C.baOf("PSCo") === "PSCO" && C.baOf(" psco ") === "PSCO" && C.baOf("") === "not stated" && C.baOf(null) === "not stated" && C.baOf("not stated") === "not stated", "a balancing authority is its code trimmed and in capitals, and \"not stated\" for none");
const power = C.PRODUCTS[0], every = C.PRODUCTS.at(-1);
ok(C.filter(Q2, power, "not stated").length === 4 && C.filter(Q2, every, "not stated").length === 4, "fault 1: \"not stated\" lists the four rows of energy, capacity and tolling that file no balancing authority (it listed none)");
ok(C.filter(Q2, power, "PSCO").length === 3 && C.filter(Q2, power, "PSCo").length === 3, "fault 2: PSCO, PSCo and a padded PSCO are one authority's three rows, whichever spelling the address names");
const bas = C.byBa(C.filter(Q2, power, null));
ok(JSON.stringify(bas) === JSON.stringify([{ ba: "not stated", rows: 4 }, { ba: "PSCO", rows: 3 }, { ba: "CISO", rows: 1 }]), "fault 2: the panel lists an authority once, most rows first");
ok(bas.reduce((a, b) => a + b.rows, 0) === C.filter(Q2, power, null).length && bas.every((b) => C.filter(Q2, power, b.ba).length === b.rows), "every entry of the panel opens exactly the rows it counts, and the entries add up to the product's rows");
ok(C.choices({ ba: "PSCo" }, ["2026-Q2"]).ba === "PSCO" && C.choices({ ba: "not stated" }, ["2026-Q2"]).ba === "not stated" && C.choices({ ba: "<x>" }, ["2026-Q2"]).ba === null, "the address's authority is read as the panel names it; one that is no code is dropped");
ok(C.heldFrom("2024-Q1", "2024-01-21") === "2024-01-21" && C.heldFrom("2024-Q1", "2024-01-01") === null && C.heldFrom("2024-Q2", "2024-01-21") === null && C.heldFrom("2024-Q1", null) === null && C.heldFrom("2024-Q1", "soon") === null,
  "fault 4: a quarter is held in part only when the first day held falls inside it, after its first day");
ok(C.inForce(summary.terms, "tolling") === 4 && C.inForce(summary.terms, "all") === 52 && C.inForce({ ...summary.terms, changes: [] }, "tolling") === null, "fault 5: the contracts in force of a product are the newest quarter's, and none when no quarter is held");

// ---- the list by quarter signed
const open = await draw({});
const t = text(open);
ok(/were signed in 2026 Q2/.test(t) && marked(open, "rows") === "8" && marked(open, "priced") === "1", "the page opens on the newest quarter listed, 2026 Q2, with its 8 rows of energy, capacity and tolling, 1 priced");
ok(marked(open, "unpriced") === String(all.length - priced) && /rows held here[\s\S]{0,700}file\s+no number\./.test(t) && !/<\/span> do\./.test(open), "fault 3: the limits box counts the rows that file no number, in those words");
ok(/data-held-here="1"/.test(open) && /The rows the first view lists: the contracts signed since 2024-01-21/.test(t) && /The other three views read every row of the newest quarter's file/.test(t), "fault 3: \"held here\" says on hover which rows it is, and that the other views read the whole file");
ok(/executed from 2024-01-21 to 2101-01-01 as filed\./.test(t), "fault 4: a last execution date after today is \"as filed\" in the panel's note");
ok((open.match(/data-held-from="/g) ?? []).length === 1 && /data-held-from="2024-Q1"/.test(open) && /Held\s+from\s+2024-01-21, not from the quarter's first day/.test(t), "fault 4: only the oldest quarter listed says it is held in part, and from which day");
ok(/data-later="1"/.test(open) && !/q=2101-Q1/.test(open), "the row dated 2101 is counted beside the list and its quarter is not listed");
const nav = open.match(/<nav aria-label="Delivered in"[\s\S]*?<\/nav>/)?.[0] ?? "";
ok((nav.match(/>PSCO</g) ?? []).length === 1 && !/>PSCo</.test(nav) && /ba=not%20stated/.test(nav), "fault 2: the panel names PSCO once; \"not stated\" is a link like the others");
ok(/3 of the 12 rows held here name ERCOT/.test(t), "ERCOT's rows are counted whatever the capitals of its code (ERCO 2, Erco 1)");
const none = await draw({ ba: "not stated" });
ok(marked(none, "rows") === "4" && (none.match(/<tbody>([\s\S]*?)<\/tbody>/)?.[1].match(/<tr\b/g) ?? []).length === 4 && /delivered in not stated/.test(text(none)), "fault 1: the address of \"not stated\" draws its four rows");
const psco = await draw({ ba: "PSCo", product: "energy" });
ok(marked(psco, "rows") === "3" && /delivered in PSCO/.test(text(psco)), "fault 2: the address of PSCo draws the authority's three rows under its one name");
sound(open, "the list by quarter signed");

// ---- the other three views
const terms = await draw({ view: "terms" });
ok(/data-tolling-in-force="4"/.test(terms) && /7 rows of 5 contracts carry the product name Tolling Energy/.test(text(terms)) && /4 of the contracts are in force/.test(text(terms)), "fault 5: the tolling tag counts every row filed and says on hover that 4 of its 5 contracts are in force");
sound(terms, "what the filings state");
for (const view of ["largest", "mw"]) {
  const html = await draw({ view, product: "capacity" });
  ok(html.includes(`data-${view}="1"`) && /data-held-here="1"/.test(html), `the ${view} view draws, with the limits box and its hover`);
  sound(html, `the ${view} view`);
}

// ---- ruling alternative 3 (session 7701, wip/alt-contracts-3, not a default on main): a row whose buyer is a market
// operator is left out of the rows signed and of the list, and the sentence says how many on hover
{
  all.push(row(40, "2026-06-21", { buyer: "PJM Settlement, Inc." }), row(41, "2026-06-22", { buyer: "Example Independent System Operator", product: "Capacity" }));
  const alt = await draw({});
  ok(marked(alt, "rows") === "8" && /data-operators="2"/.test(alt) && /2 more rows\s+name a market operator as the buyer/.test(text(alt)) && !/PJM Settlement/.test(alt),
    "alternative 3: two rows whose buyer is a market operator are left out of the 8 rows signed and of the list, and the hover says 2");
  const energy = await draw({ product: "energy" });
  ok(/data-operators="1"/.test(energy) && /1 more row\s+names a market operator/.test(text(energy)), "alternative 3: the count follows the product chosen");
  ok(C.isOperatorBuyer({ buyer: "Midcontinent Independent System Operator, Inc." }) && C.isOperatorBuyer({ buyer: "ISO New England Inc." })
    && !C.isOperatorBuyer({ buyer: "Example Power Company" }) && !C.isOperatorBuyer({ buyer: null }), "alternative 3: the operator names are matched by their words; a party's name is not");
  sound(alt, "alternative 3, the list by quarter signed");
  all.splice(all.length - 2, 2);
  ok(!/data-operators=/.test(await draw({})), "alternative 3: with no operator buyer the sentence has no such hover");
}

// ---- the decisions
const D = CONTRACTS_DECISIONS;
ok(D.length >= 15 && new Set(D.map((d) => d.key)).size === D.length && D.every((d) => d.text && d.session && d.def && d.source), `${D.length} decisions, each with its own key, its session, its default and its source`);
for (const [what, html] of [["the list", open], ["what the filings state", terms]]) {
  ok(html.includes('data-decisions="7501"') && html.includes(`data-decision-count="${D.length}"`) && D.every((d) => html.includes(`data-decision="${d.key}"`) && html.includes(`data-decision-default="${d.key}"`) && html.includes(`data-decision-source="${d.key}"`)
    && html.includes(`id="tip-decision-7501-${d.key}"`)), `${what}: the decisions block draws every choice, each with its default and its source in a hover tip`);
}
ok(!/<details[^>]*data-decisions="7501"[^>]*\bopen\b/.test(open), "the block is a fold, closed to start");
const note = fs.readFileSync(new URL("../../docs/methods/contracts.md", import.meta.url), "utf-8").replace(/\r\n/g, "\n");
const flat = (s) => s.replace(/\s+/g, " ");
const lost = D.filter((d) => !flat(note).includes(flat(d.text)) || !flat(note).includes(flat(d.def)) || !flat(note).includes(flat(d.source)));
ok(lost.length === 0, `the method note (docs/methods/contracts.md) carries every decision word for word, with its default and its source${lost.length ? `; not found: ${lost.map((d) => d.key).join(", ")}` : ""}`);
ok(D.every((d) => !/\b(should|recommend|best|we advise)\b/i.test(`${d.text} ${d.def}`)), "no decision gives advice");

// ---- a server that holds no internal token: what a request can reach while the table is internal
const before = asked;
process.env.INTERNAL_COSTS_TOKEN = "";
const bare = await draw({});
ok(asked === before && /data-contracts="unavailable"/.test(bare) && !/data-n="/.test(bare) && !/<tbody>/.test(bare) && !/Example (Seller|Buyer|Party)/.test(bare), "without the token nothing is asked of the database, and no figure, no row and no party's name is drawn");
ok(bare.includes('data-decisions="7501"') && /An internal table: this page is read only in the internal view/.test(text(bare)), "without the token the decisions and the source line are still drawn: they describe the method, not a row");
for (const view of ["largest", "mw", "terms"]) {
  const html = await draw({ view });
  ok(!/data-n="/.test(html) && !/Example Party/.test(html) && /not loaded here yet/.test(text(html)), `without the token the ${view} view draws no figure and says it is not loaded`);
}

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
