// Chain 740 (lab-desktop window 3), session 10802: the four plant types' figures pinned before the datacenter was added
// to /impact. For each technology and eight states of the fixture rows, the defaults are run and a fixed set of figures
// is compared with tests/fixtures/forecast/plant_pins.json, written by this file (PIN_WRITE=1) from the code as it stood
// before the first edit of chain 740 (origin/main 00ffa09a6). The datacenter adds a project type; it moves none of these.
// Run: node --test site/scripts/test-impact-pins.test.mjs (tests/test_session10802_impact_pins.py runs it).
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const F = await import("../lib/forecast.ts");
const data = (n) => JSON.parse(fs.readFileSync(path.join(here, "..", "data", "forecast", n), "utf8"));
const P = {
  jediCosts: data("jedi_costs.json"), eiaCapex: data("eia_capex.json"), deflator: data("deflator.json"), capacity: data("capacity_factors.json"),
  sales: data("sales_tax.json"), income: data("income_tax.json"), property: data("property_rules.json"), taxable: data("jedi_taxable.json"), gas: data("gas.json"),
  exemptions: data("sales_exemptions.json"),
};
const ROWS = JSON.parse(fs.readFileSync(path.join(here, "..", "..", "tests", "fixtures", "forecast", "jedi_rows.json"), "utf8")).rows;
const PINS = path.join(here, "..", "..", "tests", "fixtures", "forecast", "plant_pins.json");
const TECHS = ["land_based_wind", "utility_pv", "natural_gas", "geothermal"];
const STATES = ["tx", "ia", "mn", "va", "la", "wv", "ca", "nv"];
const FIGURES = ["c:jobs:total", "c:earnings:total", "o:jobs:total", "o:earnings:total", "sum:jobs", "sum:earnings", "sum:property",
  "sum:sales", "sum:income", "pv:earnings", "pv:property", "pv:sales", "pv:income", "pv:taxes", "y1:property", "y1:income"];

function figures() {
  const out = {};
  for (const tech of TECHS) for (const st of STATES) {
    const x = F.defaults(P, tech, st);
    const r = F.run(x, ROWS, P, null);
    out[`${tech}:${st}`] = { ok: r.ok, key: F.inputsKey(x), figures: Object.fromEntries(FIGURES.map((f) => [f, F.stat(r, f)])) };
  }
  return out;
}

test("the four plant types' figures are those pinned before chain 740's first edit", () => {
  const now = figures();
  if (process.env.PIN_WRITE === "1") {
    fs.writeFileSync(PINS, JSON.stringify({ about: "The four plant types' figures under the code of origin/main 00ffa09a6, before chain 740 added the datacenter to /impact (site/scripts/test-impact-pins.test.mjs).", pins: now }, null, 1) + "\n");
    return;
  }
  const pinned = JSON.parse(fs.readFileSync(PINS, "utf8")).pins;
  assert.deepEqual(Object.keys(now).sort(), Object.keys(pinned).sort());
  for (const [k, v] of Object.entries(pinned)) {
    assert.equal(now[k].ok, v.ok, k);
    assert.equal(now[k].key, v.key, `${k}: the defaults moved`);
    for (const [f, val] of Object.entries(v.figures)) {
      const got = now[k].figures[f];
      if (val === null) assert.equal(got, null, `${k} ${f}`);
      else assert.ok(Math.abs(got - val) <= 1e-9 * Math.max(1, Math.abs(val)), `${k} ${f}: ${got} is not ${val}`);
    }
  }
});
