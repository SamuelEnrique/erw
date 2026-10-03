// Energy Research Warehouse (ERW) site: every number of /cost-of-power/battery, on all twelve combinations of grid,
// duration and strategy, against this script's own read of Supabase (session 67).
//
//   node scripts/check-battery-production.mjs [base-url]
//
// For ERCOT and CAISO at 2, 4 and 8 hours under both strategies it loads the page as a visitor, reads every bs| check
// key and its raw value, recomputes the value with lib/batterystack.ts from battery_stack_monthly and
// battery_stack_stress_daily read here with the anon key, and compares. Exits 1 on any mismatch or an empty page.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
const B = await import("../lib/batterystack.ts");

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
  const m = fs.existsSync(f) ? fs.readFileSync(f, "utf-8").match(new RegExp(`^${name}=(.*)$`, "m")) : null;
  if (!m) throw new Error(`${name} is not set`);
  return m[1].trim().replace(/^"|"$/g, "");
}
const origin = new URL(env("SUPABASE_URL")).origin, key = env("SUPABASE_ANON_KEY");
async function all(params) {
  const out = [];
  for (let off = 0; ; off += 1000) {
    const r = await fetch(`${origin}/rest/v1/series?${new URLSearchParams({ ...params, limit: "1000", offset: String(off) })}`, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
    if (!r.ok) throw new Error(`Supabase: HTTP ${r.status}`);
    const b = await r.json();
    out.push(...b.map((x) => ({ ...x, value: Number(x.value) })));
    if (b.length < 1000) return out;
  }
}
const decode = (s) => s.replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"');

let bad = 0, total = 0;
for (const grid of ["ercot", "caiso"]) for (const dur of [2, 4, 8]) for (const strat of ["foresight", "dayahead"]) {
  const q = `grid=${grid}&dur=${dur}&strat=${strat}`;
  const res = await fetch(`${base}/cost-of-power/battery?${q}`);
  const html = await res.text();
  const x = B.inputsOf({ grid, dur: String(dur), strat });
  const f = { entity: `eq.${B.gridOf(grid).entity}`, variable: `like.${strat}_${dur}h_*`, order: "variable,ts_utc" };
  const rows = await all({ select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, ...f });
  const stress = await all({ select: "variable,ts_utc,value,event", table_name: `eq.${B.STRESS_TABLE}`, ...f });
  const found = new Map();
  for (const m of html.matchAll(/<span data-check="(bs\|[^"]+)" data-raw="([^"]*)"/g)) found.set(decode(m[1]), Number(m[2]));
  let n = 0, wrong = 0;
  for (const [check, raw] of found) {
    const p = check.split("|");
    const t = B.stat(rows, stress, B.parseKey(p[1]), p[2]);
    n++;
    if (t === null || Math.abs(t - raw) > 1e-9 * Math.max(1, Math.abs(t))) { wrong++; if (wrong <= 3) console.log(`  FAIL ${check}: page ${raw}, Supabase ${t}`); }
  }
  const summary = (html.match(/data-summary="1">([\s\S]*?)<\/p>/)?.[1] ?? "").replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
  // session 71: the summary sentence leads with the last twelve months
  const ok = res.status === 200 && n > 50 && wrong === 0 && summary.startsWith(`Over the last twelve months a 100 MW, ${dur}-hour battery in ${B.gridOf(grid).name}`) && B.inputsKey(x).includes(`dur=${dur}`);
  bad += ok ? 0 : 1;
  total += n;
  console.log(`${ok ? "ok  " : "FAIL"} ${q}: ${res.status}, ${n} values, ${wrong} wrong, ${rows.length} rows read. ${decode(summary)}`);
}
console.log(`battery page against Supabase at ${base}: ${12 - bad} of 12 combinations pass, ${total} values`);
process.exit(bad ? 1 : 0);
