// Chain 302 (session 7203, goal 4): the All grids tab read as the energy lead of an AI lab would read it, for five cases
// (docs/reviews/allgrids-read-2026-11-16.md). The whole tab is drawn to HTML without a build (scripts/tsx-loader.mjs) and
// each site fault the read found is held here as fixed: the row numbers are the review's. It also holds the tab to "Your
// load", the page's default view, on the figures the two share. No server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-allgrids-read.mjs
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { AllGridsView } = await import("../app/cost-of-power/AllGridsView.tsx");
const L = await import("../lib/largeloadrules.ts");
const D = await import("../lib/datacenter/delivery.ts");
const M = await import("../app/cost-of-power/model.ts");
const { DELIVERY } = await import("../lib/datacenterdata.ts");
const file = JSON.parse(fs.readFileSync(new URL("../data/siting/large_load_rules.json", import.meta.url), "utf-8"));

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<span role="tooltip"[\s\S]*?<\/span>(?=<\/span>)/g, "").replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const tips = (s) => [...s.matchAll(/<span role="tooltip"[^>]*>([\s\S]*?)<\/span><\/span>/g)].map((m) => ent(m[1].replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim());
const tab = (query) => renderToStaticMarkup(h(AllGridsView, { q: Object.fromEntries(new URLSearchParams(query)) }));
const rowOf = (html, id) => { const m = [...html.matchAll(/<tr[^>]*data-allgrids-row="([^"]+)"[^>]*>([\s\S]*?)<\/tr>/g)].find((x) => x[1] === id); return m ? Object.fromEntries([...m[2].matchAll(/<td[^>]*data-cell="([^"]+)"[^>]*>([\s\S]*?)<\/td>/g)].map(([, k, v]) => [k, v])) : null; };
// a key as the HTML writes it: its "&" as an entity
const raw = (html, key) => { const m = html.match(new RegExp(`data-check="${key.replace(/&/g, "&amp;").replace(/[|.*+?^${}()[\]\\]/g, "\\$&")}" data-raw="([^"]+)"`)); return m ? Number(m[1]) : undefined; };
const two = (v) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// ---- case 1: 1 GW in ERCOT West (the West load zone and the West hub, A and B)
const gw = tab("view=allgrids&mw=1000&a=ercot:LZ_WEST&b=ercot:HB_WEST");
const west = rowOf(gw, "ercot:LZ_WEST"), hub = rowOf(gw, "ercot:HB_WEST");
ok(west && hub && Object.keys(west).length === 8, "ERCOT's West zone and West hub are rows of the tab, with the eight columns");
ok(/^da \d+\.\d\d rt \d+\.\d\d$/.test(words(west.energy)) && gw.includes('data-da="1"'), `row 3: the energy cell names both markets in place: "${words(west.energy)}"`);
ok(tips(west.allin).some((t) => t.includes("The prices are the market's as they were: what a load of 1,000 MW would itself do to them is not modelled.")), "row 2: the all-in figure's hover says the load's own effect on the price is not modelled");
ok(tips(rowOf(tab("view=allgrids&mw=300"), "ercot:LZ_WEST").allin).some((t) => t.includes("a load of 300 MW would itself do")), "row 2: the sentence takes the load's own size");
const note = (gw.match(/<p[^>]*data-ab-note="1"[^>]*>([\s\S]*?)<\/p>/) ?? ["", ""])[1];
ok(words(note).includes("Each is rounded to the cent after B less A is taken, so a difference can stand a cent from the two figures drawn."), "row 1: A and B say how B less A is rounded");
const ea = raw(gw, "allgrids|col|energy|ercot:LZ_WEST|profile=datacenter&lf=0.9&strike=row"), eb = raw(gw, "allgrids|col|energy|ercot:HB_WEST|profile=datacenter&lf=0.9&strike=row");
const diff = raw(gw, "allgrids|diff|energy|ercot:LZ_WEST|ercot:HB_WEST|profile=datacenter&lf=0.9&strike=row");
ok(ea !== undefined && eb !== undefined && Math.abs(diff - (eb - ea)) < 1e-9, `row 1: B less A is the difference of the figures as held (${two(ea)}, ${two(eb)}, ${two(diff)})`);
// row 7: the wires utilities' own transmission lines, beside the Commission's rate
const wires = D.utilitiesOf(DELIVERY.rows).map((u) => [u, D.deliveryStat(DELIVERY.rows, 1000, `${D.slugOf(u)}:transmission`)]).filter(([, v]) => v !== undefined);
const txTip = tips(west.transmission)[0] ?? "";
ok(wires.length >= 3 && wires.every(([u, v]) => txTip.includes(`USD ${two(v)} per MWh at ${u}`)) && txTip.includes("not one utility's tariff"), `row 7: the transmission hover names each wires utility's own lines (${wires.map(([u, v]) => `${u} ${two(v)}`).join(", ")})`);
ok(!tips(rowOf(gw, "nyiso:N.Y.C.").transmission).join(" ").includes("texas_delivery_charges"), "row 7: only a Texas row names Texas's wires utilities");
ok(words(west.utility).endsWith("state's large-load rule") && words(west.connect).includes("state: its rule's timed steps"), "the West zone opens the state's rule from both cells (its utility is the state's largest retailer, which files none)");

// ---- the two pages agree on what they share: "Your load" for the same site, each market
for (const [region, key] of [["LZ_WEST", "ercot:LZ_WEST"], ["HB_WEST", "ercot:HB_WEST"]]) {
  for (const buy of ["da", "rt"]) {
    const q = { grid: "ercot", region, mw: "1000", buy };
    const m = await M.loadModel(M.inputsFrom(q), true, "ercot", q);
    const here = raw(gw, `allgrids|energy|${key}|${buy}`);
    ok(m.s12 && here !== undefined && Math.abs(m.s12.flat - here) < 1e-9 && m.market === (buy === "da" ? "day-ahead" : "real time"), `"Your load" and the tab agree on ${region}'s ${buy === "da" ? "day-ahead" : "real-time"} price for a flat load: USD ${two(here)} per MWh`);
  }
}
const dflt = M.inputsFrom({ grid: "ercot", region: "LZ_WEST" });
ok(dflt.buy === "rt", "\"Your load\" opens on real time, which is why the tab's cell names its day-ahead figure (row 3)");

// ---- cases 2 and 4: 500 MW in Dominion's Virginia, 1 GW in AEP's Ohio: PJM is one row
const pj = tab("view=allgrids&mw=500&llrow=pjm:grid");
const pjm = rowOf(pj, "pjm:grid");
const inPjm = L.largeLoadStat(file, "largeload|rules|grid|pjm");
ok(pjm && words(pjm.energy) === "license needed" && words(pjm.allin) === "not held", "PJM is one row with no price: energy license needed, no all-in figure");
ok(words(pjm.utility).endsWith(`${inPjm} large-load rules in PJM`) && words(pjm.connect).endsWith(`utilities: ${inPjm} large-load rules in PJM`) && pjm.utility.includes("llrow=pjm%3Agrid#large-load-rule"), `row 10: the PJM row's two cells open the ${inPjm} rules read in PJM, not one county's utility's`);
const uTip = tips(pjm.utility).join(" ");
ok(uTip.includes("PJM is one row for the whole grid") && uTip.includes("is the county the ERW chose to read for it") && !uTip.includes("a county this row's name places it in"), "row 10: the utility's hover says the county is the ERW's choice for the grid's one row, not the row's place");
ok(tips(rowOf(pj, "ercot:LZ_AEN").utility).join(" ").includes("Travis County, TX, a county this row's name places it in"), "row 10: a row whose name is a place keeps its words");
ok(tips(pjm.carbon).every((t) => t.startsWith("The plants eGRID places in PJM")) && !/\bThe the\b/.test(ent(pj)), "row 12: no doubled word in the carbon hover");
const panel = (pj.match(/<section[^>]*data-llr-grid-panel="pjm"[\s\S]*?<\/section>/) ?? [""])[0];
const states = [...panel.matchAll(/data-llr-grid-state="([A-Z]{2})"[^>]*>[^<]*<\/a>\s*(\d+)/g)].map((m) => [m[1], Number(m[2])]);
ok(panel && raw(panel, "largeload|rules|grid|pjm") === inPjm && states.length >= 6 && states.every(([s, k]) => k === L.lines(file).filter((l) => l.grid === "pjm" && L.statesOf(l.state).includes(s)).length), `row 10: the PJM row's panel counts the grid's rules by state (${states.map(([s, k]) => `${s} ${k}`).join(", ")})`);
ok(["VA", "OH"].every((s) => panel.includes(`rgrid=pjm&amp;rstate=${s}#large-load-rules`)) && states.find(([s]) => s === "VA")[1] >= 7 && states.find(([s]) => s === "OH")[1] >= 3, "Dominion's Virginia and AEP's Ohio are each one click from the PJM row: the table filtered by PJM and the state");
ok(!panel.includes("data-rule-card"), "the grid's panel draws no one utility's rule as the grid's");

// ---- cases 3 and 5: 300 MW in Arizona (APS), 500 MW in Georgia (Georgia Power): no row; the rules are in the table
const ids = [...gw.matchAll(/data-allgrids-row="([^"]+)"/g)].map((m) => m[1]);
ok(ids.length === 48 && !ids.some((id) => /^(azps|soco|wecc|serc)/i.test(id)), "the tab has no row outside the seven grids: Arizona and Georgia are reached through the rules table alone (the review's rows 14 and 15, asked of the data machine)");
const none = L.filterLines(L.lines(file), { ...L.NO_RULE_FILTERS, grids: ["other"] });
ok(none.length === L.largeLoadStat(file, "largeload|rules|grid|other") && ["AZ", "GA"].every((s) => none.some((l) => L.statesOf(l.state).includes(s))), `${none.length} rules are of utilities in no ISO, Arizona's and Georgia's among them, under the Grid filter's "No ISO"`);
const az = L.filterLines(L.lines(file), { ...L.NO_RULE_FILTERS, states: ["AZ"] }), ga = L.filterLines(L.lines(file), { ...L.NO_RULE_FILTERS, states: ["GA"] });
ok(az.some((l) => /Arizona Public Service/.test(l.utility)) && ga.some((l) => /Georgia Power/.test(l.utility)), "APS's and Georgia Power's rules are rows of the table");

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
