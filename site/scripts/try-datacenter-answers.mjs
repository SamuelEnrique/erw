// Session 228: the three answers of /cost-of-power for one address, computed outside the page from the live set and
// the page's own files (lib/datacenter/answers.ts), printed as JSON. node scripts/try-datacenter-answers.mjs [query]
// The reader is the one check-values uses: PostgREST with the anon key (SUPABASE_URL and SUPABASE_ANON_KEY from the
// environment, site/.env.local or the root .env).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as W from "./datacenter-ways.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
function env(name) {
  if (process.env[name]) return process.env[name];
  for (const f of [path.join(here, "..", ".env.local"), path.join(here, "..", "..", ".env")]) {
    if (!fs.existsSync(f)) continue;
    const m = fs.readFileSync(f, "utf-8").match(new RegExp(`^${name}=(.*)$`, "m"));
    if (m) return m[1].trim().replace(/^["']|["']$/g, "");
  }
  return "";
}
const origin = env("SUPABASE_URL").replace(/\/rest\/v1\/?$/, "").replace(/\/$/, ""), key = env("SUPABASE_ANON_KEY");
async function q(table, params) {
  const res = await fetch(`${origin}/rest/v1/${table}?${new URLSearchParams(params)}`, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
  if (!res.ok) throw new Error(`${table}: HTTP ${res.status} ${await res.text()}`);
  return res.json();
}
async function all(table, params) {
  const out = [];
  for (let off = 0; ; off += 1000) {
    const b = await q(table, { ...params, limit: "1000", offset: String(off) });
    out.push(...b);
    if (b.length < 1000) return out;
  }
}
const A = await import("../lib/datacenter/answers.ts");
const R = A;
const query = Object.fromEntries(new URLSearchParams(process.argv[2] ?? ""));
const page = W.pageOf(query);
const x = page.x, g = W.INDEX.grids[x.grid];
const l12 = (page.l12 ?? []).map((r) => r.m);
const t0 = Date.now();
const a = await R.readAnswers({ grid: x.grid, mw: x.mw, l12, behind: g.std_hours_behind_utc, ruled: await W.ruledWays(page), rows: all });
const stats = ["scarce:hours", "scarce:flat_usd", "scarce:off:flex", "scarce:avoided_usd:flex", "scarce:off:shift", "scarce:avoided_usd:shift", "co2:l12:kg:flat", "co2:l12:tonnes:flat", "co2:l12:kg:flex", "co2:l12:tonnes:shift", "co2:window:flat", "co2:window:flex", "co2:window:shift", "co2:window:grid", "co2:window:hours", "co2:year:2019", "co2:year:2025", "ll:latest:approved", "ll:approved_change", "notices:count"];
console.log(JSON.stringify({ x, l12: [l12[0], l12.at(-1)], ms: Date.now() - t0, held: a.held, stats: Object.fromEntries(stats.map((s) => [s, A.statOf(a, s)])), byMonth: a.scarcity.byMonth, from: a.scarcity.from, to: a.scarcity.to, window: a.carbon.window, years: a.carbon.years, latest: a.largeLoad?.latest, yearAgo: a.largeLoad?.yearAgo, notices: a.notices }, null, 1));
