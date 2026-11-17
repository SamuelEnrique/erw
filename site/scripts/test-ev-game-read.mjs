// Energy Research Warehouse (ERW) site, session 7550 (chain 304, part B): /play/ev read as the reader it is for, its
// site rows of docs/reviews/ev-game-read-2026-11-16.md held fixed. The game and its decisions fold are drawn to HTML with
// the site's own code, as the page mounts them.
//   node --import ./scripts/tsx-register.mjs scripts/test-ev-game-read.mjs      (tests/test_session7550_ev_game_read.py runs it)
// Exits 1 on any failure. No request, nothing written.
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { EvGame } = await import("../app/play/ev/EvGame.tsx");
const { EvDecisions, EV_DECISIONS } = await import("../app/play/ev/Decisions.tsx");
const { verdict, DEFAULTS } = await import("../lib/ev.ts");
const D = JSON.parse(fs.readFileSync(new URL("../data/ev_prices.json", import.meta.url), "utf-8"));
const L = JSON.parse(fs.readFileSync(new URL("../data/license_status.json", import.meta.url), "utf-8"));
const us = { code: "US", name: "United States", power: D.us.power, gas: D.us.gas };
const draw = (start) => renderToStaticMarkup(h(EvGame, { states: D.states, us, built: D.built_at, ...(start ? { start } : {}) }));
const text = (html) => html.replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ").replace(/ ([,.;:)])/g, "$1");
const tipOf = (html, id) => { const m = html.match(new RegExp(`data-field="${id}">([\\s\\S]*?)<input`)); return m ? text(m[1]) : ""; };

let bad = 0;
const check = (ok, what) => { if (!ok) bad++; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

// row 1 (case 1, a commuter in Phoenix): Arizona's gasoline is a region's; the tip says which, in words, and to whom
const az = tipOf(draw({ code: "AZ" }), "gas");
check(/Petroleum Administration for Defense District, PADD 5 except California/.test(az), "Arizona: the gasoline tip spells out PADD");
check(/the price the game gives Alaska, Arizona, Hawaii, Nevada and Oregon\./.test(az), "Arizona: the gasoline tip names the five states the game gives the region's price");
// every regional state names itself among the states given its price, and its region's entity's states are all named
let regional = 0, named = 0;
for (const s of D.states.filter((x) => x.gas?.where === "region")) {
  regional++;
  const t = tipOf(draw({ code: s.code }), "gas");
  const same = D.states.filter((x) => x.gas?.entity === s.gas.entity).map((x) => x.name);
  if (t.includes("Petroleum Administration for Defense District") && same.every((n) => t.includes(n))) named++;
}
check(regional > 0 && named === regional, `every state given a region's price names the region in words and its states (${named} of ${regional})`);
const mn = tipOf(draw({ code: "MN" }), "gas");
check(/Minnesota's own weekly series/.test(mn) && !/Petroleum Administration/.test(mn), "Minnesota (its own series): the tip unchanged");

// row 2 (case 3, a driver in Fresno): what the state average is; for California, the bill page's utility tariffs
const caHtml = draw({ code: "CA" });
const ca = tipOf(caHtml, "power");
check(/It is every utility's homes together, every hour, fixed charges included/.test(ca), "California: the electricity tip says the average is every utility's homes together");
check(/href="\/learn\/bill"[^>]*>What is on an electricity bill<\/a> draws a bill on PG&amp;E&#x27;s, SCE&#x27;s and SDG&amp;E&#x27;s own tariffs/.test(caHtml), "California: the electricity tip links the bill page's three utility tariffs");
const tx = draw({ code: "TX" });
check(/every utility's homes together/.test(tipOf(tx, "power")) && !/href="\/learn\/bill"/.test(tx), "Texas: the average said, no link to the bill page (it draws no Texas utility's tariff)");
check(/every utility's homes together/.test(tipOf(draw(null), "power")), "the United States as it opens: the average said");

// row 3 (case 3): the decisions line no longer calls E-TOU-C a rate made for EV owners, nor says it is lower
const hp = EV_DECISIONS.find((d) => d.key === "home-price");
check(!/A rate made for EV owners can be lower/.test(hp.source), "the home price decision: E-TOU-C is not called an EV rate that can be lower");
check(/not one made for EV owners/.test(hp.source) && /both above California's average of 33\.61/.test(hp.source) && /EV2-A\) is not held/.test(hp.source), "the home price decision: E-TOU-C's two rates said above the average, EV2-A said not held");
check(/both above California/.test(text(renderToStaticMarkup(h(EvDecisions)))), "the decisions fold draws the corrected words");

// row 4 (case 4, a student checking): the net present value's tip gives the yearly saving to the cent it is computed from
const D0 = Object.fromEntries(Object.entries(DEFAULTS).map(([k, d]) => [k, d.value]));
const cents = (st) => { const r = verdict({ ...D0, gasUsdPerGal: st.gas.value, powerUsdPerMwh: st.power.value, credit: 0 }); return `$${r.saveYear.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`; };
const npvTip = (html) => { const m = html.match(/data-npv="true">([\s\S]*?)<div class="mt-1/); return m ? text(m[1]) : ""; };
check(npvTip(draw(null)).includes(`(${cents(us)} a year here, to the cent: the table below rounds it to the dollar)`), `the United States: the tip gives ${cents(us)} a year`);
check(cents(us) === "$1,567.47", "the United States: the yearly saving to the cent is $1,567.47 (2,418.89 of gasoline less 851.42 of electricity)");
let allStates = 0;
for (const s of D.states) if (s.gas && s.power && npvTip(draw({ code: s.code })).includes(`(${cents(s)} a year here`)) allStates++;
check(allStates === D.states.length, `every state's net present value tip gives its saving to the cent (${allStates} of ${D.states.length})`);
check(/\$ ?5,131/.test(text(draw(null))) && /\$1,567</.test(draw(null)), "the opening figures are unchanged: $5,131, and $1,567 in the table");

// what the read commits: no license-held table is read by the game, and no em dash in the files the read wrote
for (const t of ["eia_retail_electricity_prices", "eia_regional_retail_fuel_prices"]) check((L.tables[t] === undefined && L.all[t]?.status === "public"), `${t} is public in license_status.json and not among its held tables (no held figure on the page or in the read)`);
const dash = String.fromCharCode(0x2014);
for (const f of ["../../docs/reviews/ev-game-read-2026-11-16.md", "../app/play/ev/EvGame.tsx", "../app/play/ev/Decisions.tsx", "./test-ev-game-read.mjs", "../../replication/ev_game/replicate.py"]) {
  const u = new URL(f, import.meta.url);
  check(fs.existsSync(u) && !fs.readFileSync(u, "utf-8").includes(dash), `no em dash in ${f.replace(/^[./]+/, "")}`);
}

console.log(bad ? `${bad} failed` : "the EV game's read: every check passed");
process.exitCode = bad ? 1 : 0;
