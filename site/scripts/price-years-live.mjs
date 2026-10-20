// Energy Research Warehouse (ERW) site, session 357: the battery page's last twelve months from the live set, by the
// page's own read (app/cost-of-power/battery/read.ts: the same table, entity and variable filter) and its own check-key
// stat (lib/batterystack.ts stat "l12_kw:total"), for warehouse/derived/price_years.py --live to compare with the table.
//
//   node --import ./scripts/alias-register.mjs scripts/price-years-live.mjs
//
// Reads SUPABASE_URL and SUPABASE_ANON_KEY from the environment, site/.env.local or the repository's .env (never
// printed). Prints one JSON line: {"<grid>|<strategy>_<N>h": <USD per kW>, ...}.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const B = await import("../lib/batterystack.ts");

function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    const m = fs.readFileSync(f, "utf-8").match(new RegExp(`^${name}=(.*)$`, "m"));
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  throw new Error(`${name} is not set`);
}
const url = new URL(env("SUPABASE_URL")).origin, key = env("SUPABASE_ANON_KEY");  // lib/supabase.ts's config()

/** Every row of a PostgREST read, a thousand at a time. */
async function read(params) {
  const out = [];
  for (let from = 0; ; from += 1000) {
    const q = new URLSearchParams(params);
    const r = await fetch(`${url}/rest/v1/series?${q}`, { headers: { apikey: key, Authorization: `Bearer ${key}`, Range: `${from}-${from + 999}`, "Range-Unit": "items" } });
    if (!r.ok && r.status !== 206) throw new Error(`the live set answered ${r.status} for ${params.table_name}`);
    const rows = await r.json();
    out.push(...rows);
    if (rows.length < 1000) return out;
  }
}

const out = {};
for (const g of B.READY) {
  for (const strat of ["foresight", "dayahead"]) for (const dur of B.DURATIONS) {
    const like = `like.${strat}_${dur}h_*`;
    const rows = await read({ select: "variable,ts_utc,value", table_name: `eq.${B.TABLE}`, entity: `eq.${g.entity}`, variable: like, order: "variable,ts_utc" });
    const stress = await read({ select: "variable,ts_utc,value,event", table_name: `eq.${B.STRESS_TABLE}`, entity: `eq.${g.entity}`, variable: like, order: "variable,ts_utc" });
    out[`${g.id}|${strat}_${dur}h`] = B.stat(rows, stress, { grid: g.id, dur, strat, mw: 100, fom: 0, ds: 0 }, "l12_kw:total");
  }
}
console.log(JSON.stringify(out));
