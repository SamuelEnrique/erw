// Energy Research Warehouse (ERW) site, session 293: a dated edition of the problem sets (Samuel's ruling 8a of
// 14 October 2026: a dated edition of each set beside the live one).
//
//   node --import ./scripts/alias-register.mjs scripts/build-problem-edition.mjs [YYYY-MM-DD]     (default: today, UTC)
//
// Builds all five sets with lib/problems.ts exactly as the live pages do, from the live set (SUPABASE_URL and
// SUPABASE_ANON_KEY from the environment or site/.env.local), and freezes them with their date:
//   data/problem_editions/<date>.json            every question, answer, worked solution and figure, as built
//   public/problems/<date>/<slug>-<id>.csv       for each question, the rows it needs (its download)
//   data/problem_editions/index.json             the editions held, newest first
// The rows of a question are read from its figures' check keys (the keys check-values.mjs recomputes): a series row,
// the rows of a sum or a maximum over a range, the rows of a month's mean, the two rows of a battery cycle. A figure
// computed from a committed file rather than a table (the bill rules, the severance rules, the merchant snapshot, the
// network snapshot, the game's battery) is a row of its own, its source the file, marked "computed". Nothing is typed
// or filled. Reads only; writes the three files. Every request carries x-erw-check: 1.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.join(here, "..");
const env = (k) => process.env[k] ?? (fs.readFileSync(path.join(site, ".env.local"), "utf-8").match(new RegExp(`^${k}=(.*)$`, "m"))?.[1] ?? "").trim();
for (const k of ["SUPABASE_URL", "SUPABASE_ANON_KEY"]) if (!process.env[k]) process.env[k] = env(k);
const date = process.argv[2] ?? new Date().toISOString().slice(0, 10);
if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) { console.error(`not a date: ${date}`); process.exit(2); }

const { problemSet, SETS } = await import("@/lib/problems");
let REST = process.env.SUPABASE_URL.replace(/\/$/, "");
if (!REST.endsWith("/rest/v1")) REST += "/rest/v1";
const KEY = process.env.SUPABASE_ANON_KEY;
const q = async (params) => {
  const u = `${REST}/series?${new URLSearchParams({ select: "entity,variable,ts_utc,value,unit,event", order: "entity,variable,ts_utc", ...params })}`;
  const r = await fetch(u, { headers: { apikey: KEY, Authorization: `Bearer ${KEY}`, "x-erw-check": "1" } });
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${u}`);
  return r.json();
};
const range = (a, b) => `(ts_utc.gte.${a},ts_utc.lt.${b})`;
const nextMonth = (m) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 1)).toISOString().slice(0, 7);
const FILES = { bill: "site/data/bill_rules.json", sev: "site/data/severance_rules.json", sevcert: "site/data/severance_rules.json", sevcredit: "site/data/severance_rules.json",
  mr: "site/data/merchant_snapshot.json", mrs: "site/data/merchant_snapshot.json", net: "the network snapshot (lib/network.ts)", battery: "site/lib/battery.ts" };

/** The rows behind one check key, as table rows ({ source: table, ... }) or one computed row. */
async function rowsOf(k, v, u) {
  const p = k.split("|");
  if (p[0] === "calc") return [...(await rowsOf(p[2].replaceAll("~", "|"))), ...(await rowsOf(p[3].replaceAll("~", "|")))];
  if (p[0] === "series") {
    const [, t, e, variable, ts, event] = p;
    return (await q({ table_name: `eq.${t}`, entity: `eq.${e}`, variable: `eq.${variable}`, ts_utc: `eq.${ts}`, ...(event ? { event: `eq.${event}` } : {}) })).map((r) => ({ source: t, ...r }));
  }
  if (p[0] === "series_max" || p[0] === "series_sum") {
    const [, t, variable, a, b, e] = p;
    return (await q({ table_name: `eq.${t}`, variable: `eq.${variable}`, and: range(a, b), ...(e ? { entity: `eq.${e}` } : {}) })).map((r) => ({ source: t, ...r }));
  }
  if (p[0] === "spotmean") {
    const [, e, m] = p;
    return (await q({ table_name: "eq.eia_fuel_spot_prices", entity: `eq.${e}`, variable: "eq.spot_price", and: range(`${m}-01T00:00:00Z`, `${nextMonth(m)}-01T00:00:00Z`) })).map((r) => ({ source: "eia_fuel_spot_prices", ...r }));
  }
  if (p[0] === "battery" && (p[1] === "cycle" || p[1] === "cycle_fleet")) {
    const [, , t, e, ts, buy, sell] = p;
    return (await q({ table_name: `eq.${t}`, entity: `eq.${e}`, ts_utc: `eq.${ts}`, variable: `in.(${buy},${sell})` })).map((r) => ({ source: t, ...r }));
  }
  if (p[0] === "bill" && p[3]) {
    const R = JSON.parse(fs.readFileSync(path.join(site, "data", "bill_rules.json"), "utf-8")).bills;
    const ent = R[p[1]].wholesale_entity;
    const t = (await q({ table_name: "eq.cost_of_power_monthly", entity: `eq.${ent}`, variable: "eq.rt_load_weighted", ts_utc: `eq.${p[3]}` })).map((r) => ({ source: "cost_of_power_monthly", ...r }));
    return v === undefined ? t : [...t, { source: FILES.bill, entity: "", variable: k, ts_utc: "", value: v, unit: u ?? "", event: "", note: "computed" }];
  }
  if (v === undefined) return [];  // a key inside a calc whose own figure is not shown: its rows come with the shown figure
  return [{ source: FILES[p[0]] ?? p[0], entity: "", variable: k, ts_utc: "", value: v, unit: u ?? "", event: "", note: "computed" }];
}
const isV = (x) => typeof x === "object" && x !== null && "k" in x;
const csvCell = (x) => { const s = x === null || x === undefined ? "" : String(x); return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s; };

const built = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
const out = { date, built_at: built, note: "Built by site/scripts/build-problem-edition.mjs with lib/problems.ts from the ERW live set; frozen: the live sets move as the tables update.", sets: [] };
const pub = path.join(site, "public", "problems", date);
fs.mkdirSync(pub, { recursive: true });
for (const meta of SETS) {
  const set = await problemSet(meta.slug);
  const qs = [];
  for (const [n, qu] of set.questions.entries()) {
    const parts = [...qu.answer, ...qu.steps.flat()].filter(isV);
    const rows = [];
    const seen = new Set();
    for (const x of parts) {
      for (const r of await rowsOf(x.k, x.v, x.u)) {
        const id = `${r.source}|${r.entity}|${r.variable}|${r.ts_utc}|${r.event ?? ""}`;
        if (seen.has(id)) continue;
        seen.add(id);
        rows.push({ source: r.source, entity: r.entity, variable: r.variable, ts_utc: r.ts_utc, value: r.value, unit: r.unit ?? "", event: r.event ?? "", note: r.note ?? "" });
      }
    }
    const file = `${meta.slug}-${qu.id}.csv`;
    const head = [
      `# ERW problem sets, the edition of ${date}: "${meta.title}", question ${n + 1} (${qu.id}): the rows it needs.`,
      `# Read from the ERW live set (Supabase table series) on ${built} by site/scripts/build-problem-edition.mjs; a row marked "computed" is a figure lib/ computes from the file named in "source", not a table row.`,
      `# Question: ${qu.q.replaceAll("\n", " ")}`,
    ];
    const body = ["source,entity,variable,ts_utc,value,unit,event,note", ...rows.map((r) => [r.source, r.entity, r.variable, r.ts_utc, r.value, r.unit, r.event, r.note].map(csvCell).join(","))];
    fs.writeFileSync(path.join(pub, file), [...head, ...body].join("\n") + "\n");
    qs.push({ ...qu, rows: rows.length, csv: `/problems/${date}/${file}` });
    console.log(`${meta.slug} ${qu.id}: ${rows.length} rows -> public/problems/${date}/${file}`);
  }
  out.sets.push({ ...meta, questions: qs });
}
const dir = path.join(site, "data", "problem_editions");
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, `${date}.json`), JSON.stringify(out, null, 1) + "\n");
const idx = path.join(dir, "index.json");
const held = fs.existsSync(idx) ? JSON.parse(fs.readFileSync(idx, "utf-8")).editions : [];
fs.writeFileSync(idx, JSON.stringify({ editions: [...new Set([date, ...held])].sort().reverse() }, null, 1) + "\n");
console.log(`the edition of ${date}: ${out.sets.length} sets, ${out.sets.reduce((a, s) => a + s.questions.length, 0)} questions`);
