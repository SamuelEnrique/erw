// Energy Research Warehouse (ERW) site: check rendered numbers against direct Supabase queries.
//
//   npm run build && npm start           (the site on http://localhost:3000)
//   node scripts/check-values.mjs [base-url]
//
// Every number the pages render through components/Num.tsx carries data-check (the Supabase
// table and key it was read from) and data-raw (the value as read). For each one, this script
// runs its own query against Supabase's REST API with SUPABASE_URL and SUPABASE_ANON_KEY (from the
// environment or site/.env.local), independent of lib/, and checks:
//   1. the value Supabase returns equals data-raw;
//   2. the text on the page equals data-raw rounded as displayed (2 decimals, or a whole count).
// Prints one line per value and a summary; exits 1 if any value fails or fewer than ten were checked.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3000";
const PAGES = ["/", "/prices", "/prices/ercot%3AHB_HUBAVG", "/data", "/explorer/ercot-peak-premium", "/deals", "/grid", "/map", "/datacenters", "/weekly",
  // session 18
  "/mix", "/mix?ba=erco&state=TX", "/curtailment", "/consumption",
  // session 19
  "/markets"];

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
  if (fs.existsSync(f)) {
    for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z_]+)=(.*)$/);
      if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, "");
    }
  }
  throw new Error(`${name} is not set`);
}
const origin = new URL(env("SUPABASE_URL")).origin;
const key = env("SUPABASE_ANON_KEY");

async function q(table, params, countOnly = false) {
  const res = await fetch(`${origin}/rest/v1/${table}?${new URLSearchParams(params)}`, {
    headers: { apikey: key, Authorization: `Bearer ${key}`, ...(countOnly ? { Prefer: "count=exact", Range: "0-0" } : {}) },
  });
  if (!res.ok) throw new Error(`${table}: HTTP ${res.status} ${(await res.text()).slice(0, 200)}`);
  if (countOnly) return Number(res.headers.get("content-range").split("/")[1]);
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

/** The value Supabase holds for one data-check key. */
async function truth(check) {
  const p = check.split("|");
  if (p[0] === "catalogue") {
    if (p[1] === "count") return q("catalogue", { select: "table_name", license: "eq.public" }, true);
    if (p[1] === "n_pass") return q("catalogue", { select: "table_name", license: "eq.public", validator_status: "eq.pass" }, true);
    if (p[1] === "sum_n_rows") return (await all("catalogue", { select: "n_rows", license: "eq.public" })).reduce((a, r) => a + Number(r.n_rows), 0);
    if (p[1] === "max_last_run") return (await q("catalogue", { select: "last_run", license: "eq.public", order: "last_run.desc.nullslast", limit: "1" }))[0].last_run;
    return (await q("catalogue", { select: "n_rows", table_name: `eq.${p[1]}` }))[0]?.n_rows;
  }
  if (p[0] === "latest_prices") {
    return (await q("latest_prices", { select: "value", entity: `eq.${p[1]}`, variable: `eq.${p[2]}` }))[0]?.value;
  }
  if (p[0] === "series") {
    const [, table, entity, variable, at] = p;
    const params = { select: "value,ts_utc", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}` };
    if (at === "newest") Object.assign(params, { order: "ts_utc.desc", limit: "1" });
    else params.ts_utc = `eq.${at}`;
    return (await q("series", params))[0]?.value;
  }
  // session 15: /deals and /grid
  if (p[0] === "deals") {
    const [, what, month] = p;
    const rows = await all("events", { select: "event_date,mw,ai:extra->>ai_power", table_name: "eq.energy_deals" });
    const m = rows.filter((r) => String(r.event_date).slice(0, 7) === month);
    if (what === "month_count") return m.length;
    if (what === "month_mw") return m.reduce((a, r) => a + (r.mw === null ? 0 : Number(r.mw)), 0);
    if (what === "month_ai_pct") return m.length ? Math.round((100 * m.filter((r) => r.ai === "true").length) / m.length) : null;
  }
  if (p[0] === "event") {
    const [, table, id, field] = p;
    const col = field === "mw" ? "v:mw" : `v:extra->>${field}`;
    const r = (await q("events", { select: col, table_name: `eq.${table}`, event_id: `eq.${id}` }))[0];
    return r ? Number(r.v) : undefined;
  }
  if (p[0] === "series_max" || p[0] === "series_sum") {
    const [, table, variable, start, end] = p;
    const rows = await all("series", { select: "value", table_name: `eq.${table}`, variable: `eq.${variable}`,
      and: `(ts_utc.gte.${start},ts_utc.lt.${end})`, order: "entity,ts_utc" });
    if (!rows.length) return undefined;
    return p[0] === "series_max" ? Math.max(...rows.map((r) => r.value)) : rows.reduce((a, r) => a + r.value, 0);
  }
  // session 18: a sum over one entity's rows in a time range (/mix, /curtailment, /consumption)
  if (p[0] === "series_esum") {
    const [, table, entity, variable, start, end] = p;
    const rows = await all("series", { select: "value", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${variable}`,
      and: `(ts_utc.gte.${start},ts_utc.lt.${end})`, order: "ts_utc" });
    if (!rows.length) return undefined;
    return rows.reduce((a, r) => a + r.value, 0);
  }
  // session 16: /map (energy_projects, and datacenter_projects as the kind datacenter) and /datacenters
  if (p[0] === "projects") {
    const [, what, kind, arg] = p;
    const table = kind === "datacenter" ? "datacenter_projects" : "energy_projects";
    const base = { select: "entity_id", table_name: `eq.${table}`, "extra->>kind": `eq.${kind}` };
    if (what === "count") {
      if (arg === "all") return q("entities", base, true);
      const prec = arg === "county" && kind === "datacenter" ? "in.(county,place)" : `eq.${arg}`;
      return q("entities", { ...base, "extra->>geo_precision": prec }, true);
    }
    if (what === "tech_count") return q("entities", { ...base, "extra->>technology_group": `eq.${arg}` }, true);
    if (what === "mw") {
      const rows = await all("entities", { ...base, select: "capacity_mw", order: "entity_id" });
      return rows.reduce((a, r) => a + (r.capacity_mw === null ? 0 : Number(r.capacity_mw)), 0);
    }
  }
  if (p[0] === "datacenters") {
    const [, what, key] = p;
    const rows = await all("entities", { select: "operator,mw:capacity_mw,state:extra->>state", table_name: "eq.datacenter_projects", order: "entity_id" });
    const withMw = rows.filter((r) => r.mw !== null);
    if (what === "count") return rows.length;
    if (what === "n_with_mw") return withMw.length;
    if (what === "mw_total") return withMw.reduce((a, r) => a + Number(r.mw), 0);
    if (what === "state_mw") return withMw.filter((r) => r.state === key).reduce((a, r) => a + Number(r.mw), 0);
    if (what === "operator_mw") return withMw.filter((r) => r.operator === key).reduce((a, r) => a + Number(r.mw), 0);
  }
  throw new Error(`unknown check ${check}`);
}

/** US dollars, short, as site/app/deals/DealsTable.tsx writes them (data-format usd). */
function usd(v) {
  const t = (x) => x.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (Math.abs(v) >= 1e9) return `${t(v / 1e9)} billion`;
  if (Math.abs(v) >= 1e6) return `${t(v / 1e6)} million`;
  return v.toLocaleString("en-US");
}

function shown(raw) {
  // how the page writes a raw value: a timestamp as "YYYY-MM-DD HH:MM UTC", a whole number with commas, else 2 decimals
  if (/^\d{4}-\d{2}-\d{2}T/.test(raw)) return new Date(raw).toISOString().slice(0, 16).replace("T", " ") + " UTC";
  const x = Number(raw);
  return Number.isInteger(x) ? x.toLocaleString("en-US") : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function decode(s) {
  return s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#x27;/g, "'");
}

// Session 17: /weekly. The weekly brief is markdown (docs/weekly/), not Num spans, so its numbers are
// parsed from the rendered page and recomputed here from Supabase: the day-ahead weekly means (the ISO's
// local week), the real-time peak's value at its interval, the fuel closes on their dates, and the US48
// peak demand (the maximum of the week to the hour the brief read to).
const HUB = {
  ERCOT: ["ercot_dam_hub_prices", "America/Chicago"], CAISO: ["caiso_dam_hub_prices", "America/Los_Angeles"],
  NYISO: ["nyiso_dam_zone_prices", "America/New_York"], MISO: ["miso_dam_hub_prices", "Etc/GMT+5"],
  SPP: ["spp_dam_hub_prices", "America/Chicago"], "ISO-NE": ["isone_dam_zone_prices", "America/New_York"],
};
const FUEL = { "Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent" };

function tzOffsetMs(utcMs, tz) {
  const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" }).formatToParts(new Date(utcMs)).map((x) => [x.type, x.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - utcMs;
}
function localMidnight(y, m, d, tz) {
  const guess = Date.UTC(y, m, d);
  return new Date(guess - tzOffsetMs(guess - tzOffsetMs(guess, tz), tz));
}
function isoWeekMonday(label) {
  const [y, w] = label.split("-W").map(Number);
  const jan4 = new Date(Date.UTC(y, 0, 4));
  const mon = new Date(jan4.getTime() - ((jan4.getUTCDay() + 6) % 7) * 864e5);
  return new Date(mon.getTime() + (w - 1) * 7 * 864e5);
}
const cells = (row) => [...row.matchAll(/<td[^>]*>([\s\S]*?)<\/td>/g)].map((m) => decode(m[1].replace(/<[^>]+>/g, "")).trim());

async function checkWeekly(lines) {
  const html = await fetch(base + "/weekly").then((r) => r.text());
  const label = (html.match(/Energy Week, (\d{4}-W\d{2})/) || [])[1];
  if (!label) return [0, 0];
  const mon = isoWeekMonday(label);
  let ok = 0, bad = 0;
  const report = (pass, what, shown, truth) => {
    pass ? ok++ : bad++;
    lines.push(`${pass ? "ok  " : "FAIL"} | /weekly | ${what} | page shows "${shown}" | Supabase ${truth}`);
  };
  for (const row of html.split("<tr>").slice(1)) {
    const c = cells(row);
    if (HUB[c[0]] && c.length >= 5) {
      const [table, tz] = HUB[c[0]];
      for (const [k, back] of [[2, 0], [3, 7]]) {
        if (!/^-?\d+\.\d{2}$/.test(c[k])) continue;
        const d0 = new Date(mon.getTime() - back * 864e5);
        const s0 = localMidnight(d0.getUTCFullYear(), d0.getUTCMonth(), d0.getUTCDate(), tz);
        const s1 = localMidnight(d0.getUTCFullYear(), d0.getUTCMonth(), d0.getUTCDate() + 7, tz);
        const rows = await all("series", { select: "value", table_name: `eq.${table}`, node: `eq.${c[1]}`,
          and: `(ts_utc.gte.${s0.toISOString()},ts_utc.lt.${s1.toISOString()})`, order: "ts_utc" });
        const hours = (s1 - s0) / 36e5;
        // exact: prices summed as integers of millionths, the mean rounded half up to cents (as brief.mean2)
        const micro = rows.reduce((a, r) => a + Math.round(r.value * 1e6), 0);
        const x = micro / rows.length / 1e4;
        const cents = rows.length ? Math.sign(x) * Math.floor(Math.abs(x) + 0.5) : NaN; // half away from zero, as ROUND_HALF_UP
        const truth = rows.length === hours ? (cents / 100).toFixed(2) : `${rows.length} of ${hours} hours`;
        report(truth === c[k], `dam_week_mean|${table}|${c[1]}|${back ? "week before" : "week"}`, c[k], truth);
      }
    }
    if (FUEL[c[0]]) {
      for (const k of [1, 2]) {
        const m = c[k].match(/^(\d+\.\d{2}) .*?on (\d{4}-\d{2}-\d{2})$/);
        if (!m) continue;
        const r = (await q("series", { select: "value", table_name: "eq.eia_fuel_spot_prices", entity: `eq.${FUEL[c[0]]}`,
          ts_utc: `eq.${m[2]}T00:00:00Z` }))[0];
        report(r && r.value.toFixed(2) === m[1], `fuel_close|${FUEL[c[0]]}|${m[2]}`, m[1], r ? r.value.toFixed(2) : "absent");
      }
    }
  }
  const text = decode(html.replace(/<[^>]+>/g, ""));
  // session 21: the table is a footnote ("lmp_rtm_15m_mean [2]", and "[2] nyiso_rtm_zone_prices (...)" in the Tables list)
  const foot = Object.fromEntries([...text.matchAll(/\[(\d+)\] ([a-z0-9_]+) \(/g)].map((m) => [m[1], m[2]]));
  const m0 = text.match(/Highest real-time price of the week:\s*([\d,.]+) USD\/MWh at (.+?) \([A-Z-]+\), interval starting .*?\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\), (\w+) \[(\d+)\]/);
  const rt = m0 ? [m0[0], m0[1], m0[2], m0[3], m0[4], foot[m0[5]]] : null;
  if (rt && rt[5]) {
    const r = (await q("series", { select: "value", table_name: `eq.${rt[5]}`, node: `eq.${rt[2]}`, variable: `eq.${rt[4]}`,
      ts_utc: `eq.${rt[3].replace(" ", "T")}:00Z` }))[0];
    report(r && r.value.toFixed(2) === rt[1], `rt_peak|${rt[5]}|${rt[2]}|${rt[3]}`, rt[1], r ? r.value.toFixed(2) : "absent");
  }
  const pk = text.match(/US48 peak demand of the week:\s*([\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC.*?to (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC/);
  if (pk) {
    const to = new Date(pk[3].replace(" ", "T") + ":00Z");
    const rows = await all("series", { select: "value,ts_utc", table_name: "eq.eia930_us48_demand", variable: "eq.demand_mw",
      and: `(ts_utc.gte.${mon.toISOString()},ts_utc.lte.${to.toISOString()})`, order: "ts_utc" });
    const top = rows.reduce((a, r) => (a === null || r.value > a.value ? r : a), null);
    const truth = top ? `${Math.round(top.value).toLocaleString("en-US")} at ${new Date(top.ts_utc).toISOString().slice(0, 16).replace("T", " ")}` : "absent";
    report(truth === `${pk[1]} at ${pk[2]}`, "us48_peak_week", `${pk[1]} at ${pk[2]}`, truth);
  }
  return [ok, bad];
}

async function main() {
  const found = new Map();
  for (const page of PAGES) {
    const html = await fetch(base + page).then((r) => {
      if (!r.ok) throw new Error(`${page}: HTTP ${r.status}`);
      return r.text();
    });
    const re = /<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)<\/span>/g;
    for (const m of html.matchAll(re)) {
      const text = decode(m[3].replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "")).trim();
      const check = decode(m[1]);
      const usdFormat = html.slice(Math.max(0, m.index - 30), m.index).endsWith('<span data-format="usd">');
      if (!found.has(check)) found.set(check, { page, raw: decode(m[2]), text, usdFormat });
    }
  }
  let ok = 0, bad = 0;
  const lines = [];
  for (const [check, { page, raw, text, usdFormat }] of found) {
    const t = await truth(check);
    const isTime = /^\d{4}-\d{2}-\d{2}T/.test(raw);
    // sums of floats may differ in the last bits with the order of addition: relative tolerance
    const same = isTime ? new Date(t).getTime() === new Date(raw).getTime() : Math.abs(Number(t) - Number(raw)) < 1e-9 * Math.max(1, Math.abs(Number(t)));
    // session 16: MW sums are written as whole MW (lib/format.ts count)
    const whole = /(^projects\|mw\|)|(^datacenters\|(mw_total|state_mw|operator_mw))/.test(check);
    const textOk = text.startsWith(usdFormat ? usd(Number(raw)) : whole ? Math.round(Number(raw)).toLocaleString("en-US") : shown(raw));
    const pass = t !== undefined && t !== null && same && textOk;
    pass ? ok++ : bad++;
    lines.push(`${pass ? "ok  " : "FAIL"} | ${page} | ${check} | page shows "${text}" | page read ${raw} | Supabase ${t}`);
  }
  const [wok, wbad] = await checkWeekly(lines);
  ok += wok;
  bad += wbad;
  const n = found.size + wok + wbad;
  console.log(lines.join("\n"));
  console.log(`\n${ok} of ${n} values match Supabase${bad ? `; ${bad} FAILED` : ""} (/weekly: ${wok} of ${wok + wbad})`);
  if (bad || n < 10) process.exit(1);
}

main().catch((e) => {
  console.error(`check-values FAILED: ${e.message}`);
  process.exit(1);
});
