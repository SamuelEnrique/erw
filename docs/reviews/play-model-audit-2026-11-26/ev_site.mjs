// Session 10227 (play audit): the EV game's figures by the site's own code (site/lib/ev.ts), every place of its price
// file at the defaults, beside ev_restate.py's independent figures. Writes ev_site.json and prints the largest gaps.
//   node runs/c10227/ev_site.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const E = await import(pathToFileURL(path.join(root, "site", "lib", "ev.ts")).href);
const file = JSON.parse(fs.readFileSync(path.join(root, "site", "data", "ev_prices.json"), "utf-8"));
const mine = JSON.parse(fs.readFileSync(path.join(here, "ev_restate.json"), "utf-8")).default;
const D = Object.fromEntries(Object.entries(E.DEFAULTS).map(([k, d]) => [k, d.value]));
const places = [{ code: "US", ...file.us }, ...file.states];
const out = {};
let worst = 0, n = 0, keyedBad = 0;
for (const p of places) {
  if (!p.power || !p.gas) continue;
  const v = E.verdict({ ...D, gasUsdPerGal: p.gas.value, powerUsdPerMwh: p.power.value, credit: 0 });
  const k = E.keyed(p.power.value, p.gas.value);
  out[p.code] = { verdict: v, keyed: k };
  const m = mine[p.code];
  for (const [a, b] of [["gasYear", "gas_year"], ["evYear", "ev_year"], ["saveYear", "save"], ["extra", "extra"], ["payback", "payback"], ["npv", "npv"]]) {
    const d = v[a] === null || m[b] === null ? (v[a] === m[b] ? 0 : Infinity) : Math.abs(v[a] - m[b]);
    worst = Math.max(worst, d); n++;
  }
  const kp = m.payback === null ? null : Math.round(m.payback * 10) / 10;
  if (k.payback !== kp || k.npv !== Math.round(m.npv) || k.power_cents !== Math.round(p.power.value * 10) / 100) { keyedBad++; console.log("keyed differs", p.code, k, kp, Math.round(m.npv)); }
}
fs.writeFileSync(path.join(here, "ev_site.json"), JSON.stringify(out, null, 1));
console.log(`places ${Object.keys(out).length}, figures compared ${n}, largest gap ${worst}, keyed figures differing ${keyedBad}`);
console.log("US", JSON.stringify(out.US));
