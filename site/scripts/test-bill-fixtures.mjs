// Energy Research Warehouse (ERW) site, session 52: real bills against the explainer.
//
//   node scripts/test-bill-fixtures.mjs [fixtures-dir]      (default ../tests/fixtures/bills; tests/test_session52.py runs it)
//
// Runs every de-identified bill fixture (site/scripts/bill-intake.mjs writes them from private/bills/) through
// lib/bill.ts at the fixture's kWh (and, for Texas, its plan's energy charge; California at the bill's defaults, since a
// bill does not print its time-of-use split) and reports, line by line, the real amount, ours and the difference, then
// the lines only one side has and the totals. A report, not a pass or fail: exits 1 only if a fixture cannot be read.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { billCA, billTDSP, billTOU, billTX, defaultsCA, defaultsTDSP, defaultsTOU, defaultsTX } from "../lib/bill.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const rules = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "bill_rules.json"), "utf-8"));
const dir = process.argv[2] ?? path.join(here, "..", "..", "tests", "fixtures", "bills");
const norm = (s) => s.toLowerCase().replace(/\([^)]*\)/g, " ").replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();
const usd = (v) => `${v < 0 ? "-" : ""}$${Math.abs(v).toFixed(2)}`;

export function ours(f) {
  const kwh = f.kwh;
  if (f.utility === "CA") return billCA(rules, { ...defaultsCA(rules), kwh });
  if (f.utility === "SCE" || f.utility === "SDGE") return billTOU(rules, f.utility, { ...defaultsTOU(rules, f.utility), kwh, ...(f.season ? { season: f.season } : {}) });
  if (f.utility === "TX") return billTX(rules, { ...defaultsTX(rules), kwh, ...(f.energy_rate ? { energyRate: f.energy_rate } : {}) });
  return billTDSP(rules, f.utility, { ...defaultsTDSP(rules, f.utility), kwh, ...(f.energy_rate ? { energyRate: f.energy_rate } : {}) });
}

/** Each real line matched to one of ours by name (equal, or one containing the other, after dropping parentheses,
 * punctuation and case); the energy charge by the word "energy". */
export function compare(f) {
  const b = ours(f);
  const left = [...b.lines];
  const rows = [];
  for (const r of f.lines) {
    const n = norm(r.name);
    let i = left.findIndex((l) => norm(l.name) === n);
    if (i < 0) i = left.findIndex((l) => norm(l.name).includes(n) || n.includes(norm(l.name)));
    if (i < 0 && /energy charge/.test(n)) i = left.findIndex((l) => /energy charge/.test(norm(l.name)));
    if (i < 0) { rows.push({ name: r.name, real: r.amount, ours: null }); continue; }
    rows.push({ name: r.name, real: r.amount, ours: left[i].amount, as: left[i].name });
    left.splice(i, 1);
  }
  for (const l of left) rows.push({ name: l.name, real: null, ours: l.amount });
  const real = f.lines.reduce((a, l) => a + l.amount, 0);
  return { rows, real, ours: b.total };
}

let bad = 0;
const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((x) => x.endsWith(".json")).sort() : [];
console.log(`${files.length} bill fixture(s) in ${path.relative(process.cwd(), dir) || dir}`);
for (const file of files) {
  let f;
  try { f = JSON.parse(fs.readFileSync(path.join(dir, file), "utf-8")); } catch (e) { bad++; console.log(`FAIL ${file}: ${e.message}`); continue; }
  const c = compare(f);
  console.log(`\n${file}${f.fictional ? " (FICTIONAL example)" : ""}: ${f.utility}, ${f.kwh} kWh, ${f.period?.start} to ${f.period?.end}, ${f.plan_type}`);
  for (const r of c.rows) {
    const d = r.real !== null && r.ours !== null ? r.ours - r.real : null;
    console.log(`  ${r.name.padEnd(48)} real ${r.real === null ? "  (none)" : usd(r.real).padStart(9)}  ours ${r.ours === null ? "  (none)" : usd(r.ours).padStart(9)}  ${d === null ? (r.real === null ? "only ours" : "only on the bill") : `difference ${usd(d)}`}${r.as && r.as !== r.name ? `  [as "${r.as}"]` : ""}`);
  }
  console.log(`  total: real ${usd(c.real)}, ours ${usd(c.ours)}, difference ${usd(c.ours - c.real)} (${((c.ours / c.real - 1) * 100).toFixed(2)} percent)`);
}
process.exit(bad ? 1 : 0);
