// Chain 304, part B (session 7511): the severance tool read as the reader it is for, on five cases
// (docs/reviews/severance-read-2026-11-16.md). The calculator and the lease tool are drawn to HTML without a build
// (scripts/tsx-loader.mjs) and each site fault the read found is held here as fixed: the row numbers are the review's.
// The calculator keeps its inputs in React state and reads none from the address, so a case is set by giving its state
// hooks their first values in the order the component declares them (state, product, volume, price, variant, district,
// royaltyPct, trucking, transport, option, param, tier, period, credit): what a reader's choices would leave drawn.
// Prices are given, not read: no server, no network, no click.
//   node --import ./scripts/tsx-register.mjs scripts/test-severance-read.mjs
import fs from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const React = require("react");
const realUseState = React.useState;
let first = null, at = 0;
React.useState = (init) => { const i = at++; return realUseState(first && i in first ? first[i] : init); };
const { renderToStaticMarkup } = await import("react-dom/server");
const h = React.createElement;

let n = 0, failed = 0;
const ok = (c, what) => { n++; if (c) console.log(`ok   ${what}`); else { failed++; console.log(`FAIL ${what}`); } };
const ent = (s) => s.replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const words = (s) => ent(s.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
const tipOf = (html, id) => { const m = html.match(new RegExp(`<span role="tooltip" id="tip-${id}"[^>]*>([\\s\\S]*?)</span></span>`)); return m ? words(m[1]) : null; };

const rules = JSON.parse(fs.readFileSync(new URL("../data/severance_rules.json", import.meta.url), "utf-8"));
const { Calculator } = await import("../app/severance/Calculator.tsx");
const { LeaseTool } = await import("../app/severance/lease/LeaseTool.tsx");
const { compute } = await import("../lib/severance.ts");
const L = await import("../lib/lease.ts");

// the default prices as the page gave them on 16 November 2026 (October 2026's means of eia_fuel_spot_prices)
const prices = { oil: 102.07, gas: 2.99, label: { oil: "WTI Cushing, the mean of 22 daily EIA spot prices in 2026-10, $102.07 per barrel", gas: "Henry Hub, the mean of 22 daily EIA spot prices in 2026-10, $2.99 per MMBtu, applied per Mcf as if one Mcf held one MMBtu" } };
const ORDER = ["state", "product", "volume", "price", "variant", "district", "royaltyPct", "trucking", "transport", "option", "param", "tier", "period", "credit"];
const calc = (o) => {
  first = {}; at = 0;
  for (const [k, v] of Object.entries(o)) { if (!ORDER.includes(k)) throw new Error(`no input ${k}`); first[ORDER.indexOf(k)] = v; }
  const html = renderToStaticMarkup(h(Calculator, { rules, prices }));
  first = null;
  return html;
};
const point = (value, n, month, name, unit) => ({ value, n, label: `${name}, the mean of ${n} daily EIA spot prices in ${month}, $${value.toFixed(2)} ${unit}` });
const book = {
  oil: { "2026-08": point(83.9, 21, "2026-08", "WTI Cushing", "per barrel"), "2026-09": point(97.1, 22, "2026-09", "WTI Cushing", "per barrel"), "2026-10": point(102.07, 22, "2026-10", "WTI Cushing", "per barrel") },
  gas: Object.fromEntries([["2026-05", 2.94, 20], ["2026-06", 3.14, 21], ["2026-07", 2.91, 23], ["2026-08", 2.79, 21], ["2026-09", 2.95, 22], ["2026-10", 2.99, 22]].map(([m, v, d]) => [m, point(v, d, m, "Henry Hub", "per MMBtu")])),
};
const lease = (text) => { first = null; at = 0; return renderToStaticMarkup(h(LeaseTool, { rules, prices: book, initial: { text, source: "a case" } })); };
const row = (o) => L.COLUMNS.map((c) => o[c] ?? "").join(",");
const file = (rows) => [L.COLUMNS.join(","), ...rows.map(row)].join("\n");
const days = (m) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 0)).getUTCDate();

// ---- the page as it opens is unchanged
const open = calc({});
ok(words(open).includes("$102,070.00") && words(open).includes("$4,695.22") && words(open).includes("$6.25"), "the calculator still opens on Texas oil, 1,000 bbl: gross $102,070.00, tax $4,695.22, the fee $6.25");

// ---- case 1: a Panhandle gas well at 60 Mcf a day, the low-producing gas well credit
const gas = calc({ state: "TX", product: "gas", volume: 1860, price: 2.99, option: "tx_lp_gas" });
const periods = [...gas.matchAll(/<option[^>]*>Report period (\d{4}-\d{2}): certified \$([^ ]+) \(/g)].map((m) => [m[1], m[2]]);
const cert = rules.states.TX.products.gas.options.find((o) => o.id === "tx_lp_gas").certified;
ok(periods.length === cert.prices.length && periods.every(([, p]) => /^\d+\.\d\d$/.test(p)), `row 1: each of the ${periods.length} report periods draws its certified price to the cent`);
const short = cert.prices.find((p) => String(p.price).split(".")[1]?.length === 1);
ok(short && periods.some(([m, p]) => m === short.period && p === short.price.toFixed(2)), `row 1: ${short?.period} reads $${short?.price.toFixed(2)}, not $${short?.price}`);
const r10 = compute(rules, { state: "TX", product: "gas", volume: 1860, price: 2.99, option: { id: "tx_lp_gas", period: short.period } });
ok(r10.applied[0].effect.includes(`certified price $${short.price.toFixed(2)} for ${short.period}`) && r10.withTotal === 0, "row 1: the line a credit draws states the certified price to the cent; the credit itself is unchanged");
const tip3 = tipOf(gas, "sev-period-tx_lp_gas");
ok(tip3 && tip3.includes(`The latest month this page holds is ${cert.as_of}.`) && tip3.includes("The price box is not changed by this list.") && tip3.includes("in 2026-10"), "row 3: the report period's tip names the latest month held and the month the price box opened on");
ok(/<select[^>]*aria-label="Report period, Low-producing gas well credit"/.test(gas) && words(gas).includes("Report period (the production month)"), "row 3: the list is named, and says the period is the production month");
ok(words(gas).includes("$417.11") && words(gas).includes("a 100 percent credit (certified price $1.36 for 2026-08, 2005 dollars)"), "case 1: 1,860 Mcf at $2.99: tax $417.11, a 100 percent credit for 2026-08");

const months = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"];
const panhandle = lease(file(months.map((m) => ({ state: "TX", well_id: "GAS-60", month: m, gas_mcf: 60 * days(m), well_type: "gas" }))));
const pw = words(panhandle);
ok(pw.includes("no certified price for 2026-09 is held in the rules file (its latest is 2026-08): no credit computed") && pw.includes("no certified price for 2026-10 is held in the rules file (its latest is 2026-08)"), "row 2: a gas month past the rules file says what the file holds and its latest month");
ok(!pw.includes("is published"), "row 2: no flag says a certified price is or is not published");
ok((pw.match(/the file does not hold gas in each of the three months before, so this month is the one tested/g) ?? []).length === 3 && !pw.includes("the well did not produce"), "row 4: the file's first three months say the file is short, not that the well did not produce");
ok(pw.includes("$389.21") && pw.includes("$1,629.18"), "case 1: August 2026 at its own mean, $2.79: base tax $389.21; four certified months save $1,629.18");

// ---- case 2: a three-well oil lease at 8 bbl a well a day
const oil = lease(file(["2026-08", "2026-09", "2026-10"].flatMap((m) => [1, 2, 3].map((k) => ({ state: "TX", well_id: `OIL-${k}`, month: m, oil_bbl: 8 * days(m), well_type: "oil" })))));
const ow = words(oil);
ok(ow.includes("certified price for 2026-08: $53.55 (2005 dollars), a 0 percent credit") && (ow.match(/no certified price for 2026-10 is held in the rules file \(its latest is 2026-08\)/g) ?? []).length === 3, "row 2: the oil lease's flags say the same of a month past the file");
ok(ow.includes("$9,580.59") && ow.includes("the lease averages 8 bbl per well per day over 2026-08, 2026-09, 2026-10 (3 wells), under 15"), "case 2: three months' base tax $9,580.59; the lease is under 15 barrels a well a day");
ok(/data-fees-held="1"/.test(oil) && ow.includes("$13.80") && !oil.includes("lease-fees-not-held"), "row 8: a Texas file keeps its fees figure, $13.80, and no tip");

// ---- case 3: Lea County, Jal, 3,000 bbl, a one-eighth federal royalty
const D = "LEA JAL, district 19, suffix 2541";
const table = rules.sources.nm_trd_rates_2026;
const line = (html, id) => (html.match(new RegExp(`<tr[^>]*data-base-line="${id}"[^>]*>([\\s\\S]*?)</tr>`)) ?? ["", ""]);
const jal = calc({ state: "NM", product: "oil", volume: 3000, price: 102.07, district: D, royaltyPct: 12.5 });
const [, adv] = line(jal, "nm_adval");
ok(words(adv).includes("Oil and Gas Ad Valorem Production Tax, 1.4863% $3,982.30") && adv.includes(`href="${table.url.replace(/&/g, "&amp;")}"`), "row 5: the district's ad valorem line cites TRD's rate table, the document its rate is from");
ok(words(jal).includes("$267,933.75") && words(jal).includes("$23,112.77"), "case 3: taxable value $267,933.75 after the royalty; four taxes $23,112.77");
const none = calc({ state: "NM", product: "oil", volume: 3000, price: 102.07, royaltyPct: 12.5 });
const [tr, cells] = line(none, "nm_adval");
ok(tr.includes('data-left-out="1"') && words(cells).includes("no district chosen: left out of the total (0.7105% to 1.7249% by district) left out") && !cells.includes("$0.00") && !words(cells).includes(", 0%"), "row 6: with no district the ad valorem line says left out, with the districts' range, not 0% and $0.00");
ok(words(none).includes("Tax at the base rate $19,130.47"), "row 6: the total is the other three taxes, $19,130.47, as before");
ok(!line(jal, "nm_adval")[0].includes("data-left-out"), "row 6: a district chosen draws its rate and its tax");
const nmLease = lease(file([{ state: "NM", well_id: "JAL", month: "2026-10", oil_bbl: 3000, nm_district: "2541", royalty_pct: 12.5 }]));
ok(words(nmLease).includes("$23,112.77") && /data-fees-held="0"/.test(nmLease) && words((nmLease.match(/<div[^>]*data-lease-card="3"[^>]*>([\s\S]*?)<\/div><\/div>/) ?? ["", ""])[1]).includes("not held"), "row 8: a New Mexico file's fees card reads not held; the Lease tab's tax is the calculator's, $23,112.77");

// ---- case 4: Louisiana, October 2026
const la = lease(file([
  { state: "LA", well_id: "STRIPPER", month: "2026-10", oil_bbl: 155, completion_date: "1985-06-01", days_produced: 31, well_type: "oil" },
  { state: "LA", well_id: "HORIZONTAL", month: "2026-10", gas_mcf: 300000, completion_date: "2026-03-15", depth_ft: 12000, horizontal: "yes", well_type: "gas" },
]));
const lw = words(la);
const tip8 = tipOf(la, "lease-fees-not-held");
ok(/data-fees-held="0"/.test(la) && tip8 && tip8.includes("The rules file holds regulatory fees for Texas only") && tip8.includes("La. R.S. 30:87"), "row 8: a Louisiana file's fees card reads not held, and its tip says which fees the rules file holds");
ok(!/Regulatory fees \(not in the tax\) \$0\.00/.test(lw), "row 8: no fee of $0.00 is drawn for a state whose fees are not held");
ok(lw.includes("$47,397.61") && lw.includes("$46,903.20") && lw.includes("month 8 of 18 from completion"), "case 4: base tax $47,397.61, potential savings $46,903.20, the horizontal well in month 8 of 18");
const strip = calc({ state: "LA", product: "oil", volume: 155, price: 102.07, option: "la_stripper" });
ok(words(strip).includes("$1,977.61") && words(strip).includes("$494.40") && words(strip).includes("$1,483.20"), "case 4: the stripper well on the calculator: $1,977.61 at 12.5 percent, $494.40 at 3.125 percent, the Lease tab's saving");

// ---- case 5: Reeves County, 600 bbl a day in October 2026, and a one-eighth royalty's share
const well = calc({ volume: 18600, price: 102.07 }), eighth = calc({ volume: 2325, price: 102.07 });
const tip9 = tipOf(well, "sev-volume-share");
ok(tip9 && tip9.includes("in proportion to the volume") && tip9.includes("divided by 8") && tip9.includes("is not a rule this page has read"), "row 9: the volume's tip says a share of the volume gives the tax on that share, and that who bears it is not read");
ok(/<label for="sev-volume">Monthly volume, bbl<\/label>/.test(well) && /<input[^>]*id="sev-volume"/.test(well) && !/<label[^>]*>(?:(?!<\/label>)[\s\S])*<button/.test(well), "row 9: the volume box keeps its one label, and no tip sits inside a label");
ok(words(well).includes("$87,331.09") && words(eighth).includes("$10,916.39"), "case 5: the well's month $87,331.09; a one-eighth share $10,916.39");
const same = (x) => { const a = compute(rules, x), b = compute(rules, { ...x, volume: x.volume / 8 }); return Math.abs(a.withTotal / 8 - b.withTotal) < 1e-9 && a.fees.every((f, i) => Math.abs(f.amount / 8 - b.fees[i].amount) < 1e-9); };
ok([{ state: "TX", product: "oil", volume: 18600, price: 102.07 }, { state: "TX", product: "gas", volume: 46500, price: 2.99, option: { id: "tx_lp_gas", period: "2026-08" } },
  { state: "LA", product: "oil", volume: 155, price: 102.07, option: { id: "la_stripper" }, transport: 1.5 }, { state: "LA", product: "gas", volume: 300000, price: 2.99 },
  { state: "NM", product: "oil", volume: 3000, price: 102.07, adval: 1.4863, royaltyPct: 12.5, trucking: 0.4 }, { state: "TX", product: "oil", volume: 744, price: 0.5 }].every(same),
  "row 9: in six cases of the three states an eighth of the volume owes an eighth of the tax and of the fees");

// ---- the whole of what was drawn
const all = [open, gas, panhandle, oil, jal, none, nmLease, la, strip, well, eighth].join("");
ok(![0x2014, 0x2013].some((c) => all.includes(String.fromCharCode(c))), "no em dash and no en dash in what the eleven drawings hold");
const ids = [...all.matchAll(/aria-describedby="([^"]+)"/g)].map((m) => m[1]);
ok(ids.length > 0 && ids.every((id) => all.includes(`id="${id}"`)), `the ${ids.length} tips drawn each have their target`);

console.log(`${n - failed} of ${n} passed`);
if (failed) process.exitCode = 1;
