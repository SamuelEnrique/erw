// Chain 304, part B (session 7515): the one figure the read of /impact as its reader corrected, held on the page's own
// view drawn to HTML (docs/reviews/impact-read-2026-11-16.md, row 1). Nevada's abatement (NRS 701A.370) takes 55 percent
// off the tax, not off the value: the table by year's "Taxable value" must stay the whole value in an abated year, and
// the tax must stay what it was. A state whose statute exempts value (Florida, 80 percent of a device's assessed value)
// must keep its taxable value at the taxed share. No server, no network, no click.
//
//   cd site; node --import ./scripts/tsx-register.mjs scripts/test-impact-read.mjs <nlr_jedi_multipliers.csv>
import fs from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const U = await import("../lib/forecastui.ts");
const { Forecast } = await import("../app/impact/Forecast.tsx");

const jediFile = process.argv[2];
let bad = 0, n = 0;
const ok = (cond, words) => { n++; if (!cond) bad++; console.log(`${cond ? "ok  " : "FAIL"} ${words}`); };

if (!jediFile || !fs.existsSync(jediFile)) {
  console.error("give the path of nlr_jedi_multipliers.csv");
  process.exitCode = 2;
} else {
  const lines = fs.readFileSync(jediFile, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  const rows = lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
  const P = D.params();
  const jedi = F.pack(rows);
  const rules = D.gasSeverance();
  /** the keyed numbers of the drawn page for an address: figure name -> { raw, text }, for the scenario in view */
  const draw = (qs, view) => {
    const q = Object.fromEntries(new URLSearchParams(qs));
    const start = U.withProjects(U.parse({ ...q, ...(view === "b" ? { view: "b" } : {}) }), q, []);
    const html = renderToStaticMarkup(h(Forecast, { P, jedi, start, rules, planned: [] }));
    const key = F.inputsKey(U.resolve(P, start[view]));
    const out = {};
    for (const m of html.matchAll(/<span data-check="([^"]+)" data-raw="([^"]+)"[^>]*>([\s\S]*?)<\/span>/g)) {
      const check = m[1].replace(/&amp;/g, "&");
      const cut = check.lastIndexOf("|");
      if (check.slice(0, cut) === key) out[check.slice(cut + 1)] = { raw: Number(m[2]), text: m[3].replace(/<[^>]+>/g, "") };
    }
    return out;
  };

  // Lone Mountain Geothermal (Nevada, 36 MW, USD 178,446,043): A with the abatement approved, B without, the reader's
  // rate the Department of Taxation's own (docs/methods/forecast.md, section 12.3)
  const nv = "tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&bmw=36&bcost=4956.83&bstart=2026&bown=1.0917&bownyears=60";
  const a = draw(nv, "a"), b = draw(nv, "b");
  const cost = 4956.83 * 36 * 1000;
  ok(Math.abs(a["year:2028:value"].raw - cost) < 1, `Nevada, abated, 2028: the taxable value is the whole cost (${a["year:2028:value"].text}; the Department's note: USD 178,450,621)`);
  ok(a["year:2028:value"].text === "USD 178.4 million", "and the cell reads USD 178.4 million");
  ok(Math.abs(a["year:2028:property"].raw - cost * 0.45 * 0.010917) < 1 && a["year:2028:property"].text === "USD 876,642", `the tax of 2028 is unchanged, 45 percent of the rate on the whole value (${a["year:2028:property"].text})`);
  ok(Math.abs(b["year:2028:property"].raw - cost * 0.010917) < 1, `without the abatement the tax of 2028 is the whole rate's (${b["year:2028:property"].text})`);
  let same = 0, years = 0;
  for (let y = 2028; y <= 2067; y++) { years++; if (Math.abs(a[`year:${y}:value`].raw - b[`year:${y}:value`].raw) < 1e-6) same++; }
  ok(same === years && years === 40, `the abated and the unabated scenario show one taxable value in every operating year (${same} of ${years})`);
  ok(Math.abs(a["year:2045:property"].raw / b["year:2045:property"].raw - 0.45) < 1e-9 && Math.abs(a["year:2046:property"].raw / b["year:2046:property"].raw - 1) < 1e-9, "the tax is 45 percent of the unabated through 2045 and equal from 2046 (20 years from the first construction year, as before)");
  ok(a["year:2046:value"].raw < a["year:2045:value"].raw, `the taxable value falls from 2045 to 2046 (${a["year:2045:value"].text} to ${a["year:2046:value"].text}); it rose there before`);
  ok(Math.abs(a["sum:property"].raw - 36044603.1654399) < 1 && Math.abs(a["pv:taxes"].raw - 10706988.897748992) < 1, `the life's property tax and the taxes' present value are what they were (${a["sum:property"].text}, ${a["pv:taxes"].text})`);

  // a statute that exempts value keeps the taxed share as the taxable value: Florida solar, 80 percent exempt through 2037
  const fl = draw("tech=utility_pv&state=fl&mw=100&cost=1500&start=2027&own=1&ownyears=30", "a");
  ok(Math.abs(fl["year:2028:value"].raw - 150e6 * 0.2) < 1 && Math.abs(fl["year:2028:property"].raw - 150e6 * 0.2 * 0.01) < 1, `Florida solar, 2028: the taxable value is the 20 percent the statute leaves (${fl["year:2028:value"].text})`);
  // the rule file says which: Nevada's is the only abatement of the tax
  const marked = Object.entries(P.property.states).flatMap(([s, v]) => v.rules.filter((r) => r.abates === "tax").map((r) => `${s}:${r.id}`));
  ok(marked.length === 1 && marked[0] === "nv:nv_renewable_abatement", `one rule abates the tax and not the value: ${marked.join(", ")}`);
  console.log(`${n - bad} of ${n} passed`);
  if (bad) process.exitCode = 1;
}
