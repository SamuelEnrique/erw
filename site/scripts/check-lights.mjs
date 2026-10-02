// Energy Research Warehouse (ERW) site, session 66: Part A's result on the levels a running site serves, today's
// level included (the unit test, scripts/test-battery.mjs, covers the famous days and the toy days; today's level
// lives in the live set, which a test without the network cannot read).
//
//   node scripts/check-lights.mjs [base-url]          (default http://localhost:3000)
//
// Reads the levels from the page itself (/play/battery?more=1 hands them to the game), read only: no play is posted.
// For each level, on Hard with the default battery, and with rooftop solar where the level holds a solar shape: if the
// lights can be kept on (the optimum under a prohibitive penalty stays lit), the perfect battery under this folder's
// lib/battery.ts must not end in lights out. Prints one line per level; exits 1 on a failure or when no level is read.
import { DEFAULT_SETTINGS, LIGHTS_OUT, optimum, rulesOf, simulate, validSolar } from "../lib/battery.ts";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const html = await fetch(`${base}/play/battery?more=1`).then((r) => r.text());
// the page's data: the strings Next pushes for the client, joined
let flight = "";
for (const m of html.matchAll(/self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)/g)) flight += JSON.parse(m[1]);
const at = flight.indexOf('"levels":[');
if (at < 0) { console.log(`FAIL no levels found in ${base}/play/battery?more=1`); process.exit(1); }
let depth = 0, end = -1, inStr = false;
for (let i = at + 9; i < flight.length; i++) {
  const ch = flight[i];
  if (inStr) { if (ch === "\\") i++; else if (ch === '"') inStr = false; continue; }
  if (ch === '"') inStr = true;
  else if (ch === "[" || ch === "{") depth++;
  else if (ch === "]" || ch === "}") { depth--; if (depth === 0) { end = i; break; } }
}
const levels = JSON.parse(flight.slice(at + 9, end + 1));
let bad = 0;
const ends = (l, addons, m) => {
  const r = { ...rulesOf(DEFAULT_SETTINGS, "hard", addons), penaltyMultiple: m };
  const sun = r.solarKw > 0 ? l.solar : undefined;
  return simulate(l.price, optimum(l.price, r, sun).actions, r, sun);
};
for (const l of levels) {
  for (const addons of [[], ...(validSolar(l.solar, l.price.length) ? [["solar"]] : [])]) {
    const can = ends(l, addons, 1e9).why !== "lights_out";
    const x = ends(l, addons, LIGHTS_OUT.multiple);
    const ok = !(can && x.why === "lights_out");
    if (!ok) bad++;
    console.log(`${ok ? "ok  " : "FAIL"} ${l.date} (${l.slug}), Hard${addons.length ? " with rooftop solar" : ""}: the perfect battery earns ${x.score.toFixed(2)} USD and ends ${x.why || "with a whole day"}; ${x.outageStartKwh === null ? "no outage (the dearest hour is the day's last)" : `${x.outageStartKwh.toFixed(2)} kWh at the outage's start, need ${x.outageNeedKwh.toFixed(2)}`}${can ? "" : "; the lights cannot be kept on from the starting charge"}`);
  }
}
console.log(bad ? `${bad} FAILED` : `Part A holds on the ${levels.length} levels ${base} serves (penalty ${LIGHTS_OUT.multiple} times the cap)`);
process.exit(bad || !levels.length ? 1 : 0);
