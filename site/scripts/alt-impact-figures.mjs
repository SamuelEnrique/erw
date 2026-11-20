// Energy Research Warehouse (ERW) site, ruling alternatives of /impact (session 7706, 17 November 2026; wip/alt-impact-*
// branches, not a default on main). The page's own model (lib/forecast.ts run, on lib/forecastdata.ts params and
// lib/severance.ts for a gas plant's fuel) run on the cases a Python test hands it, so that the figures under the other
// choice are pinned with the site's code. JEDI's rows are read from nlr_jedi_multipliers.csv (warehouse/output, or the
// page's download), as scripts/impact-figures.mjs reads them.
//   node --import ./scripts/tsx-register.mjs scripts/alt-impact-figures.mjs <nlr_jedi_multipliers.csv> <cases.json>
// cases.json: [{ "id": "...", "tech": "land_based_wind", "state": "ia", "given": { "mw": 252, "levy": 30 } }, ...]
// Prints, by case id: the inputs used, ok, the sums and present values of every stream, the first operating year's
// property and severance, the property rule's note, and each operating year's property tax and taxable value.
import fs from "node:fs";

const F = await import("../lib/forecast.ts");
const D = await import("../lib/forecastdata.ts");
const S = await import("../lib/severance.ts");

function readRows(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l && !l.startsWith("#"));
  const head = lines[0].split(",");
  const at = (k) => head.indexOf(k);
  return lines.slice(1).map((l) => l.split(",")).filter((c) => ["jobs", "earnings", "output"].includes(c[at("variable")]))
    .map((c) => ({ entity: c[at("entity")], variable: c[at("variable")], ts_utc: c[at("ts_utc")], value: Number(c[at("value")]) }));
}

const rows = readRows(process.argv[2]);
const cases = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const P = D.params();
const rules = D.gasSeverance();
const sev = (state, volume, price) => {
  const st = state.toUpperCase();
  if (rules.states[st]?.held) return NaN;   // wip/alt-impact-14: a held rate
  if (!rules.states[st]?.products?.gas) return null;
  const r = S.compute(rules, { state: st, product: "gas", volume, price });
  return r.baseTotal + r.fees.reduce((a, f) => a + f.amount, 0);
};
const out = {};
for (const c of cases) {
  const x = { ...F.defaults(P, c.tech, c.state), ...(c.given ?? {}) };
  const r = F.run(x, F.unpack(F.pack(rows), c.tech, c.state), P, sev);
  const ops = r.years.filter((y) => y.phase === "operations");
  out[c.id] = { x, ok: r.ok, why: r.why ?? null, sums: r.sums, pv: r.pv, y1: ops[0] ? { property: ops[0].property, severance: ops[0].severance, value: ops[0].value } : null,
    property: r.property, sales: r.sales, severance: r.severance, construction: r.construction, operations: r.operations,
    years: ops.map((y) => ({ year: y.year, property: y.property, value: y.value })) };
}
process.stdout.write(JSON.stringify(out));
